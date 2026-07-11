# GeoSphere Austria AROME — Home Assistant Integration (via Open-Meteo)

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz)
[![GitHub release](https://img.shields.io/github/v/release/fhainz/GeoSphere-Arome?include_prereleases)](https://github.com/fhainz/GeoSphere-Arome/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Home Assistant `weather`-Entity, gespeist aus dem **AROME**-Vorhersagemodell
von **GeoSphere Austria** (ex-ZAMG) — 2,5 km Raster, stündlich aktualisiert,
60h Prognose. Abgefragt über die freie **Open-Meteo**-API mit dem Parameter
`models=geosphere_arome_austria`.

**Kein API-Key. Kein Account. Keine Rate-Limit-Sorgen** (Open-Meteo, non-commercial).

## Das Problem, das das löst

In Österreich — speziell im Alpenraum/Kärnten — weicht das global gemittelte
Standardmodell von Wetterdiensten (Met.no, Open-Meteos `best_match` etc.)
teils deutlich von der Realität ab: gemeldete Bewölkung von 80%+, während
draußen die Sonne scheint, oder umgekehrt ein verpasstes Gewitter. GeoSphere
Austria betreibt mit AROME ein eigenes hochauflösendes Modell speziell für
den Alpenraum — aber:

| | Open-Meteo (Core) | GeoSphere Austria `zamg` (Core) | **Diese Integration** |
|---|---|---|---|
| Modell | `best_match` (automatisch) | keins — nur Stationsmesswerte | **fix `geosphere_arome_austria`** |
| Bewölkung | ✅ (globales Modell) | ❌ nicht enthalten | ✅ (AROME) |
| Prognose (stündlich/täglich) | ✅ | ❌ (nur Live-Werte) | ✅ (AROME) |
| API-Key | keiner | keiner | **keiner** |
| Regionalgenauigkeit AT | mittel | hoch (aber nur Punktmessung) | **hoch (Flächenmodell)** |

Die Core-Open-Meteo-Integration lässt sich aktuell nicht auf ein bestimmtes
Modell festlegen (kein UI-Parameter für `models=`), und die Core-Integration
`zamg`/„GeoSphere Austria" liefert ausschließlich Live-Messwerte der
nächstgelegenen von 228 Wetterstationen — keine Bewölkung, keine Prognose.
Diese Integration schließt die Lücke: eine vollwertige `weather`-Entity mit
AROME-Prognosedaten, überall einsetzbar, wo eine `weather_entity` erwartet
wird (z.B. als Wetterquelle in HA-Add-ons).

## Features

- 🌦️ `weather.*`-Entity mit `condition` (WMO-Code → HA-Standardcondition),
  Temperatur, gefühlter Temperatur, Luftfeuchte, Luftdruck
- ☁️ `cloud_coverage` (%) — bei Open-Meteo Core nicht immer verfügbar,
  bei `zamg` gar nicht
- 💨 Windgeschwindigkeit **und** Windböen (`wind_gust_speed`)
- 📈 Stündlicher Forecast (60h) und Tages-Forecast (3 Tage)
- 🌡️ Zusätzlich **Einzelsensoren** (`sensor.*`) für Temperatur, gefühlte
  Temperatur, Luftfeuchte, Bewölkung, Luftdruck, Windgeschwindigkeit,
  Windböen, Windrichtung, Niederschlag — für Automationen/Graphen ohne
  Attribut-Zugriff auf die weather-Entity
- 🎯 Standort frei wählbar (Config Flow), vorbelegt mit der HA-Heimatzone
- 1 API-Call pro Update-Zyklus (Standard 15 min) liefert Current + Hourly +
  Daily gemeinsam — kein unnötiger Traffic

## Installation

### HACS (empfohlen)

1. HACS → ⋮ → *Custom repositories* → hinzufügen:
   `https://github.com/fhainz/GeoSphere-Arome` als Typ *Integration*.
2. **AROME Weather AT (Open-Meteo)** installieren und Home Assistant neu
   starten.

### Manuell

`custom_components/arome_weather_at/` nach `/config/custom_components/`
kopieren und Home Assistant neu starten.

## Setup

1. *Einstellungen → Geräte & Dienste → Integration hinzufügen* →
   **AROME Weather AT**
2. Name vergeben, Breiten-/Längengrad prüfen (vorbelegt mit der HA-Heimatzone,
   frei änderbar — Abdeckung: Mitteleuropa gemäß AROME-Modellgebiet).
3. Fertig — die `weather.*`-Entity kann sofort z.B. als `weather_entity` in
   anderen Integrationen/Add-ons eingetragen werden; die Einzelsensoren
   erscheinen automatisch am selben Gerät.

## Datenherkunft

| Attribut | Open-Meteo-Feld |
|---|---|
| `condition` | `weather_code` (WMO) → HA-Condition-Mapping, Tag/Nacht-sensitiv bei Code 0 |
| `native_temperature` | `temperature_2m` |
| `native_apparent_temperature` | `apparent_temperature` |
| `cloud_coverage` | `cloud_cover` (%) |
| `native_pressure` | `pressure_msl` |
| `native_wind_speed` / `native_wind_gust_speed` | `wind_speed_10m` / `wind_gusts_10m` |
| Forecast stündlich | `hourly.*`, 60 Werte |
| Forecast täglich | `daily.*`, 3 Tage |

## Disclaimer

Nicht offiziell mit GeoSphere Austria oder Open-Meteo verbunden — nutzt
lediglich deren öffentliche APIs. AROME deckt laut Open-Meteo den
Alpenraum/Mitteleuropa ab; außerhalb dieses Gebiets liefert Open-Meteo für
`models=geosphere_arome_austria` ggf. keine sinnvollen Werte.
