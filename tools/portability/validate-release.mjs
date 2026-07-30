#!/usr/bin/env node

import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { readJson, validateMarketplace } from "./contracts.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const canonicalMarketplace = validateMarketplace(
  await readJson(path.join(ROOT, "marketplace/marketplace.json")),
  "marketplace/marketplace.json",
);
const claudeMarketplace = await readJson(path.join(ROOT, ".claude-plugin/marketplace.json"));
const codexMarketplace = await readJson(path.join(ROOT, ".agents/plugins/marketplace.json"));
const releasing = await readFile(path.join(ROOT, "RELEASING.md"), "utf8");
const errors = [];

for (const entry of canonicalMarketplace.plugins.filter(({ kind }) => kind === "local")) {
  const { name, hosts } = entry;
  const pluginRoot = path.join(ROOT, entry.path);
  const canonical = await readJson(path.join(pluginRoot, "plugin.json"));
  const claude = hosts.includes("claude")
    ? await readJson(path.join(pluginRoot, ".claude-plugin/plugin.json"))
    : null;
  const codex = hosts.includes("codex")
    ? await readJson(path.join(pluginRoot, ".codex-plugin/plugin.json"))
    : null;
  const claudeEntry = claudeMarketplace.plugins.find((plugin) => plugin.name === name);
  const codexEntry = codexMarketplace.plugins.find((plugin) => plugin.name === name);
  const changelog = await readFile(path.join(pluginRoot, "CHANGELOG.md"), "utf8");
  const versions = [];
  if (claude) versions.push(["Claude manifest", claude.version], ["Claude marketplace", claudeEntry?.version]);
  if (codex) versions.push(["Codex manifest", codex.version]);
  for (const [location, version] of versions) {
    if (version !== canonical.version) errors.push(`${name}: ${location} has ${version}, expected ${canonical.version}`);
  }
  if (hosts.includes("claude") !== Boolean(claudeEntry)) errors.push(`${name}: Claude marketplace eligibility mismatch`);
  if (hosts.includes("codex") !== Boolean(codexEntry)) errors.push(`${name}: Codex marketplace eligibility mismatch`);
  if (!changelog.includes(`## [${canonical.version}]`)) errors.push(`${name}: changelog missing ${canonical.version}`);
  if (!releasing.includes(`${name}--v${canonical.version}`)) errors.push(`${name}: intended release tag is missing`);
}

if (errors.length) {
  process.stderr.write(`${errors.join("\n")}\n`);
  process.exitCode = 1;
} else {
  process.stdout.write("Plugin versions, changelogs, projections, and intended tags are consistent.\n");
}
