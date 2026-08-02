---
name: ingest-labs
description: Ingest new lab results, imaging reports, vaccine records, or other health documents dropped into raw_pdfs/ for AK or RK, and get them showing correctly on the Kashyap House, MD dashboard. Use whenever the user says they've added new PDFs/results/files to ingest, or asks to update/refresh someone's health data.
---

# Ingest Labs — Kashyap House, MD pipeline

A runbook for safely getting new health documents from `raw_pdfs/` into the
dashboard. The underlying scripts (`ingestion/*.py`) don't change — this is
the *procedure* for using them correctly, plus the gotchas that have
actually bitten this pipeline before. Read the project's `CLAUDE.md` first
for architecture; this skill is about execution discipline.

## 0. Find the new files

New files often land in `raw_pdfs/` **root**, not the correct `AK/`/`RK/`
subfolder — always check both:

```bash
ls raw_pdfs/
ls raw_pdfs/AK/ | grep -v archive
ls raw_pdfs/RK/ | grep -v archive
```

Move anything new into the right person folder before doing anything else.

## 1. Read the content before deciding how to process it

Don't assume every PDF fits the standard single-report pipeline. Extract
the raw text first (`pdfplumber`, or `openpyxl`/`pandas` for spreadsheets)
and classify it:

- **Single visit, one date, one panel** → standard pipeline (`rename.py` →
  `extract.py` → `load.py`).
- **Multi-date cumulative table** (a CCD/CDA export, a "Result Trends"
  portal printout, anything with one column per visit date) → **do not**
  run this through `extract.py` as-is. Its one-report-per-file schema plus
  the ~8192 `max_tokens` cap will silently keep only one date and drop the
  rest. Write or reuse a dedicated multi-report parser instead — see
  `ingestion/parse_ccd_xml.py` (XML, parsed locally with `xml.etree`, no
  Claude call) and `ingestion/parse_trend_pdf.py` (rendered PDF table,
  sent to Claude with a custom `{"reports": [...]}` schema because a
  table's column alignment can't be reliably reconstructed from
  `pdfplumber`'s linearized text — verify a sample against a rendered page
  image before trusting it, especially where reference ranges shift
  mid-table).
- **Non-lab structured records** (vaccine/immunization history, etc.) →
  check whether a table/schema already exists for this data type before
  assuming it fits `reports`/`biomarkers`. See `ingestion/parse_vaccines.py`
  for a precedent (new `vaccinations` table, parsed directly with no
  Claude call since both source formats seen so far — a bulleted PDF, a
  spreadsheet — are already structured).

## 2. Renaming — the sharpest edge in this pipeline

`rename.py --person X` processes **every** file in that person's folder
every time, not just new ones. Two failure modes to know about:

- **It will corrupt multi-date aggregate files.** If `ccda.xml` (or any
  other special aggregate file) is sitting in the folder without a
  matching `data/processed/<PERSON>/<name>.json`, running `rename.py` on
  the whole folder will try to Claude-infer a *single* date/provider for
  it, silently destroying its identity (this has happened — it was
  renamed to `20251031_LabCorp_RK.xml` with a made-up date). **Move any
  such file out of the folder before running `rename.py` on the rest**,
  then move it back.
- **It mangles multi-word provider names.** `normalise_provider()` maps
  known providers via a dict (safe), but falls back to `.title()` for
  anything else — which collapses camelCase/multi-word names with no
  separator (`QuestDiagnostics` → `Questdiagnostics`, `HealthSummary` →
  `Healthsummary`). This only bites files that get **re-processed**
  through the pattern-matching path (i.e. re-running on already-correctly
  named files), not fresh Claude-inferred ones. After any whole-folder
  `rename.py` run, diff the before/after filenames and revert any
  unintended casing changes to previously-correct names.

**For a single new file**, it's usually safer and cheaper to rename it
yourself: read the content, note the collected date and provider, and
`mv raw_pdfs/<PERSON>/<original> raw_pdfs/<PERSON>/YYYYMMDD_Provider_<PERSON>.pdf`
directly (copy the original into `archive/` first to match convention).
This skips a Claude call and every risk above.

## 3. Extract

```bash
python ingestion/extract.py --person X --file <exact_filename>
```

Always pass `--file` for a targeted run. Running without it processes the
whole folder — if `ccda.xml` (or similar) has no matching JSON, it'll
attempt (and fail) to re-extract it, wasting an API call. Harmless but
avoidable.

For multi-date/non-standard files, use the dedicated parser from step 1
instead (`--dry-run` first if it supports one).

## 4. Check normalization before trusting "this is a new test"

After extraction, look at what didn't normalize to an existing canonical
name (`biomarker_map.normalize_name` falls back to `raw.strip().title()`
on no match). A name that *looks* new is very often just this lab's
phrasing not matching an existing alias — not a genuinely new test type.
Compare against `ingestion/biomarker_map.py`'s `REGISTRY`. Real examples
from this project: `"Lymphocytes Automated"` → should be `Lymphocytes %`,
`"eGFR 2021 CKD-EPI"` → should be `eGFR`, `"Vitamin D, 25 OH"` → should be
`Vitamin D`. Add the missing alias rather than letting it fall through.

Two specific classes of bug to actively check for, because they've both
happened and are easy to miss by eyeballing values alone:

- **Unit-scale bugs.** Don't assume a unit needs the same multiplier as a
  similar-looking one. `THDS/CMM` and `MILL/CMM` already spell out their
  own scale (thousand/million per cubic mm) — same scale as this
  project's canonical `10³/µL`/`10⁶/µL`, so multiplier `1`. They are
  **not** the same as a bare `/cumm` raw count, which does need
  `×0.001`/`×0.000001`. Confusing these silently divided a real WBC of 9.9
  down to 0.0099. When adding a new `unit_conversions` key, compute the
  converted value by hand and sanity-check it against the number printed
  on the source document.
- **Name-collision bugs.** The same plain-English phrase can name two
  clinically different tests in different panel contexts. `"White Blood
  Cells"`/`"Red Blood Cells"` means the CBC blood count in one panel and a
  urine-microscopic per-high-power-field finding in another — aliasing
  both to the same canonical marker silently merges unrelated data. If a
  registry entry's aliases could plausibly apply to more than one panel
  type, give the other context (e.g. urinalysis) its own canonical entry
  instead (see `Urine WBC`/`Urine RBC`).

If the user asked to skip tests that were never previously recorded for
that person: compare each new biomarker's canonical name against
`SELECT DISTINCT name FROM biomarkers b JOIN reports r ON ... WHERE
r.person_id = ?` for the existing DB, and drop anything not already
present — **but only after** the normalization check above, so a real
alias gap doesn't get silently discarded as "new." Report what was
skipped. Note: filtering the processed JSON in place is destructive — if
a normalization fix is needed afterward, delete the JSON and re-extract
rather than trying to recover already-trimmed entries.

## 5. Load

```bash
python ingestion/load.py --person X
```

Idempotent by `source_file`, safe to re-run. **One real trap**: if raw
files were renamed in an *earlier* session after already being loaded
under their old filename, re-running `extract.py` creates fresh JSONs
under the new filename that `load.py` will insert as if they were new
reports — silently doubling the data (this happened: 43 already-loaded
reports were about to be re-inserted). Before loading anything from a
bulk/unexpected batch of "new" JSONs, cross-check each `report_date`
against existing DB rows for that person; if the date is already present
under a *different* `source_file`, it's almost certainly a re-extraction
duplicate, not new data — delete the duplicate JSON instead of loading it.

## 6. Check for duplicate overlaps

```bash
python ingestion/find_duplicates.py --person X
```

Read-only. Don't assume a flagged pair is a clean duplicate to resolve by
dropping one side — inspect the actual source (e.g. a CCD's lab-location
column) to see whether it's a true full duplicate (same draw, re-imported)
or a partial one (some shared external results plus other genuinely
unique in-house results). Only remove confirmed full duplicates, and only
with the user's explicit go-ahead — this tool never deletes anything
itself.

## 7. Start/verify the dashboard

```bash
uvicorn backend.main:app --port 8000     # from repo root
npm run dev                              # from frontend/
```

Before starting, check for and kill stray duplicate processes from
earlier sessions — filter precisely
(`Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object
{ $_.CommandLine -like '*uvicorn*' }`), not a broad `CommandLine LIKE
'%uvicorn%'` filter, which also matches your own diagnostic command and
its wrapper shells.

**Verify by actually looking, not just checking numbers.** Hit
`/api/latest` and `/api/biomarker` for the new data and confirm values,
units, and flags look right — then load the actual chart in a browser
(Playwright is fine for this) and look at it. Pure data checks would have
missed both a WBC/RBC unit-scale bug and a chart line-disconnection bug
that were only obvious on screen.

## 8. Report back

Summarize: what was ingested (dates, panel types), what was skipped and
why, any registry/normalization bugs found and fixed along the way,
updated totals (report count, date range, distinct biomarkers), and
confirm the dashboard is live. Don't commit/push unless asked.
