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
