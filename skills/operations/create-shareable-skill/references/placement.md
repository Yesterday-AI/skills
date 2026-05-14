# Placement -- where a shareable skill goes

Three decisions, in order: **which catalog**, **standalone or bundle**, **which category**. Each one narrows the path the skill lands at.

## Decision 1 -- which catalog

| | Public `Yesterday-AI/skills` | Private `Yesterday-AI/yesterday-skills` |
| --- | --- | --- |
| Marketplace name | `yesterday-public-plugins` | `yesterday-private-plugins` |
| Audience | anyone with Claude Code / Cursor | Yesterday team |
| May depend on private infra | no | yes |
| Cross-marketplace deps | avoid (see below) | allowed -- depends on `yesterday-public-plugins` |

A skill goes **public** only if BOTH hold:

1. Installable and -- for the no-key paths -- usable by anyone with a stock public Claude Code / Cursor install. SaaS-key-gated skills are fine when the SaaS is publicly available (Figma, Mistral, ...).
2. No dependency on private hostnames, private package registries, internal-only auth providers, or services that are not publicly reachable.

Fail either test -> the skill goes **private**. Examples that force private placement: a skill that talks to an internal LLM gateway hostname, one that needs an internal-only auth provider, one whose `references/` carry internal service topology.

Borderline calls:

- **Documents a Yesterday-built but publicly reachable API** (e.g. a hosted product API anyone can sign up for) -> public is fine; treat the API like any third-party SaaS and document the key requirement from the user's perspective.
- **Generic workflow, no infra at all** (a methodology, a code pattern) -> public.
- **Needs an internal package registry or a repo ending in `-internal`** -> private, no exceptions.

Cross-marketplace dependency rule: `allowCrossMarketplaceDependenciesOn` is a *permission whitelist, not an installer*. A public-catalog bundle that declares a cross-marketplace dep errors in `/doctor` on a clean install because the user never added the other marketplace. So **public bundles must be installable + `/doctor`-clean with a single `/plugin install`** -- avoid cross-marketplace deps entirely. The private catalog intentionally cross-depends on the public one; that is expected there.

## Decision 2 -- standalone or bundle

### Standalone skill

Lives at `skills/<category>/<slug>/SKILL.md` (+ optional `.plugin.json`). `compile.mjs` discovers it, scaffolds a per-skill plugin under `.compiled/skill-plugins/<slug>/`, and lists it in the marketplace as its own installable plugin. This is the default for a single, self-contained capability.

### Bundle member

A bundle (`plugins/<bundle>/plugin.json`) composes several skills. A skill becomes part of a bundle one of two ways:

- it is dropped into `plugins/<bundle>/skills/<slug>/SKILL.md`, or
- it is a standalone skill and the bundle lists it in `dependencies[]`.

Either way, **extending a bundle changes the payload that every existing installer of that bundle already receives.** That is a user-visible change to a shipped product surface.

> **Bundle extension requires explicit user confirmation.** Never add a skill to a bundle's `skills/` folder or `dependencies[]` silently. Ask: "this will add `<slug>` to everyone who has `<bundle>` installed -- confirm?" Only proceed on an explicit yes.

Prefer standalone unless the skill is genuinely part of a coherent set the bundle already represents. When unsure, ship standalone first; it can be added to a bundle later (with confirmation).

## Decision 3 -- which category (standalone only)

Slug = parent folder name = `.plugin.json` `name` field. Pick a category folder under `skills/`.

**Use a category that already exists in the target repo.** Check the live tree before deciding:

```bash
find skills -maxdepth 2 -type d | sort
```

In this repo the category folders that currently exist are `capabilities`, `operations`, `productivity`, and `travel` (nested grouping under a category is allowed -- e.g. `skills/capabilities/memory/<slug>/`). The README's "What's in the catalog" section groups some skills under headings that do not match the on-disk folder (`concepts`, `development-operations`) -- that is pre-existing README drift, not a set of real folders. **Route by the actual on-disk folders, and flag the README/folder mismatch as an `audit-skills` INCONSISTENCY finding rather than perpetuating it.**

Propose a **new category** only when no existing one is a reasonable fit, and confirm it with the user before creating the folder. A new category is a deliberate taxonomy decision -- record it in `.ytstack/DECISIONS.md`.

Naming rules for the slug (also enforced by `audit-skills`):

- Names the concrete capability, not the tool or domain in general: `github-worktrees`, not `github`; `web-design`, not `wd`; `paperclip-api`, not `pc`.
- Self-explanatory in a `/skills` list with no conversation context.
- kebab-case, no spaces, collision-free across all of `skills/**` (a collision makes `compile.mjs` skip one skill with a warning).

## Resulting paths

| Decision | Path |
| --- | --- |
| Public standalone | `skills/<category>/<slug>/SKILL.md` (+ `.plugin.json`) in `Yesterday-AI/skills` |
| Public bundle member (folder) | `plugins/<bundle>/skills/<slug>/SKILL.md` in `Yesterday-AI/skills` -- **confirm first** |
| Public bundle member (dependency) | standalone path above + `<slug>` added to `plugins/<bundle>/plugin.json` `dependencies[]` -- **confirm first** |
| Private standalone | `skills/<category>/<slug>/SKILL.md` in `Yesterday-AI/yesterday-skills` |
| Private bundle member | `plugins/<bundle>/...` in `Yesterday-AI/yesterday-skills` -- **confirm first** |
| Repo-local tooling (pure verification / build machinery) | `.agents/skills/<slug>/SKILL.md` -- not compiled, not published |

The last row is where `audit-skills` lives -- it is pure verification machinery, not a user-facing capability, so it stays repo-local. `create-shareable-skill` itself ships in the catalog as a standalone skill (`skills/operations/create-shareable-skill/`): authoring a shareable skill *is* a user-facing capability.
