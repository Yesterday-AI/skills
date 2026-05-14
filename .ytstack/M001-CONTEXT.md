---
milestone: M001
project: skills
created: 2026-05-14T12:10:58Z
size: M
---

# M001 -- Context

## Goal

Ein `create-shareable-skill` Metaskill, der Agent/User durch das Shareable-Machen eines
bestehenden oder das Neuerstellen eines Skills führt: Routing ins richtige Repo
(public `skills` vs. privates `yesterday-skills`) und Placement (standalone + Kategorie
vs. Bundle-Erweiterung mit Confirmation), Qualitäts-Gate, Doku-Updates, PR auf main --
abgeglichen mit der company-orga AI-Skills-Strategie.

## Exit criteria

- `create-shareable-skill` SKILL.md liegt in der richtigen Kategorie, `node compile.mjs`
  läuft sauber durch, der Skill erscheint im Marketplace-Output.
- Skill kodiert die Repo-Policies: public-installability, no-internal-perspective,
  folder/name-Parität, standalone-vs-bundle Entscheidungsbaum, public-vs-private
  Repo-Routing -- abgeglichen mit dem company-orga Strategie-Doc.
- Skill treibt den vollständigen Ablauf: Intake → Quality-Gate → Placement-Entscheidung
  → Doku-Update → PR auf main.
- README / CONTRIBUTING / AGENTS.md verweisen auf den Metaskill; Sister-Repo-Parität
  (`yesterday-skills`) ist berücksichtigt.

## Size

M -- see `M001-ROADMAP.md` for slice breakdown.

## Decisions locked in discuss phase

- 2026-05-14 (REVIDIERT, siehe nächster Punkt): zunächst entschieden, `create-shareable-skill` in
  `.agents/skills/` zu legen statt im Marketplace-`skills/`-Baum -- wegen des Leak-Risikos beim
  Benennen des privaten `yesterday-skills`-Repos. Per PR #1 so umgesetzt.
- 2026-05-14: Auf User-Review revidiert -- `create-shareable-skill` ist ein **standalone Catalog-Skill**
  unter `skills/operations/create-shareable-skill/`, kompiliert + im Marketplace gelistet (Count 14→15).
  Authoring ist selbst eine user-facing Capability. Nur `audit-skills` bleibt in `.agents/`
  (reine Verifikations-Maschinerie). User-Anweisung schlägt Agent-Architektur-Urteil. Voller
  Eintrag + Supersede in `DECISIONS.md`.
- 2026-05-14: Kein Mirror im privaten `yesterday-skills`. Der Skill *kennt* beide Kataloge und
  routet zwischen ihnen; er muss nicht doppelt existieren. Ein Repo, ein Skill.
- 2026-05-14: Policies werden NICHT dupliziert -- der Skill verweist auf die Single Source of
  Truth (`.ytstack/DECISIONS.md` für die Acceptance-Kriterien, `CONTRIBUTING.md` für Commit-/
  Versioning-Format, company-orga `04_ai-skills-und-plugins.md` für den Qualitätsanspruch) und
  fasst nur das Nötige operativ zusammen.
- 2026-05-14: Milestone direkt umgesetzt ohne formalen slice/task/TDD-Pass -- auf explizite
  User-Anweisung. `using-ytstack` Instruction-Priority 1 (User-Anweisung schlägt ytstack-Flow).

## Open questions

(Alle vor Umsetzung geklärt -- siehe "Decisions locked".)

### Surfaced, nicht Teil von M001 (für reassess-roadmap / separaten Task)

- README "What's in the catalog" gruppiert Skills unter `concepts` / `development-operations`,
  aber die echten On-Disk-Ordner sind `capabilities` / `operations` / `productivity` / `travel`.
  Die README-Links zeigen ins Leere. Pre-existing Drift, in `placement.md` als
  `audit-skills`-INCONSISTENCY-Finding vermerkt -- sollte separat bereinigt werden.
