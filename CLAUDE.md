# Health Dashboard — CLAUDE.md

## Project purpose
Personal health dashboard for two users (AK = Anirudh Kashyap, RK = wife).
Tracks pathology results, CBC, vitals over 15 years via PDF ingestion.

## Stack
- **Ingestion**: Python + Claude API (claude-opus-4-8) for PDF parsing
- **Database**: SQLite at `data/health.db` (local only, never committed)
- **Backend**: FastAPI + uvicorn
- **Frontend**: React + shadcn/ui + Recharts

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
backend/              ← FastAPI app
frontend/             ← React + shadcn/ui
```

## Drop-in workflow
1. Drop new PDF into `raw_pdfs/AK/` or `raw_pdfs/RK/`
2. Run `.\update.ps1`
3. Dashboard auto-refreshes

## PHI rules
Never commit: raw_pdfs/, data/health.db, data/processed/, .env
These are in .gitignore. Always verify before pushing.
