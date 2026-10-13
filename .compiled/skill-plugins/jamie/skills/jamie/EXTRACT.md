
# Extraktion erstellen

Nimmt ein Meeting (Transkript, roh oder bereinigt) und schreibt heraus, was für die Zukunft zählt:
Kontext, Entscheidungen, was geklärt ist, was offen ist, die daraus folgende Spezifikation. Keine
Nacherzählung, kein Ablauf, kein Hin-und-Her. Wer das liest — Mensch oder Agent — soll wissen,
**was zu tun ist**, nicht, was gesagt wurde.


## Ablauf

### Schritt 1: Input + Zielgruppe klären

- **Input:** Datei benannt? → nutzen. Sonst prüfen, ob im Zielordner schon ein frisch gefetchtes
  `raw_*.md` oder eine `*_meeting_*.md` liegt. Sonst das passende Meeting nach [SKILL.md, Phase 1](SKILL.md#phase-1--meeting-holen)
  holen: klare Treffer direkt verwenden, bei Unsicherheit bis zu drei Kandidaten inhaltlich prüfen
  und nur bei verbleibender Mehrdeutigkeit nachfragen.
- **Zielgruppe** (steuert Schritt 4): Bleibt das Dokument intern (Team + eigene Agenten), oder geht
  es auch an eine externe Person/Firma bzw. deren Agenten? Falls nicht erkennbar → kurz fragen.
  Diese Antwort entscheidet, ob strategische/interne Passagen rausgefiltert werden.

### Schritt 2: Kontext + Vokabel-Register

Wie in CLEANUP.md: Nur bereitgestellte oder ausdrücklich freigegebene Projektunterlagen lesen, Eigennamen/Fachbegriffe/Personen auflösen, bekannte
Fehltranskriptionen still korrigieren (Register nicht mit ausgeben, im Zweifel `[?Original]` statt
falsch zu korrigieren). Zusätzlich hier klären: **wer ist wer** — Rolle, Firma, Verhältnis zum Nutzer.
Das entscheidet in Schritt 3+4, wie eine Aussage einzuordnen ist und ob sie exportierbar ist.

### Schritt 3: Extrahieren, nicht zusammenfassen

Aus dem **gesamten Transkript** arbeiten, nicht nur der Jamie-Summary — die glättet exakt die
Details weg, um die es hier geht (konkrete Zahlen, das Warum hinter einer Entscheidung, was explizit
offen blieb). Nach **Thema**, nicht nach Zeit, folgende Fragen beantworten:

- **Kontext/Ausgangslage** — was führte zu dem Gespräch? Als Fakt hinschreiben ("X zeigt Y"),
  nicht als Nacherzählung ("es wurde besprochen, dass...").
- **Entscheidungen** — was ist gefallen? Je Entscheidung: die Entscheidung selbst, das **Warum**
  (sonst wird sie später neu aufgerollt), wer sie trägt.
- **Spezifikation** — welches Zielbild folgt daraus, konkret genug, dass jemand, der nicht dabei
  war, es bauen/umsetzen kann? Bei Produkt-/UX-Meetings meist der dickste Abschnitt.
- **Offene Fragen** — was blieb bewusst ungeklärt oder nur angerissen? Nicht schönreden, nicht
  verschweigen. Eine Aussage, die im Gespräch als "ich bin noch am laut Denken" markiert wurde,
  bleibt offen — auch wenn am Ende eine Tendenz erkennbar war.
- **Begriffe & Konzepte** — was wurde neu geprägt oder umdefiniert (Feature-Name, Phasen-Bezeichnung,
  Methodik)? Taucht später ohne Erklärung wieder auf — kurzes Glossar.
- **Rollen & Ownership** — wer macht was, als Fakt (keine Beziehungsanalyse).
- **Nächste Schritte** — mit Frist/Owner, eigener Abschnitt, aber nur einer von vielen.

Exaktes Dateiformat + Frontmatter-Schema: [`EXTRACT-TEMPLATE.md`](EXTRACT-TEMPLATE.md). Abschnitte ohne Substanz
weglassen, nicht auffüllen.

### Schritt 4: Zielgruppen-Filter (nur wenn extern geteilt wird)

Wenn das Dokument auch nach außen geht: einmal komplett durchgehen und rauswerfen, was nicht für
die Zielgruppe bestimmt ist —

- interne Preis-/Margen-/Strategieüberlegungen (z.B. Recurring-Revenue-Kalkül, Kapazitätsfragen zu
  anderen Kunden/Projekten)
- unverblümte interne Einschätzungen zu Personen oder Beziehungen
- alles, was aus einem anderen Projekt/Kontext hereinragt und die Zielgruppe nichts angeht

Was bleibt, muss trotzdem vollständig und konkret genug sein, dass die Zielgruppe direkt loslegen
kann — **filtern heißt nicht verwässern**.

### Schritt 5: Speichern

`YYYY-MM-DD_extract_[thema-kebab-case].md`, im selben Ordner wie das Quell-Meeting (bzw. die
`meetings/`-Zielordner-Logik aus jamie-fetch Schritt 5).

### Schritt 6: Bestätigung

```
✅ Extraktion fertig: meetings/YYYY-MM-DD_extract_beispielthema.md
   Entscheidungen: 6 | Offene Punkte: 3 | Spezifikations-Abschnitte: 5
   Zielgruppe: intern (Team + Agenten) — kein externer Filter nötig
```

---

## Qualitätscheck

- [ ] Kein Satz beginnt mit "Zuerst... dann... danach" (Chronologie-Test)
- [ ] Jede Entscheidung hat ein Warum
- [ ] Offene Punkte sind als offen erkennbar, nicht in Entscheidungen versteckt
- [ ] Ein Fremder (Mensch oder Agent) könnte aus dem Dokument allein loslegen
- [ ] Bei externer Zielgruppe: Filter-Pass durchgeführt und im Abschlussbericht vermerkt

## Anti-Pattern (NIE machen)

- ❌ Zusammenfassung mit "Zuerst wurde X besprochen, dann Y" — das ist jamie-go, nicht das hier
- ❌ Nur eine Action-Item-Liste ohne Kontext/Entscheidungs-Begründung
- ❌ Offene Punkte als erledigt hinschreiben, weil eine Tendenz erkennbar war
- ❌ Bei externer Zielgruppe interne Strategie/Preise ungefiltert durchreichen
