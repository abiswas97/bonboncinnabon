import assert from "node:assert/strict";
import { cp, mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { validateRepository } from "../tools/portability/validate-repository.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function fixtureFilter(source) {
  const segments = path.relative(ROOT, source).split(path.sep);
  return !segments.includes(".git") && !segments.includes("node_modules");
}

test("current repository contracts are valid", async () => {
  const result = await validateRepository(ROOT);
  assert.deepEqual(result, { plugins: 2, projections: 15 });
});

test("missing generated components fail with an actionable path", async () => {
  const root = await mkdtemp(path.join(os.tmpdir(), "bonbon-invalid-"));
  await cp(ROOT, root, {
    recursive: true,
    filter: fixtureFilter,
  });
  await rm(path.join(root, "plugins/standards/skills/standards/SKILL.md"));
  await assert.rejects(() => validateRepository(root), /skills\/standards\/SKILL\.md: missing component/);
});

test("clean CI installs the Claude native validator explicitly", async () => {
  const root = await mkdtemp(path.join(os.tmpdir(), "bonbon-invalid-ci-"));
  await cp(ROOT, root, {
    recursive: true,
    filter: fixtureFilter,
  });
  const workflow = path.join(root, ".github/workflows/validate.yml");
  const contents = await readFile(workflow, "utf8");
  await writeFile(workflow, contents.replace("      - run: npm run validators:install\n", ""));
  await assert.rejects(
    () => validateRepository(root),
    /npm run validators:install must follow npm ci --ignore-scripts/,
  );
});
