#!/usr/bin/env node

import { execFile } from "node:child_process";
import { access, mkdir, mkdtemp, readdir } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";

const execFileAsync = promisify(execFile);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");

async function localBinary(name) {
  const candidate = path.join(ROOT, "node_modules/.bin", name);
  try {
    await execFileAsync(candidate, ["--version"], { timeout: 10_000 });
    return candidate;
  } catch {
    return name;
  }
}

async function run(command, args, env) {
  try {
    return await execFileAsync(command, args, {
      cwd: ROOT,
      env: { ...process.env, ...env, NO_COLOR: "1" },
      timeout: 60_000,
      maxBuffer: 2 * 1024 * 1024,
    });
  } catch (error) {
    throw new Error(`${command} ${args.join(" ")} failed:\n${error.stdout ?? ""}${error.stderr ?? error.message}`);
  }
}

function parseJson(stdout, command) {
  try {
    return JSON.parse(stdout);
  } catch {
    throw new Error(`${command}: expected JSON, got ${stdout.slice(0, 500)}`);
  }
}

async function installedFile(config, suffix) {
  const entries = await readdir(config, { recursive: true });
  const normalized = suffix.replaceAll("\\", "/");
  const match = entries.find((entry) => entry.replaceAll("\\", "/").endsWith(normalized));
  if (!match) throw new Error(`Installed package is missing ${suffix}`);
  await access(path.join(config, match));
}

async function smokeClaude() {
  const home = await mkdtemp(path.join(os.tmpdir(), "bonbon-claude-home-"));
  const config = path.join(home, ".claude");
  await mkdir(config);
  const env = { HOME: home, CLAUDE_CONFIG_DIR: config };
  const claude = await localBinary("claude");
  await run(claude, ["plugin", "marketplace", "add", ROOT], env);
  const available = parseJson((await run(claude, ["plugin", "list", "--available", "--json"], env)).stdout, "claude plugin list");
  const serializedAvailable = JSON.stringify(available);
  for (const name of ["postgres", "devlab", "butler", "standards"]) {
    if (!serializedAvailable.includes(name)) throw new Error(`Claude marketplace is missing ${name}`);
  }
  for (const name of ["butler", "standards"]) await run(claude, ["plugin", "install", `${name}@bonboncinnabon`], env);
  const installed = JSON.stringify(parseJson((await run(claude, ["plugin", "list", "--json"], env)).stdout, "claude plugin list"));
  for (const name of ["butler", "standards"]) if (!installed.includes(name)) throw new Error(`Claude did not install ${name}`);
  for (const suffix of [
    "butler/0.11.0/commands/decompose.md",
    "butler/0.11.0/skills/decompose/SKILL.md",
    "standards/0.1.0/commands/standards.md",
    "standards/0.1.0/skills/standards/SKILL.md",
    "standards/0.1.0/hooks/claude.json",
  ]) {
    await installedFile(config, suffix);
  }
}

async function smokeCodex() {
  const home = await mkdtemp(path.join(os.tmpdir(), "bonbon-codex-home-"));
  const config = path.join(home, ".codex");
  await mkdir(config);
  const env = { HOME: home, CODEX_HOME: config };
  const codex = await localBinary("codex");
  await run(codex, ["plugin", "marketplace", "add", ROOT, "--json"], env);
  const available = JSON.stringify(
    parseJson((await run(codex, ["plugin", "list", "--available", "--json"], env)).stdout, "codex plugin list"),
  );
  for (const name of ["butler", "standards"]) {
    if (!available.includes(name)) throw new Error(`Codex marketplace is missing ${name}`);
  }
  for (const excluded of ["postgres", "devlab"]) {
    if (available.includes(excluded)) throw new Error(`Codex marketplace must omit ${excluded}`);
  }
  for (const name of ["butler", "standards"]) {
    await run(codex, ["plugin", "add", `${name}@bonboncinnabon`, "--json"], env);
  }
  const installed = JSON.stringify(parseJson((await run(codex, ["plugin", "list", "--json"], env)).stdout, "codex plugin list"));
  for (const name of ["butler", "standards"]) if (!installed.includes(name)) throw new Error(`Codex did not install ${name}`);
  for (const suffix of [
    "butler/0.11.0/.codex-plugin/plugin.json",
    "butler/0.11.0/skills/decompose/SKILL.md",
    "standards/0.1.0/.codex-plugin/plugin.json",
    "standards/0.1.0/skills/standards/SKILL.md",
    "standards/0.1.0/hooks/hooks.json",
  ]) {
    await installedFile(config, suffix);
  }
}

const requestedHost = process.argv.find((argument) => argument.startsWith("--host="))?.split("=")[1];
if (!requestedHost || requestedHost === "claude") await smokeClaude();
if (!requestedHost || requestedHost === "codex") await smokeCodex();
process.stdout.write(`Isolated ${requestedHost ?? "Claude and Codex"} installation smoke tests passed.\n`);
