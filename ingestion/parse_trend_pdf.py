"""
One-off extractor for MyChart "Result Trends" PDF exports: a cumulative
table with one column per visit date, spanning multiple visits in a single
file. extract.py's one-report-per-file schema can't represent that (same
problem as the ccda.xml CCD export), and pdfplumber's text extraction
garbles the column alignment for these particular tables (reference ranges
and values interleave across lines), so this sends the PDF to Claude
directly and asks for a list of per-date reports instead of one.

Usage:
    python ingestion/parse_trend_pdf.py --file "RK - Result Trends - CBC - Jul 19, 2026.PDF" --person RK
    python ingestion/parse_trend_pdf.py --file ... --person RK --dry-run
"""

import argparse
import json
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from rich.console import Console

from doc_utils import build_content_blocks
from biomarker_map import normalize_name, normalize_unit, get_fallback_refs

load_dotenv()
console = Console()

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "raw_pdfs"
PROC_DIR = ROOT / "data" / "processed"
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

EXTRACTION_PROMPT = """This is a "Result Trends" export from a patient portal: a cumulative table
with one column per visit/draw date, and one row group per lab component.
Some components appear twice with different reference ranges (the lab
changed its reference range at some point) -- each such group still
belongs to the SAME component, just applies to different date column(s);
use your best judgment reading the visual table layout to attribute each
value to the correct date and component.

Return ONLY a JSON object with this exact schema -- no markdown, no explanation:

{
  "lab_name": "string or null if not shown in the document",
  "reports": [
    {
      "report_date": "YYYY-MM-DD",
      "biomarkers": [
        {
          "name": "string, raw component name exactly as printed",
          "value": number | null,
          "text_value": "string | null",
          "unit": "string, raw unit exactly as printed",
          "ref_low": number | null,
          "ref_high": number | null,
          "flag": "H" | "L" | "HH" | "LL" | null
        }
      ]
    }
  ]
}

Rules:
- One entry in "reports" per distinct date column found in the table(s) -- do not skip any date, do not merge dates together.
- For each date column, include every component that has a value in that column.
- Use the raw component name and raw unit exactly as printed -- do not abbreviate, expand, or convert. Our system normalizes and converts.
- If a value falls outside the printed reference range, set flag to "H" or "L" (or "HH"/"LL" if marked critical); otherwise null.
- If a component has no value for a given date, omit it from that date's biomarkers list rather than inventing a null entry.
"""


def extract_trends(path: Path) -> dict:
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=8192,
        messages=[{
            "role": "user",
            "content": [
                *build_content_blocks(path),
                {"type": "text", "text": EXTRACTION_PROMPT},
            ],
        }],
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        first_nl = raw.find("\n")
        if first_nl != -1 and raw[:first_nl].strip().lower() in ("json", ""):
            raw = raw[first_nl + 1:]
    return json.loads(raw)


def process(file_name: str, person: str, dry_run: bool):
    path = RAW_DIR / person / file_name
    console.print(f"[cyan]Sending to Claude:[/cyan] {path.name}")
    data = extract_trends(path)
    lab_name = data.get("lab_name") or "Patient Portal (MyChart)"
    reports = data.get("reports", [])
    console.print(f"Found {len(reports)} distinct report dates")

    out_dir = PROC_DIR / person
    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for rep in sorted(reports, key=lambda r: r["report_date"]):
        date = rep["report_date"]
        biomarkers = []
        for bm in rep.get("biomarkers", []):
            canonical = normalize_name(bm["name"])
            raw_value = bm.get("value")
            raw_unit = bm.get("unit") or ""
            if raw_value is not None:
                unit, value = normalize_unit(canonical, raw_unit, raw_value)
                text_value = None
            else:
                unit, value = raw_unit, None
                text_value = bm.get("text_value")
            ref_low, ref_high = get_fallback_refs(canonical)
            if bm.get("ref_low") is not None:
                ref_low = bm["ref_low"]
            if bm.get("ref_high") is not None:
                ref_high = bm["ref_high"]
            biomarkers.append({
                "name": canonical, "value": value, "text_value": text_value,
                "unit": unit, "ref_low": ref_low, "ref_high": ref_high,
                "flag": bm.get("flag"),
            })

        report = {
            "report_date": date,
            "lab_name": lab_name,
            "report_type": "CBC",
            "biomarkers": biomarkers,
            "vitals": {
                "weight_lbs": None, "height_in": None, "bmi": None,
                "bp_systolic": None, "bp_diastolic": None, "pulse": None,
                "temperature_f": None,
            },
            "source_file": f"{file_name}#{date}",
            "person_id": person,
        }
        out_path = out_dir / f"{Path(file_name).stem}_{date}.json"
        if dry_run:
            print(f"  [dry-run] would write {out_path.name} ({len(biomarkers)} biomarkers)")
        else:
            out_path.write_text(json.dumps(report, indent=2))
        written += 1

    console.print(f"{'Would write' if dry_run else 'Wrote'} {written} per-date report JSONs to {out_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a multi-date 'Result Trends' PDF into per-date report JSONs")
    parser.add_argument("--file", required=True, help="PDF filename in raw_pdfs/<PERSON>/")
    parser.add_argument("--person", required=True, choices=["AK", "RK"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    process(args.file, args.person, args.dry_run)
