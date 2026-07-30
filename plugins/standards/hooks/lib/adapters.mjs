import path from "node:path";

const EVENT_LIFECYCLE = new Map([
  ["SessionStart", "session"],
  ["PostToolUse", "edit"],
  ["SubagentStart", "subagent"],
]);
const CONTEXT_EVENTS = new Set(["SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse", "SubagentStart"]);

function inside(root, candidate) {
  if (typeof candidate !== "string" || candidate.length === 0) return null;
  const absolute = path.resolve(root, candidate);
  const relative = path.relative(root, absolute);
  if (relative.startsWith("..") || path.isAbsolute(relative)) return null;
  return relative.replaceAll(path.sep, "/") || ".";
}

export function patchPaths(value) {
  if (typeof value !== "string") return [];
  const paths = [];
  for (const line of value.split(/\r?\n/)) {
    const match = line.match(/^\*\*\* (?:Add|Update|Delete) File: (.+)$/) ?? line.match(/^\*\*\* Move to: (.+)$/);
    if (match) paths.push(match[1].trim());
  }
  return paths;
}

export function affectedPaths(payload, repositoryRoot) {
  const input = payload?.tool_input ?? {};
  const candidates = [
    input.file_path,
    input.path,
    input.old_path,
    input.new_path,
    ...patchPaths(input.command),
    ...patchPaths(input.input),
    ...patchPaths(input.patch),
  ];
  return [...new Set(candidates.map((candidate) => inside(repositoryRoot, candidate)).filter(Boolean))];
}

function lifecycle(payload) {
  if (payload?.hook_event_name === "PreToolUse" && payload?.tool_name === "ExitPlanMode") return "plan";
  if (payload?.hook_event_name === "UserPromptSubmit") {
    return payload?.permission_mode === "plan" || payload?.mode === "plan" ? "plan" : null;
  }
  return EVENT_LIFECYCLE.get(payload?.hook_event_name) ?? null;
}

export function adaptPayload(host, payload, repositoryRoot) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return null;
  const resolvedLifecycle = lifecycle(payload);
  if (!resolvedLifecycle) return null;
  const toolName = typeof payload.tool_name === "string" ? payload.tool_name : null;
  if (resolvedLifecycle === "edit" && !["Write", "Edit", "apply_patch"].includes(toolName)) return null;
  return {
    host,
    nativeEvent: payload.hook_event_name,
    lifecycle: resolvedLifecycle,
    sessionId: typeof payload.session_id === "string" ? payload.session_id : null,
    repositoryRoot,
    paths: resolvedLifecycle === "edit" ? affectedPaths(payload, repositoryRoot) : [],
    role: "implementation",
    toolName,
    source: resolvedLifecycle === "session" && typeof payload.source === "string" ? payload.source : null,
  };
}

export function nativeResponse(event, guidance) {
  if (!event || !guidance || !CONTEXT_EVENTS.has(event.nativeEvent)) return null;
  return {
    hookSpecificOutput: {
      hookEventName: event.nativeEvent,
      additionalContext: guidance,
    },
  };
}
