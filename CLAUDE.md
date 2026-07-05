# Health Dashboard — CLAUDE.md

## Project purpose
Personal health dashboard for Anirudh Kashyap (AK) and Rashmi Kashyap (RK, wife).
Tracks pathology results, CBC, vitals over 15 years via PDF ingestion.
A `PersonSwitcher` in the header toggles between AK and RK; backend endpoints
already accept a `person` query param (`AK`/`RK`) for every route.

## Stack
- **Ingestion**: Python + Claude API (claude-opus-4-8) for PDF parsing
- **Database**: SQLite at `data/health.db` (local only, never committed)
- **Backend**: FastAPI + uvicorn on port 8000
- **Frontend**: Next.js 16 (App Router, Turbopack) + Recharts, port 3000

## Naming convention
`YYYYMMDD_Provider_<PERSON>.pdf`  where PERSON is AK or RK.

## Folder layout
```
raw_pdfs/AK/          ← AK's renamed PDFs (gitignored)
raw_pdfs/AK/archive/  ← originals before rename
raw_pdfs/RK/          ← RK's renamed PDFs (gitignored)
data/health.db        ← SQLite DB (gitignored)
data/processed/AK/    ← extracted JSON (gitignored)
data/processed/RK/
data/schema.sql       ← committed
ingestion/            ← rename.py, extract.py, load.py
backend/main.py       ← FastAPI app
frontend/             ← Next.js app
frontend/app/         ← App Router pages
frontend/components/  ← BiomarkerChart, VitalsPanel, LatestCard
frontend/lib/api.ts   ← typed API client
frontend/lib/biomarker-info.ts  ← static blurbs for 30+ markers
```

## Drop-in workflow
1. Drop new PDF into `raw_pdfs/AK/`
2. Run `.\update.ps1`
3. Dashboard auto-refreshes at http://localhost:3000

## PHI rules
**Never commit**: raw_pdfs/, data/health.db, data/processed/, .env
These are in .gitignore. Always verify before pushing.

---

## Frontend architecture

### Design system — "Warm Olive" theme
All visual properties use **inline styles**, not Tailwind classes (Tailwind v4 `@theme {}` tokens are defined in globals.css but unreliable in Turbopack; inline styles are the source of truth).

Color constants (defined at top of every component file as `const C = {...}`):
```ts
bg: "#FAF7F2"        // page background
surface: "#F0EBE0"   // subtle section bg
card: "#FFFFFF"
border: "rgba(77,124,15,0.11)"
borderHover: "rgba(77,124,15,0.28)"
olive: "#4D7C0F"     // primary accent
oliveLight: "#65A30D"
amber: "#B45309"     // warnings / low flags
green: "#15803D"
red: "#DC2626"       // high flags
text: "#1C1917"
muted: "#78716C"
ghost: "#A8A099"
```

Font constants:
```ts
const SANS = "'Satoshi', system-ui, sans-serif";
const MONO = "var(--font-dm-mono, 'DM Mono', monospace)";
```

Satoshi is loaded via `<link>` tag in layout.tsx (Fontshare, not Google Fonts — cannot use next/font).
DM Mono is loaded via `next/font/google` with CSS variable `--font-dm-mono`.

### Page layout (app/page.tsx)
- `person` is component state (`useState<Person>("AK")`), toggled via `PersonSwitcher` in the header. Switching person refetches categories/latest/vitals and resets the active tab and selected biomarker.
- The "5-Year Narrative" overview section (prose + milestone timeline) is hardcoded AK medical history — gated behind `person === "AK"`. RK's overview shows stats bar, flagged grid, and latest values only, until RK-specific narrative copy is written.
- Sticky header with blur backdrop, horizontal tab bar
- Tabs: Overview + one per category + Vitals
- Switching tabs resets selected biomarker and chart
- `isQuantitative(v)` filter: `v.value !== null` — removes text-only readings (Yellow, Negative, etc.)
- Clicking a StatCard toggles the inline chart below the grid (toggle same = collapse)
- `openBiomarker(name, tab?)` handles fetch + tab switch atomically

### Overview tab sections (in order)
1. **5-Year Narrative** — prose card + vertical milestone timeline + dynamic trend chips (normal/high/low counts from live data)
2. **Stats bar** — biomarkers tracked, flagged count, categories
3. **Flagged values grid** — StatCards for all flagged markers
4. **Inline chart** — expands below flagged grid when a marker is selected
5. **Latest values grid** — all 58+ quantitative markers as StatCards

### BiomarkerChart.tsx
- ComposedChart with Area (gradient fill) + Line
- **`connectNulls={true}`** on both Area and Line — critical, do not change. Event date injection adds null points; false breaks the line.
- Event annotations: `EVENTS` array with `{ date: "YYYY-MM", label, color }`. Currently: Thyroidectomy (PTC) at 2025-04.
- Event date is injected as a null-value placeholder into `chartData` so the categorical XAxis always has a tick for it — this is what makes `ReferenceLine x={ev.date}` render.
- `relevantEvents` filter: only show if event date falls within the chart's data range.
- YAxis autoscale: pad ±22% beyond data + ref range bounds; yMin floored at 0.
- Info blurb panel below chart: 3-column grid (What it measures / Good ranges / How to improve) sourced from `getBiomarkerInfo(name)`.

### biomarker-info.ts
- `INFO` object with 30+ entries. **The closing `};` must come after ALL entries** — the ratios (A/G Ratio, HDL/LDL Ratio, LDL/HDL Ratio, Cholesterol/HDL Ratio) are inside the object, not after it.
- `getBiomarkerInfo(name)` does case-insensitive exact match then partial match fallback.
- When adding new entries, add them inside the `INFO = { ... }` block before its closing `};`.

---

## Backend architecture (backend/main.py)

### Data filters
```python
EXCLUDED_DATES = ("2018-11",)          # Sunrise Medical — bad data
EXCLUDED_CATEGORIES = {"Drug Screen"}
MIN_REPORTS = 2                        # biomarker must appear in ≥2 reports
```

### Computed ratios
Ratios not stored in DB are computed on the fly:
```python
COMPUTED_RATIOS = {
    "A/G Ratio":     ("Albumin", "Globulin", "", 1.1, 2.5),
    "HDL/LDL Ratio": ("HDL Cholesterol", "LDL Cholesterol", "", 0.3, None),
    "LDL/HDL Ratio": ("LDL Cholesterol", "HDL Cholesterol", "", None, 3.5),
}
DERIVED_MARKERS = {
    "Globulin": ("Total Protein", "Albumin", "subtract"),  # not stored directly
}
```

### Critical: biomarker endpoint uses query param, not path param
Names like "A/G Ratio" contain `/` which breaks FastAPI path routing even with `{name:path}` (ASGI rejects URL-encoded slashes at transport layer).

```python
@app.get("/api/biomarker")
def biomarker_history(name: str = Query(...), person: str = Query("AK")):
```

Frontend api.ts must match:
```ts
biomarker: (name: string, person: Person) =>
  get<BiomarkerHistory>(`/api/biomarker?name=${encodeURIComponent(name)}&person=${person}`),
```

### Category ordering
```python
CATEGORY_ORDER = [
    "CBC", "CBC Differential", "Metabolic", "Lipids",
    "Thyroid", "Vitamins", "Iron Studies", "Hormones",
    "Urinalysis", "Infectious Disease", "Pulmonary", "Other",
]
```

---

## Known gotchas

| Issue | Fix |
|---|---|
| Tailwind v4 classes not applying | Use inline styles. `tailwind.config.ts` is ignored in v4; tokens in `@theme {}` work in CSS but are unreliable via className in Turbopack. |
| `ReferenceLine x=` not rendering | The x value must exactly match a data point's date string. Inject a null placeholder into chartData for the event month. |
| Line breaks when event date injected | `connectNulls={true}` on Area and Line. Never set to false. |
| `defs`/`linearGradient`/`stop` import error | These are SVG JSX elements, not Recharts exports. Remove from recharts import; use as plain JSX inside the chart. |
| Biomarker endpoint 404 for names with `/` | Use query param (`?name=...`), not path param. |
| Ratio charts empty | Ratios must be computed from constituents via `COMPUTED_RATIOS`. Globulin = Total Protein − Albumin via `DERIVED_MARKERS`. |
| Syntax error in biomarker-info.ts | All entries must be inside `const INFO = { ... }` before its closing `};`. Do not add entries after the closing brace. |
| Uvicorn not picking up changes | Start with `--reload` flag. |
| Font not loading | Satoshi requires a `<link>` tag to Fontshare in layout.tsx `<head>`. Cannot use `next/font` for non-Google fonts. |

---

## Ingestion pipeline & ETL

The pipeline is **four scripts** run in order. All are idempotent — safe to re-run.

```
ingestion/
  rename.py          # Phase 1 — rename raw PDFs/HTML to YYYYMMDD_Provider_AK.<ext>
  extract.py         # Phase 2 — Claude API → structured JSON
  renormalize.py     # Phase 2b — re-apply biomarker_map without re-calling API
  load.py            # Phase 3 — JSON → SQLite
  biomarker_map.py   # Registry — canonical names, units, conversions, ref ranges
  doc_utils.py        # Shared helper — builds Claude content blocks for PDF or HTML source files
  find_duplicates.py  # Dev utility — read-only report flagging likely duplicate reports across sources
  debug_noise.py      # Dev utility — inspect unrecognized biomarker names
```

### Phase 1 — rename.py
Renames PDFs **and HTML files** dropped into `raw_pdfs/AK/` or `raw_pdfs/RK/` to the canonical `YYYYMMDD_Provider_PERSON.<ext>` format (original extension preserved). Originals are moved to `raw_pdfs/<PERSON>/archive/`.

### Phase 2 — extract.py
- Sends each file to `claude-opus-4-8`: PDFs as base64 document blocks, HTML/HTM as raw text (there's no "document" media type for HTML in the Messages API — Claude reads inline markup fine)
- The prompt instructs Claude to return raw names and raw units **exactly as printed** — normalization is handled by our code, not the model
- After extraction, immediately applies `normalize_name()`, `normalize_unit()`, and `get_fallback_refs()` from `biomarker_map.py`
- Output saved to `data/processed/<PERSON>/<filename>.json`
- **Idempotent**: skips files that already have a `.json` output

### find_duplicates.py — cross-source duplicate detection
If a provider portal export (e.g. HTML) might be re-reporting a blood draw already captured by a PDF from another lab, run `python ingestion/find_duplicates.py --person RK` after `extract.py`. It compares `report_date` and biomarker value overlap across all processed JSONs for a person and prints a table of likely-duplicate pairs. It's **read-only** — it never deletes anything; you decide which source file (if any) to drop before running `load.py`.

Key extraction rules baked into the prompt:
- `report_date`: specimen collection date preferred over report date
- Numeric results → `value` field; qualitative results (Negative, Positive, Trace, 1+) → `text_value` field, `value = null`
- eGFR `>60` reference → `ref_low=60, ref_high=null`
- Vitals converted to US units (lbs, inches, °F) by the model

### Phase 2b — renormalize.py
Re-applies the latest `biomarker_map.py` to all existing JSONs **without** calling the Claude API again. Use this whenever the registry is updated (new aliases, unit conversions, ref ranges).

Additional logic beyond basic normalization:
- **% vs Abs disambiguation**: if a differential marker (e.g. Neutrophils %) has an absolute-count unit (k/uL, 10³/µL), it is renamed to the Abs variant (Neutrophils Abs)
- **Deduplication**: within a single report JSON, keeps only the first occurrence of each canonical name — handles labs that print eGFR twice (non-African-Am and African-Am rows)
- **Unit backfill**: if unit is still empty after normalization, fills from the registry's `canonical_unit`

### Phase 3 — load.py
- Reads all JSONs from `data/processed/<PERSON>/` and inserts into SQLite
- **Idempotent**: checks `source_file` column in `reports` table; skips if already present
- Inserts: one `reports` row, N `biomarkers` rows, one `vitals` row (if any vitals present)

---

## biomarker_map.py — canonical registry

The registry is the single source of truth for all name and unit normalization. Every biomarker has:
- `canonical_name` — display name used in DB and dashboard
- `canonical_unit` — the one unit stored in DB
- `unit_conversions` — dict of `raw_unit_alias → multiplier`. Conversion: `stored = raw × multiplier`
- `name_aliases` — list of raw strings Claude might return (case-insensitive, noise-stripped)
- `ref_low` / `ref_high` — fallback reference range if PDF didn't include one
- `category` — dashboard grouping

**Noise stripping** before alias lookup (via `_NOISE` regex):
Strips words: `calculated`, `calc`, `serum`, `blood`, `level`, `levels` — so "Glucose, Serum" and "Glucose" both resolve to the same entry.

### Unit conversion reference (key biomarkers)

| Biomarker | Canonical Unit | Notable conversions |
|---|---|---|
| WBC, Platelets | 10³/µL | `/cumm` × 0.001, `/mm³` × 0.001 |
| RBC | 10⁶/µL | `/cumm` × 0.000001 |
| Hemoglobin | g/dL | `g/L` × 0.1, `mmol/L` × 1.6113 |
| Hematocrit | % | `L/L` × 100 |
| Glucose | mg/dL | `mmol/L` × 18.018 |
| BUN | mg/dL | `mmol/L` × 2.8 |
| Creatinine | mg/dL | `µmol/L` × 0.01131 |
| Calcium | mg/dL | `mmol/L` × 4.008 |
| Total Cholesterol, LDL, HDL | mg/dL | `mmol/L` × 38.67 |
| Triglycerides | mg/dL | `mmol/L` × 88.57 |
| TSH | mIU/L | `µIU/mL` × 1 (same scale) |
| Free T4 | ng/dL | `pmol/L` × 0.07752 |
| Vitamin D | ng/mL | `nmol/L` × 0.4006 |
| Vitamin B12 | pg/mL | `pmol/L` × 1.355 |
| Iron, TIBC | µg/dL | `µmol/L` × 5.585 |
| CRP | mg/L | `mg/dL` × 10 |
| HbA1c | % | `mmol/mol` × 0.09148 (IFCC→NGSP) |
| Testosterone | ng/dL | `nmol/L` × 28.84 |
| Cortisol | µg/dL | `nmol/L` × 0.03625 |

### Adding a new biomarker to the registry

1. Add a `Biomarker(...)` entry to `REGISTRY` in `biomarker_map.py`
2. Include all raw name variants you've seen across labs as `name_aliases`
3. Include all raw unit variants as `unit_conversions` with their multipliers
4. Set `ref_low` / `ref_high` as a fallback (PDF-provided ranges take precedence at load time)
5. Assign the correct `category` (must match `CATEGORY_ORDER` in `backend/main.py` for proper tab ordering)
6. Run `python ingestion/renormalize.py` to apply to existing JSONs without re-calling the API
7. Run `python ingestion/load.py` to reload into SQLite

### Categories and dashboard tab order

```python
CATEGORY_ORDER = [
    "CBC", "CBC Differential", "Metabolic", "Lipids",
    "Thyroid", "Vitamins", "Iron Studies", "Hormones",
    "Urinalysis", "Infectious Disease", "Pulmonary", "Other",
]
```
Categories not in this list appear after in alphabetical order. `Drug Screen` is explicitly excluded from the dashboard (`EXCLUDED_CATEGORIES` in `backend/main.py`).

### Data quality decisions recorded

| Decision | Detail |
|---|---|
| Exclude 2018-11 | Sunrise Medical panel — unreliable data, all markers excluded from trending |
| MIN_REPORTS = 2 | A biomarker must appear in ≥2 reports to show in dashboard — filters one-off noise |
| Qualitative filter | `isQuantitative(v) = v.value !== null` — removes text-only readings (Yellow, Negative, Trace) from dashboard views |
| eGFR dedup | Two eGFR rows per report (non-African-Am / African-Am) — renormalize.py keeps first occurrence only |
| % vs Abs CBC | Differential markers reported in absolute-count units are renamed to Abs variant to avoid double-counting |

---

## Medical context (AK)

- **15-year record**: 2010 – present, 58+ quantitative biomarkers, 8+ lab visits
- **Thyroidectomy**: April 2025, total, for papillary thyroid carcinoma (PTC). Now on lifelong levothyroxine.
- **Post-surgical monitoring**: TSH (suppressed target), Thyroglobulin (should be undetectable), Free T4
- **Active flags**: LDL elevated, HDL chronically low, Triglycerides high, Cholesterol/HDL ratio >5.0 — cardiometabolic pattern
- **Positive trend**: Vitamin D and B12 recovered to normal range after supplementation
- **Excluded panel**: 2018-11 Sunrise Medical — data quality issue, removed from all trending
