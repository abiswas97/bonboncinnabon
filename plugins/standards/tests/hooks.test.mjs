import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { mkdir, mkdtemp, readFile, readdir, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { Readable } from "node:stream";
import { promisify } from "node:util";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { adaptPayload, affectedPaths, nativeResponse, patchPaths } from "../hooks/lib/adapters.mjs";
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
    ["codex-session-compact.json", "codex", "session"],
    ["claude-prompt-plan.json", "claude", "plan"],
    ["codex-prompt-plan.json", "codex", "plan"],
    ["claude-plan.json", "claude", "plan"],
    ["claude-edit.json", "claude", "edit"],
    ["codex-patch.json", "codex", "edit"],
    ["claude-subagent.json", "claude", "subagent"],
    ["codex-subagent.json", "codex", "subagent"],
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

test("Claude and Codex startup, resume, and clear sessions contain commandments and index without Git context", async () => {
  const root = await repository();
  for (const host of ["claude", "codex"]) {
    for (const source of ["startup", "resume", "clear"]) {
      const response = await handleEvent(
        host,
        await fixture("claude-session.json", { cwd: root, session_id: `${host}-${source}`, source }),
        {
          pluginRoot: PLUGIN_ROOT,
          env: {},
        },
      );
      const guidance = response.hookSpecificOutput.additionalContext;
      for (let index = 1; index <= 10; index += 1) {
        assert.match(guidance, new RegExp(`C${String(index).padStart(2, "0")}\\.`));
      }
      assert.match(guidance, /## Supporting rule index/);
      assert(!guidance.includes("## Working context"));
      assert(guidance.length <= 7_000);
      assert.deepEqual(Object.keys(response.hookSpecificOutput).sort(), ["additionalContext", "hookEventName"]);
    }
  }
});

test("Claude and Codex compacted sessions include capped secret-safe Git context", async () => {
  const root = await repository();
  await writeFile(path.join(root, "tracked.txt"), "token=super-secret-value\n");
  await execFileAsync("git", ["-C", root, "add", "tracked.txt"]);
  await execFileAsync("git", ["-C", root, "remote", "add", "origin", "https://user:secret@example.invalid/repo.git"]);
  for (const host of ["claude", "codex"]) {
    const response = await handleEvent(host, await fixture("codex-session-compact.json", { cwd: root, session_id: `${host}-compact` }), {
      pluginRoot: PLUGIN_ROOT,
      env: { API_TOKEN: "super-secret-value" },
    });
    const guidance = response.hookSpecificOutput.additionalContext;
    assert.match(guidance, /Changed tracked paths: 1/);
    assert(!guidance.includes("super-secret-value"));
    assert(!guidance.includes("example.invalid"));
    assert(!guidance.includes(root));
  }
});

test("subagent start contains exact commandments and precedence without index or Git context", async () => {
  const root = await repository();
  const canonical = (await readFile(path.join(PLUGIN_ROOT, "standards/commandments.md"), "utf8")).trim();
  for (const [host, name] of [
    ["claude", "claude-subagent.json"],
    ["codex", "codex-subagent.json"],
  ]) {
    const response = await handleEvent(host, await fixture(name, { cwd: root }), {
      pluginRoot: PLUGIN_ROOT,
      env: {},
    });
    const guidance = response.hookSpecificOutput.additionalContext;
    assert.equal(guidance, canonical);
    assert(!guidance.includes("## Supporting rule index"));
    assert(!guidance.includes("## Working context"));
  }
});

test("normal prompts are silent while permission_mode plan is advisory", async () => {
  const root = await repository();
  const normal = await handleEvent(
    "codex",
    { hook_event_name: "UserPromptSubmit", permission_mode: "default", cwd: root },
    { pluginRoot: PLUGIN_ROOT, env: {} },
  );
  assert.equal(normal, null);
  for (const [host, name] of [
    ["claude", "claude-prompt-plan.json"],
    ["codex", "codex-prompt-plan.json"],
  ]) {
    const response = await handleEvent(host, await fixture(name, { cwd: root }), {
      pluginRoot: PLUGIN_ROOT,
      env: {},
    });
    assert(response.hookSpecificOutput.additionalContext.length <= 2_500);
  }
});

test("every registered event emits only its allowed native output fields", async () => {
  const root = await repository();
  const cases = [
    ["claude", "claude-session.json"],
    ["codex", "codex-session-compact.json"],
    ["claude", "claude-prompt-plan.json"],
    ["codex", "codex-prompt-plan.json"],
    ["claude", "claude-plan.json"],
    ["claude", "claude-edit.json"],
    ["codex", "codex-patch.json"],
    ["claude", "claude-subagent.json"],
    ["codex", "codex-subagent.json"],
  ];
  for (const [host, name] of cases) {
    const response = await handleEvent(host, await fixture(name, { cwd: root, session_id: `${host}-${name}` }), {
      pluginRoot: PLUGIN_ROOT,
      env: {},
    });
    assert.deepEqual(Object.keys(response), ["hookSpecificOutput"]);
    assert.deepEqual(Object.keys(response.hookSpecificOutput).sort(), ["additionalContext", "hookEventName"]);
  }
});

test("native response rejects additionalContext for unregistered lifecycle events", () => {
  for (const nativeEvent of ["PreCompact", "Stop"]) {
    assert.equal(nativeResponse({ nativeEvent }, "must not be emitted"), null);
  }
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
  const response = await handleEvent("codex", await fixture("codex-prompt-plan.json", { cwd: root }), {
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
  assert.equal(adaptPayload("codex", { hook_event_name: "PreCompact" }, root), null);
  assert.equal(adaptPayload("codex", { hook_event_name: "Stop" }, root), null);
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
