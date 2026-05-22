"""infographic_builder -- compose premium Excalidraw infographics programmatically.

A shape library gives you *shapes*; it can never give you *layout* -- arrangement
is always per-diagram. This module is the thin composition layer that sits between
the library and a finished `.excalidraw` file: it places library items by name,
adds the connective tissue (text, arrows, numbered badges, pills), and dumps valid
JSON. It exists so an agent does not have to hand-write 100+ raw element dicts (or
re-invent coordinate math) for every complex infographic.

Pairs with:
  - libraries/infographic-elements.excalidrawlib  -- the shape vocabulary (`place` by name)
  - color-palette.md                              -- PREMIUM + YESTERDAY palettes (mirrored here)
  - signature-elements.md                         -- the catalog these pieces implement
  - render_excalidraw.py                          -- renders the file this produces

Quickstart:
    import sys; sys.path.insert(0, "<.../references>")
    from infographic_builder import Scene, PREMIUM, FONT

    s = Scene(1400, 800)                                  # cream premium canvas
    s.title("KV Caching", 80, 56)                         # display title + highlighter swipe
    x = s.place("Query envelope", 120, 240, h=70)         # drop a library item, scaled to 70px tall
    s.arrow(x + 10, 270, dx=80, numbered=1)               # dashed flow arrow + numbered badge
    s.place("Vector DB", x + 110, 235, h=90)
    s.text(120, 360, "grounded chunks", color=PREMIUM.GRAY, fam=FONT.SANS)
    s.thesis("Cache the past; don't recompute it.")       # mandatory bottom-summary
    s.save("/tmp/out.excalidraw")
    # render: uv run python render_excalidraw.py /tmp/out.excalidraw --theme light

Then ALWAYS run the render-verify-adapt loop (see SKILL.md): render, inspect the
PNG, fix overlaps, re-render. The builder removes coordinate drudgery; it does not
guarantee the layout looks right.
"""
from __future__ import annotations
import copy
import json
from pathlib import Path

_LIBDIR = Path(__file__).resolve().parent / "libraries"
_DEFAULT_LIB = "infographic-elements"


class PREMIUM:
    """Hand-drawn Daily-Dose-of-DS / Akshay-Pachaar palette (use roughness=1)."""
    CANVAS = "#F7F3E9"; INK = "#1F1F1F"; GRAY = "#737373"
    BLUE = "#D3EBF7"; BLUE_S = "#2F6FA8"
    MINT = "#C2E7B0"; MINT_S = "#4E8C3F"
    LAV = "#D2B9DE"; LAV_S = "#7B5BA6"
    CORAL = "#F9BC9E"; CORAL_S = "#C75A3A"
    BUTTER = "#FCEDCE"; BUTTER_S = "#B5872B"
    NEUTRAL = "#ECECE8"; NEUTRAL_S = "#8A8A82"


class YESTERDAY:
    """Yesterday CI editorial palette (use roughness=0, clean cards)."""
    CANVAS = "#F7F3E9"; INK = "#0A0A0A"; GRAY = "#737373"
    ORANGE = "#FC4E14"; ORANGE_L = "#FFD8CB"
    GOLD = "#FFBB38"; GOLD_L = "#FFECB9"; AMBER_S = "#92610F"
    GREEN = "#1B7340"; GREEN_L = "#E6F4EC"
    RED = "#C43D2E"; RED_L = "#FCEAE7"
    BLUE = "#2563EB"; BLUE_L = "#EFF6FF"
    CARD = "#FFFFFF"; BORDER = "#E3DDD0"


class DARK:
    """Flat dark-mode technical-reference palette. Dark canvas + flat colored cards;
    render with --theme light (NOT --theme dark, which inverts). This is the
    reproducible flat-dark style -- distinct from the glowing-neon family (avoid)."""
    CANVAS = "#1C1A2B"; CARD = "#14131C"; CARD_BR = "#5B4E86"; DIV = "#3A3550"; TRACK = "#262236"
    TXT = "#E8E6F2"; MUTED = "#9A95B5"
    PURPLE = "#A78BFA"; TEAL = "#34D3C0"; GREEN = "#6BD46B"
    ORANGE = "#F2913D"; PINK = "#FB6FA0"; RED = "#F2655C"


class FONT:
    """Verified renderer fontFamily IDs (see KNOWLEDGE.md / font-catalog.png)."""
    DISPLAY = 7   # Lilita One (bold display)
    HAND = 5      # Excalifont (hand-drawn)
    SANS = 6      # Nunito
    MONO = 3      # Cascadia (code/data/kicker)


class Scene:
    """Accumulates elements and writes a valid `.excalidraw` document."""

    def __init__(self, width: int = 1400, height: int = 900, canvas: str = PREMIUM.CANVAS,
                 roughness: int = 1):
        self.W, self.H = width, height
        self.canvas = canvas
        self.roughness = roughness          # 1 = hand-drawn (premium); 0 = clean (Yesterday CI)
        self._els: list[dict] = []
        self._n = 0
        self._libcache: dict[str, dict] = {}

    # ---- internals -------------------------------------------------------
    def _id(self, p: str = "e") -> str:
        self._n += 1
        return f"{p}{self._n}"

    def _el(self, **k) -> dict:
        self._n += 1
        base = dict(fillStyle="solid", strokeWidth=2, strokeStyle="solid",
                    roughness=self.roughness, opacity=100, angle=0, version=1,
                    isDeleted=False, groupIds=[], boundElements=None, link=None,
                    locked=False, frameId=None)
        e = {**base, **k}
        e.setdefault("seed", self._n * 131 + 7)
        e.setdefault("versionNonce", self._n * 779 + 3)
        e["id"] = k.get("id") or f"e{self._n}"
        self._els.append(e)
        return e

    # ---- primitives ------------------------------------------------------
    def rect(self, x, y, w, h, fill, stroke, *, dash=False, rounded=True, sw=2, rough=None):
        return self._el(type="rectangle", x=x, y=y, width=w, height=h,
                        backgroundColor=fill, strokeColor=stroke, strokeWidth=sw,
                        roughness=self.roughness if rough is None else rough,
                        strokeStyle="dashed" if dash else "solid",
                        roundness={"type": 3} if rounded else None)

    def ellipse(self, x, y, w, h, fill, stroke, *, dash=False, sw=2):
        return self._el(type="ellipse", x=x, y=y, width=w, height=h,
                        backgroundColor=fill, strokeColor=stroke, strokeWidth=sw,
                        strokeStyle="dashed" if dash else "solid")

    def text(self, x, y, s, *, fs=18, color=PREMIUM.INK, align="left", fam=FONT.HAND, w=None):
        return self._el(type="text", x=x, y=y, width=w or (len(s) * fs * 0.6 + 8),
                        height=fs + 6, text=s, originalText=s, fontSize=fs, fontFamily=fam,
                        textAlign=align, verticalAlign="middle", strokeColor=color,
                        backgroundColor="transparent", containerId=None, lineHeight=1.25)

    def line(self, x, y, pts, *, color=PREMIUM.INK, sw=2, dash=False):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        return self._el(type="line", x=x, y=y, width=max(1, max(xs) - min(xs)),
                        height=max(1, max(ys) - min(ys)), strokeColor=color,
                        backgroundColor="transparent", strokeWidth=sw,
                        strokeStyle="dashed" if dash else "solid", points=pts)

    def arrow(self, x, y, *, pts=None, dx=None, dy=0, color=PREMIUM.INK, sw=2,
              dash=True, numbered=None):
        """Dashed flow arrow (the premium default). `dx`/`dy` is a shortcut for a
        straight segment; or pass explicit `pts`. `numbered=N` drops a badge at the
        midpoint."""
        if pts is None:
            pts = [[0, 0], [dx if dx is not None else 80, dy]]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        self._el(type="arrow", x=x, y=y, width=max(1, max(xs) - min(xs)),
                 height=max(1, max(ys) - min(ys)), strokeColor=color,
                 backgroundColor="transparent", strokeWidth=sw,
                 strokeStyle="dashed" if dash else "solid", points=pts,
                 startArrowhead=None, endArrowhead="arrow")
        if numbered is not None:
            mx = x + (pts[0][0] + pts[-1][0]) / 2
            my = y + (pts[0][1] + pts[-1][1]) / 2
            self.numbered_badge(mx, my, numbered)

    # ---- composites ------------------------------------------------------
    def pill(self, x, y, w, h, label, fill, stroke, *, fs=20, fam=FONT.HAND, sub=None):
        self.rect(x, y, w, h, fill, stroke)
        if sub:
            self.text(x, y + h * 0.16, label, fs=fs, color=PREMIUM.INK, align="center", w=w)
            self.text(x, y + h * 0.56, sub, fs=14, color=stroke, align="center", w=w)
        else:
            self.text(x, y + (h - fs) / 2 - 2, label, fs=fs, color=PREMIUM.INK, align="center", w=w)

    def numbered_badge(self, cx, cy, n, *, fill=PREMIUM.BUTTER, stroke=PREMIUM.BUTTER_S):
        d = 30
        self.ellipse(cx - d / 2, cy - d / 2, d, d, fill, stroke, dash=True)
        self.text(cx - d / 2, cy - 11, str(n), fs=16, color="#92610F", align="center", w=d)

    def numbered_circle(self, cx, cy, n, fill, stroke, *, d=30, color=None, fam=FONT.MONO):
        """Solid filled circle with a CENTERED number (the correctly-centered counterpart
        to a manual ellipse+text -- use this so the digit can't drift to a corner)."""
        self.ellipse(cx - d / 2, cy - d / 2, d, d, fill, stroke)
        self.text(cx - d / 2, cy - 11, str(n), fs=int(d * 0.53), color=color or stroke,
                  align="center", w=d, fam=fam)

    def meter(self, x, y, w, pct, fill, *, track=DARK.TRACK, track_br=DARK.DIV, h=16):
        """Capacity / usage bar: a track + a fill at `pct` (0..1)."""
        self.rect(x, y, w, h, track, track_br, sw=1)
        if pct > 0:
            self.rect(x, y, max(2, w * pct), h, fill, fill, sw=0)

    def gauge(self, cx, cy, value, *, d=116, ring=DARK.TEAL, track="#2A2740",
              color=DARK.TXT, label=None, muted=DARK.MUTED):
        """Circular timer/gauge ring with a centered value (and optional label below)."""
        self.ellipse(cx - d / 2, cy - d / 2, d, d, "transparent", track, sw=10)
        self.ellipse(cx - d / 2, cy - d / 2, d, d, "transparent", ring, sw=4)
        self.text(cx - d / 2, cy - d * 0.14, value, fs=int(d * 0.26), color=color,
                  align="center", w=d, fam=FONT.DISPLAY)
        if label:
            self.text(cx - d / 2, cy + d * 0.5 + 10, label, fs=13, color=muted, align="center", w=d, fam=FONT.SANS)

    def top_accent(self, x, y, w, color, *, r=30, h=7, gap=3):
        """A top accent strip for a ROUNDED card. Inset by the corner radius and
        rounded at its own ends, so it doesn't poke past the card's rounded corners
        (Excalidraw has no per-corner radius). Place a card first, then call this."""
        self.rect(x + r, y + gap, w - 2 * r, h, color, color, sw=0, rounded=True)

    def highlighter(self, x, y, w, h, color=PREMIUM.BLUE):
        """A swipe rect with transparent stroke -- draw BEFORE the text it sits behind."""
        return self._el(type="rectangle", x=x, y=y, width=w, height=h,
                        backgroundColor=color, strokeColor="transparent",
                        roughness=self.roughness, roundness={"type": 3})

    def title(self, s, x, y, *, fs=46, swipe=PREMIUM.BLUE, fam=FONT.DISPLAY, accent=None):
        """Display headline with a highlighter swipe behind it (+ optional left accent bar)."""
        if accent:
            self.rect(x - 32, y + 2, 14, fs + 12, accent, accent, rounded=False)
        self.highlighter(x + 4, y + fs * 0.30, len(s) * fs * 0.52, fs * 0.78, swipe)
        self.text(x, y, s, fs=fs, color=PREMIUM.INK, align="left", fam=fam, w=len(s) * fs * 0.62 + 40)

    def thesis(self, s, *, y=None, fs=24, fam=FONT.HAND):
        """Mandatory bottom-summary sentence, centered near the canvas bottom."""
        yy = self.H - 60 if y is None else y
        self.text(80, yy, s, fs=fs, color=PREMIUM.INK, align="center", fam=fam, w=self.W - 160)

    # ---- library placement (the key capability) --------------------------
    def _load_lib(self, lib: str) -> dict:
        if lib not in self._libcache:
            data = json.loads((_LIBDIR / f"{lib}.excalidrawlib").read_text())
            items = data.get("libraryItems") or data.get("library") or []
            by_name = {}
            for it in items:
                els = it["elements"] if isinstance(it, dict) else it
                name = it.get("name") if isinstance(it, dict) else None
                if name:
                    by_name[name] = els
            self._libcache[lib] = by_name
        return self._libcache[lib]

    def list_items(self, lib: str = _DEFAULT_LIB) -> list[str]:
        """Names available for `place()` in the given library."""
        return sorted(self._load_lib(lib).keys())

    def place(self, name, x, y, *, h=None, w=None, lib=_DEFAULT_LIB, drop_text=False) -> float:
        """Drop a library item by name at (x, y), scaled so its bounding box is `h`
        tall (or `w` wide). Returns the placed right edge (x + width) so callers can
        chain horizontal positions. `drop_text=True` strips the item's baked-in labels."""
        src = self._load_lib(lib).get(name)
        if src is None:
            raise KeyError(f"{name!r} not in {lib}.excalidrawlib. Available: {self.list_items(lib)}")
        els = [e for e in src if not (drop_text and e.get("type") == "text")]
        xs = [e["x"] for e in els]; ys = [e["y"] for e in els]
        xe = [e["x"] + e.get("width", 0) for e in els]
        ye = [e["y"] + e.get("height", 0) for e in els]
        minx, miny = min(xs), min(ys)
        bw = max(1, max(xe) - minx); bh = max(1, max(ye) - miny)
        s = (h / bh) if h else (w / bw) if w else 1.0
        gid = self._id("grp")
        for se in els:
            self._n += 1
            e = copy.deepcopy(se)
            e["x"] = x + (se["x"] - minx) * s
            e["y"] = y + (se["y"] - miny) * s
            e["width"] = se.get("width", 0) * s
            e["height"] = se.get("height", 0) * s
            if e.get("points"):
                e["points"] = [[p[0] * s, p[1] * s] for p in e["points"]]
            if e.get("type") == "text":
                e["fontSize"] = e.get("fontSize", 16) * s
            e["id"] = f"x{self._n}"; e["seed"] = self._n * 7 + 1
            e["versionNonce"] = self._n * 31 + 9
            e["groupIds"] = [gid]; e["boundElements"] = None
            self._els.append(e)
        return x + bw * s

    # ---- output ----------------------------------------------------------
    def save(self, path) -> str:
        doc = {"type": "excalidraw", "version": 2, "source": "infographic_builder",
               "appState": {"viewBackgroundColor": self.canvas, "gridSize": 20},
               "files": {}, "elements": self._els}
        Path(path).write_text(json.dumps(doc))
        return str(path)


if __name__ == "__main__":
    # Tiny smoke test: build, place two library items, save.
    s = Scene(900, 360)
    s.title("RAG, in one line", 60, 48, accent=PREMIUM.LAV)
    rx = s.place("Query envelope", 90, 170, h=64, drop_text=True)
    s.arrow(rx + 10, 200, dx=70, numbered=1)
    s.place("Vector DB", rx + 100, 165, h=86, drop_text=True)
    s.thesis("Retrieve, then generate.")
    out = s.save("/tmp/builder_smoketest.excalidraw")
    print("wrote", out, "elements:", len(s._els))
