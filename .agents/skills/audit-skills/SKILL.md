---
name: audit-skills
description: Audit this repo's skills + plugins on three axes -- (1) leaks of personal info or Yesterday-internal references in user-facing artifacts, (2) catalog consistency (folder/name/dep/install-target alignment), (3) plugin-spec compliance (Claude Code + Cursor manifest schemas, layout rules). Reports findings as a triage list; does not auto-fix. Use before publishing, before merging skill PRs, or as a periodic hygiene pass.
metadata:
  category: hygiene
  scope: repo-local
---

# audit-skills

Heuristic scanner + structured checker for everything that should not ship. Fast (grep + JSON parse), false-positive-tolerant, never silently rewrites files. The agent classifies and the human decides.

## When to use

- Before publishing a new skill / plugin
- Before merging a skill PR from another contributor
- After a refactor that touched multiple SKILL.md, plugin.json, README.md, or marketplace.json files
- After bumping plugin/marketplace conventions or rename rounds
- Periodic hygiene pass (monthly, before releases)
- After the official validator (`claude plugin validate .`) surfaces a warning that smells like a structural drift

## Three axes

### 1. Leaks (personal info + internal references)

User-facing fields (description, keywords, frontmatter, README excerpts) where the content shouldn't be public.

**Personal info (always blocking, regardless of catalog visibility):**

- Real names of contributors (other than `Yesterday` org / public author handles)
- Private email addresses (look for `@` not on documented public domains)
- Local filesystem paths that reveal a username (`/Users/<name>/`, `/home/<name>/`, `C:\Users\<name>\`)
- Personal IPs, hostnames, machine names (e.g. `kcma-d8`, `nas1`, `192.168.x.x`, `*.lan`, `*.local`)
- Personal API keys / tokens (`sk-…`, `ghp_…`, `xoxb-…`, anything matching common secret patterns)
- Browser bookmarks, session cookies, OAuth callback URLs with state tokens

**Yesterday-internal (blocking in PUBLIC catalogs, expected in PRIVATE):**

- Internal repo names ending in `-internal` (e.g. `yopstack-internal`, `ystacks-internal`)
- Internal infrastructure hostnames (`*.yester.cloud` is mostly public; `*.yesterday.internal` / `*.ys.internal` is not)
- Internal Slack channels, Linear project codes, internal Notion URLs
- Refactoring history phrases ("promoted from .*-internal", "moved out of .*-internal", "vendored from temp-home")
- Internal team member shorthand
- Yesterday-only dependency declarations (`marketplace: "<name>-internal"`) in plugins meant for the public catalog
- TODO/FIXME/XXX comments referencing internal Jira/Linear tickets

**Migration-history framing (blocking in PUBLIC catalogs, OK in `.ytstack/` history records):**

- `formerly X`, `previously X`, `predecessor`, `(renamed: X)`, `migrated from`
- Old plugin names that have been renamed (`yopstack`, `yastack`, `ydstack`, `ydstack-extras`, `ystacks` in the public Yesterday catalog)

### 2. Catalog consistency (structural drift)

Mechanical alignment checks across the repo. Failures here usually mean install will silently break or the marketplace will surface mismatched info.

| Check | Why it matters |
| --- | --- |
| `marketplace.json.name` matches every install command in READMEs / docs | Users copy-paste commands; mismatched marketplace name = "no such plugin" errors |
| Bundle folder name === `plugin.json.name` | Inconsistency confuses maintainers; `compile.mjs` slug = folder name but marketplace surfaces `plugin.name` |
| Every cross-marketplace dep target (`{name, marketplace}`) actually exists in that marketplace | Spec blocks cross-mp deps not allow-listed; install fails silently |
| `marketplace.json.allowCrossMarketplaceDependenciesOn` covers every marketplace named in any bundle's `dependencies[]` | Spec rule: cross-mp deps from un-allowlisted marketplaces are blocked at install |
| README plugin counts (`X plugins total`, per-section counts) match `.compiled/marketplace.json` | Doc rot when new skills are added but README isn't bumped |
| Every plugin.json `dependencies[]` entry resolves: bare-string deps refer to a same-marketplace plugin; object-form deps refer to a real plugin in the named marketplace | Same as above |
| `compile.mjs` + `clean.mjs` are byte-identical with the sister catalog | Drift between two compile pipelines wastes engineering time |
| `.gitignore` covers `.compiled/` and root marketplace symlinks | Otherwise generated artifacts leak into commits |

### 3. Plugin-spec compliance

Validate against the official schemas:

- [Claude Code Plugins reference](https://code.claude.com/docs/en/plugins-reference) -- plugin.json schema, folder layout, slug conventions
- [Claude Code Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) -- marketplace.json schema, source types, plugin entry fields
- [Cursor Plugins](https://cursor.com/docs/plugins) -- `.cursor-plugin/` mirror manifest, skills/rules layout

**Plugin-manifest rules (`.claude-plugin/plugin.json`):**

| Rule | Source |
| --- | --- |
| `name` is the only required field; kebab-case, no spaces | plugins-reference §"Required fields" |
| `version` is optional; if set, plugin is pinned to that string until you bump it; if omitted, Claude Code uses the git commit SHA | plugins-reference §"Metadata fields" |
| `author` documented fields: `name` (required), `email` (optional). `url` is **not** in the schema | plugins-reference §"Metadata fields" |
| Other optional fields: `$schema`, `description`, `homepage`, `repository`, `license`, `keywords`, `dependencies` | plugins-reference §"Metadata fields" |
| `.claude-plugin/` contains only `plugin.json`. Skills, agents, commands, hooks, mcp, lsp folders MUST be at plugin root, not inside `.claude-plugin/` | plugins-reference §"Standard plugin layout" warning |
| Skills location: `skills/<name>/SKILL.md` at plugin root (or custom paths via `skills` field) | plugins-reference §"Skills" |

**Marketplace-manifest rules (`.claude-plugin/marketplace.json`):**

| Rule | Source |
| --- | --- |
| Required: `name` (kebab-case), `owner` (with `name`), `plugins` array | plugin-marketplaces §"Required fields" |
| `owner` documented fields: `name` (required), `email` (optional). `url` is **not** in the schema | plugin-marketplaces §"Owner fields" |
| Per-plugin entry required: `name`, `source` | plugin-marketplaces §"Required fields" |
| Relative path sources must start with `./`, never use `..` | plugin-marketplaces §"Relative paths" |
| `allowCrossMarketplaceDependenciesOn` lists every other marketplace that this catalog's plugins depend on; missing entries block install | plugin-marketplaces §"Optional fields" |
| Reserved marketplace names: `claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `knowledge-work-plugins`, `life-sciences` | plugin-marketplaces §"Reserved names" |

**Cursor parity:**

| Rule | Source |
| --- | --- |
| Cursor mirror manifest at `.cursor-plugin/plugin.json` (per-plugin) and `.cursor-plugin/marketplace.json` (catalog) | cursor.com/docs/plugins |
| Skills, rules, MCP servers in same default locations as Claude Code (`skills/`, `rules/`, `mcp.json`) | cursor.com/docs/plugins |

## Where to look

Public-facing surfaces in this repo:

| Surface | Path glob | Why it's user-facing |
| --- | --- | --- |
| Skill frontmatter | `skills/**/SKILL.md` (top YAML block, esp. `description`) | Read by the model; surfaced in plugin listings |
| Skill body | `skills/**/SKILL.md` | Loaded into the agent's context every time the skill fires |
| Skill manifests | `skills/**/.plugin.json` | Symlinked into the marketplace; description is shown in `/plugin install` |
| Bundle manifests | `plugins/*/plugin.json` (canonical) | Authoritative; `.claude-plugin/` and `.cursor-plugin/` symlink to it |
| Marketplace header | `marketplace.json` | Top-level catalog metadata |
| Compiled marketplace | `.compiled/marketplace.json` | Generated; should match sources |
| Skill READMEs | `plugins/*/README.md`, `skills/**/README.md` | Often included verbatim in plugin install pages |
| Skill references | `skills/**/references/*.md` | Loaded on-demand by skills; same exposure as body |
| Catalog docs | `README.md`, `CONTRIBUTING.md`, `AGENTS.md`, `NOTICE` | Public install + contributor guide |

## Procedure

1. **Run axis 1** (leak scan) -- inline command below or `references/leak-patterns.md` regex set.
2. **Run axis 2** (consistency scan) -- inline checks below.
3. **Run axis 3** (spec compliance) -- where possible, run the official validator (`claude plugin validate .` from inside any `<plugin-folder>` or marketplace root) and supplement with the inline checks below.
4. **Classify each hit** as one of:
   - `LEAK` -- clear personal/internal info, must be removed before publishing
   - `JARGON` -- internal-sounding phrasing that should be rewritten in user-facing language
   - `INCONSISTENCY` -- structural drift (renames, dep targets, doc counts)
   - `SPEC` -- violates the Claude Code or Cursor plugin spec
   - `OK` -- false positive
5. **Report** the triage table to the user, grouped by file. Quote the offending line. Suggest a replacement when obvious. Do NOT auto-fix.
6. **For each non-OK finding**, ask the user whether to apply the suggested fix (one-by-one) or batch.
7. **Re-run** the relevant axis after fixes to confirm zero blocking findings remain.

## Inline scan commands

### Axis 1: Leak scan

```bash
# from repo root. Use find+xargs (recursive, glob-safe) and `grep -e` so
# patterns starting with `-` aren't parsed as options.
PATTERNS='\b\w*-internal\b|/Users/[a-z]+/|/home/[a-z]+/|\bkcma-d8\b|\bnas1\b|\b192\.168\.|\b10\.0\.|\.local\b|\.lan\b|\btemp-home\b|promoted from .*-internal|vendored from temp-home|formerly\b|previously lived|migrated from|\(renamed:|TODO\([^)]+\)|\bFIXME\b|\bXXX:|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}'

find skills plugins marketplace.json README.md AGENTS.md CONTRIBUTING.md NOTICE -type f \
  \( -name '*.md' -o -name '*.json' -o -name 'NOTICE' -o -name 'LICENSE' \) \
  -not -path '*/.compiled/*' \
  -not -path '*/node_modules/*' \
  -not -path '*/.agents/*' \
  -not -path '*/.ytstack/*' \
  2>/dev/null \
  | xargs grep -nE -e "$PATTERNS" 2>/dev/null
```

Excluded: `.compiled/` (generated), `.agents/` (this skill's own pattern docs), `.ytstack/` (project memory is allowed to keep history records per the "no migration framing in user-facing files" rule).

### Axis 2: Consistency checks

```bash
# from repo root.

# 2a. Marketplace name must match every install command
MP_NAME=$(node -e "console.log(JSON.parse(require('fs').readFileSync('marketplace.json','utf8')).name)")
echo "Marketplace name: $MP_NAME"
echo "Install commands referencing other names:"
grep -rn '/plugin install [^@]*@' README.md AGENTS.md CONTRIBUTING.md plugins/*/README.md 2>/dev/null \
  | grep -v "@$MP_NAME"

# 2b. Bundle folder name vs plugin.json name
echo "Folder/name mismatches:"
for f in plugins/*/plugin.json; do
  n=$(node -e "console.log(JSON.parse(require('fs').readFileSync('$f','utf8')).name)" 2>/dev/null)
  fold=$(basename $(dirname $f))
  [ "$n" != "$fold" ] && echo "  $fold -> $n"
done

# 2c. Cross-marketplace deps that point to non-existent plugins
# (requires sister marketplace .compiled/marketplace.json to compare against;
#  inline this check with the actual sister-repo path you cross-depend on)

# 2d. README plugin count vs compiled count
COMPILED=$(node -e "console.log(JSON.parse(require('fs').readFileSync('.compiled/marketplace.json','utf8')).plugins.length)")
README_CLAIM=$(grep -oE '[0-9]+ plugins total' README.md | head -1)
echo "Compiled count: $COMPILED   README claim: $README_CLAIM"

# 2e. compile.mjs / clean.mjs / .gitignore parity with sister catalog
# Adapt SISTER_PATH to your sister repo
SISTER_PATH=../yesterday-skills   # or ../skills, depending which side you are
diff -q compile.mjs $SISTER_PATH/compile.mjs
diff -q clean.mjs $SISTER_PATH/clean.mjs
diff -q .gitignore $SISTER_PATH/.gitignore

# 2f. .compiled/ / root marketplace symlinks gitignored
grep -E '^\.compiled/?$|^\.claude-plugin/marketplace\.json|^\.cursor-plugin/marketplace\.json' .gitignore
```

### Axis 3: Spec compliance

```bash
# 3a. Run the official validator on the marketplace + every bundle
claude plugin validate .                          # marketplace check
for d in plugins/*/; do claude plugin validate "$d"; done

# 3b. plugin.json: required field present
for f in plugins/*/plugin.json skills/**/.plugin.json; do
  node -e "
    const d=JSON.parse(require('fs').readFileSync('$f','utf8'));
    if (!d.name) console.log('MISSING name:', '$f');
  "
done

# 3c. plugin.json: undocumented author fields
for f in plugins/*/plugin.json skills/**/.plugin.json; do
  node -e "
    const d=JSON.parse(require('fs').readFileSync('$f','utf8'));
    const ok=new Set(['name','email']);
    if (d.author) Object.keys(d.author).filter(k=>!ok.has(k)).forEach(k=>console.log('AUTHOR.$f has undocumented .'+k));
  "
done

# 3d. plugin.json: forbidden version pin (project policy: omit version, use git SHA)
for f in plugins/*/plugin.json skills/**/.plugin.json; do
  grep -l '"version"' "$f" 2>/dev/null | xargs -I{} echo "VERSION pin in {}"
done

# 3e. marketplace.json: required fields + undocumented owner fields
node -e "
  const m=JSON.parse(require('fs').readFileSync('marketplace.json','utf8'));
  for (const k of ['name','owner','plugins']) if (!m[k]) console.log('MARKETPLACE missing:', k);
  if (m.owner) Object.keys(m.owner).filter(k=>!['name','email'].includes(k)).forEach(k=>console.log('OWNER undocumented field: .'+k));
"

# 3f. relative source paths must start with ./, no ..
node -e "
  const m=JSON.parse(require('fs').readFileSync('.compiled/marketplace.json','utf8'));
  m.plugins.filter(p=>typeof p.source==='string').forEach(p=>{
    if (!p.source.startsWith('./')) console.log('SOURCE not ./-relative:', p.name, p.source);
    if (p.source.includes('..')) console.log('SOURCE contains ..:', p.name, p.source);
  });
"
```

## Output format

Report a table per file. Example:

```
plugins/office/plugin.json
  L3: JARGON  "...live in ydstack-extras"
       -> office-extras (renamed plugin)

README.md
  L60: INCONSISTENCY  "13 plugins total: ... 8 standalone"
       -> compiled count is 14 / 9; bump and add new standalone to category section

plugins/<name>/plugin.json
  -:  SPEC     author has undocumented `url` field
       -> remove or replace with email (spec only documents name + email)
```

End the report with a one-line summary: `<L> LEAK, <J> JARGON, <I> INCONSISTENCY, <S> SPEC across <F> files. Suggest fixes? (y / per-file / skip)`.

## What NOT to flag

- Public Yesterday brand mentions (`Yesterday`, `Yesterday-AI`, `yester.cloud`) -- intentionally public.
- Plugin descriptions that mention other PUBLIC plugins by name (e.g. `office-extras` referencing `office`) -- catalog cross-refs.
- README install commands that reference org names.
- Keyword arrays containing `yesterday`.
- Internal references in PRIVATE catalogs (sister `yesterday-skills`) -- flag for awareness, but they are intentional content there.
- Migration history living in `.ytstack/DECISIONS.md` -- intentional history record (project memory is allowed to keep what user-facing files cannot).

## False-positive examples

- `kcma-d8` inside a `local-llm` skill that legitimately documents that the home-network GPU server is reachable at that hostname for users who set up the same topology -- if the doc explains the assumption, classify as JARGON not LEAK.
- `/Users/alex/` inside a code block that demonstrates path-handling -- annotate or replace with `/Users/<you>/`.
- The word "internal" in a sentence like "internal state of the function" -- pure English usage; the regex `\b\w*-internal\b` requires a hyphen prefix, so this should not match. If it does, tighten the regex.
- `promoted from corrections` in self-improvement docs -- pattern `promoted from .*-internal` was tightened to avoid this; flag any regression to `promoted from` bare.

## Limits of this skill

- Heuristic. Will miss findings that don't match patterns and over-flag legitimate uses. The human verdict is the source of truth.
- Does not parse YAML / JSON semantically for axis 1 -- regex on raw bytes. A leak that spans multiple lines after a key may be partially shown.
- Axis 3 (`claude plugin validate`) is the closest thing to a definitive spec check; the inline JSON checks are supplemental.
- Does not check git history. A clean current tree may still have leaks in earlier commits; rewriting history is out of scope.
- Does not verify whether a `homepage` or `repository` URL actually points to a public repo. Use `gh repo view <owner/repo>` separately.

## See also

- `references/leak-patterns.md` -- canonical regex list for axis 1, easier to extend than editing the skill body
- `~/.claude/CLAUDE.md` user rules section "PUBLIC: As skills are public, skills NEED to: be depersonalized..."
- `.ytstack/DECISIONS.md` "Migration history lives only in .ytstack/ docs" -- the rule that drives axis 1's migration-framing patterns
- `.ytstack/DECISIONS.md` "Acceptance criterion -- public-installability" -- internal-perspective framing rule
