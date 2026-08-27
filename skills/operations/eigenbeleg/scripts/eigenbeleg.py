#!/usr/bin/env python3
"""Config-driven generator for German Eigenbelege (substitute receipts).

Renders one A4 PDF per transaction: page 1 = Eigenbeleg with all required
fields, page 2 (optional) = the payment proof embedded verbatim as attachment.

Usage:
  uv run --with reportlab python eigenbeleg.py <config.json> <out-dir> [--only-month YYYY-MM]

Config schema: see references/config.md next to this script's skill.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

W, H = A4
LM, RM = 22 * mm, 22 * mm
TW = W - LM - RM

DEFAULT_VAT_NOTE = (
    "Bruttobetrag; enthaltene USt ist mangels Rechnung i. S. d. §§ 14, 15 UStG nicht als Vorsteuer",
    "abziehbar – Verbuchung als Betriebsausgabe mit Steuersatz „Keine“.",
)
AFFIRMATION = ("Ich versichere, dass die Aufwendung betrieblich veranlasst war, der Betrag in der "
               "angegebenen Höhe gezahlt wurde und ein Originalbeleg nicht erlangt werden konnte.")


def fmt_eur(v: float) -> str:
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " EUR"


def wrap(c, text, font, size, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if c.stringWidth(t, font, size) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(c, x, y, text, font="Helvetica", size=10, maxw=TW, lead=None):
    lead = lead or size * 1.35
    for ln in wrap(c, text, font, size, maxw):
        c.setFont(font, size)
        c.drawString(x, y, ln)
        y -= lead
    return y


def field(c, y, label, value, label_w=48 * mm, size=10):
    c.setFont("Helvetica-Bold", size)
    c.drawString(LM, y, label)
    yy = y
    for v in value if isinstance(value, list) else [value]:
        yy = para(c, LM + label_w, yy, v, size=size, maxw=TW - label_w)
    return yy - 3 * mm


def draw_beleg(c, cfg, tx, nr, created):
    dt = tx["dt"]
    y = H - 25 * mm
    issuer = cfg["issuer"]["lines"]
    c.setFont("Helvetica-Bold", 10)
    c.drawString(LM, y, issuer[0])
    c.setFont("Helvetica", 9)
    for i, ln in enumerate(issuer[1:], start=1):
        c.drawString(LM, y - i * 4.2 * mm, ln)
    c.setFont("Helvetica", 9)
    c.drawRightString(W - RM, y, f"Beleg-Nr. {nr}")
    c.drawRightString(W - RM, y - 4.2 * mm, f"Erstellt am {created.strftime('%d.%m.%Y')}")

    y -= 26 * mm
    c.setFont("Helvetica-Bold", 20)
    c.drawString(LM, y, "Eigenbeleg")
    c.setFont("Helvetica", 11)
    c.drawString(LM + 62 * mm, y + 1, "(Ersatzbeleg für fehlende Rechnung/Quittung)")
    y -= 5 * mm
    c.setLineWidth(0.8)
    c.line(LM, y, W - RM, y)
    y -= 12 * mm

    subject = tx.get("subject", "")
    y = field(c, y, "Zahlungsempfänger", cfg["payee"]["lines"])
    y = field(c, y, "Art der Aufwendung", cfg["expense_type"])
    y = field(c, y, "Datum der Zahlung", f"{dt.strftime('%d.%m.%Y')} (Kartenzahlung, {dt.strftime('%H:%M')} Uhr)"
              if tx.get("show_time", True) else dt.strftime("%d.%m.%Y"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(LM, y, "Betrag (brutto)")
    c.setFont("Helvetica-Bold", 13)
    c.drawString(LM + 48 * mm, y, fmt_eur(tx["amount_val"]))
    y -= 5 * mm
    c.setFont("Helvetica", 8.5)
    for ln in cfg.get("vat_note") or DEFAULT_VAT_NOTE:
        c.drawString(LM + 48 * mm, y, ln)
        y -= 3.6 * mm
    y -= 4.4 * mm
    y = field(c, y, "Zahlungsart", cfg["payment_method"])
    y = field(c, y, "Betriebliche Veranlassung", cfg["purpose"])
    y = field(c, y, "Grund für Eigenbeleg", cfg["reason"].format(subject=subject))
    if tx.get("proof_lines"):
        y = field(c, y, "Nachweis", [ln.format(subject=subject) for ln in tx["proof_lines"]])

    y -= 6 * mm
    y = para(c, LM, y, AFFIRMATION, size=10)

    y -= 22 * mm
    c.setLineWidth(0.5)
    c.line(LM, y, LM + 70 * mm, y)
    c.line(W - RM - 70 * mm, y, W - RM, y)
    c.setFont("Helvetica", 9)
    c.drawString(LM, y - 4.5 * mm, "Ort, Datum")
    c.drawString(LM, y - 9 * mm, f"{cfg['issuer']['city']}, {created.strftime('%d.%m.%Y')}")
    c.drawString(W - RM - 70 * mm, y - 4.5 * mm, "Unterschrift")
    c.drawString(W - RM - 70 * mm, y - 9 * mm, cfg["issuer"]["signer"])

    pages = "1/2" if tx.get("evidence_headers") or tx.get("evidence_lines") else "1/1"
    c.setFont("Helvetica", 7.5)
    c.drawString(LM, 15 * mm, f"{nr} · Seite {pages} · Eigenbeleg {cfg['expense_type'][0]} "
                              f"{dt.strftime('%d.%m.%Y')} · {fmt_eur(tx['amount_val'])}")
    c.showPage()


def draw_anlage(c, cfg, tx, nr):
    y = H - 25 * mm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(LM, y, tx.get("evidence_title") or cfg.get("evidence_title", "Anlage: Zahlungsnachweis"))
    y -= 4 * mm
    c.setLineWidth(0.8)
    c.line(LM, y, W - RM, y)
    y -= 10 * mm
    for k, v in tx.get("evidence_headers", []):
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(LM, y, k)
        y = para(c, LM + 28 * mm, y, v, font="Courier", size=9, maxw=TW - 28 * mm)
        y -= 1.5 * mm
    y -= 4 * mm
    c.setLineWidth(0.3)
    c.line(LM, y, W - RM, y)
    y -= 9 * mm

    bold = set(tx.get("evidence_bold", []))
    for ln in tx.get("evidence_lines", []):
        font = "Courier-Bold" if ln in bold else "Courier"
        y = para(c, LM, y, ln, font=font, size=9, maxw=TW, lead=4.4 * mm)
        if not (ln.endswith(":") or ln in bold):
            y -= 1.5 * mm
    y -= 5 * mm
    note = tx.get("evidence_note") or cfg.get("evidence_note")
    if note:
        y = para(c, LM, y, note, font="Helvetica-Oblique", size=8.5)
    c.setFont("Helvetica", 7.5)
    c.drawString(LM, 15 * mm, f"{nr} · Seite 2/2 · Anlage Zahlungsnachweis")
    c.showPage()


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    cfg = json.loads(Path(sys.argv[1]).read_text())
    out_dir = Path(sys.argv[2])
    only_month = sys.argv[sys.argv.index("--only-month") + 1] if "--only-month" in sys.argv else None

    txs = []
    for tx in cfg["transactions"]:
        tx = dict(tx)
        tx["dt"] = datetime.fromisoformat(tx["datetime"])
        if tx["dt"].tzinfo is None:
            raise SystemExit(f"datetime without offset: {tx['datetime']}")
        tx["amount_val"] = float(tx["amount"].replace(".", "").replace(",", "."))
        txs.append(tx)
    txs.sort(key=lambda t: t["dt"])

    created = datetime.now().astimezone()
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for tx in txs:
        d = tx["dt"].strftime("%Y-%m-%d")
        if only_month and not d.startswith(only_month):
            continue
        nr = f"{cfg['nr_prefix']}-{d}-{tx['dt'].strftime('%H%M')}"
        fn = out_dir / f"Eigenbeleg_{cfg['file_slug']}_{d}_{tx['amount'].replace(',', '-')}EUR.pdf"
        if fn.exists():
            fn = fn.with_name(fn.stem + f"_{tx['dt'].strftime('%H%M')}.pdf")
        c = canvas.Canvas(str(fn), pagesize=A4)
        c.setTitle(f"Eigenbeleg {nr} – {cfg['expense_type'][0]} {fmt_eur(tx['amount_val'])}")
        c.setAuthor(cfg["issuer"]["lines"][0])
        c.setSubject("Eigenbeleg")
        draw_beleg(c, cfg, tx, nr, created)
        if tx.get("evidence_headers") or tx.get("evidence_lines"):
            draw_anlage(c, cfg, tx, nr)
        c.save()
        manifest.append({"nr": nr, "file": fn.name, "date": d, "time": tx["dt"].strftime("%H:%M"),
                         "amount": tx["amount_val"], "amount_str": tx["amount"]})
        print(f"{d} {tx['dt'].strftime('%H:%M')}  {tx['amount']:>8} EUR  -> {fn.name}")

    assert len({m["nr"] for m in manifest}) == len(manifest), "Beleg-Nummern nicht eindeutig"
    assert len({m["file"] for m in manifest}) == len(manifest), "Dateinamen nicht eindeutig"
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
    print(f"{len(manifest)} Belege, Summe {fmt_eur(sum(m['amount'] for m in manifest))}")


if __name__ == "__main__":
    main()
