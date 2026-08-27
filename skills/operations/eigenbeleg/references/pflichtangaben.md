# Eigenbeleg — Pflichtangaben, Steuerbehandlung, Buchhaltungs-Upload

Reference for German substitute receipts (Eigenbelege/Ersatzbelege). Sources checked 2026-08; re-verify before relying on thresholds.

## Pflichtangaben (required fields on page 1)

For acceptance by the Finanzamt an Eigenbeleg needs
(sources: [lexware.de Unternehmerlexikon "Eigenbeleg"](https://www.lexware.de/wissen/unternehmerlexikon/eigenbeleg/), [fuer-gruender.de](https://www.fuer-gruender.de/wissen/unternehmen-fuehren/buchhaltung/eigenbeleg/), [buchhaltungsbutler.de](https://www.buchhaltungsbutler.de/wiki/eigenbeleg-vorlage/)):

| Field | Notes |
|---|---|
| Label "Eigenbeleg" | plus a subtitle like "(Ersatzbeleg für fehlende Rechnung/Quittung)" |
| Unique, sequential receipt number | derive from prefix + date + time so two same-day payments cannot collide |
| Zahlungsempfänger with **full address** | the operating company, not the brand on the card statement — verify via Impressum |
| Art der Aufwendung | what was bought/paid, with location |
| Datum der Zahlung | payment date (+ time when known); mail `Date:` headers are UTC → convert to Europe/Berlin, label MESZ/MEZ by season |
| Bruttobetrag | gross amount |
| Grund für den Eigenbeleg | truthful: why no original document exists ("no receipt received, no invoice available"), plus the evidence reference |
| Betriebliche Veranlassung | the business purpose |
| Ausstellungsdatum + Ort | creation date — **never backdate** |
| Unterschrift | handwritten signature of the issuer (name + role printed) |

Attach the payment proof (page 2): source headers (From/To/Date/Subject/Message-ID for a mail), the body text verbatim (mark removed layout duplicates), and where the original is kept. The bank statement remains the primary payment proof; retention period for Belege is 10 years (§ 147 AO).

## Tax rules

- **No input-VAT deduction.** An Eigenbeleg is not an invoice within §§ 14, 14a UStG; § 15 Abs. 1 S. 1 Nr. 1 S. 2 UStG requires possession of a proper invoice for the Vorsteuerabzug. A Kleinbetragsrechnung (§ 33 UStDV, ≤ 250 EUR) must also be issued by the supplier — an Eigenbeleg never qualifies. The gross amount is still fully deductible as a Betriebsausgabe. (Sources: [gesetze-im-internet.de §15 UStG](https://www.gesetze-im-internet.de/ustg_1980/__15.html), [§33 UStDV](https://www.gesetze-im-internet.de/ustdv_1980/__33.html), [Haufe "Kein Vorsteuerabzug bei Not- bzw. Ersatzbeleg"](https://www.haufe.de/id/beitrag/eigenbelege-der-richtige-umgang-mit-eigenbelegen-und-er-6-kein-vorsteuerabzug-bei-not-bzw-ersatzbeleg-HI2197985.html))
- Print this on the receipt, e.g.: *"Bruttobetrag; enthaltene USt ist mangels Rechnung i. S. d. §§ 14, 15 UStG nicht als Vorsteuer abziehbar – Verbuchung als Betriebsausgabe mit Steuersatz „Keine"."*
- **Zeitnah erstellen** (GoBD timely recording — unbare Vorgänge within ~10 days). Later creation is legal but weakens credibility; never backdate, set the *booking* date to the payment date instead.
- Eigenbelege should be the exception; amounts ≥ 150–250 EUR and frequent use invite scrutiny.

## Bookkeeping-upload notes (Lexware & co.)

- Document/booking date = **payment date**, not the Eigenbeleg creation date; assign the receipt to the matching bank transaction.
- Tax rate = **"Keine"** — OCR often prefills 19 % from "USt" strings; correct it.
- OCR contact detection often picks the issuer block (top-left company) as the vendor — set the contact to the payee.
- If the merchant offers account/plate registration with monthly invoicing (common for parking operators), recommend switching: a real invoice restores the Vorsteuerabzug and removes the recurring Eigenbeleg work.
