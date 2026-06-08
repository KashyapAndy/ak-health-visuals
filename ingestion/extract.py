"""
Phase 2: Extract structured health data from renamed PDFs using Claude API.

Usage:
    python ingestion/extract.py --person AK
    python ingestion/extract.py --person RK
    python ingestion/extract.py --person AK --file 20180625_Medstar_AK.pdf

Outputs JSON to data/processed/<PERSON>/<filename>.json
Skips files that already have a processed JSON (idempotent).
"""

import os
import json
import base64
import argparse
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import track
from biomarker_map import normalize_name, normalize_unit, get_fallback_refs

load_dotenv()
console = Console()

ROOT     = Path(__file__).parent.parent
RAW_DIR  = ROOT / "raw_pdfs"
PROC_DIR = ROOT / "data" / "processed"
client   = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

EXTRACTION_PROMPT = """You are a medical records parser for a US-based patient. Extract all health data from this PDF.

Return ONLY a valid JSON object matching this exact schema — no markdown, no explanation:

{
  "report_date": "YYYY-MM-DD",
  "lab_name": "string",
  "report_type": "string",
  "biomarkers": [
    {
      "name": "string",
      "value": number | null,
      "text_value": "string | null",
      "unit": "string",
      "ref_low": number | null,
      "ref_high": number | null,
      "flag": "H" | "L" | "HH" | "LL" | null
    }
  ],
  "vitals": {
    "weight_lbs": number | null,
    "height_in":  number | null,
    "bmi":        number | null,
    "bp_systolic":  number | null,
    "bp_diastolic": number | null,
    "pulse":        number | null,
    "temperature_f": number | null
  }
}

Rules:
- report_date: use the specimen collection date if present, otherwise the report date.
- report_type must be one of: CBC, MetabolicPanel, LipidPanel, Thyroid, Urinalysis, Comprehensive, Allergy, Vaccine, Checkup, Other.
- For biomarker names: use the raw name exactly as printed — do NOT abbreviate or expand. Our system normalizes.
- For biomarker units: use the raw unit exactly as printed — do NOT convert. Our system converts.
- For NUMERIC results: put the number in "value", set "text_value" to null.
- For QUALITATIVE results (e.g. "Positive", "Negative", "Reactive", "O+", "Trace", "1+", "None seen"):
    put null in "value", put the result string in "text_value".
- For eGFR: if the reference range shows ">60", set ref_low=60, ref_high=null.
- Vitals — use US units:
    weight → lbs (convert kg × 2.20462 if needed)
    height → inches (convert cm ÷ 2.54 if needed)
    temperature → °F (convert °C via × 9/5 + 32 if needed)
- If any field is missing or unreadable, use null.
- If the document has no lab results (e.g. pure vaccine record), return an empty biomarkers array.
"""


def _strip_fences(raw: str) -> str:
    """Remove markdown code fences regardless of capitalisation."""
    if raw.startswith("```"):
        parts = raw.split("```")
        # parts[1] is the content between first and second fence
        content = parts[1] if len(parts) > 1 else raw
        # Strip optional language tag (json, JSON, etc.)
        first_newline = content.find("\n")
        if first_newline != -1:
            tag = content[:first_newline].strip().lower()
            if tag in ("json", ""):
                content = content[first_newline + 1:]
        return content.strip()
    return raw


def extract_pdf(pdf_path: Path, person: str) -> dict:
    pdf_b64 = base64.standard_b64encode(pdf_path.read_bytes()).decode()
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=8192,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_b64,
                    },
                },
                {"type": "text", "text": EXTRACTION_PROMPT},
            ],
        }],
    )
    raw = _strip_fences(response.content[0].text.strip())
    data = json.loads(raw)

    # Normalize biomarker names, units, and values to canonical form
    for bm in data.get("biomarkers", []):
        canonical_name = normalize_name(bm.get("name", ""))
        canonical_unit, converted_value = normalize_unit(
            canonical_name, bm.get("unit", ""), bm.get("value")
        )
        bm["name"]       = canonical_name
        bm["unit"]       = canonical_unit
        bm["value"]      = converted_value
        # Preserve text_value as-is (qualitative results)
        if "text_value" not in bm:
            bm["text_value"] = None

        # Fall back to registry ref range if PDF didn't include one
        if bm.get("ref_low") is None and bm.get("ref_high") is None:
            bm["ref_low"], bm["ref_high"] = get_fallback_refs(canonical_name)

    data["source_file"] = pdf_path.name
    data["person_id"]   = person
    return data


def process_person(person: str, single_file: str | None = None):
    person_raw  = RAW_DIR / person
    person_proc = PROC_DIR / person
    person_proc.mkdir(parents=True, exist_ok=True)

    if single_file:
        pdfs = [person_raw / single_file]
    else:
        pdfs = sorted(person_raw.glob("*.pdf"))

    to_process = []
    for pdf in pdfs:
        out = person_proc / f"{pdf.stem}.json"
        if out.exists():
            console.print(f"[dim]Skipping (already processed): {pdf.name}[/dim]")
        else:
            to_process.append(pdf)

    if not to_process:
        console.print("[green]All files already processed.[/green]")
        return

    errors = []
    for pdf in track(to_process, description=f"Extracting {person}..."):
        out = person_proc / f"{pdf.stem}.json"
        try:
            data = extract_pdf(pdf, person)
            out.write_text(json.dumps(data, indent=2))
            n_bm = len(data.get("biomarkers", []))
            console.print(f"[green]OK[/green] {pdf.name} -> {n_bm} biomarkers")
        except Exception as e:
            console.print(f"[red]FAIL[/red] {pdf.name}: {e}")
            errors.append((pdf.name, str(e)))

    if errors:
        console.print(f"\n[red]{len(errors)} file(s) failed:[/red]")
        for name, err in errors:
            console.print(f"  {name}: {err}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract health data from PDFs")
    parser.add_argument("--person", required=True, choices=["AK", "RK"])
    parser.add_argument("--file", help="Process a single file (filename only, not full path)")
    args = parser.parse_args()
    process_person(args.person, args.file)
