# Health Dashboard — CLAUDE.md

## Project purpose
Personal health dashboard for Anirudh Kashyap (AK).
Tracks pathology results, CBC, vitals over 15 years via PDF ingestion.
RK (wife) data exists in the DB but the dashboard is AK-only — do not add a person switcher.

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
- `PERSON = "AK"` hardcoded — no person switcher
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

## Medical context (AK)

- **15-year record**: 2010 – present, 58+ quantitative biomarkers, 8+ lab visits
- **Thyroidectomy**: April 2025, total, for papillary thyroid carcinoma (PTC). Now on lifelong levothyroxine.
- **Post-surgical monitoring**: TSH (suppressed target), Thyroglobulin (should be undetectable), Free T4
- **Active flags**: LDL elevated, HDL chronically low, Triglycerides high, Cholesterol/HDL ratio >5.0 — cardiometabolic pattern
- **Positive trend**: Vitamin D and B12 recovered to normal range after supplementation
- **Excluded panel**: 2018-11 Sunrise Medical — data quality issue, removed from all trending
