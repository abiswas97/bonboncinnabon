import assert from "node:assert/strict";
import test from "node:test";
import {
  validateMarketplace,
  validateOverlay,
  validatePlugin,
  validateRegistry,
} from "../tools/portability/contracts.mjs";

function validRule(id = "TEST-RULE") {
  return {
    id,
    title: "Test rule",
    summary: "A test rule with complete metadata.",
    class: "review",
    lifecycles: ["plan"],
    paths: ["**/*"],
    roles: ["implementation"],
    reference: "references/test.md",
  };
}

test("canonical marketplace rejects unsupported external Codex entries", () => {
  assert.throws(
    () =>
      validateMarketplace({
        schemaVersion: 1,
        name: "example",
        displayName: "Example",
        description: "Example marketplace",
        owner: { name: "Owner" },
        plugins: [
          {
            name: "remote",
            kind: "external",
            hosts: ["codex"],
            claudeEntry: { name: "remote" },
          },
        ],
      }),
    /native local Codex package/,
  );
});

test("canonical plugin reports a field-level missing version diagnostic", () => {
  assert.throws(
    () =>
      validatePlugin({
        schemaVersion: 1,
        name: "example",
      }),
    /plugin\.json\.version: expected non-empty string/,
  );
});

test("registry rejects duplicate rule IDs", () => {
  assert.throws(
    () => validateRegistry({ schemaVersion: 1, rules: [validRule(), validRule()] }),
    /duplicate rule/,
  );
});

test("overlay rejects unknown fields and immutable commandments", () => {
  assert.throws(
    () =>
      validateOverlay({
        schemaVersion: 1,
        extends: "default",
        surprise: true,
        rules: [validRule("C01")],
      }),
    /unknown field[\s\S]*commandment IDs are immutable/,
  );
});

test("overlay rejects unsupported schema versions and selectors", () => {
  const rule = validRule();
  rule.lifecycles = ["ship"];
  assert.throws(
    () => validateOverlay({ schemaVersion: 2, rules: [rule] }),
    /unsupported schema version[\s\S]*unsupported value "ship"/,
  );
});

test("registry rejects the removed complete lifecycle", () => {
  const rule = validRule();
  rule.lifecycles = ["complete"];
  assert.throws(
    () => validateRegistry({ schemaVersion: 1, rules: [rule] }),
    /unsupported value "complete"/,
  );
});
