import assert from "node:assert/strict";
import { cp, mkdir, mkdtemp, readFile, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { buildProjections, sync } from "../tools/portability/sync-plugins.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

async function fixtureRoot() {
  const root = await mkdtemp(path.join(os.tmpdir(), "bonbon-projection-"));
  await mkdir(path.join(root, "marketplace"), { recursive: true });
  await mkdir(path.join(root, "plugins/butler/skills"), { recursive: true });
  await mkdir(path.join(root, "plugins/standards/skills"), { recursive: true });
  await cp(path.join(ROOT, "marketplace/marketplace.json"), path.join(root, "marketplace/marketplace.json"));
  await cp(path.join(ROOT, "plugins/butler/plugin.json"), path.join(root, "plugins/butler/plugin.json"));
  await cp(path.join(ROOT, "plugins/standards/plugin.json"), path.join(root, "plugins/standards/plugin.json"));
  return root;
}

test("projection order and host filtering are deterministic", async () => {
  const first = await buildProjections({ root: ROOT });
  const second = await buildProjections({ root: ROOT });
  assert.deepEqual([...first], [...second]);
  assert.equal([...first.keys()].some((target) => target.startsWith("openspec/specs/")), false);
  const claude = JSON.parse(first.get(".claude-plugin/marketplace.json"));
  const codex = JSON.parse(first.get(".agents/plugins/marketplace.json"));
  assert.deepEqual(claude.plugins.map(({ name }) => name), ["postgres", "devlab", "butler", "standards"]);
  assert.deepEqual(codex.plugins.map(({ name }) => name), ["butler", "standards"]);
});

test("host hook projections intentionally differ and Codex declares its hook path", async () => {
  const projections = await buildProjections({ root: ROOT });
  const claude = JSON.parse(projections.get("plugins/standards/hooks/claude.json"));
  const codex = JSON.parse(projections.get("plugins/standards/hooks/hooks.json"));
  assert.notDeepEqual(claude, codex);
  assert.deepEqual(Object.keys(claude.hooks).sort(), [
    "PostToolUse",
    "PreToolUse",
    "SessionStart",
    "SubagentStart",
    "UserPromptSubmit",
  ]);
  assert.deepEqual(Object.keys(codex.hooks).sort(), [
    "PostToolUse",
    "SessionStart",
    "SubagentStart",
    "UserPromptSubmit",
  ]);
  assert.equal(claude.hooks.PreToolUse[0].matcher, "ExitPlanMode");
  assert.equal(codex.hooks.PreToolUse, undefined);
  const manifest = JSON.parse(projections.get("plugins/standards/.codex-plugin/plugin.json"));
  assert.equal(manifest.hooks, "./hooks/hooks.json");
  assert(projections.has(path.posix.join("plugins/standards", manifest.hooks)));
});

test("single-host plugins generate only eligible host artifacts", async () => {
  const root = await fixtureRoot();
  const marketplaceFile = path.join(root, "marketplace/marketplace.json");
  const pluginFile = path.join(root, "plugins/standards/plugin.json");
  const marketplace = JSON.parse(await readFile(marketplaceFile, "utf8"));
  const plugin = JSON.parse(await readFile(pluginFile, "utf8"));
  marketplace.plugins.find(({ name }) => name === "standards").hosts = ["claude"];
  plugin.hosts = ["claude"];
  delete plugin.components.hooks.codex;
  await writeFile(marketplaceFile, `${JSON.stringify(marketplace, null, 2)}\n`);
  await writeFile(pluginFile, `${JSON.stringify(plugin, null, 2)}\n`);

  const projections = await buildProjections({ root });
  assert(projections.has("plugins/standards/.claude-plugin/plugin.json"));
  assert(projections.has("plugins/standards/hooks/claude.json"));
  assert.equal(projections.has("plugins/standards/.codex-plugin/plugin.json"), false);
  assert.equal(projections.has("plugins/standards/hooks/hooks.json"), false);
  assert.equal(
    [...projections.keys()].some((target) =>
      target.startsWith("plugins/standards/skills/") && target.endsWith("/agents/openai.yaml")),
    false,
  );
});

test("marketplace and plugin host eligibility must match exactly", async () => {
  const root = await fixtureRoot();
  const marketplaceFile = path.join(root, "marketplace/marketplace.json");
  const marketplace = JSON.parse(await readFile(marketplaceFile, "utf8"));
  marketplace.plugins.find(({ name }) => name === "standards").hosts = ["claude"];
  await writeFile(marketplaceFile, `${JSON.stringify(marketplace, null, 2)}\n`);
  await assert.rejects(
    () => buildProjections({ root }),
    /plugins\/standards\/plugin\.json\.hosts: must exactly match marketplace hosts/,
  );
});

test("hook projections are driven by each plugin's canonical host contract", async () => {
  const root = await fixtureRoot();
  const pluginFile = path.join(root, "plugins/standards/plugin.json");
  const plugin = JSON.parse(await readFile(pluginFile, "utf8"));
  plugin.components.hooks.claude.manifest = "hooks/custom.json";
  plugin.components.hooks.claude.script = "hooks/scripts/custom.mjs";
  plugin.components.hooks.claude.registrations = [
    { event: "PostToolUse", matcher: "CustomTool", timeout: 7 },
  ];
  await writeFile(pluginFile, `${JSON.stringify(plugin, null, 2)}\n`);

  const projections = await buildProjections({ root });
  const manifest = JSON.parse(projections.get("plugins/standards/.claude-plugin/plugin.json"));
  const hookMap = JSON.parse(projections.get("plugins/standards/hooks/custom.json"));
  assert.equal(manifest.hooks, "./hooks/custom.json");
  assert.deepEqual(Object.keys(hookMap.hooks), ["PostToolUse"]);
  assert.equal(hookMap.hooks.PostToolUse[0].matcher, "CustomTool");
  assert.equal(hookMap.hooks.PostToolUse[0].hooks[0].timeout, 7);
  assert.match(hookMap.hooks.PostToolUse[0].hooks[0].command, /hooks\/scripts\/custom\.mjs/);
});

test("generated hook commands use host plugin roots and timeout shape", async () => {
  const projections = await buildProjections({ root: ROOT });
  for (const [host, target, expectedRoot] of [
    ["claude", "plugins/standards/hooks/claude.json", "${CLAUDE_PLUGIN_ROOT}"],
    ["codex", "plugins/standards/hooks/hooks.json", "$PLUGIN_ROOT"],
  ]) {
    const hookMap = JSON.parse(projections.get(target));
    for (const registrations of Object.values(hookMap.hooks)) {
      for (const registration of registrations) {
        for (const hook of registration.hooks) {
          assert.equal(hook.type, "command", host);
          assert.equal(hook.timeout, 10, host);
          assert.match(hook.command, new RegExp(expectedRoot.replace(/[${}]/g, "\\$&")), host);
        }
      }
    }
  }
});

test("unsupported platform fails clearly", async () => {
  await assert.rejects(() => buildProjections({ root: ROOT, platform: "win32" }), /supports macOS and Linux/);
});

test("check mode detects missing, stale, and extra projections without writing", async () => {
  const root = await fixtureRoot();
  await sync({ root });
  const marketplace = path.join(root, ".claude-plugin/marketplace.json");
  await writeFile(marketplace, "stale\n");
  const extra = path.join(root, "plugins/butler/skills/ghost/agents/openai.yaml");
  await mkdir(path.dirname(extra), { recursive: true });
  await writeFile(extra, "extra\n");
  await assert.rejects(() => sync({ root, check: true }), /stale[\s\S]*extra generated projection/);
  assert.equal(await readFile(marketplace, "utf8"), "stale\n");
  assert.equal(await readFile(extra, "utf8"), "extra\n");
});

test("generation preserves unrelated worktree files and becomes a no-op", async () => {
  const root = await fixtureRoot();
  const unrelated = path.join(root, "notes.txt");
  await writeFile(unrelated, "mine\n");
  await sync({ root });
  const before = await readFile(path.join(root, ".agents/plugins/marketplace.json"), "utf8");
  await sync({ root });
  const after = await readFile(path.join(root, ".agents/plugins/marketplace.json"), "utf8");
  assert.equal(before, after);
  assert.equal(await readFile(unrelated, "utf8"), "mine\n");
});
