import { access, readFile } from "node:fs/promises";
import path from "node:path";

const COMMANDMENTS = new Set(Array.from({ length: 10 }, (_, index) => `C${String(index + 1).padStart(2, "0")}`));
const LIFECYCLES = new Set(["session", "plan", "edit", "subagent"]);
const CLASSES = new Set(["enforced", "review", "advisory"]);
const RULE_KEYS = new Set(["id", "title", "summary", "class", "lifecycles", "paths", "roles", "reference"]);

async function exists(file) {
  try {
    await access(file);
    return true;
  } catch {
    return false;
  }
}

async function readJson(file) {
  try {
    return JSON.parse(await readFile(file, "utf8"));
  } catch (error) {
    throw new Error(`${file}: invalid JSON (${error.message})`);
  }
}

function validateRule(rule, at, seen) {
  if (!rule || typeof rule !== "object" || Array.isArray(rule)) throw new Error(`${at}: expected object`);
  for (const key of Object.keys(rule)) {
    if (!RULE_KEYS.has(key)) throw new Error(`${at}.${key}: unknown field`);
  }
  for (const key of RULE_KEYS) {
    if (!(key in rule)) throw new Error(`${at}.${key}: missing field`);
  }
  if (!/^[A-Z][A-Z0-9-]+$/.test(rule.id)) throw new Error(`${at}.id: invalid rule ID`);
  if (COMMANDMENTS.has(rule.id)) throw new Error(`${at}.id: commandment IDs are immutable`);
  if (seen.has(rule.id)) throw new Error(`${at}.id: duplicate rule "${rule.id}"`);
  seen.add(rule.id);
  if (!CLASSES.has(rule.class)) throw new Error(`${at}.class: unsupported value "${rule.class}"`);
  for (const [key, allowed] of [["lifecycles", LIFECYCLES], ["paths", null], ["roles", null]]) {
    if (!Array.isArray(rule[key])) throw new Error(`${at}.${key}: expected array`);
    if (new Set(rule[key]).size !== rule[key].length) throw new Error(`${at}.${key}: duplicate selector`);
    if (allowed) {
      const invalid = rule[key].find((entry) => !allowed.has(entry));
      if (invalid) throw new Error(`${at}.${key}: unsupported value "${invalid}"`);
    }
  }
  if (typeof rule.title !== "string" || typeof rule.summary !== "string" || typeof rule.reference !== "string") {
    throw new Error(`${at}: title, summary, and reference must be strings`);
  }
}

function validateRules(value, file, { overlay = false } = {}) {
  const keys = new Set(overlay ? ["schemaVersion", "extends", "rules"] : ["schemaVersion", "rules"]);
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error(`${file}: expected object`);
  for (const key of Object.keys(value)) if (!keys.has(key)) throw new Error(`${file}.${key}: unknown field`);
  if (value.schemaVersion !== 1) throw new Error(`${file}.schemaVersion: unsupported schema version ${JSON.stringify(value.schemaVersion)}`);
  if (overlay && value.extends !== undefined && value.extends !== "default") {
    throw new Error(`${file}.extends: only "default" is supported`);
  }
  if (!Array.isArray(value.rules)) throw new Error(`${file}.rules: expected array`);
  const seen = new Set();
  value.rules.forEach((rule, index) => validateRule(rule, `${file}.rules[${index}]`, seen));
  return value;
}

export async function findRepositoryRoot(start = process.cwd()) {
  let current = path.resolve(start);
  for (;;) {
    if (await exists(path.join(current, ".git")) || await exists(path.join(current, ".standards/standards.json"))) return current;
    const parent = path.dirname(current);
    if (parent === current) return path.resolve(start);
    current = parent;
  }
}

function expandBraces(pattern) {
  const match = pattern.match(/\{([^{}]+)\}/);
  if (!match) return [pattern];
  return match[1]
    .split(",")
    .flatMap((choice) => expandBraces(`${pattern.slice(0, match.index)}${choice}${pattern.slice(match.index + match[0].length)}`));
}

function globRegex(pattern) {
  let source = "";
  for (let index = 0; index < pattern.length; index += 1) {
    const char = pattern[index];
    if (char === "*" && pattern[index + 1] === "*") {
      if (pattern[index + 2] === "/") {
        source += "(?:.*/)?";
        index += 2;
      } else {
        source += ".*";
        index += 1;
      }
    } else if (char === "*") {
      source += "[^/]*";
    } else if (char === "?") {
      source += "[^/]";
    } else {
      source += /[.+^$()|[\]\\]/.test(char) ? `\\${char}` : char;
    }
  }
  return new RegExp(`^${source}$`);
}

export function matchesGlob(file, pattern) {
  const normalized = file.replaceAll(path.sep, "/");
  return expandBraces(pattern).some((expanded) => globRegex(expanded).test(normalized));
}

export function selectRules(rules, { lifecycle, role, paths = [] } = {}) {
  return rules.filter((rule) => {
    if (lifecycle && !rule.lifecycles.includes(lifecycle)) return false;
    if (role && rule.roles.length && !rule.roles.includes(role)) return false;
    if (paths.length && rule.paths.length && !paths.some((file) => rule.paths.some((pattern) => matchesGlob(file, pattern)))) return false;
    return true;
  });
}

export async function resolveStandards({
  pluginRoot,
  repositoryRoot,
  lifecycle,
  role,
  paths = [],
  instructionOverrides = [],
} = {}) {
  const registryFile = path.join(pluginRoot, "standards/registry.json");
  const defaults = validateRules(await readJson(registryFile), registryFile).rules;
  const overlayFile = path.join(repositoryRoot, ".standards/standards.json");
  let effective = defaults;
  if (await exists(overlayFile)) {
    const overlay = validateRules(await readJson(overlayFile), overlayFile, { overlay: true });
    const repositoryRules = overlay.rules.map((rule) => ({ ...rule, referenceRoot: path.dirname(overlayFile) }));
    if (overlay.extends === "default") {
      const merged = new Map(defaults.map((rule) => [rule.id, { ...rule, referenceRoot: path.join(pluginRoot, "standards") }]));
      repositoryRules.forEach((rule) => merged.set(rule.id, rule));
      effective = [...merged.values()];
    } else {
      effective = repositoryRules;
    }
  } else {
    effective = defaults.map((rule) => ({ ...rule, referenceRoot: path.join(pluginRoot, "standards") }));
  }
  const defaultIds = new Set(defaults.map((rule) => rule.id));
  const conflicts = instructionOverrides
    .filter(({ ruleId }) => defaultIds.has(ruleId))
    .map(({ ruleId, source, reason }) => ({
      ruleId,
      source,
      message: `${source} supersedes portable supporting rule ${ruleId}${reason ? `: ${reason}` : ""}`,
    }));
  return {
    rules: selectRules(effective, { lifecycle, role, paths }),
    conflicts,
    overlayFile: (await exists(overlayFile)) ? overlayFile : null,
  };
}
