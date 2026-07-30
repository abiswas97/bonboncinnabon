import { execFile } from "node:child_process";
import path from "node:path";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);
const OPTIONS = {
  timeout: 750,
  maxBuffer: 16 * 1024,
  encoding: "utf8",
  windowsHide: true,
};

async function git(root, args) {
  const { stdout } = await execFileAsync("git", ["-C", root, ...args], OPTIONS);
  return stdout.trim();
}

async function safeGit(root, args) {
  try {
    return await git(root, args);
  } catch {
    return "";
  }
}

export async function compactGitContext(root) {
  try {
    const inside = await git(root, ["rev-parse", "--is-inside-work-tree"]);
    if (inside !== "true") return null;
    const [branch, status, recent] = await Promise.all([
      safeGit(root, ["branch", "--show-current"]),
      safeGit(root, ["status", "--porcelain=v1", "-uno"]),
      safeGit(root, ["log", "-1", "--pretty=%h %s"]),
    ]);
    const changed = status
      .split("\n")
      .filter(Boolean)
      .map((line) => line.slice(3))
      .slice(0, 12);
    const omitted = Math.max(0, status.split("\n").filter(Boolean).length - changed.length);
    return [
      `Repository: ${path.basename(root)}`,
      `Branch: ${branch || "detached HEAD"}`,
      `Changed tracked paths: ${changed.length}${omitted ? ` (+${omitted} more)` : ""}${changed.length ? ` — ${changed.join(", ")}` : ""}`,
      recent ? `Recent commit: ${recent.slice(0, 160)}` : null,
    ]
      .filter(Boolean)
      .join("\n");
  } catch {
    return null;
  }
}
