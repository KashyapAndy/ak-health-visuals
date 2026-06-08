"""
Phase 1: Rename all PDFs to YYYYMMDD_Provider_<PERSON>.pdf

Usage:
    python ingestion/rename.py --person AK   # renames files in raw_pdfs/AK/
    python ingestion/rename.py --person NK
    python ingestion/rename.py --person AK --dry-run

For UUID-named or unrecognizable files, the script calls the Claude API
to read the PDF and infer the lab name and date of service.

Originals are moved to raw_pdfs/<PERSON>/archive/ before renaming.
"""

import os
import re
import sys
import json
import shutil
import argparse
import base64
from pathlib import Path
from datetime import datetime

import anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()

ROOT      = Path(__file__).parent.parent
RAW_DIR   = ROOT / "raw_pdfs"
client    = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ---------------------------------------------------------------------------
# Pattern-based renaming for already-structured filenames
# ---------------------------------------------------------------------------

KNOWN_PATTERNS = [
    # 120113_LabCorp_Denver.pdf  →  date=2012-01-13, provider=LabCorp
    (r"^(\d{2})(\d{2})(\d{2})_([A-Za-z]+)", "yy_mm_dd_provider"),
    # 20180625_Medstar_AnnualCheckup_AKA.pdf
    (r"^(\d{4})(\d{2})(\d{2})_([A-Za-z]+)", "yyyy_mm_dd_provider"),
    # 2013-2016 NW Physicians_AK.pdf  →  multi-year, use first year
    (r"^(\d{4})-\d{4}\s+(.+?)(?:_AK|\.pdf)", "year_range"),
    # ANIRUDH KASHYAP_health-summary-06202018-to-07122017.pdf
    (r"health-summary-(\d{2})(\d{2})(\d{4})", "health_summary"),
]

PROVIDER_ALIASES = {
    "labcorp":               "LabCorp",
    "nwphysicians":          "NWPhysicians",
    "nwphysicianshealth":    "NWPhysicians",
    "medstar":               "Medstar",
    "healthscan":            "HealthScan",
    "sunrisemedical":        "SunriseMedical",
    "advancedintmedicine":   "AdvancedInternalMedicine",
    "metropolis":            "Metropolis",
    "bloodgroup":            "Metropolis",
}


def normalise_provider(raw: str) -> str:
    key = raw.lower().replace(" ", "").replace("-", "")
    for k, v in PROVIDER_ALIASES.items():
        if k in key:
            return v
    # Title-case whatever we have
    return raw.strip().replace(" ", "").title()


def try_pattern_rename(stem: str) -> tuple[str, str] | None:
    """Return (date_str YYYYMMDD, provider) or None if no pattern matches."""
    # UUID check — skip immediately
    if re.match(r"^[0-9a-f\-]{36}$", stem, re.I):
        return None
    # Long random-looking base64 strings
    if len(stem) > 60 and re.match(r"^[A-Za-z0-9_\-]+$", stem):
        return None

    # ANIRUDH KASHYAP health-summary
    m = re.search(r"health-summary-(\d{2})(\d{2})(\d{4})", stem, re.I)
    if m:
        mm, dd, yyyy = m.groups()
        return f"{yyyy}{mm}{dd}", "HealthSummary"

    # 20180625_Medstar... or 20120113_LabCorp...
    m = re.match(r"^(\d{4})(\d{2})(\d{2})_([A-Za-z]+)", stem)
    if m:
        yyyy, mm, dd, prov = m.groups()
        return f"{yyyy}{mm}{dd}", normalise_provider(prov)

    # 120113_LabCorp_Denver  (assume 20xx)
    m = re.match(r"^(\d{2})(\d{2})(\d{2})_([A-Za-z]+)", stem)
    if m:
        yy, mm, dd, prov = m.groups()
        yyyy = f"20{yy}"
        return f"{yyyy}{mm}{dd}", normalise_provider(prov)

    # 2013-2016 NW Physicians_AK
    m = re.match(r"^(\d{4})-\d{4}\s+(.+?)(?:_[A-Z]{2})?$", stem)
    if m:
        yyyy, prov = m.groups()
        return f"{yyyy}0101", normalise_provider(prov)

    # Blood Group - Metropolis
    m = re.match(r"^Blood\s+Group\s*-\s*(.+)$", stem, re.I)
    if m:
        return None  # let Claude figure out the date

    return None


# ---------------------------------------------------------------------------
# Claude-based renaming for unrecognisable files
# ---------------------------------------------------------------------------

EXTRACTION_PROMPT = """You are a medical document parser.
Read this PDF and return ONLY a JSON object with these fields:
{
  "date": "YYYYMMDD",        // date of service or report date (best guess)
  "provider": "ProviderName" // lab or clinic name, no spaces, TitleCase
}
If you cannot determine the date, use "00000000".
If you cannot determine the provider, use "UnknownLab".
Return ONLY the JSON object, nothing else."""


def claude_infer(pdf_path: Path) -> tuple[str, str]:
    """Ask Claude to extract date + provider from a PDF."""
    pdf_b64 = base64.standard_b64encode(pdf_path.read_bytes()).decode()
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=256,
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
    raw = response.content[0].text.strip()
    try:
        data = json.loads(raw)
        return data.get("date", "00000000"), data.get("provider", "UnknownLab")
    except json.JSONDecodeError:
        console.print(f"[yellow]Warning: Claude returned non-JSON for {pdf_path.name}[/yellow]")
        return "00000000", "UnknownLab"


# ---------------------------------------------------------------------------
# Main rename logic
# ---------------------------------------------------------------------------

def build_new_name(date_str: str, provider: str, person: str, existing: set[str]) -> str:
    base = f"{date_str}_{provider}_{person}"
    candidate = f"{base}.pdf"
    counter = 1
    while candidate in existing:
        candidate = f"{base}_{counter}.pdf"
        counter += 1
    return candidate


def rename_all(person: str, dry_run: bool = False):
    person_dir = RAW_DIR / person
    archive_dir = person_dir / "archive"

    if not person_dir.exists():
        console.print(f"[red]Folder not found: {person_dir}[/red]")
        sys.exit(1)

    pdfs = [f for f in person_dir.iterdir() if f.suffix.lower() == ".pdf" and f.is_file()]
    if not pdfs:
        console.print(f"[yellow]No PDFs found in {person_dir}[/yellow]")
        return

    table = Table(title=f"Rename Plan — {person}", show_lines=True)
    table.add_column("Original", style="dim")
    table.add_column("New Name", style="green")
    table.add_column("Method", style="cyan")

    used_names: set[str] = set()
    plan: list[tuple[Path, str, str]] = []

    for pdf in sorted(pdfs):
        stem = pdf.stem
        result = try_pattern_rename(stem)
        if result:
            date_str, provider = result
            method = "pattern"
        else:
            console.print(f"[cyan]Calling Claude for:[/cyan] {pdf.name}")
            date_str, provider = claude_infer(pdf)
            method = "claude"

        new_name = build_new_name(date_str, provider, person, used_names)
        used_names.add(new_name)
        plan.append((pdf, new_name, method))
        table.add_row(pdf.name, new_name, method)

    console.print(table)

    if dry_run:
        console.print("[yellow]Dry run — no files moved.[/yellow]")
        return

    archive_dir.mkdir(parents=True, exist_ok=True)
    for pdf, new_name, _ in plan:
        # Archive original
        shutil.copy2(pdf, archive_dir / pdf.name)
        # Rename in place
        pdf.rename(person_dir / new_name)

    console.print(f"[green]Done. {len(plan)} files renamed. Originals backed up to {archive_dir}[/green]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename health PDFs to standard format")
    parser.add_argument("--person", required=True, choices=["AK", "RK"], help="Whose PDFs to rename")
    parser.add_argument("--dry-run", action="store_true", help="Preview renames without moving files")
    args = parser.parse_args()
    rename_all(args.person, args.dry_run)
