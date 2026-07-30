#!/usr/bin/env node

import path from "node:path";
import { fileURLToPath } from "node:url";
import { run } from "../lib/runtime.mjs";

const derivedRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
await run("codex", { pluginRoot: process.env.PLUGIN_ROOT || derivedRoot });
