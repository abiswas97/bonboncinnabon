import { readFile } from "node:fs/promises";
import path from "node:path";
import { adaptPayload, nativeResponse } from "./adapters.mjs";
import { compactGitContext } from "./git-context.mjs";
import { resolveStandards } from "./resolver.mjs";
import { readDeliveryState, recordDelivered } from "./state.mjs";

const SESSION_LIMIT = 7_000;
const EVENT_LIMIT = 2_500;
const RULE_LIMIT = 6;

function boundedRules(rules) {
  const selected = [];
  for (const rule of rules) {
    if (selected.length === RULE_LIMIT) break;
    const next = [...selected, rule];
    const rendered = renderRules(next, rules.length > next.length);
    if (rendered.length > EVENT_LIMIT) break;
    selected.push(rule);
  }
  return selected;
}

function renderRules(rules, truncated = false) {
  if (!rules.length) return "";
  const lines = ["Applicable standards:"];
  rules.forEach((rule) => lines.push(`- ${rule.id}: ${rule.summary}`));
  if (truncated) lines.push("- More rules apply. Use $standards for the resolved details.");
  return lines.join("\n");
}

async function sessionGuidance(pluginRoot, includeGit, repositoryRoot) {
  const commandments = (await readFile(path.join(pluginRoot, "standards/commandments.md"), "utf8")).trim();
  const registry = JSON.parse(await readFile(path.join(pluginRoot, "standards/registry.json"), "utf8"));
  const index = registry.rules.map((rule) => `- ${rule.id}: ${rule.summary}`).join("\n");
  const git = includeGit ? await compactGitContext(repositoryRoot) : null;
  const guidance = [commandments, "## Supporting rule index", index, git ? `## Working context\n\n${git}` : null]
    .filter(Boolean)
    .join("\n\n");
  if (guidance.length > SESSION_LIMIT) {
    throw new Error(`Session guidance exceeds ${SESSION_LIMIT} characters; commandments must not be truncated`);
  }
  return guidance;
}

export async function handleEvent(host, payload, { pluginRoot, env = process.env } = {}) {
  const repositoryRoot = path.resolve(typeof payload?.cwd === "string" ? payload.cwd : process.cwd());
  const event = adaptPayload(host, payload, repositoryRoot);
  if (!event) return null;
  if (event.lifecycle === "session" || event.lifecycle === "compact") {
    return nativeResponse(event, await sessionGuidance(pluginRoot, event.lifecycle === "compact", repositoryRoot));
  }
  const resolved = await resolveStandards({
    pluginRoot,
    repositoryRoot,
    lifecycle: event.lifecycle,
    role: event.role,
    paths: event.paths,
  });
  let rules = resolved.rules;
  const state = await readDeliveryState(host, event.sessionId, { env });
  if (state) {
    const delivered = new Set(state.value.deliveredRuleIds ?? []);
    rules = rules.filter((rule) => !delivered.has(rule.id));
  }
  const selected = boundedRules(rules);
  if (!selected.length) return null;
  let guidance = renderRules(selected, selected.length < rules.length);
  if (resolved.conflicts.length) guidance += `\n${resolved.conflicts.map(({ message }) => `- Conflict: ${message}`).join("\n")}`;
  if (guidance.length > EVENT_LIMIT) guidance = guidance.slice(0, EVENT_LIMIT - 1).trimEnd();
  await recordDelivered(host, event.sessionId, selected.map(({ id }) => id), { env });
  return nativeResponse(event, guidance);
}

export async function readPayload(stream = process.stdin, maxBytes = 1024 * 1024) {
  let input = "";
  for await (const chunk of stream) {
    input += chunk;
    if (Buffer.byteLength(input) > maxBytes) return null;
  }
  try {
    return JSON.parse(input);
  } catch {
    return null;
  }
}

export async function run(host, { pluginRoot, env = process.env } = {}) {
  const payload = await readPayload();
  if (!payload) return;
  try {
    const response = await handleEvent(host, payload, { pluginRoot, env });
    if (response) process.stdout.write(`${JSON.stringify(response)}\n`);
  } catch (error) {
    if (env.STANDARDS_DEBUG === "1") process.stderr.write(`[standards] ${error.message}\n`);
  }
}
