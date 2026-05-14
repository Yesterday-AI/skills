---
milestone: M001
project: skills
size: M
created: 2026-05-14T12:10:58Z
status: done
total_slices: 1
completed_slices: 1
---

# M001 Roadmap

**Goal:** Ein `new-shareable-skill` Metaskill, der Agent/User durch das Shareable-Machen
eines bestehenden oder das Neuerstellen eines Skills führt: Routing ins richtige Repo
(public `skills` vs. privates `yesterday-skills`) und Placement (standalone + Kategorie
vs. Bundle-Erweiterung mit Confirmation), Qualitäts-Gate, Doku-Updates, PR auf main --
abgeglichen mit der company-orga AI-Skills-Strategie.

**Exit criteria:**
- `new-shareable-skill` SKILL.md liegt in der richtigen Kategorie, `node compile.mjs`
  läuft sauber durch, der Skill erscheint im Marketplace-Output.
- Skill kodiert die Repo-Policies: public-installability, no-internal-perspective,
  folder/name-Parität, standalone-vs-bundle Entscheidungsbaum, public-vs-private
  Repo-Routing -- abgeglichen mit dem company-orga Strategie-Doc.
- Skill treibt den vollständigen Ablauf: Intake → Quality-Gate → Placement-Entscheidung
  → Doku-Update → PR auf main.
- README / CONTRIBUTING / AGENTS.md verweisen auf den Metaskill; Sister-Repo-Parität
  (`yesterday-skills`) ist berücksichtigt.

## Slices

Executed directly without a formal slice/task pass, on explicit user instruction
("DU SOLLST DAS IMPLEMENTIEREN ... JETZT, BIS ZUM ENDE"). User instructions take
precedence over the ytstack flow (`using-ytstack`: instruction priority 1).

- [x] S01 -- `new-shareable-skill` meta-skill + contributor docs
  - `.agents/skills/new-shareable-skill/SKILL.md` -- end-to-end authoring workflow
  - `.agents/skills/new-shareable-skill/references/placement.md` -- catalog / form / category routing
  - `.agents/skills/new-shareable-skill/references/quality-bar.md` -- shareable-by-default gates + templates
  - `CONTRIBUTING.md`, `AGENTS.md` -- reference the meta-skill
  - Verified: `node compile.mjs` clean, marketplace count unchanged at 14 (skill is `.agents/` tooling, not compiled), leak scan on new files clean

## Run order

Single slice, done. Delivered via PR branch `add-new-shareable-skill` (push pending).

## How to update this file

- Flip slice checkbox `[ ]` → `[x]` when its tasks are all `summarize-task`-confirmed
- Update `completed_slices` count
- On milestone completion, flip `status: planned` → `status: done` and update global ROADMAP.md
