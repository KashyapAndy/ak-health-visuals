"""
Remove a report identified as a duplicate by find_duplicates.py: deletes its
biomarkers/vitals/report rows from the DB and its processed JSON file.

Does not touch raw_pdfs/ — remove the source PDF/HTML/XML there yourself if
you don't want it re-extracted.

Usage:
    python ingestion/remove_report.py --source-file <name> --person RK
"""

import argparse
import json
import sqlite3
from pathlib import Path

from rich.console import Console

console = Console()

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "data" / "health.db"
PROC_DIR = ROOT / "data" / "processed"


def find_processed_json(person: str, source_file: str) -> Path | None:
    person_dir = PROC_DIR / person
    if not person_dir.exists():
        return None
    for jf in person_dir.glob("*.json"):
        data = json.loads(jf.read_text())
        if data.get("source_file") == source_file:
            return jf
    return None


def remove_report(source_file: str, person: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    report = conn.execute(
        "SELECT id, report_date, lab_name, report_type FROM reports WHERE source_file = ? AND person_id = ?",
        (source_file, person),
    ).fetchone()
    if report is None:
        console.print(f"[red]No report found for source_file={source_file!r}, person={person}[/red]")
        conn.close()
        return

    report_id = report["id"]
    bm_count = conn.execute(
        "SELECT COUNT(*) FROM biomarkers WHERE report_id = ?", (report_id,)
    ).fetchone()[0]
    vitals_count = conn.execute(
        "SELECT COUNT(*) FROM vitals WHERE report_id = ?", (report_id,)
    ).fetchone()[0]
    json_path = find_processed_json(person, source_file)

    console.print(f"[yellow]Report:[/yellow] {source_file} — {report['report_date']} — {report['lab_name']} ({report['report_type']})")
    console.print(f"  {bm_count} biomarker rows, {vitals_count} vitals rows")
    console.print(f"  Processed JSON: {json_path if json_path else '[not found]'}")

    confirm = input("Delete this report from the DB and its processed JSON? [y/N] ").strip().lower()
    if confirm != "y":
        console.print("[dim]Aborted — nothing changed.[/dim]")
        conn.close()
        return

    conn.execute("DELETE FROM biomarkers WHERE report_id = ?", (report_id,))
    conn.execute("DELETE FROM vitals WHERE report_id = ?", (report_id,))
    conn.execute("DELETE FROM reports WHERE id = ?", (report_id,))
    conn.commit()
    conn.close()

    if json_path:
        json_path.unlink()

    console.print(f"[green]Removed report {source_file} ({bm_count} biomarkers, {vitals_count} vitals rows) and its processed JSON.[/green]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove a duplicate report's DB rows and processed JSON")
    parser.add_argument("--source-file", required=True, help="source_file value as stored in the reports table")
    parser.add_argument("--person", required=True, choices=["AK", "RK"])
    args = parser.parse_args()
    remove_report(args.source_file, args.person)
