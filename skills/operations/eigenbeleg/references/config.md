# Config schema for `scripts/eigenbeleg.py`

```bash
uv run --with reportlab python scripts/eigenbeleg.py config.json out/ [--only-month YYYY-MM]
```

One JSON file drives a whole batch (one PDF per transaction). All strings are rendered as-is — write them in the bookkeeping language (German).

```jsonc
{
  "file_slug": "Parkhaus-XY",               // filename part: Eigenbeleg_<slug>_<date>_<amount>EUR.pdf
  "nr_prefix": "EB-P1",                     // receipt no.: <prefix>-<YYYY-MM-DD>-<HHMM>
  "issuer": {
    "lines": [                              // issuer block, first line bold
      "Beispiel GmbH",
      "Musterstraße 1",
      "44787 Bochum",
      "USt-IdNr. DE000000000 · HRB 00000 (AG Bochum)"
    ],
    "city": "Bochum",                       // for the "Ort, Datum" signature line
    "signer": "Vorname Nachname, Geschäftsführer"
  },
  "payee": {
    "lines": [                              // Zahlungsempfänger block — verified via Impressum!
      "Betreiber GmbH",
      "(Betreiber Parkhaus XY)",
      "Straße 10",
      "44787 Bochum",
      "USt-IdNr. DE000000000 · HRB 0000 (AG Bochum)"
    ]
  },
  "expense_type": ["Parkgebühr (Pkw)", "Parkhaus XY, Bochum-Innenstadt"],
  "payment_method": "Firmenkarte XY (Mastercard Debit, •••• 0000), Karteninhaber Vorname Nachname",
  "purpose": "Geschäftliche Fahrt zum Firmensitz …",   // betriebliche Veranlassung
  "reason": "Bezahlung am Kassenautomaten … Es wurde kein Beleg erhalten, eine Rechnung des Betreibers liegt nicht vor. Zahlungsnachweis: Benachrichtigung „{subject}“ (Anlage).",
  "vat_note": null,                         // optional override of the default no-input-VAT note
  "evidence_title": "Anlage: Zahlungsnachweis (E-Mail-Benachrichtigung)",   // default for page 2
  "evidence_note": "Textextrakt der HTML-Mail in Originalreihenfolge (Layout-Wiederholungen entfernt, Wortlaut unverändert; fett = Transaktionsdaten). Das Original liegt im Mail-Postfach.",
  "transactions": [
    {
      "datetime": "2026-06-09T21:59:06+02:00",   // ISO-8601 WITH offset (payment time, local)
      "amount": "14,40",                          // German decimal notation, gross EUR
      "subject": "Sie haben eine Zahlung durchgeführt",   // substituted into {subject} in reason/proof
      "proof_lines": [                            // page-1 "Nachweis" field (evidence reference)
        "Qonto-E-Mail vom 09.06.2026 21:59 Uhr, Betreff „{subject}“",
        "Message-ID <...> (siehe Anlage, Seite 2)"
      ],
      "evidence_headers": [                       // page-2 header block (omit → single-page PDF)
        ["Von:", "\"Qonto.com\" <support@qonto.com>"],
        ["An:", "billing@example.com"],
        ["Datum:", "Tue, 09 Jun 2026 19:59:06 +0000 (UTC)"],
        ["Betreff:", "Sie haben eine Zahlung durchgeführt"],
        ["Message-ID:", "<...>"],
        ["Quelle:", "Mail-Postfach billing@example.com, Ordner „Rechnungen“ (unverändert)"]
      ],
      "evidence_lines": ["…verbatim text lines of the proof…"],
      "evidence_bold": ["14,40 EUR", "Parkhaus XY"]        // lines to render bold on page 2
    }
  ]
}
```

Notes:

- `{subject}` in `reason` and `proof_lines` is replaced per transaction — notification templates change over time, so extract the subject from each source message instead of assuming one wording.
- Receipt numbers and filenames are asserted unique (time suffix handles two payments per day).
- The script prints a manifest (`manifest.json` in the out dir) with number, file, date, time, amount per receipt plus the total — use it for the verification pass.
- Page 2 renders `evidence_headers`/`evidence_lines` verbatim — put converted local times (e.g. "… (= 09.06.2026 21:59 Uhr MESZ)") directly into those strings; label MESZ vs MEZ by season.
- Transactions without `evidence_headers`/`evidence_lines` produce a single-page PDF.
