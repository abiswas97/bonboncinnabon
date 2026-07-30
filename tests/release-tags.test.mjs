import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { mkdir, mkdtemp, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { promisify } from "node:util";
import { createReleaseTags, planReleaseTags } from "../tools/portability/release-tags.mjs";

const execFileAsync = promisify(execFile);

async function git(root, args) {
  const { stdout } = await execFileAsync("git", args, { cwd: root, encoding: "utf8" });
  return stdout.trim();
}

async function writeRelease(root, version, { changelog = true } = {}) {
  await mkdir(path.join(root, "marketplace"), { recursive: true });
  await mkdir(path.join(root, "plugins/example"), { recursive: true });
  await writeFile(
    path.join(root, "marketplace/marketplace.json"),
    `${JSON.stringify({
      plugins: [{ name: "example", kind: "local", path: "./plugins/example", hosts: ["claude"] }],
    })}\n`,
  );
  await writeFile(
    path.join(root, "plugins/example/plugin.json"),
    `${JSON.stringify({ name: "example", version })}\n`,
  );
  await writeFile(
    path.join(root, "plugins/example/CHANGELOG.md"),
    changelog ? `# Changelog\n\n## [${version}]\n` : "# Changelog\n",
  );
  await writeFile(path.join(root, "RELEASING.md"), `- \`example--v${version}\`\n`);
}

async function commit(root, message) {
  await git(root, ["add", "."]);
  await git(root, ["commit", "-m", message]);
  return git(root, ["rev-parse", "HEAD"]);
}

async function repository() {
  const root = await mkdtemp(path.join(os.tmpdir(), "bonbon-release-tags-"));
  await git(root, ["init", "-q"]);
  await git(root, ["config", "user.name", "Test"]);
  await git(root, ["config", "user.email", "test@example.invalid"]);
  await writeRelease(root, "0.1.0");
  const initial = await commit(root, "initial");
  return { root, initial };
}

test("unchanged versions do not backfill missing tags", async () => {
  const { root, initial } = await repository();
  await writeFile(path.join(root, "README.md"), "unrelated\n");
  const after = await commit(root, "unrelated");
  assert.deepEqual(await planReleaseTags({ root, before: initial, after }), []);
});

test("version transitions create annotated tags on the validated commit", async () => {
  const { root, initial } = await repository();
  await writeRelease(root, "0.2.0");
  const after = await commit(root, "release example 0.2.0");
  const plans = await createReleaseTags({ root, before: initial, after, push: false });
  assert.deepEqual(plans, [{
    plugin: "example",
    version: "0.2.0",
    tag: "example--v0.2.0",
    commit: after,
    action: "create",
  }]);
  assert.equal(await git(root, ["cat-file", "-t", "example--v0.2.0"]), "tag");
  assert.equal(await git(root, ["rev-parse", "example--v0.2.0^{}"]), after);
});

test("reruns accept an immutable tag already on the release commit", async () => {
  const { root, initial } = await repository();
  await writeRelease(root, "0.2.0");
  const after = await commit(root, "release example 0.2.0");
  await git(root, ["tag", "-a", "example--v0.2.0", after, "-m", "example 0.2.0"]);
  const plans = await planReleaseTags({ root, before: initial, after });
  assert.equal(plans[0].action, "exists");
  assert.equal(plans[0].commit, after);
});

test("version transitions require matching release metadata", async () => {
  const { root, initial } = await repository();
  await writeRelease(root, "0.2.0", { changelog: false });
  const after = await commit(root, "invalid release");
  await assert.rejects(
    () => planReleaseTags({ root, before: initial, after }),
    /CHANGELOG\.md is missing version 0\.2\.0/,
  );
});

test("versions cannot move backwards", async () => {
  const { root, initial } = await repository();
  await writeRelease(root, "0.0.9");
  const after = await commit(root, "invalid downgrade");
  await assert.rejects(
    () => planReleaseTags({ root, before: initial, after }),
    /version must increase from 0\.1\.0, got 0\.0\.9/,
  );
});

test("immutable tags cannot be moved to a later version commit", async () => {
  const { root, initial } = await repository();
  await git(root, ["tag", "-a", "example--v0.2.0", initial, "-m", "conflict"]);
  await writeRelease(root, "0.2.0");
  const after = await commit(root, "release example 0.2.0");
  await assert.rejects(
    () => planReleaseTags({ root, before: initial, after }),
    /immutable tag already targets/,
  );
});
