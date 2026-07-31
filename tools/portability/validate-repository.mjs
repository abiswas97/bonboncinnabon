#!/usr/bin/env node

import { access, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { buildProjections } from "./sync-plugins.mjs";
import { readJson, validateMarketplace, validatePlugin, validateRegistry } from "./contracts.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");

async function exists(file) {
  try {
    await access(file);
    return true;
  } catch {
    return false;
  }
}

function frontmatterDescription(text, file, errors) {
  const match = text.match(/^---\n([\s\S]*?)\n---/);
  if (!match) {
    errors.push(`${file}: missing YAML frontmatter`);
    return;
  }
  const description = match[1].split("\n").find((line) => line.startsWith("description:"));
  if (!description) errors.push(`${file}: missing frontmatter description`);
  const value = description?.slice("description:".length).trim() ?? "";
  if (value.includes(":") && !(value.startsWith('"') && value.endsWith('"'))) {
    errors.push(`${file}: descriptions containing a colon must be quoted`);
  }
}

export async function validateRepository(root = ROOT) {
  const errors = [];
  const packageFile = path.join(root, "package.json");
  const workflowFile = path.join(root, ".github/workflows/validate.yml");
  const packageJson = await readJson(packageFile);
  const workflow = await readFile(workflowFile, "utf8");
  const validatorInstall = "node node_modules/@anthropic-ai/claude-code/install.cjs";
  if (packageJson.scripts?.["validators:install"] !== validatorInstall) {
    errors.push("package.json: scripts.validators:install must explicitly install the pinned Claude native validator");
  }
  const cleanInstall = workflow.indexOf("npm ci --ignore-scripts");
  const nativeInstall = workflow.indexOf("npm run validators:install");
  if (cleanInstall === -1 || nativeInstall <= cleanInstall) {
    errors.push(
      ".github/workflows/validate.yml: npm run validators:install must follow npm ci --ignore-scripts",
    );
  }
  const releaseJob = workflow.match(/\n  release-tags:\n([\s\S]*)$/)?.[1] ?? "";
  for (const [fragment, message] of [
    [
      "if: github.event_name == 'push' && github.ref == 'refs/heads/main'",
      "release-tags must run only for pushes to main",
    ],
    ["needs: validate", "release-tags must wait for validation"],
    ["contents: write", "release-tags must declare its scoped tag-write permission"],
    ["tools/portability/release-tags.mjs", "release-tags must invoke the canonical tag publisher"],
  ]) {
    if (!releaseJob.includes(fragment)) {
      errors.push(`.github/workflows/validate.yml: ${message}`);
    }
  }
  const marketplaceFile = path.join(root, "marketplace/marketplace.json");
  let marketplace;
  try {
    marketplace = validateMarketplace(await readJson(marketplaceFile), marketplaceFile);
  } catch (error) {
    errors.push(error.message);
    marketplace = { plugins: [] };
  }
  for (const entry of marketplace.plugins.filter(({ kind }) => kind === "local")) {
    const pluginRoot = path.join(root, entry.path);
    const pluginFile = path.join(pluginRoot, "plugin.json");
    let plugin;
    try {
      plugin = validatePlugin(await readJson(pluginFile), pluginFile);
    } catch (error) {
      errors.push(error.message);
      continue;
    }
    for (const skill of plugin.components.skills) {
      const files = [`skills/${skill.name}/SKILL.md`];
      if (entry.hosts.includes("codex")) files.push(`skills/${skill.name}/agents/openai.yaml`);
      for (const relative of files) {
        if (!(await exists(path.join(pluginRoot, relative)))) errors.push(`${entry.path}/${relative}: missing component`);
      }
    }
    for (const command of plugin.components.commands) {
      const file = path.join(pluginRoot, `commands/${command}.md`);
      if (!(await exists(file))) {
        errors.push(`${entry.path}/commands/${command}.md: missing component`);
      } else {
        frontmatterDescription(await readFile(file, "utf8"), file, errors);
      }
    }
    const projections = [];
    if (entry.hosts.includes("claude")) projections.push(".claude-plugin/plugin.json");
    if (entry.hosts.includes("codex")) projections.push(".codex-plugin/plugin.json");
    for (const relative of projections) {
      if (!(await exists(path.join(pluginRoot, relative)))) errors.push(`${entry.path}/${relative}: missing projection`);
    }
    if (plugin.components.hooks) {
      for (const config of Object.values(plugin.components.hooks)) {
        for (const relative of [config.manifest, config.script]) {
          if (!(await exists(path.join(pluginRoot, relative)))) errors.push(`${entry.path}/${relative}: missing hook component`);
        }
      }
    }
  }
  try {
    validateRegistry(
      await readJson(path.join(root, "plugins/standards/standards/registry.json")),
      "plugins/standards/standards/registry.json",
    );
  } catch (error) {
    errors.push(error.message);
  }
  const projections = await buildProjections({ root });
  for (const [relative, expected] of projections) {
    if (expected.includes("[TODO:")) errors.push(`${relative}: contains scaffold placeholder`);
  }
  const standardsFiles = [
    "plugins/standards/skills/standards/SKILL.md",
    "plugins/standards/skills/standards-init/SKILL.md",
    "plugins/standards/standards/commandments.md",
  ];
  for (const relative of standardsFiles) {
    const file = path.join(root, relative);
    if (!(await exists(file))) continue;
    const text = await readFile(file, "utf8");
    if (text.includes("[TODO:")) errors.push(`${relative}: contains scaffold placeholder`);
  }
  if (errors.length) throw new Error(errors.join("\n"));
  return { plugins: marketplace.plugins.filter(({ kind }) => kind === "local").length, projections: projections.size };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  validateRepository()
    .then(({ plugins, projections }) => process.stdout.write(`Validated ${plugins} local plugins and ${projections} projections.\n`))
    .catch((error) => {
      process.stderr.write(`${error.message}\n`);
      process.exitCode = 1;
    });
}
