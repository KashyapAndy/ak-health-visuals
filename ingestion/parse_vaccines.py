"""
Parse vaccination/immunization records into the `vaccinations` table.

Both source formats seen so far are already structured (a bulleted list PDF
for AK, a spreadsheet for RK) so this parses them directly -- no Claude API
call needed, unlike the lab-report pipeline.

Usage:
    python ingestion/parse_vaccines.py --file AK_Vaccination_History.pdf --person AK
    python ingestion/parse_vaccines.py --file "Rashmi Immunization Records.xlsx" --person RK
    python ingestion/parse_vaccines.py --file ... --person AK --dry-run
"""

import argparse
import re
import sqlite3
from datetime import datetime
from pathlib import Path

import pdfplumber
import openpyxl
from rich.console import Console

console = Console()

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "raw_pdfs"
DB_PATH = ROOT / "data" / "health.db"
SCHEMA = ROOT / "data" / "schema.sql"

_DATE_LINE_RE = re.compile(
    r"^\W*([A-Z][a-z]+ \d{1,2},\s*\d{4})\s+(.*)$"
)


def _parse_pdf(path: Path) -> list[dict]:
    """Bulleted-list format: a vaccine-name line followed by one or more
    '<bullet> Month Day, Year Provider' lines naming that vaccine."""
    records = []
    current_name = None
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.split("\n"):
                line = line.strip()
                if not line or line.lower().startswith("page ") or "vaccination history" in line.lower():
                    continue
                m = _DATE_LINE_RE.match(line)
                if m:
                    if current_name is None:
                        continue
                    date_str, provider = m.groups()
                    date = datetime.strptime(date_str, "%B %d, %Y").strftime("%Y-%m-%d")
                    records.append({"vaccine_name": current_name, "date_given": date, "provider": provider.strip() or None})
                else:
                    # A non-dated line is a new vaccine-name header, unless it's
                    # the intro/disclaimer text at the top of the document.
                    if "available vaccine history" in line.lower() or "self-reported" in line.lower():
                        continue
                    current_name = line
    return records


def _parse_xlsx(path: Path) -> list[dict]:
    """Spreadsheet format: Year | Date | Immunization | Location | Address.
    The Date column is the authoritative date (Year has been seen to be
    inconsistent/mislabeled in this source)."""
    wb = openpyxl.load_workbook(path, data_only=True)
    records = []
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            continue
        header = [str(h).strip().lower() if h else "" for h in rows[0]]
        try:
            date_i = header.index("date")
            name_i = header.index("immunization")
        except ValueError:
            continue
        loc_i = header.index("location") if "location" in header else None
        for row in rows[1:]:
            if not row or row[date_i] is None or row[name_i] is None:
                continue
            date_val = row[date_i]
            date = date_val.strftime("%Y-%m-%d") if hasattr(date_val, "strftime") else str(date_val)
            provider = row[loc_i] if loc_i is not None else None
            records.append({"vaccine_name": str(row[name_i]).strip(), "date_given": date, "provider": provider})
    return records


def process(file_name: str, person: str, dry_run: bool):
    path = RAW_DIR / person / file_name
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        records = _parse_pdf(path)
    elif suffix in (".xlsx", ".xls"):
        records = _parse_xlsx(path)
    else:
        console.print(f"[red]Unsupported file type: {suffix}[/red]")
        return

    console.print(f"Parsed {len(records)} vaccination records from {path.name}")
    for r in records:
        console.print(f"  {r['date_given']}  {r['vaccine_name']:<45} {r['provider'] or ''}")

    if dry_run:
        console.print("[yellow]Dry run — nothing written.[/yellow]")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA.read_text())
    inserted = skipped = 0
    for r in records:
        cur = conn.execute(
            """INSERT OR IGNORE INTO vaccinations (person_id, vaccine_name, date_given, provider, source_file)
               VALUES (?, ?, ?, ?, ?)""",
            (person, r["vaccine_name"], r["date_given"], r["provider"], file_name),
        )
        if cur.rowcount:
            inserted += 1
        else:
            skipped += 1
    conn.commit()
    conn.close()
    console.print(f"[green]{person}:[/green] {inserted} inserted, {skipped} skipped (already recorded)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse vaccination/immunization records into the DB")
    parser.add_argument("--file", required=True, help="Filename in raw_pdfs/<PERSON>/")
    parser.add_argument("--person", required=True, choices=["AK", "RK"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    process(args.file, args.person, args.dry_run)
