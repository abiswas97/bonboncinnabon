#!/usr/bin/env node

import { execFile } from "node:child_process";
import path from "node:path";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";

const execFileAsync = promisify(execFile);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");

async function binary(name) {
  const local = path.join(ROOT, "node_modules/.bin", name);
  try {
    await execFileAsync(local, ["--version"], { timeout: 10_000 });
    return local;
  } catch {
    return name;
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

const claude = await binary("claude");
const codex = await binary("codex");
for (const target of ["plugins/butler", "plugins/standards", ".claude-plugin/marketplace.json"]) {
  await run(claude, ["plugin", "validate", "--strict", target]);
}
const { stdout: codexVersion } = await run(codex, ["--version"]);
if (!codexVersion.includes("0.145.0")) throw new Error(`Expected pinned Codex 0.145.0, got ${codexVersion.trim()}`);
process.stdout.write("Pinned Claude manifests and Codex CLI contract validated.\n");
