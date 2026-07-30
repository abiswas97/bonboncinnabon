import assert from "node:assert/strict";
import { cp, mkdir, mkdtemp, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { matchesGlob, resolveStandards } from "../hooks/lib/resolver.mjs";

const PLUGIN_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

async function repository(overlay) {
  const root = await mkdtemp(path.join(os.tmpdir(), "standards-resolver-"));
  await mkdir(path.join(root, ".git"));
  if (overlay) {
    await mkdir(path.join(root, ".standards"));
    await writeFile(path.join(root, ".standards/standards.json"), `${JSON.stringify(overlay, null, 2)}\n`);
  }
  return root;
}

function rule(id, paths = ["**/*"]) {
  return {
    id,
    title: id,
    summary: `${id} summary`,
    class: "review",
    lifecycles: ["edit"],
    paths,
    roles: ["implementation"],
    reference: "references/clean-code.md",
  };
}

test("glob matching supports recursive paths and extension alternatives", () => {
  assert.equal(matchesGlob("src/lib/code.ts", "**/*.{js,ts}"), true);
  assert.equal(matchesGlob("src/lib/code.py", "**/*.{js,ts}"), false);
  assert.equal(matchesGlob("db/migrations/001.sql", "**/migrations/**"), true);
});

test("default rules resolve by lifecycle, role, and path", async () => {
  const root = await repository();
  const result = await resolveStandards({
    pluginRoot: PLUGIN_ROOT,
    repositoryRoot: root,
    lifecycle: "edit",
    role: "implementation",
    paths: ["src/main.rs"],
  });
  assert(result.rules.some(({ id }) => id === "CODE-COHESION"));
  assert(!result.rules.some(({ id }) => id === "DATA-MIGRATION"));
});

test("overlay extends defaults and overrides matching supporting IDs", async () => {
  const replacement = rule("CODE-COHESION", ["src/**"]);
  replacement.summary = "Repository-specific cohesion.";
  const root = await repository({ schemaVersion: 1, extends: "default", rules: [replacement] });
  const result = await resolveStandards({
    pluginRoot: PLUGIN_ROOT,
    repositoryRoot: root,
    lifecycle: "edit",
    role: "implementation",
    paths: ["src/main.go"],
  });
  assert.equal(result.rules.find(({ id }) => id === "CODE-COHESION").summary, "Repository-specific cohesion.");
  assert(result.rules.some(({ id }) => id === "SEC-SECRETS"));
});

test("overlay without extends replaces supporting defaults", async () => {
  const root = await repository({ schemaVersion: 1, rules: [rule("REPO-ONLY")] });
  const result = await resolveStandards({
    pluginRoot: PLUGIN_ROOT,
    repositoryRoot: root,
    lifecycle: "edit",
    role: "implementation",
    paths: ["anything.txt"],
  });
  assert.deepEqual(result.rules.map(({ id }) => id), ["REPO-ONLY"]);
});

test("invalid overlay is rejected atomically", async () => {
  const root = await repository({ schemaVersion: 1, extends: "default", rules: [rule("C01")] });
  await assert.rejects(
    () => resolveStandards({ pluginRoot: PLUGIN_ROOT, repositoryRoot: root }),
    /commandment IDs are immutable/,
  );
});

test("unknown fields, duplicates, selectors, and schema versions are rejected", async () => {
  for (const overlay of [
    { schemaVersion: 1, rules: [{ ...rule("REPO-A"), unknown: true }] },
    { schemaVersion: 1, rules: [rule("REPO-A"), rule("REPO-A")] },
    { schemaVersion: 1, rules: [{ ...rule("REPO-A"), lifecycles: ["ship"] }] },
    { schemaVersion: 2, rules: [] },
  ]) {
    const root = await repository(overlay);
    await assert.rejects(() => resolveStandards({ pluginRoot: PLUGIN_ROOT, repositoryRoot: root }));
  }
});

test("structured host-native instruction overrides produce explicit conflicts", async () => {
  const root = await repository();
  const result = await resolveStandards({
    pluginRoot: PLUGIN_ROOT,
    repositoryRoot: root,
    instructionOverrides: [{ ruleId: "ARCH-REUSE", source: "AGENTS.md", reason: "generated code is authoritative" }],
  });
  assert.match(result.conflicts[0].message, /AGENTS\.md supersedes portable supporting rule ARCH-REUSE/);
});
