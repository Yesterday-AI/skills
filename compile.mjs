#!/usr/bin/env node
//
// compile.mjs -- Skills + Plugins -> Marketplace compile pipeline
// =================================================================
//
// Spec source: tbd
// Decisions:   ./.ytstack/DECISIONS.md  (rationale, alternatives, why)
// Knowledge:   ./.ytstack/KNOWLEDGE.md  (conventions, gotchas)
//
// What it does
// ------------
// 1. Wipes and rebuilds `.compiled/skill-plugins/`.
// 2. Discovers every `skills/**/SKILL.md`. Slug = parent-folder name.
//    Collisions are skipped with a warning.
// 3. Per skill, creates `.compiled/skill-plugins/<slug>/`:
//      - skills/<slug>                 -> symlink to source folder
//      - .claude-plugin/plugin.json    -> symlink to source `.plugin.json` if it
//                                         exists, else generated from SKILL.md
//                                         frontmatter (name + description)
//      - .cursor-plugin/plugin.json    -> same
// 4. Generates `.compiled/marketplace.json` by merging:
//      - top-level header from `./marketplace.json`
//        (name + description + owner + optional `plugins[]` for externals like
//         github-sourced ytstack)
//      - bundles auto-discovered from `plugins/<bundle>/plugin.json`
//      - standalone auto-discovered from `.compiled/skill-plugins/<slug>/`
//    Then symlinks it into `./.claude-plugin/marketplace.json` and
//    `./.cursor-plugin/marketplace.json` at workspace root.
//
// Run
// ---
//   node compile.mjs        (from skills/ repo root)
//
// Idempotent. Wipes `.compiled/skill-plugins/` each run; do not hand-edit there.
//

import { readdir, readFile, mkdir, symlink, rm, writeFile, stat } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join, relative, resolve, basename } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(fileURLToPath(import.meta.url));
const SKILLS_DIR = join(ROOT, "skills");
const COMPILED_DIR = join(ROOT, ".compiled");
const OUT_DIR = join(COMPILED_DIR, "skill-plugins");
const MARKETPLACE_HEADER = join(ROOT, "marketplace.json");
const MARKETPLACE_OUT = join(COMPILED_DIR, "marketplace.json");
const PLUGINS_DIR = join(ROOT, "plugins");

async function walk(dir, out = []) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    if (entry.name.startsWith(".")) continue;
    const full = join(dir, entry.name);
    if (entry.isDirectory()) await walk(full, out);
    else if (entry.isFile() && entry.name === "SKILL.md") out.push(full);
  }
  return out;
}

function parseFrontmatter(md) {
  const m = md.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) return {};
  const fm = {};
  for (const line of m[1].split(/\r?\n/)) {
    const kv = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!kv) continue;
    let v = kv[2].trim();
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
      v = v.slice(1, -1);
    }
    fm[kv[1]] = v;
  }
  return fm;
}

async function ensureSymlink(target, linkPath) {
  if (existsSync(linkPath)) await rm(linkPath, { recursive: true, force: true });
  await mkdir(dirname(linkPath), { recursive: true });
  const rel = relative(dirname(linkPath), target);
  await symlink(rel, linkPath);
}

async function writePluginJson(linkPath, data) {
  if (existsSync(linkPath)) await rm(linkPath, { force: true });
  await mkdir(dirname(linkPath), { recursive: true });
  await writeFile(linkPath, JSON.stringify(data, null, 2) + "\n");
}

function toMarketplaceEntry(plugin, source) {
  const entry = {
    name: plugin.name,
    description: plugin.description || "",
    source,
  };
  if (plugin.author) entry.author = plugin.author;
  if (Array.isArray(plugin.keywords) && plugin.keywords.length) entry.keywords = plugin.keywords;
  return entry;
}

// For each bundle with a canonical `plugins/<name>/plugin.json`, ensure the
// editor-specific manifest folders exist with a relative symlink back to the
// canonical file. Idempotent: existing correct symlinks are left alone.
async function scaffoldBundleSymlinks() {
  if (!existsSync(PLUGINS_DIR)) return;
  for (const entry of await readdir(PLUGINS_DIR, { withFileTypes: true })) {
    if (!entry.isDirectory() || entry.name.startsWith(".")) continue;
    const bundleDir = join(PLUGINS_DIR, entry.name);
    const canonical = join(bundleDir, "plugin.json");
    if (!existsSync(canonical)) continue;
    for (const sub of [".claude-plugin", ".cursor-plugin"]) {
      await ensureSymlink(canonical, join(bundleDir, sub, "plugin.json"));
    }
  }
}

async function discoverBundleEntries() {
  const entries = [];
  if (!existsSync(PLUGINS_DIR)) return entries;
  for (const entry of await readdir(PLUGINS_DIR, { withFileTypes: true })) {
    if (!entry.isDirectory() || entry.name.startsWith(".")) continue;
    const manifest = join(PLUGINS_DIR, entry.name, "plugin.json");
    if (!existsSync(manifest)) continue;
    const plugin = JSON.parse(await readFile(manifest, "utf8"));
    entries.push(toMarketplaceEntry(plugin, `./plugins/${entry.name}`));
  }
  return entries.sort((a, b) => a.name.localeCompare(b.name));
}

async function discoverStandaloneEntries() {
  const entries = [];
  if (!existsSync(OUT_DIR)) return entries;
  for (const entry of await readdir(OUT_DIR, { withFileTypes: true })) {
    if (!entry.isDirectory() || entry.name.startsWith(".")) continue;
    const manifest = join(OUT_DIR, entry.name, ".claude-plugin", "plugin.json");
    if (!existsSync(manifest)) continue;
    const plugin = JSON.parse(await readFile(manifest, "utf8"));
    entries.push(toMarketplaceEntry(plugin, `./.compiled/skill-plugins/${entry.name}`));
  }
  return entries.sort((a, b) => a.name.localeCompare(b.name));
}

async function compileMarketplace() {
  if (!existsSync(MARKETPLACE_HEADER)) {
    console.warn(`! ${relative(ROOT, MARKETPLACE_HEADER)} not found -- skipping marketplace`);
    return;
  }
  const header = JSON.parse(await readFile(MARKETPLACE_HEADER, "utf8"));
  const externals = Array.isArray(header.plugins) ? header.plugins : [];
  const bundles = await discoverBundleEntries();
  const standalone = await discoverStandaloneEntries();

  // Pass through every top-level field except `plugins` (rebuilt from sources).
  // This keeps optional spec fields like `allowCrossMarketplaceDependenciesOn`,
  // `metadata`, `version` flowing into the compiled marketplace.
  const { plugins: _ignore, ...passthrough } = header;
  const data = {
    ...passthrough,
    plugins: [...externals, ...bundles, ...standalone],
  };

  if (existsSync(MARKETPLACE_OUT)) await rm(MARKETPLACE_OUT, { force: true });
  await writeFile(MARKETPLACE_OUT, JSON.stringify(data, null, 2) + "\n");
  await ensureSymlink(MARKETPLACE_OUT, join(ROOT, ".claude-plugin", "marketplace.json"));
  await ensureSymlink(MARKETPLACE_OUT, join(ROOT, ".cursor-plugin", "marketplace.json"));
  console.log(
    `\nMarketplace -> ${relative(ROOT, MARKETPLACE_OUT)}  ` +
      `(${externals.length} external + ${bundles.length} bundles + ${standalone.length} standalone)` +
      `\n              + symlinks: ./.claude-plugin/marketplace.json, ./.cursor-plugin/marketplace.json`,
  );
}

async function compile() {
  if (!existsSync(SKILLS_DIR)) {
    console.error(`No skills/ at ${SKILLS_DIR}`);
    process.exit(1);
  }
  await rm(OUT_DIR, { recursive: true, force: true });
  await mkdir(OUT_DIR, { recursive: true });

  await scaffoldBundleSymlinks();

  const skillFiles = await walk(SKILLS_DIR);
  const seen = new Map();
  let count = 0;

  for (const skillMd of skillFiles) {
    const sourceDir = dirname(skillMd);
    const slug = basename(sourceDir);

    if (seen.has(slug)) {
      console.error(`! slug collision "${slug}": ${sourceDir} vs ${seen.get(slug)} -- skipping`);
      continue;
    }
    seen.set(slug, sourceDir);

    const fm = parseFrontmatter(await readFile(skillMd, "utf8"));
    const pluginDir = join(OUT_DIR, slug);

    // 1. skills/<slug> symlink -> source folder
    await ensureSymlink(sourceDir, join(pluginDir, "skills", slug));

    // 2. plugin.json: symlink source/.plugin.json if present, else generate
    const sourcePluginJson = join(sourceDir, ".plugin.json");
    const claudeTarget = join(pluginDir, ".claude-plugin", "plugin.json");
    const cursorTarget = join(pluginDir, ".cursor-plugin", "plugin.json");

    if (existsSync(sourcePluginJson)) {
      await ensureSymlink(sourcePluginJson, claudeTarget);
      await ensureSymlink(sourcePluginJson, cursorTarget);
    } else {
      const generated = {
        name: fm.name || slug,
        description: fm.description || "",
      };
      await writePluginJson(claudeTarget, generated);
      await writePluginJson(cursorTarget, generated);
    }

    count++;
    console.log(`  ${slug}  (${existsSync(sourcePluginJson) ? "symlinked" : "generated"})`);
  }

  console.log(`\nCompiled ${count} skill-plugins -> ${relative(ROOT, OUT_DIR)}`);
  await compileMarketplace();
}

compile().catch((e) => {
  console.error(e);
  process.exit(1);
});
