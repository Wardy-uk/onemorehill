# One More Hill

> **While you're there, bag them all**

UK & Ireland hill and trig-point bagging app. 96 challenges, 27,657 locations, cross-list
credit, and route augmentation.

## Read first

The full spec lives in the Obsidian vault, **not** in this repo:

```
~/Documents/Nicks Knowledge Base/Projects/Hill Bagging App/
├── Hill Bagging App.md                    ← THE SPEC. Read this first.
├── Hill Bagging App - Challenge Lists.md  ← all 96 challenges, licensing
├── Hill Bagging App - Join Results.md     ← trig↔hill join, validation
├── Hill Bagging App - Infrastructure.md   ← free tiers, weather, hosting
├── Hill Bagging App - Weather.md          ← MWIS-style forecast method
├── Hill Bagging App - Outreach Drafts.md  ← forum post + email
└── Hill Bagging App - Build 0..8 *.md     ← paste-and-go stage prompts
```

**Each build stage is a fresh Claude Code session.** Open the relevant
`Build N` note and paste it whole.

## Repo layout

```
data/     pipeline: source CSVs → challenges, locations, rounds, groups, peak sets
site/     Stage 0 probe page (static, no build step)
app/      SvelteKit + Capacitor app (from Build 1)
```

Run `data/fetch-sources.sh` first — source CSVs are gitignored, not vendored.

## Non-negotiables

These were established by research and cost real time to discover. Do not rediscover them.

- **Never read DoBIH's `Classification` column.** It is a display summary: omits TuMPs
  entirely, under-reports HuMPs (1,808 vs 3,815). Use the **boolean columns**.
- **Ship Grahams as "Fionas"** — `G` AND height ≥ 609.6m → exactly 219. "Grahams" is
  trademarked; the derived set is also what the SMC Full House actually uses.
- **Trig and summit are distinct locations.** Coincidence threshold **10m, not 100m**.
  Helvellyn's pillar is 89m from the summit.
- **Keep ODbL data separate.** Dartmoor tors come from OSM (share-alike). DoBIH is CC BY 4.0,
  OS trig is OGL. Do not let them mix.
- **No AI in the routing or planning path.** Geometry and graph search only. A hallucinated
  route in a mountain app is indefensible.
- **Never auto-tick an OCR import.** Always confirm before writing.
- **Capacitor's Preferences plugin is not a database.** Use structured local storage.
- **Weather: MET Norway primary.** `fog_area_fraction` is useless (reads 0.0 everywhere).
  Use dew-point spread + low-cloud fraction at summit altitude.

## Attribution required in-app

- Database of British and Irish Hills v18.6 — CC BY 4.0
- "Contains OS data © Crown copyright and database right 2026"
- MET Norway / yr.no — CC BY 4.0, identifying User-Agent required
- OpenStreetMap contributors (tors, and any OSM-derived routing)

## Costs

~£91/year: Apple Developer £79 + domain £12. Everything else on free tiers.
Break-even at £6.99 (net £5.94) = 16 sales/year.
