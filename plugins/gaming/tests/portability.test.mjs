import assert from "node:assert/strict";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { buildProjections } from "../../../tools/portability/sync-plugins.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const PLUGIN = path.join(ROOT, "plugins/gaming");
const SKILLS = ["setup", "onboard", "sync", "backup", "configure", "cheats"];
const MAX_SKILL_BYTES = 8000;

test("gaming canonical metadata generates both host projections and six skill UIs", async () => {
  const outputs = await buildProjections({ root: ROOT });
  assert(outputs.has("plugins/gaming/.claude-plugin/plugin.json"));
  assert(outputs.has("plugins/gaming/.codex-plugin/plugin.json"));
  for (const skill of SKILLS) assert(outputs.has(`plugins/gaming/skills/${skill}/agents/openai.yaml`));
});

test("gaming skills stay portable, calm and small", async () => {
  const forbidden = [
    /\$ARGUMENTS/,
    /CLAUDE_SKILL_DIR/,
    /CLAUDE_PLUGIN_(ROOT|DATA)/,
    /mcp__/,
    /\/gaming:/,
    /model:\s*(sonnet|opus|haiku|fable|gpt)/i,
    /\b(MUST|NEVER|ALWAYS|IMPORTANT|CRITICAL|REQUIRED|SHALL|DO NOT)\b/,
    /\u2014/,
  ];
  const texts = await Promise.all(
    SKILLS.map((skill) => readFile(path.join(PLUGIN, `skills/${skill}/SKILL.md`), "utf8")),
  );
  SKILLS.forEach((skill, index) => {
    const text = texts[index];
    assert.match(text, new RegExp(`^---\\nname: ${skill}\\ndescription: .+\\n---\\n`), `${skill} frontmatter`);
    assert(Buffer.byteLength(text) < MAX_SKILL_BYTES, `${skill} exceeds ${MAX_SKILL_BYTES} bytes`);
    for (const pattern of forbidden) assert.doesNotMatch(text, pattern, `${skill} contains ${pattern}`);
  });
});

test("every plugin-root path a skill or reference names exists", async () => {
  const files = [
    ...SKILLS.map((skill) => `skills/${skill}/SKILL.md`),
    "references/profile.md",
    "references/library-layout.md",
    "references/verification.md",
    "references/reviewer.md",
    "references/device-install.md",
    "references/frontend-baseline.md",
    "references/acquisition.md",
  ];
  const named = /`(?:<plugin root>\/)?((?:references|scripts)\/[\w./-]+?\.(?:md|py))`/g;
  const texts = await Promise.all(files.map((relative) => readFile(path.join(PLUGIN, relative), "utf8")));
  const targets = files.flatMap((relative, index) =>
    [...texts[index].matchAll(named)].map(([, target]) => ({ relative, target })),
  );
  assert(targets.length > 0, "expected skills and references to name bundled files");
  await Promise.all(
    targets.map(({ relative, target }) =>
      assert.doesNotReject(stat(path.join(PLUGIN, target)), `${relative} names missing ${target}`),
    ),
  );
});
