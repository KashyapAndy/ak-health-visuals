"""
Phase 3: Load extracted JSON into SQLite (data/health.db).

Usage:
    python ingestion/load.py --person AK
    python ingestion/load.py --person RK
    python ingestion/load.py            # loads both

Idempotent: skips reports whose source_file is already in the DB.
"""

import json
import sqlite3
import argparse
from pathlib import Path

from rich.console import Console

console = Console()

ROOT     = Path(__file__).parent.parent
DB_PATH  = ROOT / "data" / "health.db"
PROC_DIR = ROOT / "data" / "processed"
SCHEMA   = ROOT / "data" / "schema.sql"


def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA.read_text())
    return conn


def load_person(conn: sqlite3.Connection, person: str):
    person_dir = PROC_DIR / person
    if not person_dir.exists():
        console.print(f"[yellow]No processed data for {person}[/yellow]")
        return

    jsons = sorted(person_dir.glob("*.json"))
    inserted = skipped = 0

    for jf in jsons:
        data = json.loads(jf.read_text())
        source_file = data.get("source_file", jf.stem + ".pdf")

        # Check idempotency
        exists = conn.execute(
            "SELECT id FROM reports WHERE source_file = ?", (source_file,)
        ).fetchone()
        if exists:
            skipped += 1
            continue

        # Insert report
        cur = conn.execute(
            """INSERT INTO reports (person_id, report_date, lab_name, report_type, source_file)
               VALUES (?, ?, ?, ?, ?)""",
            (
                data.get("person_id", person),
                data.get("report_date", "0000-00-00"),
                data.get("lab_name"),
                data.get("report_type"),
                source_file,
            ),
        )
        report_id = cur.lastrowid

        # Insert biomarkers
        for bm in data.get("biomarkers", []):
            conn.execute(
                """INSERT INTO biomarkers
                   (report_id, name, value, text_value, unit, ref_low, ref_high, flag)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    report_id,
                    bm.get("name"),
                    bm.get("value"),
                    bm.get("text_value"),
                    bm.get("unit"),
                    bm.get("ref_low"),
                    bm.get("ref_high"),
                    bm.get("flag"),
                ),
            )

        # Insert vitals
        v = data.get("vitals", {})
        if any(v.values()):
            conn.execute(
                """INSERT INTO vitals
                   (report_id, weight_lbs, height_in, bmi, bp_systolic, bp_diastolic, pulse, temperature)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    report_id,
                    v.get("weight_lbs"),
                    v.get("height_in"),
                    v.get("bmi"),
                    v.get("bp_systolic"),
                    v.get("bp_diastolic"),
                    v.get("pulse"),
                    v.get("temperature_f"),
                ),
            )

        inserted += 1

    conn.commit()
    console.print(f"[green]{person}:[/green] {inserted} inserted, {skipped} skipped (already loaded)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load extracted JSON into SQLite")
    parser.add_argument("--person", choices=["AK", "RK"], help="Load one person (default: both)")
    args = parser.parse_args()

    conn = get_db()
    persons = [args.person] if args.person else ["AK", "RK"]
    for p in persons:
        load_person(conn, p)
    conn.close()
