# AK Health Visuals

A personal health dashboard tracking 15 years of pathology results, CBC panels, vitals, and metabolic markers — built to turn a drawer full of PDF lab reports into an interactive, longitudinal health record.

> **PHI notice** — `raw_pdfs/`, `data/health.db`, and `data/processed/` are gitignored and never committed. The repo contains only code and schema.

---

## Screenshot

<img width="2217" height="1236" alt="image" src="https://github.com/user-attachments/assets/09d7f836-da7c-4fd8-b1cc-7da9e66a3da9" />


---

## What it does

- Ingests lab PDFs using the Claude API (claude-opus-4-8) — extracts dates, biomarker names, values, units, reference ranges, and flags
- Stores everything in a local SQLite database with a canonical biomarker registry for name normalization across labs and years
- Serves a FastAPI backend with endpoints for categories, time-series, latest values, vitals, and computed ratios
- Renders a Next.js dashboard with a "Warm Olive" design theme: horizontal tab navigation, inline expandable charts per biomarker, a 15-year narrative overview, and a vertical milestone timeline

---

## Stack

| Layer | Technology |
|---|---|
| PDF ingestion | Python + Anthropic Claude API (claude-opus-4-8) |
| Database | SQLite (`data/health.db`) |
| Backend | FastAPI + uvicorn |
| Frontend | Next.js 16 (App Router, Turbopack) + Recharts |
| Fonts | Satoshi (Fontshare) + DM Mono (Google Fonts) |

---

## Folder layout

```
ak-health-visuals/
├── ingestion/
│   ├── rename.py          # renames PDFs to YYYYMMDD_Provider_AK.pdf
│   ├── extract.py         # Claude API → structured JSON
│   ├── load.py            # JSON → SQLite
│   └── biomarker_map.py   # canonical registry (name normalization)
├── backend/
│   └── main.py            # FastAPI app — categories, biomarker, vitals, latest
├── frontend/
│   ├── app/
│   │   ├── layout.tsx     # Satoshi font, DM Mono, global styles
│   │   └── page.tsx       # Dashboard — Overview, category tabs, Vitals
│   ├── components/
│   │   ├── BiomarkerChart.tsx   # Area+Line chart with ref bands & event annotations
│   │   └── VitalsPanel.tsx      # Weight, BMI, BP, pulse area charts
│   └── lib/
│       ├── api.ts               # Typed API client
│       └── biomarker-info.ts    # Static blurbs for 30+ biomarkers
├── data/
│   └── schema.sql         # SQLite schema (committed; DB itself is gitignored)
├── update.ps1             # End-to-end: extract → load → done
└── CLAUDE.md              # Full architecture spec for AI-assisted development
```

---

## Running locally

### Prerequisites
- Python 3.11+
- Node.js 20+
- An Anthropic API key (for ingestion only)

### 1 — Install dependencies

```powershell
# Backend
pip install fastapi uvicorn anthropic pypdf2

# Frontend
cd frontend
npm install
```

### 2 — Set up the database

```powershell
# Create the schema
sqlite3 data/health.db < data/schema.sql
```

### 3 — Ingest PDFs

Drop renamed PDFs into `raw_pdfs/AK/` following the naming convention `YYYYMMDD_Provider_AK.pdf`, then:

```powershell
.\update.ps1
```

Or run steps individually:
```powershell
python ingestion/extract.py   # Claude API → JSON in data/processed/AK/
python ingestion/load.py      # JSON → SQLite
```

### 4 — Start the servers

**Backend** (port 8000):
```powershell
uvicorn backend.main:app --reload
```

**Frontend** (port 3000):
```powershell
cd frontend
npm run dev
```

Open **http://localhost:3000**

---

## API endpoints

| Endpoint | Description |
|---|---|
| `GET /api/persons` | List persons in the DB |
| `GET /api/categories?person=AK` | Biomarker categories + names |
| `GET /api/biomarker?name=LDL Cholesterol&person=AK` | Full time-series for one marker |
| `GET /api/latest?person=AK` | Latest value + delta for every marker |
| `GET /api/vitals?person=AK` | Weight, BMI, BP, pulse over time |

> Biomarker names with `/` (e.g. `A/G Ratio`) must be query-param encoded — path params break at the ASGI layer.

### Computed ratios

The following ratios are derived on the fly from stored constituents — not read from the DB:

| Ratio | Formula |
|---|---|
| A/G Ratio | Albumin ÷ (Total Protein − Albumin) |
| HDL/LDL Ratio | HDL ÷ LDL |
| LDL/HDL Ratio | LDL ÷ HDL |
| Cholesterol/HDL Ratio | stored directly |

---

## Dashboard features

- **Overview tab** — 5-year health narrative, key milestone timeline, dynamic normal/flagged/low counts, flagged value cards, full latest-values grid
- **Category tabs** — CBC, Metabolic, Lipids, Thyroid, Vitamins, and more; click any marker to expand an inline chart
- **Biomarker charts** — 15-year area+line chart, reference band shading, event annotations (e.g. Thyroidectomy Apr 2025), abnormal readings highlighted in red/amber, info blurb panel below
- **Vitals tab** — weight, BMI, blood pressure, pulse with mini area charts
- **Filtering** — text-only readings (Negative, Yellow, etc.) excluded; bad-data panels excluded by date; minimum 2 reports required to surface a marker

---

## Design system

All visual properties use inline styles (not Tailwind classes) for reliability with Next.js Turbopack + Tailwind v4.

**Palette — "Warm Olive"**
| Token | Value |
|---|---|
| Background | `#FAF7F2` |
| Card | `#FFFFFF` |
| Surface | `#F0EBE0` |
| Primary (olive) | `#4D7C0F` |
| High flag (red) | `#DC2626` |
| Low flag (amber) | `#B45309` |
| Text | `#1C1917` |
| Muted | `#78716C` |

**Fonts**: Satoshi (headings/body) · DM Mono (data labels, values, timestamps)

---

## PDF naming convention

```
YYYYMMDD_Provider_AK.pdf
```

Examples:
```
20240315_LabCorp_AK.pdf
20250601_QuestDiagnostics_AK.pdf
```

---

## Gitignore / PHI policy

The following are **never committed**:
```
raw_pdfs/          ← source PDFs
data/health.db     ← SQLite database
data/processed/    ← extracted JSON
.env               ← API keys
```

Only `data/schema.sql` is committed.
