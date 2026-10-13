# Protokoll erstellen

Arbeite aus dem vollständigen Transkript. Erhalte die Rohdatei unverändert und schreibe eine getrennte bereinigte Fassung.

## Ablauf

1. Datum, Thema und bestätigte Teilnehmende aus der Quelle erfassen. Nur ausdrücklich bereitgestellte oder für dieses Meeting freigegebene Projektunterlagen zur Begriffsklärung hinzunehmen. Keine anderen Kundenordner oder persönlichen Wikis durchsuchen.
2. Ein Vokabelregister aus belegten Begriffen bilden. Eindeutige Transkriptionsfehler korrigieren; bei Unsicherheit `[?Originalwort]` erhalten. Sprecher nicht aus Plausibilität erfinden: `Unbekannte sprechende Person` bleibt stehen, bis die Identität belegt ist.
3. Summary, Entscheidungen samt Begründung, Zusagen, Action Items mit belegtem Owner/Termin und offene Fragen schreiben. Interpretationen als Analyse kennzeichnen und mit konkreten Passagen begründen. Keine Absicht oder Zusage aus einer bloßen Tendenz ableiten.
4. Füllwörter und bedeutungslose Doppelungen entfernen, Wortwahl, Aussagen und Chronologie erhalten. Bestätigungen behalten, wenn sie eine Zusage oder Entscheidung tragen. Zusammenhängende Beiträge derselben Person bündeln. Das Ergebnis als bereinigtes Transkript kennzeichnen, nicht als wortgetreues Zitat.
5. Nur bei belastbaren Zeitmarken Redezeitanteile berechnen; Wortanteile separat ausweisen. Fehlende oder überlappende Zeitmarken als Einschränkung nennen. Keine Prozentwerte schätzen.
6. Im vereinbarten Zielordner `YYYY-MM-DD_meeting_thema.md` speichern. Vor externer Weitergabe Zielgruppe prüfen, unnötige personenbezogene Angaben und fremde Projektkontexte entfernen. Speichern ist keine Sendeerlaubnis.

## Vorlage (Platzhalter, keine realen Personen)

```yaml
---
type: meeting-record
date: YYYY-MM-DD
title: "[Thema]"
participants: ["[Bestätigte Person oder Rollenbezeichnung]"]
source: "[Quellreferenz]"
---
```

```markdown
# [Thema]

## Zusammenfassung
[Ergebnis und Bedeutung]

## Entscheidungen
[Was, warum, verantwortliche Rolle, Quellstelle]

## Zusagen und nächste Schritte
- [ ] [Belegter Auftrag] — [Rolle] — [belegter Termin oder offen]

## Offene Fragen
[Ungeklärt bleibt ungeklärt]

## Analyse
[Interpretation mit Beleg; weglassen, wenn nicht erforderlich]

## Bereinigtes Transkript
**[00:04] [Bestätigte Person oder unbekannt]:**
[Aussage aus der Quelle]
```

Abschnitte ohne Substanz weglassen. Abschluss: Dateipfade, Quellenumfang, verbleibende Sprecher-/Datenlücken. Zurück zu [SKILL.md](SKILL.md).
