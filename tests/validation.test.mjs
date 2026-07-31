import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { copyFile, mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";
import { buildProjections } from "../tools/portability/sync-plugins.mjs";
import { validateRepository } from "../tools/portability/validate-repository.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const execFileAsync = promisify(execFile);

async function trackedFixture(prefix) {
  const root = await mkdtemp(path.join(os.tmpdir(), prefix));
  const { stdout } = await execFileAsync("git", ["-C", ROOT, "ls-files", "-z"], {
    encoding: "buffer",
    maxBuffer: 4 * 1024 * 1024,
  });
  for (const relative of stdout.toString("utf8").split("\0").filter(Boolean)) {
    const target = path.join(root, relative);
    await mkdir(path.dirname(target), { recursive: true });
    await copyFile(path.join(ROOT, relative), target);
  }
  return root;
}

test("current repository contracts are valid", async () => {
  const result = await validateRepository(ROOT);
  const marketplace = JSON.parse(await readFile(path.join(ROOT, "marketplace/marketplace.json"), "utf8"));
  assert.deepEqual(result, {
    plugins: marketplace.plugins.filter(({ kind }) => kind === "local").length,
    projections: (await buildProjections({ root: ROOT })).size,
  });
});

test("missing generated components fail with an actionable path", async () => {
  const root = await trackedFixture("bonbon-invalid-");
  await rm(path.join(root, "plugins/standards/skills/standards/SKILL.md"));
  await assert.rejects(() => validateRepository(root), /skills\/standards\/SKILL\.md: missing component/);
});

test("clean CI installs the Claude native validator explicitly", async () => {
  const root = await trackedFixture("bonbon-invalid-ci-");
  const workflow = path.join(root, ".github/workflows/validate.yml");
  const contents = await readFile(workflow, "utf8");
  await writeFile(workflow, contents.replace("      - run: npm run validators:install\n", ""));
  await assert.rejects(
    () => validateRepository(root),
    /npm run validators:install must follow npm ci --ignore-scripts/,
  );
});

test("release tag publication remains gated by successful main validation", async () => {
  const root = await trackedFixture("bonbon-invalid-release-ci-");
  const workflow = path.join(root, ".github/workflows/validate.yml");
  const contents = await readFile(workflow, "utf8");
  await writeFile(workflow, contents.replace("    needs: validate\n", ""));
  await assert.rejects(
    () => validateRepository(root),
    /release-tags must wait for validation/,
  );
});
