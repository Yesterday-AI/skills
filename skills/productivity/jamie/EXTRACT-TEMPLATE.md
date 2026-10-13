# Jamie Extract — Dateiformat

## Frontmatter

```yaml
---
type: extraction
date: YYYY-MM-DD
title: "[Titel des Themas — nicht des Meetings]"
source_meeting:
  title: "[Jamie-Titel]"
  date: YYYY-MM-DD
  participants: ["[Name 1]", "[Name 2]"]
  duration: "NN min"
  meeting_id: "[jamie meeting id]"
audience: internal | external-shareable
shared_with: ["[Name/Firma, falls extern]"]
project: "[Projekt/Repo-Kontext]"
tags: [extraction, ...]
---
```

`title` ist das **Thema**, nicht "Meeting mit X am Y" — die Datei ist kein Protokoll, sie
beschreibt einen Zustand. Das Meeting steht nur noch als `source_meeting` in den Metadaten.

## Body

```markdown
# [Thema] — Stand nach dem Gespräch vom DD.MM.YYYY

## Kontext
[Ausgangslage: was davor war, was das Gespräch ausgelöst hat, welche Beobachtungen/Daten zugrunde
liegen. Als Fakten, nicht als Nacherzählung des Gesprächs.]

## Entscheidungen
[Pro Entscheidung: **Was**, **Warum**, **wer trägt sie**. Als Tabelle bei vielen kurzen
Entscheidungen, als Fließtext mit Zwischenüberschriften bei wenigen komplexen.]

## Spezifikation
[Das Zielbild, geordnet nach Baustein/Komponente/Feature — nicht nach Gesprächsverlauf. So konkret,
dass jemand ohne Meeting-Teilnahme danach bauen/entscheiden kann. Bei Produkt-/UX-Themen meist der
größte Abschnitt — gerne mit Unterüberschriften je Komponente.]

## Offene Fragen / bewusst nicht entschieden
[Explizit als offen kennzeichnen. Tendenz nennen, wenn erkennbar, aber nicht als Entscheidung
verkaufen. Das ist der Abschnitt, der verhindert, dass jemand falsche Sicherheit annimmt.]

## Begriffe & Konzepte
[Nur wenn neue/umdefinierte Begriffe gefallen sind. Kurz erklären — sonst weglassen.]

## Rollen & Ownership
[Wer macht/verantwortet was. Nur Fakten, keine Beziehungs- oder Motivationsanalyse.]

## Nächste Schritte
- [ ] [Was] — [Wer] — [Bis wann]
```

Abschnitte ohne Substanz komplett weglassen (nicht mit "keine besonderen Punkte" auffüllen).
Reihenfolge ist der Standardfall — bei sehr technischen Themen kann „Spezifikation" vor
„Entscheidungen" sinnvoller sein, wenn die Spezifikation selbst die Entscheidung ist.
