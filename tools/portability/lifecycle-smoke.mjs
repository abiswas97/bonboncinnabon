#!/usr/bin/env node

import { execFile, spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import { access, mkdir, mkdtemp, readFile, readdir, symlink, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import readline from "node:readline";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";

const execFileAsync = promisify(execFile);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const OPT_IN = "BONBON_AUTHENTICATED_LIFECYCLE_SMOKE";
const TIMEOUT = 180_000;

if (process.platform !== "darwin") throw new Error("Authenticated lifecycle smoke is supported on macOS only.");
if (process.env[OPT_IN] !== "1") {
  throw new Error(`Authenticated lifecycle smoke is opt-in. Re-run with ${OPT_IN}=1.`);
}

async function localBinary(name) {
  const candidate = path.join(ROOT, "node_modules/.bin", name);
  try {
    await access(candidate);
    return candidate;
  } catch {
    return name;
  }
}

async function run(command, args, { cwd = ROOT, env = {}, timeout = TIMEOUT } = {}) {
  try {
    return await execFileAsync(command, args, {
      cwd,
      env: { ...process.env, ...env, NO_COLOR: "1" },
      timeout,
      maxBuffer: 8 * 1024 * 1024,
    });
  } catch (error) {
    throw new Error(`${command} ${args.join(" ")} failed:\n${error.stdout ?? ""}${error.stderr ?? error.message}`);
  }
}

async function installedStandardsRoot(config) {
  const entries = await readdir(config, { recursive: true });
  const manifest = entries.find((entry) =>
    entry.replaceAll("\\", "/").endsWith("standards/0.1.0/plugin.json"),
  );
  if (!manifest) throw new Error(`Standards installation not found under ${config}`);
  return path.dirname(path.join(config, manifest));
}

async function installClaude(root) {
  const home = path.join(root, "claude-home");
  const config = path.join(home, ".claude");
  await mkdir(config, { recursive: true });
  const claude = await localBinary("claude");
  const env = { HOME: home, CLAUDE_CONFIG_DIR: config };
  await run(claude, ["plugin", "marketplace", "add", ROOT], { env });
  await run(claude, ["plugin", "install", "standards@bonboncinnabon"], { env });
  return { claude, config, env, pluginRoot: await installedStandardsRoot(config) };
}

async function installCodex(root) {
  const home = path.join(root, "codex-home");
  const config = path.join(home, ".codex");
  await mkdir(config, { recursive: true });
  const authSource = process.env.CODEX_AUTH_FILE ?? path.join(os.homedir(), ".codex/auth.json");
  await access(authSource);
  await symlink(authSource, path.join(config, "auth.json"));
  const codex = await localBinary("codex");
  const env = { HOME: home, CODEX_HOME: config };
  await run(codex, ["plugin", "marketplace", "add", ROOT, "--json"], { env });
  await run(codex, ["plugin", "add", "standards@bonboncinnabon", "--json"], { env });
  const configFile = path.join(config, "config.toml");
  await writeFile(
    configFile,
    `model_auto_compact_token_limit = 30000\n${await readFile(configFile, "utf8")}`,
  );
  return { codex, config, env, pluginRoot: await installedStandardsRoot(config) };
}

async function readTrace(file) {
  const contents = await readFile(file, "utf8");
  return contents.split("\n").filter(Boolean).map((line) => JSON.parse(line));
}

function requireTrace(records, predicate, label) {
  if (!records.some(predicate)) throw new Error(`Lifecycle smoke did not observe ${label}`);
}

async function smokeClaude(root, workspace) {
  const installed = await installClaude(root);
  const trace = path.join(root, "claude-lifecycle.jsonl");
  const authConfig = process.env.CLAUDE_AUTH_CONFIG_DIR ??
    (await access(path.join(os.homedir(), ".cloak/profiles/personal")).then(
      () => path.join(os.homedir(), ".cloak/profiles/personal"),
      () => path.join(os.homedir(), ".claude"),
    ));
  const env = {
    ...installed.env,
    HOME: os.homedir(),
    CLAUDE_CONFIG_DIR: authConfig,
    STANDARDS_TRACE_FILE: trace,
  };
  const prompt = [
    "Use the Write tool to create claude-smoke.txt containing ok.",
    "Start one Explore subagent and ask it to confirm the file name.",
    "Then reply exactly CLAUDE_LIFECYCLE_OK.",
  ].join(" ");
  await run(
    installed.claude,
    [
      "-p",
      "--plugin-dir",
      installed.pluginRoot,
      "--permission-mode",
      "bypassPermissions",
      "--allowedTools",
      "Write,Agent,Read",
      "--max-turns",
      "8",
      prompt,
    ],
    { cwd: workspace, env },
  );
  try {
    await run(
      installed.claude,
      [
        "-p",
        "--plugin-dir",
        installed.pluginRoot,
        "--permission-mode",
        "plan",
        "--max-turns",
        "2",
        "Draft a two-line implementation plan. Do not edit files.",
      ],
      { cwd: workspace, env },
    );
  } catch (error) {
    if (!error.message.includes("Reached max turns")) throw error;
  }
  const compactSession = randomUUID();
  await run(
    installed.claude,
    ["-p", "--plugin-dir", installed.pluginRoot, "--session-id", compactSession, "Reply exactly ONE."],
    { cwd: workspace, env },
  );
  await run(
    installed.claude,
    ["-p", "--plugin-dir", installed.pluginRoot, "--resume", compactSession, "Reply exactly TWO."],
    { cwd: workspace, env },
  );
  await run(
    installed.claude,
    ["-p", "--plugin-dir", installed.pluginRoot, "--resume", compactSession, "/compact"],
    { cwd: workspace, env },
  );
  const records = await readTrace(trace);
  requireTrace(records, (record) => record.event === "SessionStart" && record.source === "startup" && record.delivered, "Claude startup delivery");
  requireTrace(records, (record) => record.event === "UserPromptSubmit", "Claude prompt delivery");
  requireTrace(records, (record) => record.event === "UserPromptSubmit" && record.permissionMode === "plan" && record.delivered, "Claude Plan-mode delivery");
  requireTrace(records, (record) => record.event === "PostToolUse" && record.toolName === "Write" && record.delivered, "Claude edit delivery");
  requireTrace(records, (record) => record.event === "SubagentStart" && record.delivered, "Claude subagent delivery");
  requireTrace(records, (record) => record.event === "SessionStart" && record.source === "compact" && record.delivered, "Claude compact delivery");
  return {
    installedPlugin: path.relative(root, installed.pluginRoot),
    events: [...new Set(records.map(({ event }) => event))],
    sessionSources: [...new Set(records.filter(({ event }) => event === "SessionStart").map(({ source }) => source))],
    planPermissionMode: records.find(({ event, permissionMode }) => event === "UserPromptSubmit" && permissionMode === "plan")?.permissionMode,
    shutdown: "normal command exit",
  };
}

class AppServer {
  constructor(command, { cwd, env }) {
    this.pending = new Map();
    this.notifications = [];
    this.nextId = 1;
    this.waiters = new Map();
    this.child = spawn(command, ["app-server", "--stdio"], {
      cwd,
      env: { ...process.env, ...env, NO_COLOR: "1" },
      stdio: ["pipe", "pipe", "pipe"],
    });
    readline.createInterface({ input: this.child.stdout }).on("line", (line) => this.onLine(line));
    this.stderr = "";
    this.child.stderr.on("data", (chunk) => {
      this.stderr += chunk.toString();
    });
  }

  onLine(line) {
    let message;
    try {
      message = JSON.parse(line);
    } catch {
      return;
    }
    if (message.id !== undefined && this.pending.has(message.id)) {
      const { resolve, reject, timer, method } = this.pending.get(message.id);
      clearTimeout(timer);
      this.pending.delete(message.id);
      if (message.error) reject(new Error(`${method}: ${message.error.message}`));
      else resolve(message.result);
      return;
    }
    this.notifications.push(message);
    const waiters = this.waiters.get(message.method) ?? [];
    waiters.splice(0).forEach(({ resolve, timer }) => {
      clearTimeout(timer);
      resolve(message.params);
    });
  }

  send(message) {
    this.child.stdin.write(`${JSON.stringify(message)}\n`);
  }

  request(method, params) {
    return new Promise((resolve, reject) => {
      const id = this.nextId++;
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`${method} timed out`));
      }, TIMEOUT);
      this.pending.set(id, { resolve, reject, timer, method });
      this.send({ id, method, params });
    });
  }

  waitFor(method) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error(`${method} notification timed out`)), TIMEOUT);
      const waiters = this.waiters.get(method) ?? [];
      waiters.push({ resolve, timer });
      this.waiters.set(method, waiters);
    });
  }

  async close() {
    this.child.stdin.end();
    await new Promise((resolve) => {
      const timer = setTimeout(() => {
        this.child.kill("SIGTERM");
        resolve();
      }, 5_000);
      this.child.once("exit", () => {
        clearTimeout(timer);
        resolve();
      });
    });
  }
}

async function smokeCodex(root, workspace) {
  const installed = await installCodex(root);
  const trace = path.join(root, "codex-lifecycle.jsonl");
  const server = new AppServer(installed.codex, {
    cwd: workspace,
    env: { ...installed.env, STANDARDS_TRACE_FILE: trace },
  });
  try {
    await server.request("initialize", {
      clientInfo: { name: "bonbon_lifecycle_smoke", title: "Bonbon Lifecycle Smoke", version: "0.1.0" },
      capabilities: { experimentalApi: true },
    });
    server.send({ method: "initialized", params: {} });
    const listed = await server.request("hooks/list", { cwds: [workspace] });
    const hooks = listed.data?.flatMap((entry) => entry.hooks ?? []) ?? [];
    const standardsHooks = hooks.filter((hook) =>
      [hook.key, hook.source, hook.command].some((value) => JSON.stringify(value ?? "").includes("standards")),
    );
    if (!standardsHooks.length) {
      throw new Error(
        `Codex app-server did not list installed Standards hooks: ${JSON.stringify(
          hooks.map(({ key, eventName, source }) => ({ key, eventName, source })),
        )}`,
      );
    }
    if (standardsHooks.some(({ currentHash }) => typeof currentHash !== "string" || !currentHash)) {
      throw new Error("Codex app-server returned a Standards hook without a current hash");
    }
    await server.request("config/batchWrite", {
      edits: [
        {
          keyPath: "hooks.state",
          value: Object.fromEntries(
            standardsHooks.map((hook) => [hook.key, { enabled: true, trusted_hash: hook.currentHash }]),
          ),
          mergeStrategy: "upsert",
        },
      ],
      reloadUserConfig: true,
    });
    const started = await server.request("thread/start", {
      cwd: workspace,
      approvalPolicy: "never",
      sandbox: "danger-full-access",
      ephemeral: true,
      serviceName: "bonbon_lifecycle_smoke",
    });
    const threadId = started.thread.id;
    let completed = server.waitFor("turn/completed");
    await server.request("turn/start", {
      threadId,
      input: [
        {
          type: "text",
          text: "Use apply_patch to create codex-smoke.txt containing ok. Start one subagent to confirm the filename, wait for it, then reply CODEX_LIFECYCLE_OK.",
          text_elements: [],
        },
      ],
    });
    await completed;

    const modes = await server.request("collaborationMode/list", {});
    const plan = modes.data.find(({ mode }) => mode === "plan");
    if (!plan) throw new Error("Codex app-server does not advertise Plan mode");
    completed = server.waitFor("turn/completed");
    await server.request("turn/start", {
      threadId,
      input: [{ type: "text", text: "Provide a two-line plan. Do not call tools.", text_elements: [] }],
      collaborationMode: {
        mode: "plan",
        settings: {
          model: plan.model ?? "gpt-5.6-sol",
          ...(plan.reasoning_effort ? { reasoning_effort: plan.reasoning_effort } : {}),
        },
      },
    });
    await completed;

    await server.request("thread/inject_items", {
      threadId,
      items: [
        {
          type: "message",
          role: "user",
          content: [{ type: "input_text", text: "neutral lifecycle context ".repeat(7_000) }],
        },
      ],
    });
    completed = server.waitFor("turn/completed");
    await server.request("turn/start", {
      threadId,
      input: [{ type: "text", text: "Reply exactly AFTER_COMPACT_OK.", text_elements: [] }],
    });
    await completed;
    completed = server.waitFor("turn/completed");
    await server.request("turn/start", {
      threadId,
      input: [{ type: "text", text: "Reply exactly COMPACTION_CONFIRMED.", text_elements: [] }],
    });
    await completed;

    const records = await readTrace(trace);
    requireTrace(records, (record) => record.event === "SessionStart" && record.source === "startup" && record.delivered, "Codex startup delivery");
    requireTrace(records, (record) => record.event === "SessionStart" && record.source === "compact" && record.delivered, "Codex compact delivery");
    requireTrace(records, (record) => record.event === "UserPromptSubmit", "Codex prompt delivery");
    requireTrace(records, (record) => record.event === "PostToolUse" && record.toolName === "apply_patch" && record.delivered, "Codex edit delivery");
    requireTrace(records, (record) => record.event === "SubagentStart" && record.delivered, "Codex subagent delivery");
    const completedTurns = server.notifications.filter(({ method }) => method === "turn/completed").length;
    if (completedTurns < 4) throw new Error("Codex app-server did not complete all lifecycle turns");
    return {
      installedPlugin: path.relative(root, installed.pluginRoot),
      trustedHookHashes: standardsHooks.map(({ currentHash }) => currentHash),
      events: [...new Set(records.map(({ event }) => event))],
      sessionSources: [...new Set(records.filter(({ event }) => event === "SessionStart").map(({ source }) => source))],
      planPermissionMode: records.filter(({ event }) => event === "UserPromptSubmit")[1]?.permissionMode ?? null,
      completedTurns,
      shutdown: "normal app-server close",
    };
  } finally {
    await server.close();
  }
}

const root = await mkdtemp(path.join(os.tmpdir(), "bonbon-lifecycle-"));
const workspace = path.join(root, "workspace");
await mkdir(workspace);
await writeFile(path.join(workspace, "README.md"), "# Lifecycle smoke\n");
await run("git", ["init", "-q"], { cwd: workspace });
const [claude, codex] = await Promise.all([
  smokeClaude(root, workspace),
  smokeCodex(root, workspace),
]);
process.stdout.write(`${JSON.stringify({ claude, codex }, null, 2)}\n`);
