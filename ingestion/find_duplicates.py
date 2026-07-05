"""
Flag potential duplicate reports (e.g. a provider portal HTML export that
re-reports the same blood draw already captured in a PDF) so a human can
decide whether one should be excluded before running load.py.

Read-only: never modifies or deletes anything, just prints a report.

Usage:
    python ingestion/find_duplicates.py --person RK
    python ingestion/find_duplicates.py --person RK --date-window 5
"""

import argparse
import json
from datetime import date, timedelta
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()
ROOT = Path(__file__).parent.parent
PROC_DIR = ROOT / "data" / "processed"


def load_reports(person: str) -> list[dict]:
    person_dir = PROC_DIR / person
    if not person_dir.exists():
        console.print(f"[red]No processed data for {person} — run extract.py first.[/red]")
        return []
    reports = []
    for jf in sorted(person_dir.glob("*.json")):
        data = json.loads(jf.read_text())
        data["_file"] = jf.name
        reports.append(data)
    return reports


def biomarker_values(report: dict) -> dict:
    out = {}
    for bm in report.get("biomarkers", []):
        out[bm["name"]] = bm.get("value") if bm.get("value") is not None else bm.get("text_value")
    return out


def overlap(a: dict, b: dict) -> tuple[int, int]:
    """Return (matching, common) biomarker counts between two reports' values."""
    common = set(a) & set(b)
    matching = sum(1 for k in common if a[k] == b[k])
    return matching, len(common)


def find_duplicates(person: str, date_window: int):
    reports = load_reports(person)
    if len(reports) < 2:
        console.print("[yellow]Not enough reports to compare.[/yellow]")
        return

    dated = []
    for r in reports:
        if not r.get("report_date"):
            continue
        r["_date"] = date.fromisoformat(r["report_date"])
        r["_bm"] = biomarker_values(r)
        dated.append(r)
    dated.sort(key=lambda r: r["_date"])

    table = Table(title=f"Potential duplicate reports — {person}", show_lines=True)
    table.add_column("File A", style="dim")
    table.add_column("File B", style="dim")
    table.add_column("Date A")
    table.add_column("Date B")
    table.add_column("Matching / Common biomarkers", style="cyan")

    found = False
    for i, a in enumerate(dated):
        for b in dated[i + 1:]:
            if (b["_date"] - a["_date"]) > timedelta(days=date_window):
                break
            matching, common = overlap(a["_bm"], b["_bm"])
            if common == 0:
                continue
            ratio = matching / common
            if ratio >= 0.6 or a["_date"] == b["_date"]:
                found = True
                table.add_row(
                    a["_file"], b["_file"],
                    str(a["_date"]), str(b["_date"]),
                    f"{matching}/{common} ({ratio:.0%})",
                )

    if found:
        console.print(table)
        console.print(
            "\n[dim]Read-only report — nothing was changed. If two rows look like the "
            "same blood draw reported by two sources, decide which source_file to drop, "
            "then remove that file from raw_pdfs/ and its .json from data/processed/ "
            "before running load.py.[/dim]"
        )
    else:
        console.print(f"[green]No likely duplicates found within a {date_window}-day window.[/green]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flag potential duplicate reports for a person")
    parser.add_argument("--person", required=True, choices=["AK", "RK"])
    parser.add_argument("--date-window", type=int, default=3, help="Max days apart to still compare (default 3)")
    args = parser.parse_args()
    find_duplicates(args.person, args.date_window)
