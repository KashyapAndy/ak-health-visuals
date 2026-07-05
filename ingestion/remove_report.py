"""
Remove a single report (and its cascaded biomarkers/vitals rows) from
data/health.db by source_file. load.py only inserts — it has no
concept of deletion — so this is the counterpart for undoing a
duplicate once find_duplicates.py has flagged it and you've decided
which source to drop.

By default also deletes the matching data/processed/<PERSON>/<file>.json,
since load.py's idempotency check is DB-based: if the JSON is left in
place, the next `load.py` run will just re-insert it. The raw source
file in raw_pdfs/<PERSON>/ is left alone — remove it yourself if you
don't want a future rename.py/extract.py rerun to regenerate the JSON.

Usage:
    python ingestion/remove_report.py --source-file 20190605_LabCorp_RK.pdf --person RK
    python ingestion/remove_report.py --source-file ccda.xml --person RK --keep-json
    python ingestion/remove_report.py --source-file ccda.xml --person RK --yes
"""

import argparse
import sqlite3
from pathlib import Path

from rich.console import Console

console = Console()

ROOT     = Path(__file__).parent.parent
DB_PATH  = ROOT / "data" / "health.db"
PROC_DIR = ROOT / "data" / "processed"


def remove_report(source_file: str, person: str, keep_json: bool, assume_yes: bool):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    report = conn.execute(
        "SELECT id, person_id, report_date, lab_name FROM reports WHERE source_file = ?",
        (source_file,),
    ).fetchone()

    if not report:
        console.print(f"[red]No report found with source_file = {source_file!r}[/red]")
        conn.close()
        return

    report_id = report["id"]
    n_bm = conn.execute("SELECT COUNT(*) FROM biomarkers WHERE report_id = ?", (report_id,)).fetchone()[0]
    n_vitals = conn.execute("SELECT COUNT(*) FROM vitals WHERE report_id = ?", (report_id,)).fetchone()[0]

    console.print(
        f"[yellow]About to delete:[/yellow] report id={report_id} "
        f"({report['person_id']}, {report['report_date']}, {report['lab_name']}) "
        f"— {n_bm} biomarker rows, {n_vitals} vitals row(s)"
    )

    if not assume_yes:
        confirm = input("Proceed? [y/N] ").strip().lower()
        if confirm != "y":
            console.print("[dim]Cancelled — nothing was changed.[/dim]")
            conn.close()
            return

    conn.execute("DELETE FROM biomarkers WHERE report_id = ?", (report_id,))
    conn.execute("DELETE FROM vitals WHERE report_id = ?", (report_id,))
    conn.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    conn.commit()
    conn.close()
    console.print(f"[green]Deleted report {report_id} ({source_file}) from the database.[/green]")

    json_path = PROC_DIR / person / f"{Path(source_file).stem}.json"
    if keep_json:
        console.print(f"[dim]Left processed JSON in place: {json_path}[/dim]")
    elif json_path.exists():
        json_path.unlink()
        console.print(f"[green]Also deleted processed JSON: {json_path}[/green]")
    else:
        console.print(f"[dim]No processed JSON found at {json_path} (nothing to delete there).[/dim]")

    console.print(
        "\n[dim]Note: the raw source file in raw_pdfs/<PERSON>/ was left untouched. "
        "Remove or archive it yourself if you don't want a future rename.py/extract.py "
        "rerun to regenerate this JSON.[/dim]"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete a report from the DB by source_file")
    parser.add_argument("--source-file", required=True, help="Exact source_file value as stored in the reports table")
    parser.add_argument("--person", required=True, choices=["AK", "RK"], help="Used to locate the processed JSON to also delete")
    parser.add_argument("--keep-json", action="store_true", help="Don't delete the processed JSON, only the DB rows")
    parser.add_argument("--yes", action="store_true", help="Skip the confirmation prompt")
    args = parser.parse_args()
    remove_report(args.source_file, args.person, args.keep_json, args.yes)
