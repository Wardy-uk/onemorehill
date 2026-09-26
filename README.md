# One More Hill

**While you're there, bag them all.**

A UK & Ireland hill and trig-point bagging app — 96 challenges, 27,657 locations, and the
thing no other app does: **one visit credits every list that location belongs to.**

## What's here

| | |
|---|---|
| `data/` | Pipeline: two open datasets → 96 challenges |
| `site/` | Public trig↔hill cross-reference page (static) |
| `app/` | The app (SvelteKit + Capacitor, iOS first) |

## Quick start

```bash
./data/fetch-sources.sh      # download DoBIH + OS trig archive
python3 data/build.py        # generate challenges + locations
cd site && python3 -m http.server 8731
```

## The data

**21,576 hills** from the [Database of British and Irish Hills](https://www.hill-bagging.co.uk/dobih)
v18.6 (CC BY 4.0) · **6,081 standing trig pillars** from the OS Complete Trig Archive (OGL).

Joined for the first time: **1,510 pillars sit within 10m of a named hill.** Scafell Pike's is
0.3m from the summit, and that summit belongs to 13 separate challenge lists.

## Licences

Code MIT. Data as above — attribution required, see `CLAUDE.md`.
