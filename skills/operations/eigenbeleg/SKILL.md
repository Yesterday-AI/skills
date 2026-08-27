---
name: eigenbeleg
description: Create German Eigenbelege (Ersatzbelege, substitute receipts) as signature-ready two-page PDFs for business expenses where no invoice or receipt exists — parking ticket machines, vending machines, tips, coat checks, lost receipts. Collects the transactions from payment-notification emails or bank records, verifies the payee's master data against primary sources, embeds the payment proof as an attachment page, and applies the correct German tax treatment (Eigenbeleg is no invoice — no input-VAT deduction). Use when the user asks for an Eigenbeleg or Ersatzbeleg, says a receipt or invoice is missing ("keine Rechnung", "Beleg fehlt", "nur eine Zahlungsbestätigung"), or needs substitute receipts to upload into bookkeeping software such as Lexware, DATEV, or sevdesk.
metadata:
  category: bookkeeping
---

# eigenbeleg

Turn payment evidence (a payment-notification email, a bank/card transaction) into a signature-ready German **Eigenbeleg** PDF that a bookkeeper can file: page 1 is the Eigenbeleg with all Pflichtangaben, page 2 embeds the payment proof verbatim as an attachment. One PDF per payment.

## When to use

- "Erstell mir einen Eigenbeleg / Ersatzbeleg für ..."
- A recurring expense has no invoice (parking garage pay machine, vending machine, tip, laundromat, lost receipt) but payment confirmations exist (bank notification mails, card statements).
- Receipts are needed for a bookkeeping upload (Lexware, DATEV, sevdesk) and only payment evidence exists.

Not for expenses where a real invoice can still be obtained — always prefer the original document (ask the merchant, check the provider portal) and say so before falling back to an Eigenbeleg.

## Procedure

1. **Collect the transactions.** Source is whatever payment evidence exists: search the user's mail store (e.g. a Thunderbird mbox via Python's `mailbox` module), a bank CSV export, or screenshots. Extract per payment: date+time (mail `Date:` headers are usually UTC — convert to `Europe/Berlin`), gross amount, merchant, payment instrument, and an identifier (e.g. the mail's `Message-ID`). **Dedupe by identifier** — mail folders often hold duplicate copies. Cross-check the resulting list against any known bookkeeping list (booking dates typically lag the payment mail by one day).
2. **Gather the issuer data.** Company name, address, VAT-ID/HRB, and the signer (name + role) — from the repo's company-legal file if one exists, otherwise ask. Also establish the business purpose (betriebliche Veranlassung) — state your assumption explicitly if you infer it.
3. **Verify the payee.** The Zahlungsempfänger with full address is a Pflichtangabe. Research the merchant's operating company via its website Impressum (name, legal form, address, HRB, VAT-ID) and verify against a second source. Never guess the operator behind a card-statement merchant name.
4. **Write the config** (see `references/config.md`) and generate the PDFs:
   ```bash
   uv run --with reportlab python scripts/eigenbeleg.py config.json out/
   ```
   The `reason` field must state *why* no original document exists, truthfully — for a payment-notification mail, reference its actual subject line (the script substitutes `{subject}` per transaction; notification templates change over time, so never hardcode one subject for all).
5. **Verify every PDF against the source** before delivering: amount, date/time (timezone!), identifier, and that every evidence line on page 2 occurs verbatim in the source. Render a sample page to an image and inspect it (clipping, umlauts, €). For larger batches, verify with independent subagents.
6. **Deliver with the booking notes** (from `references/pflichtangaben.md`): sign page 1 by hand; in the bookkeeping tool set the document date to the *payment* date (not the creation date) and the tax rate to **"Keine"** — an Eigenbeleg grants no input-VAT deduction (§ 15 Abs. 1 UStG); check OCR-prefilled contact/date fields, they routinely mis-detect the issuer block as the vendor.

## Ground rules

- **Truthfulness over polish.** Never backdate the creation date, never invent an amount, never paraphrase the evidence — page 2 renders the actual text of the proof (layout duplicates removed, wording unchanged, marked as an extract).
- **Zeitnah.** Create Eigenbelege in the same month as the expense where possible; months-later batches are legal but weaken credibility (GoBD timely-recording principle).
- **Unique numbering.** Receipt numbers must be unique and traceable — the script derives them from prefix + date + time and asserts uniqueness.
- **Fix the root cause.** If the merchant offers registration with monthly invoicing (many parking operators do), recommend it — a real invoice restores the input-VAT deduction and removes the Eigenbeleg need.

## Limits

- Germany-specific (UStG/GoBD); other jurisdictions have different substitute-receipt rules.
- An Eigenbeleg documents a real payment — this skill must never be used to fabricate expenses that did not happen.
- Amounts far above petty-cash levels (guideline: ≥ 250 EUR) face higher scrutiny; warn the user.

## See also

- `references/pflichtangaben.md` — required fields, tax rules with sources, bookkeeping-upload notes
- `references/config.md` — config schema for `scripts/eigenbeleg.py`
- `scripts/eigenbeleg.py` — config-driven PDF generator (reportlab, run via `uv run --with reportlab`)
