#!/usr/bin/env node

import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { readJson } from "./contracts.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const marketplace = await readJson(path.join(ROOT, ".claude-plugin/marketplace.json"));
const codexMarketplace = await readJson(path.join(ROOT, ".agents/plugins/marketplace.json"));
const releasing = await readFile(path.join(ROOT, "RELEASING.md"), "utf8");
const errors = [];

for (const name of ["butler", "standards"]) {
  const canonical = await readJson(path.join(ROOT, `plugins/${name}/plugin.json`));
  const claude = await readJson(path.join(ROOT, `plugins/${name}/.claude-plugin/plugin.json`));
  const codex = await readJson(path.join(ROOT, `plugins/${name}/.codex-plugin/plugin.json`));
  const claudeEntry = marketplace.plugins.find((plugin) => plugin.name === name);
  const codexEntry = codexMarketplace.plugins.find((plugin) => plugin.name === name);
  const changelog = await readFile(path.join(ROOT, `plugins/${name}/CHANGELOG.md`), "utf8");
  for (const [location, version] of [
    ["Claude manifest", claude.version],
    ["Codex manifest", codex.version],
    ["Claude marketplace", claudeEntry?.version],
  ]) {
    if (version !== canonical.version) errors.push(`${name}: ${location} has ${version}, expected ${canonical.version}`);
  }
  if (!codexEntry) errors.push(`${name}: missing Codex marketplace entry`);
  if (!changelog.includes(`## [${canonical.version}]`)) errors.push(`${name}: changelog missing ${canonical.version}`);
  if (!releasing.includes(`${name}--v${canonical.version}`)) errors.push(`${name}: intended release tag is missing`);
}

if (errors.length) {
  process.stderr.write(`${errors.join("\n")}\n`);
  process.exitCode = 1;
} else {
  process.stdout.write("Plugin versions, changelogs, projections, and intended tags are consistent.\n");
}
