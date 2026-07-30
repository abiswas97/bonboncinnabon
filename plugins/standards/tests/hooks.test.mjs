import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { mkdir, mkdtemp, readFile, readdir, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { Readable } from "node:stream";
import { promisify } from "node:util";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { adaptPayload, affectedPaths, patchPaths } from "../hooks/lib/adapters.mjs";
import { handleEvent, readPayload } from "../hooks/lib/runtime.mjs";

const execFileAsync = promisify(execFile);
const PLUGIN_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const FIXTURES = path.resolve(PLUGIN_ROOT, "../../tests/fixtures/hooks");

async function fixture(name, overrides = {}) {
  return { ...JSON.parse(await readFile(path.join(FIXTURES, name), "utf8")), ...overrides };
}

async function repository() {
  const root = await mkdtemp(path.join(os.tmpdir(), "standards-hook-"));
  await execFileAsync("git", ["init", "-q", root]);
  return root;
}

test("native fixtures map to neutral lifecycle contracts", async () => {
  const root = await repository();
  const cases = [
    ["claude-session.json", "claude", "session"],
    ["claude-plan.json", "claude", "plan"],
    ["claude-edit.json", "claude", "edit"],
    ["codex-patch.json", "codex", "edit"],
    ["codex-compact.json", "codex", "compact"],
    ["codex-stop.json", "codex", "complete"],
  ];
  for (const [name, host, lifecycle] of cases) {
    const payload = await fixture(name, { cwd: root });
    assert.equal(adaptPayload(host, payload, root).lifecycle, lifecycle);
  }
});

test("patch parser extracts add, update, delete, and move paths", () => {
  const patch = [
    "*** Add File: src/add.ts",
    "*** Update File: src/update.ts",
    "*** Move to: src/moved.ts",
    "*** Delete File: src/delete.ts",
  ].join("\n");
  assert.deepEqual(patchPaths(patch), ["src/add.ts", "src/update.ts", "src/moved.ts", "src/delete.ts"]);
});

test("affected paths are normalized, deduplicated, and cannot escape the repository", () => {
  const root = path.resolve("/tmp/example-root");
  const paths = affectedPaths(
    {
      tool_input: {
        file_path: "src/a.ts",
        new_path: "src/a.ts",
        command: "*** Update File: ../outside.txt\n*** Move to: src/b.ts",
      },
    },
    root,
  );
  assert.deepEqual(paths, ["src/a.ts", "src/b.ts"]);
});

test("session output contains all commandments once and stays within budget", async () => {
  const root = await repository();
  const response = await handleEvent("claude", await fixture("claude-session.json", { cwd: root }), {
    pluginRoot: PLUGIN_ROOT,
    env: {},
  });
  const guidance = response.hookSpecificOutput.additionalContext;
  for (let index = 1; index <= 10; index += 1) {
    assert.match(guidance, new RegExp(`C${String(index).padStart(2, "0")}\\.`));
  }
  assert(guidance.length <= 7_000);
  assert.deepEqual(Object.keys(response.hookSpecificOutput).sort(), ["additionalContext", "hookEventName"]);
});

test("compaction includes capped safe Git context without secrets or absolute roots", async () => {
  const root = await repository();
  await writeFile(path.join(root, "tracked.txt"), "token=super-secret-value\n");
  await execFileAsync("git", ["-C", root, "add", "tracked.txt"]);
  await execFileAsync("git", ["-C", root, "remote", "add", "origin", "https://user:secret@example.invalid/repo.git"]);
  const response = await handleEvent("codex", await fixture("codex-compact.json", { cwd: root }), {
    pluginRoot: PLUGIN_ROOT,
    env: { API_TOKEN: "super-secret-value" },
  });
  const guidance = response.hookSpecificOutput.additionalContext;
  assert.match(guidance, /Changed tracked paths: 1/);
  assert(!guidance.includes("super-secret-value"));
  assert(!guidance.includes("example.invalid"));
  assert(!guidance.includes(root));
});

test("event output is advisory, bounded, and deduplicated by session", async () => {
  const root = await repository();
  const data = await mkdtemp(path.join(os.tmpdir(), "standards-data-"));
  const payload = await fixture("claude-plan.json", { cwd: root, session_id: "raw-session-secret" });
  const options = { pluginRoot: PLUGIN_ROOT, env: { PLUGIN_DATA: data } };
  const first = await handleEvent("claude", payload, options);
  assert(first.hookSpecificOutput.additionalContext.length <= 2_500);
  assert((first.hookSpecificOutput.additionalContext.match(/^- /gm) ?? []).length <= 7);
  assert.equal("permissionDecision" in first.hookSpecificOutput, false);
  const second = await handleEvent("claude", payload, options);
  assert(second === null || !second.hookSpecificOutput.additionalContext.includes("ARCH-BOUNDARY"));
  const [stateName] = await readdir(path.join(data, "standards-sessions"));
  const state = await readFile(path.join(data, "standards-sessions", stateName), "utf8");
  assert(!state.includes("raw-session-secret"));
  assert.deepEqual(Object.keys(JSON.parse(state)).sort(), ["deliveredRuleIds", "host", "sessionHash", "updatedAt"]);
});

test("unwritable or absent state remains a non-blocking optimization", async () => {
  const root = await repository();
  const response = await handleEvent("codex", await fixture("codex-stop.json", { cwd: root }), {
    pluginRoot: PLUGIN_ROOT,
    env: {},
  });
  assert(response?.hookSpecificOutput.additionalContext);
});

test("unsupported, incomplete, non-plan prompt, and malformed payloads are silent", async () => {
  const root = await repository();
  assert.equal(adaptPayload("claude", {}, root), null);
  assert.equal(adaptPayload("codex", { hook_event_name: "Notification" }, root), null);
  assert.equal(adaptPayload("claude", { hook_event_name: "UserPromptSubmit", mode: "default" }, root), null);
  assert.equal(await readPayload(Readable.from(["not-json"])), null);
  assert.equal(await readPayload(Readable.from(["x".repeat(1_100_000)])), null);
});

test("edit with no in-repository affected path emits no path-specific migration rule", async () => {
  const root = await repository();
  const payload = await fixture("codex-patch.json", {
    cwd: root,
    tool_input: { command: "*** Update File: ../outside.sql" },
  });
  const response = await handleEvent("codex", payload, { pluginRoot: PLUGIN_ROOT, env: {} });
  assert(!response?.hookSpecificOutput.additionalContext.includes("DATA-MIGRATION"));
});
