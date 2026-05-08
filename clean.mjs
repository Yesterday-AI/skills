#!/usr/bin/env node
// Wipe all compiled artifacts so `node compile.mjs` rebuilds from scratch.
// Touches only `.compiled/` -- bundle symlinks under `plugins/*/` are source-of-truth and stay.

import { rm, lstat } from "node:fs/promises";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

async function exists(p) {
  try { await lstat(p); return true; } catch { return false; }
}

const ROOT = dirname(fileURLToPath(import.meta.url));
const TARGETS = [
  ".compiled/skill-plugins",
  ".compiled/marketplace.json",
  ".claude-plugin/marketplace.json",
  ".cursor-plugin/marketplace.json",
];

for (const t of TARGETS) {
  const p = join(ROOT, t);
  if (await exists(p)) {
    await rm(p, { recursive: true, force: true });
    console.log(`  removed  ${relative(ROOT, p)}`);
  } else {
    console.log(`  skip     ${relative(ROOT, p)} (not present)`);
  }
}

console.log("\nClean. Run `node compile.mjs` to regenerate.");
