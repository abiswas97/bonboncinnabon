import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, rename, stat, unlink, writeFile } from "node:fs/promises";
import path from "node:path";

const MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000;

function dataDirectory(env = process.env) {
  return env.PLUGIN_DATA || env.CLAUDE_PLUGIN_DATA || null;
}

function key(host, sessionId) {
  return createHash("sha256").update(`${host}\0${sessionId}`).digest("hex").slice(0, 32);
}

async function prune(directory, now) {
  try {
    for (const name of await readdir(directory)) {
      if (!name.endsWith(".json")) continue;
      const file = path.join(directory, name);
      if (now - (await stat(file)).mtimeMs > MAX_AGE_MS) await unlink(file);
    }
  } catch {
    // Delivery state is an optimization. Never fail a host hook for cleanup.
  }
}

export async function readDeliveryState(host, sessionId, { env = process.env } = {}) {
  const root = dataDirectory(env);
  if (!root || !sessionId) return null;
  const directory = path.join(root, "standards-sessions");
  const file = path.join(directory, `${key(host, sessionId)}.json`);
  try {
    return { directory, file, value: JSON.parse(await readFile(file, "utf8")) };
  } catch {
    return { directory, file, value: { host, sessionHash: key(host, sessionId), deliveredRuleIds: [], updatedAt: null } };
  }
}

export async function recordDelivered(host, sessionId, ruleIds, { env = process.env, now = Date.now() } = {}) {
  const state = await readDeliveryState(host, sessionId, { env });
  if (!state) return false;
  try {
    await mkdir(state.directory, { recursive: true });
    const delivered = [...new Set([...(state.value.deliveredRuleIds ?? []), ...ruleIds])].sort();
    const value = {
      host,
      sessionHash: key(host, sessionId),
      deliveredRuleIds: delivered,
      updatedAt: new Date(now).toISOString(),
    };
    const temporary = `${state.file}.tmp-${process.pid}`;
    await writeFile(temporary, `${JSON.stringify(value, null, 2)}\n`, { mode: 0o600 });
    await rename(temporary, state.file);
    await prune(state.directory, now);
    return true;
  } catch {
    return false;
  }
}
