# Jamie API — getestete Referenz (tRPC + superjson)

> Maßgebliche, **aus dokumentierten API-Tests abgeleitete** Referenz (Stand 2026-06-21, getestet in einer früheren Integration).
> Offizielle Doku: Index `https://docs.meetjamie.ai/llms.txt` · OpenAPI
> `https://docs.meetjamie.ai/api-reference/openapi.json` · Endpoint-Seiten `…/developers/api/meetings/*.md`.

## ⭐ Die EINE Regel (sonst antwortet die API falsch)

**Jamie ist eine tRPC-API mit superjson-Transformer.** Jeder Parameter — `limit`, `cursor`, `startDate`,
`endDate`, `query`, `meetingId`, `tag` — MUSS in den Wrapper

```
input={"json":{ …alle Parameter hier… }}
```

Parameter **als separate Query-Strings** (`?limit=50`, `?startDate=…`, `?cursor=…`) werden **still
ignoriert** — die API liefert dann ihren Default (50 neueste Meetings), und Datumsfilter/Pagination
wirken „kaputt". Prüfe deshalb, ob Filter und Cursor im Input-Objekt stehen.

**Warum:** tRPC-`httpLink` codiert GET-Inputs als `?input=<URL-encoded JSON>`; der superjson-Transformer
verlangt zusätzlich den `{"json":…}`-Wrapper (er erlaubt u. a. echte Date-Typen). Kein `batch=1` und kein
`{"0":…}`-Index, weil Jamie **ohne** httpBatchLink fährt. (Beleg: trpc.io/docs/rpc + Data-Transformers.)

## Aufruf-Muster (curl) — immer `-G --data-urlencode`

`-G --data-urlencode` URL-encodet das JSON korrekt; **nie** das `{"json":…}` von Hand zusammenbauen.

```bash
B=https://beta-api.meetjamie.ai/v1/me        # personal key  (workspace: /v1/workspace)
H="x-api-key: $JAMIE_API_KEY"

# Liste, 100 neueste
curl -s -G "$B/meetings.list" --data-urlencode 'input={"json":{"limit":100}}' -H "$H"

# Liste mit Datumsfenster (funktioniert!)
curl -s -G "$B/meetings.list" \
  --data-urlencode 'input={"json":{"limit":100,"startDate":"2026-03-01T00:00:00Z","endDate":"2026-03-31T23:59:59Z"}}' -H "$H"

# Meeting-Detail (Summary+Transcript+Tasks+Participants)
curl -s -G "$B/meetings.get" --data-urlencode 'input={"json":{"meetingId":"MEETING_ID"}}' -H "$H"

# Semantische Suche
curl -s -G "$B/meetings.search" --data-urlencode 'input={"json":{"query":"Beispielthema"}}' -H "$H"
```

> ⚠️ **Kein urllib/`requests`** für die Calls: Python-`urllib` bekommt **HTTP 403** (fehlender
> Browser-User-Agent). In Skripten **curl via `subprocess`** aufrufen (siehe Pagination unten).

## Endpoints & Parameter (alle im `input.json`)

### `meetings.list` — chronologische Liste
| Param | Typ | Default / Grenze | Wirkung |
|---|---|---|---|
| `limit` | number | **default 50, max 100** | >100 → Zod-Fehler `too_big` (max 100); `0`/<1 → Zod-Fehler `too_small` |
| `cursor` | string | — | Pagination, Wert aus `nextCursor` der Vorseite |
| `startDate` | string (ISO 8601) | — | Meetings **am/nach** diesem Zeitpunkt |
| `endDate` | string (ISO 8601) | — | Meetings **am/vor** diesem Zeitpunkt |
| `tag` | string (Tag-**Name**) | — | nur `/v1/me`; `tagIds` o. Ä. wird ignoriert |
| `userEmail` | string | — | nur `/v1/workspace` |

Antwort: `result.data.json.meetings[]` (Felder: `id, title, generatedTitle, startTime, endTime,
calendarEventId, userId, isShared`) + `result.data.json.nextCursor` (`null` am Ende).
**nextCursor-Format:** `"2026-06-09T14:21:13.000Z::<meetingId>"`.

### `meetings.get` — Volldetail
`meetingId` (string, Pflicht). Antwort: `…json` mit `title, startTime, endTime, summary.markdown,
transcript, participants[], tasks[]`.

### `meetings.search` — semantische Suche (nur personal key)
`query` (Pflicht) · `startDate` · `endDate`. **Kein `limit`/`cursor`** — gibt **bis 40** relevanteste
**Text-Chunks** zurück, **Default-Fenster: letzte 6 Monate** (mit `startDate` weiter zurück möglich).
Antwort: `…json.results[]` mit `id` (`<meetingId>-chunk-N`), `text`, `meetingId`, `meetingTitle`,
`meetingDate`. → Für „älteres Meeting finden, das jenseits der Listen-Pagination liegt": **search**, dann
`meetingId` (Präfix vor `-chunk`) per `meetings.get` auflösen.

### Weitere (laut offizieller Doku, hier nicht selbst getestet)
`meetings.delete` (POST, `meetingId`) · `tasks.list` · `tags.list`. Zwei Key-Typen mit gleichem
Request-Format: `/v1/me/*` (eigene + geteilte) und `/v1/workspace/*`.

## Pagination — getestetes Muster (curl via subprocess)

`cursor` gehört **ins `input.json`**. Folge dem Cursor nur innerhalb des beauftragten Zeitraums und Umfangs:

```python
import json, subprocess, os
KEY = os.environ['JAMIE_API_KEY']
def page(**params):                      # z.B. page(limit=100) / page(limit=100, cursor=cur)
    inp = json.dumps({"json": params})
    out = subprocess.run(
        ["curl","-s","-G","https://beta-api.meetjamie.ai/v1/me/meetings.list",
         "--data-urlencode","input="+inp,"-H",f"x-api-key: {KEY}"],
        capture_output=True, text=True).stdout
    return json.loads(out)["result"]["data"]["json"]

allm, cur = [], None
while True:
    d = page(limit=100, **({"cursor": cur} if cur else {}))
    allm += d["meetings"]
    # Stop here once the authorized date range or result budget is covered.
    cur = d.get("nextCursor")
    if not cur: break
```

## Fehler-Struktur (tRPC/Zod)

Bei ungültigem Input kommt **kein** `result`, sondern:
`{"error":{"json":{"message":"[{…Zod-Issue…}]","code":-32600, …}}}` — die `message` ist ein
JSON-String mit Zod-Issues (z. B. `too_small` bei `limit:0`). In Skripten auf `"error" in resp` prüfen.

## Verifikations-Belege (2026-06-21, kontrollierte Experimente)

| Test | Query-Param (alt) | im `input.json` (korrekt) |
|---|---|---|
| `limit:3` | 50 zurück (ignoriert) | **3 zurück** ✅ |
| `cursor` (Seite 2) | gleiche IDs (kaputt) | **andere IDs**, Cursor schreitet ✅ |
| `startDate/endDate` März | neueste zurück (ignoriert) | **nur März-Treffer** ✅ |
| `limit` Grenze | — | 100 ok · **101 → Zod-Fehler `too_big`** · 0 → Zod-Fehler `too_small` |
| Datum **+** cursor | — | kombinierbar ✅ |

> Hinweis: Es existiert auch ein **offizielles Jamie-MCP** (`list_meetings`/`search_meetings` mit
> Date-Range, Tag, Pagination eingebaut). Dieser Skill nutzt bewusst **curl** (volle Kontrolle,
> reproduzierbar, kein MCP-Auth-Overhead) — nicht das alte `user-jamie`-MCP.

API-Fehler und HTTP-Status vor dem Parsen prüfen; keine Erfolgsaussage bei unvollständigen Antworten. Bei wiederholtem Cursor abbrechen. Die Beispiele sind Muster; Meeting-IDs stammen erst aus der autorisierten Abfrage.
