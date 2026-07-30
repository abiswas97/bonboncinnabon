#!/usr/bin/env node

import { execFile } from "node:child_process";
import { readFile } from "node:fs/promises";
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

async function run(command, args) {
  try {
    return await execFileAsync(command, args, {
      cwd: ROOT,
      timeout: 30_000,
      maxBuffer: 1024 * 1024,
      env: { ...process.env, NO_COLOR: "1" },
    });
  } catch (error) {
    throw new Error(`${command} ${args.join(" ")} failed:\n${error.stdout ?? ""}${error.stderr ?? error.message}`);
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
process.stdout.write("Pinned Claude manifests and Codex CLI contract validated.\n");
