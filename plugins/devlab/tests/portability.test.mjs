import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { buildProjections } from "../../../tools/portability/sync-plugins.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const PLUGIN = path.join(ROOT, "plugins/devlab");
const SKILLS = ["setup", "sync", "dashboard", "brainstorm", "task", "task-pick", "task-close", "task-transition"];

test("DevLab canonical metadata generates both host projections and eight skill UIs", async () => {
  const outputs = await buildProjections({ root: ROOT });
  assert(outputs.has("plugins/devlab/.claude-plugin/plugin.json"));
  assert(outputs.has("plugins/devlab/.codex-plugin/plugin.json"));
  for (const skill of SKILLS) {
    assert(outputs.has(`plugins/devlab/skills/${skill}/agents/openai.yaml`));
  }
});

test("shared skills do not embed host-only workflow contracts", async () => {
  const forbidden = [
    /\$ARGUMENTS/,
    /CLAUDE_SKILL_DIR/,
    /mcp__plugin_/,
    /\.claude\/devlab-notion\.yaml/,
    /model:\s*(sonnet|opus)/i,
    /\/devlab:/,
  ];
  for (const skill of SKILLS) {
    const file = path.join(PLUGIN, `skills/${skill}/SKILL.md`);
    const text = await readFile(file, "utf8");
    assert.match(text, new RegExp(`^---\\nname: ${skill}\\ndescription: .+\\n---`));
    for (const pattern of forbidden) assert.doesNotMatch(text, pattern, `${skill} contains ${pattern}`);
  }
});
