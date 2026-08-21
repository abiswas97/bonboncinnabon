#!/usr/bin/env node

import { execFile } from "node:child_process";
import { access, mkdir, mkdtemp, readFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";
import { readJson, validateMarketplace } from "./contracts.mjs";

const execFileAsync = promisify(execFile);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const PACKAGE = JSON.parse(await readFile(path.join(ROOT, "package.json"), "utf8"));
const EXPECTED_CLAUDE_VERSION = PACKAGE.devDependencies?.["@anthropic-ai/claude-code"];
const EXPECTED_CODEX_VERSION = PACKAGE.devDependencies?.["@openai/codex"];

async function pinnedBinary(name) {
  const local = path.join(ROOT, "node_modules/.bin", name);
  try {
    const { stdout } = await execFileAsync(local, ["--version"], { timeout: 10_000 });
    return { command: local, version: stdout.trim() };
  } catch (error) {
    throw new Error(
      `${name}: pinned validator is unavailable at ${path.relative(ROOT, local)}; run npm ci --ignore-scripts and npm run validators:install (${error.message})`,
    );
  }
}

async function run(command, args, environment = {}) {
  try {
    return await execFileAsync(command, args, {
      cwd: ROOT,
      timeout: 30_000,
      maxBuffer: 1024 * 1024,
      env: { ...process.env, NO_COLOR: "1", ...environment },
    });
  } catch (error) {
    throw new Error(`${command} ${args.join(" ")} failed:\n${error.stdout ?? ""}${error.stderr ?? error.message}`);
  }
}

async function assertSkills(installedPath, skillNames, host) {
  for (const skill of skillNames) {
    for (const relative of [
      `skills/${skill}/SKILL.md`,
      ...(host === "Codex" ? [`skills/${skill}/agents/openai.yaml`] : []),
    ]) {
      try {
        await access(path.join(installedPath, relative));
      } catch {
        throw new Error(`${host} clean install is missing ${relative}`);
      }
    }
  }
}

async function validateDevlabInstall(claude, codex) {
  const plugin = await readJson(path.join(ROOT, "plugins/devlab/plugin.json"));
  const selector = "devlab@bonboncinnabon";
  const temporary = await mkdtemp(path.join(os.tmpdir(), "bonbon-devlab-install-"));
  const claudeHome = path.join(temporary, "claude");
  const codexHome = path.join(temporary, "codex");
  try {
    await Promise.all([mkdir(claudeHome), mkdir(codexHome)]);
    await run(codex.command, ["plugin", "marketplace", "add", ROOT, "--json"], { CODEX_HOME: codexHome });
    const codexInstall = await run(codex.command, ["plugin", "add", selector, "--json"], { CODEX_HOME: codexHome });
    const codexResult = JSON.parse(codexInstall.stdout);
    if (codexResult.version !== plugin.version) {
      throw new Error(`Codex installed DevLab ${codexResult.version}, expected ${plugin.version}`);
    }
    await assertSkills(codexResult.installedPath, plugin.components.skills.map(({ name }) => name), "Codex");

    await run(claude.command, ["plugin", "marketplace", "add", ROOT, "--scope", "user"], { CLAUDE_CONFIG_DIR: claudeHome });
    await run(claude.command, ["plugin", "install", selector, "--scope", "user", "--yes"], { CLAUDE_CONFIG_DIR: claudeHome });
    const claudeList = await run(claude.command, ["plugin", "list", "--json"], { CLAUDE_CONFIG_DIR: claudeHome });
    const claudePayload = JSON.parse(claudeList.stdout);
    const claudeInstalled = Array.isArray(claudePayload) ? claudePayload : claudePayload.installed;
    const claudeResult = claudeInstalled.find(({ id }) => id === selector);
    if (!claudeResult || claudeResult.version !== plugin.version) {
      throw new Error(`Claude clean install did not resolve ${selector} at ${plugin.version}`);
    }
    await assertSkills(claudeResult.installPath, plugin.components.skills.map(({ name }) => name), "Claude");
  } finally {
    await rm(temporary, { recursive: true, force: true });
  }
}

const marketplace = validateMarketplace(
  await readJson(path.join(ROOT, "marketplace/marketplace.json")),
  "marketplace/marketplace.json",
);
const claude = await pinnedBinary("claude");
const codex = await pinnedBinary("codex");
for (const entry of marketplace.plugins.filter(
  ({ kind, hosts }) => kind === "local" && hosts.includes("claude"),
)) {
  await run(claude.command, ["plugin", "validate", "--strict", entry.path]);
}
await run(claude.command, ["plugin", "validate", "--strict", ".claude-plugin/marketplace.json"]);
for (const [host, expected, actual] of [
  ["Claude", EXPECTED_CLAUDE_VERSION, claude.version],
  ["Codex", EXPECTED_CODEX_VERSION, codex.version],
]) {
  if (!expected || !actual.includes(expected)) {
    throw new Error(`Expected pinned ${host} ${expected ?? "(missing)"}, got ${actual}`);
  }
}
await validateDevlabInstall(claude, codex);
process.stdout.write("Pinned host contracts and clean DevLab installs validated.\n");
