---
name: vrr-efa-api
description: >
  Live-Fahrplanauskunft für den VRR (Verkehrsverbund Rhein-Ruhr) via EFA API.
  Abfahrten, Verbindungen, Haltestellen -- Echtzeit, kostenlos, kein API Key.
  Use when: user asks for train/bus/tram connections, departures, or transit
  info in NRW/Ruhrgebiet. Also works for DB Regionalverkehr in the region.
metadata:
  category: research
  author: ManniTheRaccoon
  version: "1.0"
compatibility: Requires curl, jq. No API key needed.
---

# VRR Fahrplan 🚂

Live-Fahrplanauskunft für Bus & Bahn im Rhein-Ruhr-Gebiet. Echtzeit-Daten, kostenlos, kein Key.

**Base URL:** `https://efa.vrr.de/vrr`

## Quick Reports

### Verbindung A → B

```bash
curl -sf "https://efa.vrr.de/vrr/XML_TRIP_REQUEST2?outputFormat=rapidJSON&type_origin=stop&name_origin=ORIGIN&type_destination=stop&name_destination=DEST&useRealtime=1&itdTripDateTimeDepArr=dep" \
| jq -r '
  .journeys[:6][] |
  .legs[0] as $first | .legs[-1] as $last |
  ($first.origin.departureTimePlanned // "")[11:16] as $dep |
  ($first.origin.departureTimeEstimated // "")[11:16] as $dep_est |
  ($last.destination.arrivalTimePlanned // "")[11:16] as $arr |
  ($first.transportation.product.name // "") + " " + ($first.transportation.disassembledName // "") |
  ltrimstr(" ") as $line |
  ($first.origin.properties.platformName // "?") as $gl |
  (if $dep_est != "" and $dep_est != $dep then " (+" + (($dep_est[3:5] | tonumber) - ($dep[3:5] | tonumber) | tostring) + ")" else "" end) as $delay |
  "\($dep)\($delay) | Gl. \($gl) | \($line) → an \($arr)"
'
```

**Beispiel:** `name_origin=Dortmund%20Hbf&name_destination=Bochum%20Hbf`

**Output:**
```
11:45 (+1) | Gl. 16 | Regionalzug RE1 → an 11:54
11:53 | Gl. 7 | S-Bahn S1 → an 12:16
12:07 | Gl. 16 | Regionalzug RE6 → an 12:18
```

### Abfahrtstafel (nächste Abfahrten ab Haltestelle)

```bash
curl -sf "https://efa.vrr.de/vrr/XML_DM_REQUEST?outputFormat=rapidJSON&type_dm=stop&name_dm=HALTESTELLE&mode=direct&useRealtime=1" \
| jq -r '
  .stopEvents[:10][] |
  (.departureTimePlanned // "")[11:16] as $dep |
  (.departureTimeEstimated // "")[11:16] as $dep_est |
  (.transportation.disassembledName // .transportation.name // "?") as $line |
  (.transportation.destination.name // "?") as $dest |
  (.location.properties.platformName // "?") as $gl |
  (if $dep_est != "" and $dep_est != $dep then " (+" + (($dep_est[3:5] | tonumber) - ($dep[3:5] | tonumber) | tostring) + ")" else "" end) as $delay |
  "\($dep)\($delay) | Gl. \($gl) | \($line) → \($dest)"
'
```

**Beispiel:** `name_dm=Essen%20Hbf`

**Output:**
```
11:37 (+4) | Gl. 3 | 105 → Finefraustr.
11:38 (+3) | Gl. 1 | U11 → Gelsenkirchen
11:40 (+9) | Gl. 8 | RE2 → Osnabrück Hbf
```

### Haltestelle suchen

```bash
curl -sf "https://efa.vrr.de/vrr/XML_STOPFINDER_REQUEST?outputFormat=rapidJSON&type_sf=any&name_sf=SUCHBEGRIFF" \
| jq -r '.locations[:5][] | "\(.name) [\(.type)] id:\(.id)"'
```

**Beispiel:** `name_sf=Dortmund%20Signal`

**Output:**
```
Dortmund Signal Iduna Park [stop] id:de:05913:8610
```

## API Endpoints

| Endpoint | Zweck |
|---|---|
| `XML_TRIP_REQUEST2` | Verbindungssuche A → B |
| `XML_DM_REQUEST` | Abfahrtstafel einer Haltestelle |
| `XML_STOPFINDER_REQUEST` | Haltestelle suchen |

## Wichtige Parameter

### Verbindungssuche (TRIP_REQUEST)

| Parameter | Wert | Beschreibung |
|---|---|---|
| `outputFormat` | `rapidJSON` | JSON-Output |
| `type_origin` | `stop` | Typ der Starthaltestelle |
| `name_origin` | z.B. `Dortmund Hbf` | Name der Starthaltestelle |
| `type_destination` | `stop` | Typ der Zielhaltestelle |
| `name_destination` | z.B. `Bochum Hbf` | Name der Zielhaltestelle |
| `useRealtime` | `1` | Echtzeit-Daten einbeziehen |
| `itdTripDateTimeDepArr` | `dep` / `arr` | Abfahrt oder Ankunft |
| `itdDateDay` | `31` | Tag (optional, default: jetzt) |
| `itdDateMonth` | `3` | Monat |
| `itdDateYear` | `2026` | Jahr |
| `itdTimeHour` | `14` | Stunde |
| `itdTimeMinute` | `30` | Minute |

### Abfahrtstafel (DM_REQUEST)

| Parameter | Wert | Beschreibung |
|---|---|---|
| `outputFormat` | `rapidJSON` | JSON-Output |
| `type_dm` | `stop` | Haltestellentyp |
| `name_dm` | z.B. `Essen Hbf` | Haltestellenname |
| `mode` | `direct` | Nur direkte Abfahrten |
| `useRealtime` | `1` | Echtzeit |
| `limit` | `10` | Max. Ergebnisse |

## Response-Struktur

### Verbindung (Journey)

```
journey.legs[0].origin.departureTimePlanned     → "2026-03-31T09:45:00Z" (UTC!)
journey.legs[0].origin.departureTimeEstimated    → "2026-03-31T09:46:30Z" (mit Verspätung)
journey.legs[0].origin.properties.platformName   → "16" (Gleis)
journey.legs[0].transportation.product.name      → "Regionalzug"
journey.legs[0].transportation.disassembledName  → "RE1"
journey.legs[-1].destination.arrivalTimePlanned   → "2026-03-31T09:54:00Z"
```

### Abfahrt (StopEvent)

```
stopEvent.departureTimePlanned                   → "2026-03-31T09:37:00Z" (UTC!)
stopEvent.departureTimeEstimated                 → "2026-03-31T09:41:24Z"
stopEvent.transportation.disassembledName        → "105"
stopEvent.transportation.destination.name        → "Essen Finefraustr."
stopEvent.location.properties.platformName       → "3"
```

## ⚠️ Wichtige Hinweise

- **Zeiten sind UTC!** Für deutsche Ortszeit +1h (MEZ) oder +2h (MESZ) addieren
- **URL-Encoding:** Leerzeichen und Umlaute encoden (`%20`, `%C3%BC` etc.)
- **Kein API Key nötig** -- öffentliche API, aber Fair Use beachten
- **Abdeckung:** Primär VRR (Ruhrgebiet, Rheinland, Wuppertal), aber auch DB Fernverkehr und angrenzende Verbünde werden angezeigt
- **Haltestellen-Format:** `Stadt Haltestelle` (z.B. `Dortmund Hbf`, `Essen Hauptbahnhof`)

## Formatting für Chat

Wenn du Ergebnisse an den User sendest:

**Verbindung:**
```
🚂 **11:45** (+1) | **Gl. 16** | RE1 → an 11:54
🚋 **11:53** | **Gl. 7** | S1 → an 12:16
```

**Abfahrtstafel:**
```
📋 Abfahrten Essen Hbf:
🚋 11:37 (+4) | Gl. 3 | 105 → Finefraustr.
🚇 11:38 (+3) | Gl. 1 | U11 → Gelsenkirchen
```

**Icons nach Verkehrsmittel:**
- 🚂 Regionalzug (RE, RB)
- 🚄 Fernverkehr (IC, ICE)
- 🚇 U-Bahn
- 🚋 Straßenbahn / S-Bahn
- 🚌 Bus
- 🚶 Fußweg (Umstieg)

---
*v1.0 -- VRR EFA API Skill. ManniTheRaccoon 2026-03-31.* 🚂
