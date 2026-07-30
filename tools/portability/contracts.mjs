import { readFile } from "node:fs/promises";
import path from "node:path";

const HOSTS = new Set(["claude", "codex"]);
const LIFECYCLES = new Set(["session", "compact", "plan", "edit", "complete"]);
const CLASSES = new Set(["enforced", "review", "advisory"]);
const RULE_ID = /^[A-Z][A-Z0-9-]+$/;
const NAME = /^[a-z0-9-]+$/;
const SEMVER = /^\d+\.\d+\.\d+$/;
const RESERVED_COMMANDMENT_IDS = new Set(
  Array.from({ length: 10 }, (_, index) => `C${String(index + 1).padStart(2, "0")}`),
);

export async function readJson(file) {
  try {
    return JSON.parse(await readFile(file, "utf8"));
  } catch (error) {
    throw new Error(`${file}: invalid JSON (${error.message})`);
  }
}

function object(value, at, errors) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    errors.push(`${at}: expected object`);
    return false;
  }
  return true;
}

function exactKeys(value, allowed, at, errors) {
  if (!object(value, at, errors)) return;
  for (const key of Object.keys(value)) {
    if (!allowed.includes(key)) errors.push(`${at}.${key}: unknown field`);
  }
}

function string(value, at, errors, pattern) {
  if (typeof value !== "string" || value.length === 0) {
    errors.push(`${at}: expected non-empty string`);
  } else if (pattern && !pattern.test(value)) {
    errors.push(`${at}: invalid value "${value}"`);
  }
}

function strings(value, at, errors, allowed) {
  if (!Array.isArray(value)) {
    errors.push(`${at}: expected array`);
    return;
  }
  const seen = new Set();
  value.forEach((entry, index) => {
    string(entry, `${at}[${index}]`, errors);
    if (allowed && !allowed.has(entry)) errors.push(`${at}[${index}]: unsupported value "${entry}"`);
    if (seen.has(entry)) errors.push(`${at}[${index}]: duplicate value "${entry}"`);
    seen.add(entry);
  });
}

function schemaVersion(value, at, errors) {
  if (value !== 1) errors.push(`${at}.schemaVersion: unsupported schema version ${JSON.stringify(value)}`);
}

function throwErrors(errors) {
  if (errors.length) throw new Error(errors.join("\n"));
}

export function validateMarketplace(value, file = "marketplace.json") {
  const errors = [];
  exactKeys(value, ["schemaVersion", "name", "displayName", "description", "owner", "plugins"], file, errors);
  schemaVersion(value?.schemaVersion, file, errors);
  string(value?.name, `${file}.name`, errors, NAME);
  string(value?.displayName, `${file}.displayName`, errors);
  string(value?.description, `${file}.description`, errors);
  exactKeys(value?.owner, ["name"], `${file}.owner`, errors);
  string(value?.owner?.name, `${file}.owner.name`, errors);
  if (!Array.isArray(value?.plugins)) errors.push(`${file}.plugins: expected array`);
  const names = new Set();
  for (const [index, plugin] of (value?.plugins ?? []).entries()) {
    const at = `${file}.plugins[${index}]`;
    exactKeys(plugin, ["name", "kind", "path", "hosts", "claudeEntry"], at, errors);
    string(plugin?.name, `${at}.name`, errors, NAME);
    if (names.has(plugin?.name)) errors.push(`${at}.name: duplicate plugin "${plugin?.name}"`);
    names.add(plugin?.name);
    if (!["local", "external"].includes(plugin?.kind)) errors.push(`${at}.kind: expected local or external`);
    strings(plugin?.hosts, `${at}.hosts`, errors, HOSTS);
    if (plugin?.kind === "local") string(plugin?.path, `${at}.path`, errors, /^\.\/plugins\/[a-z0-9-]+$/);
    if (plugin?.kind === "external" && !object(plugin?.claudeEntry, `${at}.claudeEntry`, errors)) continue;
    if (plugin?.kind === "external" && plugin?.hosts?.includes("codex")) {
      errors.push(`${at}.hosts: external plugins require a native local Codex package`);
    }
  }
  throwErrors(errors);
  return value;
}

export function validatePlugin(value, file = "plugin.json") {
  const errors = [];
  exactKeys(
    value,
    ["schemaVersion", "name", "version", "description", "author", "repository", "license", "category", "tags", "hosts", "components", "interface"],
    file,
    errors,
  );
  schemaVersion(value?.schemaVersion, file, errors);
  string(value?.name, `${file}.name`, errors, NAME);
  string(value?.version, `${file}.version`, errors, SEMVER);
  string(value?.description, `${file}.description`, errors);
  exactKeys(value?.author, ["name"], `${file}.author`, errors);
  string(value?.author?.name, `${file}.author.name`, errors);
  string(value?.repository, `${file}.repository`, errors, /^https:\/\//);
  string(value?.license, `${file}.license`, errors);
  string(value?.category, `${file}.category`, errors);
  strings(value?.tags, `${file}.tags`, errors);
  strings(value?.hosts, `${file}.hosts`, errors, HOSTS);
  exactKeys(value?.components, ["skills", "commands", "hooks"], `${file}.components`, errors);
  if (!Array.isArray(value?.components?.skills)) errors.push(`${file}.components.skills: expected array`);
  const skills = new Set();
  for (const [index, skill] of (value?.components?.skills ?? []).entries()) {
    const at = `${file}.components.skills[${index}]`;
    exactKeys(skill, ["name", "displayName", "shortDescription", "defaultPrompt"], at, errors);
    string(skill?.name, `${at}.name`, errors, NAME);
    if (skills.has(skill?.name)) errors.push(`${at}.name: duplicate skill "${skill?.name}"`);
    skills.add(skill?.name);
    string(skill?.displayName, `${at}.displayName`, errors);
    string(skill?.shortDescription, `${at}.shortDescription`, errors);
    if (typeof skill?.shortDescription === "string" && (skill.shortDescription.length < 25 || skill.shortDescription.length > 64)) {
      errors.push(`${at}.shortDescription: expected 25-64 characters`);
    }
    string(skill?.defaultPrompt, `${at}.defaultPrompt`, errors);
    if (typeof skill?.defaultPrompt === "string" && !skill.defaultPrompt.includes(`$${skill?.name}`)) {
      errors.push(`${at}.defaultPrompt: must mention $${skill?.name}`);
    }
  }
  strings(value?.components?.commands, `${file}.components.commands`, errors);
  if (typeof value?.components?.hooks !== "boolean") errors.push(`${file}.components.hooks: expected boolean`);
  exactKeys(
    value?.interface,
    ["displayName", "shortDescription", "longDescription", "developerName", "capabilities", "defaultPrompt"],
    `${file}.interface`,
    errors,
  );
  for (const key of ["displayName", "shortDescription", "longDescription", "developerName", "defaultPrompt"]) {
    string(value?.interface?.[key], `${file}.interface.${key}`, errors);
  }
  strings(value?.interface?.capabilities, `${file}.interface.capabilities`, errors);
  throwErrors(errors);
  return value;
}

export function validateRule(rule, at, errors = []) {
  exactKeys(rule, ["id", "title", "summary", "class", "lifecycles", "paths", "roles", "reference"], at, errors);
  string(rule?.id, `${at}.id`, errors, RULE_ID);
  string(rule?.title, `${at}.title`, errors);
  string(rule?.summary, `${at}.summary`, errors);
  if (!CLASSES.has(rule?.class)) errors.push(`${at}.class: unsupported value "${rule?.class}"`);
  strings(rule?.lifecycles, `${at}.lifecycles`, errors, LIFECYCLES);
  strings(rule?.paths, `${at}.paths`, errors);
  strings(rule?.roles, `${at}.roles`, errors);
  string(rule?.reference, `${at}.reference`, errors, /^references\/[a-z0-9-]+\.md$/);
  return errors;
}

export function validateRegistry(value, file = "registry.json") {
  const errors = [];
  exactKeys(value, ["schemaVersion", "rules"], file, errors);
  schemaVersion(value?.schemaVersion, file, errors);
  if (!Array.isArray(value?.rules)) errors.push(`${file}.rules: expected array`);
  const ids = new Set();
  for (const [index, rule] of (value?.rules ?? []).entries()) {
    validateRule(rule, `${file}.rules[${index}]`, errors);
    if (ids.has(rule?.id)) errors.push(`${file}.rules[${index}].id: duplicate rule "${rule?.id}"`);
    if (RESERVED_COMMANDMENT_IDS.has(rule?.id)) errors.push(`${file}.rules[${index}].id: commandment IDs are reserved`);
    ids.add(rule?.id);
  }
  throwErrors(errors);
  return value;
}

export function validateOverlay(value, file = ".standards/standards.json") {
  const errors = [];
  exactKeys(value, ["schemaVersion", "extends", "rules"], file, errors);
  schemaVersion(value?.schemaVersion, file, errors);
  if (value?.extends !== undefined && value.extends !== "default") {
    errors.push(`${file}.extends: only "default" is supported`);
  }
  if (!Array.isArray(value?.rules)) errors.push(`${file}.rules: expected array`);
  const ids = new Set();
  for (const [index, rule] of (value?.rules ?? []).entries()) {
    validateRule(rule, `${file}.rules[${index}]`, errors);
    if (ids.has(rule?.id)) errors.push(`${file}.rules[${index}].id: duplicate rule "${rule?.id}"`);
    if (RESERVED_COMMANDMENT_IDS.has(rule?.id)) errors.push(`${file}.rules[${index}].id: commandment IDs are immutable`);
    ids.add(rule?.id);
  }
  throwErrors(errors);
  return value;
}

export function assertPathInside(root, candidate) {
  const relative = path.relative(path.resolve(root), path.resolve(root, candidate));
  if (relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative))) return relative || ".";
  return null;
}

export { RESERVED_COMMANDMENT_IDS };
