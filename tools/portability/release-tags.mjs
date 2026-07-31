#!/usr/bin/env node

import { execFile } from "node:child_process";
import path from "node:path";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";

const execFileAsync = promisify(execFile);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const ZERO_SHA = /^0+$/;

async function git(root, args, { optional = false, env = {} } = {}) {
  try {
    const { stdout } = await execFileAsync("git", args, {
      cwd: root,
      encoding: "utf8",
      maxBuffer: 4 * 1024 * 1024,
      env: { ...process.env, ...env },
    });
    return stdout.trim();
  } catch (error) {
    if (optional) return null;
    throw new Error(`git ${args.join(" ")} failed: ${error.stderr?.trim() || error.message}`);
  }
}

function repositoryPath(value) {
  return value.replace(/^\.\//, "").replaceAll("\\", "/");
}

function compareVersions(left, right) {
  const parse = (value) => {
    if (!/^\d+\.\d+\.\d+$/.test(value)) throw new Error(`invalid semantic version "${value}"`);
    return value.split(".").map(Number);
  };
  const leftParts = parse(left);
  const rightParts = parse(right);
  for (let index = 0; index < leftParts.length; index += 1) {
    if (leftParts[index] !== rightParts[index]) return leftParts[index] - rightParts[index];
  }
  return 0;
}

async function fileAt(root, revision, relative, { optional = false } = {}) {
  const relativePath = repositoryPath(relative);
  if (optional) {
    const files = await git(root, ["ls-tree", "--name-only", revision, "--", relativePath]);
    if (!files.split("\n").includes(relativePath)) return null;
  }
  return git(root, ["show", `${revision}:${relativePath}`]);
}

async function jsonAt(root, revision, relative, options) {
  const contents = await fileAt(root, revision, relative, options);
  if (contents === null) return null;
  try {
    return JSON.parse(contents);
  } catch (error) {
    throw new Error(`${relative} at ${revision}: invalid JSON (${error.message})`);
  }
}

async function tagTarget(root, tag) {
  return git(root, ["rev-parse", "-q", "--verify", `refs/tags/${tag}^{}`], { optional: true });
}

export async function planReleaseTags({ root = ROOT, before, after }) {
  const releaseCommit = await git(root, ["rev-parse", `${after}^{commit}`]);
  if (ZERO_SHA.test(before)) return [];
  const previousCommit = await git(root, ["rev-parse", `${before}^{commit}`]);
  const marketplace = await jsonAt(root, releaseCommit, "marketplace/marketplace.json");
  const releasing = await fileAt(root, releaseCommit, "RELEASING.md");
  const plans = [];

  for (const entry of marketplace.plugins.filter(({ kind }) => kind === "local")) {
    const pluginFile = path.posix.join(repositoryPath(entry.path), "plugin.json");
    const current = await jsonAt(root, releaseCommit, pluginFile);
    const previous = await jsonAt(root, previousCommit, pluginFile, { optional: true });
    if (previous?.version === current.version) continue;
    if (previous && compareVersions(current.version, previous.version) <= 0) {
      throw new Error(
        `${entry.name}: version must increase from ${previous.version}, got ${current.version}`,
      );
    }

    const tag = `${entry.name}--v${current.version}`;
    const changelogFile = path.posix.join(repositoryPath(entry.path), "CHANGELOG.md");
    const changelog = await fileAt(root, releaseCommit, changelogFile);
    if (!changelog.includes(`## [${current.version}]`)) {
      throw new Error(`${entry.name}: ${changelogFile} is missing version ${current.version}`);
    }
    if (!releasing.includes(`- \`${tag}\``)) {
      throw new Error(`${entry.name}: RELEASING.md does not declare ${tag}`);
    }

    const existingTarget = await tagTarget(root, tag);
    if (existingTarget && existingTarget !== releaseCommit) {
      throw new Error(`${tag}: immutable tag already targets ${existingTarget}, not ${releaseCommit}`);
    }
    plans.push({
      plugin: entry.name,
      version: current.version,
      tag,
      commit: releaseCommit,
      action: existingTarget ? "exists" : "create",
    });
  }

  return plans;
}

export async function createReleaseTags({
  root = ROOT,
  before,
  after,
  push = true,
  remote = "origin",
}) {
  const plans = await planReleaseTags({ root, before, after });
  const pending = plans.filter(({ action }) => action === "create");
  if (!pending.length) return plans;

  const taggerEnv = {
    GIT_COMMITTER_NAME: process.env.GIT_COMMITTER_NAME || "github-actions[bot]",
    GIT_COMMITTER_EMAIL:
      process.env.GIT_COMMITTER_EMAIL || "41898282+github-actions[bot]@users.noreply.github.com",
  };
  for (const plan of pending) {
    await git(root, ["tag", "-a", plan.tag, plan.commit, "-m", `${plan.plugin} ${plan.version}`], {
      env: taggerEnv,
    });
  }

  if (push) {
    try {
      await git(root, [
        "push",
        "--atomic",
        remote,
        ...pending.map(({ tag }) => `refs/tags/${tag}`),
      ]);
    } catch (error) {
      for (const { tag } of pending) await git(root, ["tag", "-d", tag], { optional: true });
      throw error;
    }
  }
  return plans;
}

function argument(name) {
  const index = process.argv.indexOf(name);
  return index === -1 ? null : process.argv[index + 1];
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const before = argument("--before");
  const after = argument("--after");
  const publish = process.argv.includes("--publish");
  if (!before || !after) throw new Error("--before and --after are required");
  if (publish && process.env.GITHUB_ACTIONS === "true" && process.env.GITHUB_REF !== "refs/heads/main") {
    throw new Error("Tag publication is restricted to the main branch");
  }
  const plans = publish
    ? await createReleaseTags({ before, after })
    : await planReleaseTags({ before, after });
  process.stdout.write(`${JSON.stringify({ plans }, null, 2)}\n`);
}
