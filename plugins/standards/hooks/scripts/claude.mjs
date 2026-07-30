#!/usr/bin/env node

import path from "node:path";
import { fileURLToPath } from "node:url";
import { run } from "../lib/runtime.mjs";

const derivedRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
await run("claude", { pluginRoot: process.env.CLAUDE_PLUGIN_ROOT || derivedRoot });
