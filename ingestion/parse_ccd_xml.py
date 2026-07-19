"""
Phase 2 alternative for CCD/CDA XML exports that aggregate many years of lab
results in a single Results-section narrative table (e.g. a specialty
practice's full patient-history export via Flatiron/Epic Care Everywhere).

extract.py's model is one-file-per-visit: a single report_date + one flat
biomarkers list, sent to Claude. That doesn't fit a CCD where the Results
section is one big table with a Date column spanning years and thousands of
rows -- Claude's max_tokens cap alone makes returning it all impossible, and
the schema has nowhere to put multiple visit dates. This script sidesteps
the API entirely: the table is already structured data, so it's parsed
directly (stdlib xml.etree, no Claude call, no cost) and split into one
report JSON per distinct Date column value.

Usage:
    python ingestion/parse_ccd_xml.py --file ccda.xml --person RK
    python ingestion/parse_ccd_xml.py --file ccda.xml --person RK --dry-run
"""

import argparse
import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

from biomarker_map import normalize_name, normalize_unit, get_fallback_refs

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "raw_pdfs"
PROC_DIR = ROOT / "data" / "processed"

NS = {"v3": "urn:hl7-org:v3"}
RESULTS_SECTION_CODE = "30954-2"
VITALS_SECTION_CODE = "8716-3"
DEFAULT_LAB_NAME = "Northern Virginia Hematology Oncology Associates"

# Narrative rows that aren't lab values (comments, pathologist names, blood
# bank typing, admin metadata embedded in the same table) -- not real
# biomarker data, so they're dropped rather than stored as garbage rows.
_SKIP_DESCRIPTIONS = {
    "comment:", "please note:", "pdf", "pdf image", "result",
    "specimen type", "clinical information", "flow interpretation",
    "flow comment", "resulting path name", "analysis and gating strategy",
    "viability", "phenotype chart", "assessment of leukocytes",
    "hematology comments:", "lupus reflex interpretation", "pathologist",
    "pathologist interpretation", "written authorization",
    "comments/recommendations", "abo grouping", "rh factor",
    # Composite of Baso+Eos+Mono -- redundant with the 3 components already
    # captured individually; would otherwise clear MIN_REPORTS=2 and show
    # up as clutter under an unmapped raw name.
    "basophils+eosinophils+monocytes bld ncnc pt qn",
    "basophils+eosinophils+monocytes/100 leukocytes bld nfr pt qn",
}

_INTERP_FLAG = {
    "normal": None,
    "abnormal": "H",
    "above high threshold": "H",
    "below low threshold": "L",
    "critical high": "HH",
    "critical low": "LL",
    "": None,
}

# value+unit are concatenated with no separator in Vitals ("224.6lb", "98f")
# and with a space in Results ("3.15 number"); this handles both, and
# tolerates the doubled-decimal glitch seen in a couple of source rows
# ("98..1f").
_VALUE_UNIT_RE = re.compile(r"^(-?\d+(?:\.\d+)?)\.?\s*(.*)$")

VITALS_FIELD_MAP = {
    "body height patient len pt qn": "height_in",
    "body weight patient mass pt qn": "weight_lbs",
    "body temperature patient temp pt qn": "temperature_f",
    "heart rate nrat pt qn": "pulse",
    "intravascular systolic arterial system pres pt qn": "bp_systolic",
    "intravascular diastolic arterial system pres pt qn": "bp_diastolic",
}
# Not part of the vitals schema and no registry entry -- dropped, not stored.
VITALS_SKIP = {"breaths respiratory system nrat pt qn"}
# No vitals slot, but has a registry biomarker -- stored as a biomarker instead.
VITALS_AS_BIOMARKER = {"oxygen saturation blda mfr pt qn": "Oxygen Saturation"}


def split_value_unit(raw: str):
    raw = raw.strip()
    if not raw or raw.startswith("----"):
        return None, None
    m = _VALUE_UNIT_RE.match(raw)
    if not m:
        return None, raw  # qualitative (Negative, <9 IU/mL as text, etc.)
    return float(m.group(1)), m.group(2).strip()


def cells_of(tr):
    return ["".join(td.itertext()).strip() for td in tr.findall("v3:td", NS)]


def find_section(root, code):
    for sec in root.iter("{urn:hl7-org:v3}section"):
        code_el = sec.find("v3:code", NS)
        if code_el is not None and code_el.get("code") == code:
            return sec
    return None


def parse_results(sec, by_date):
    text_el = sec.find("v3:text", NS)
    rows = list(text_el.iter("{urn:hl7-org:v3}tr"))
    n_skipped = 0
    for tr in rows:
        cells = cells_of(tr)
        if len(cells) != 6:
            continue
        _code, desc, value_unit, interp, _lab, date = cells
        if not date:
            n_skipped += 1
            continue
        if desc.strip().lower() in _SKIP_DESCRIPTIONS:
            continue
        value, rest = split_value_unit(value_unit)
        if value is None and rest is None:
            n_skipped += 1
            continue

        canonical = normalize_name(desc)
        if value is not None:
            unit, value = normalize_unit(canonical, rest, value)
            text_value = None
        else:
            unit, text_value = None, rest

        ref_low, ref_high = get_fallback_refs(canonical)
        by_date[date]["biomarkers"].append({
            "name": canonical,
            "value": value,
            "text_value": text_value,
            "unit": unit,
            "ref_low": ref_low,
            "ref_high": ref_high,
            "flag": _INTERP_FLAG.get(interp.strip().lower(), None),
        })
    return n_skipped, len(rows)


def parse_vitals(sec, by_date):
    text_el = sec.find("v3:text", NS)
    rows = list(text_el.iter("{urn:hl7-org:v3}tr"))
    n_skipped = 0
    for tr in rows:
        cells = cells_of(tr)
        if len(cells) != 4:
            continue
        desc, value_unit, date, _provider = cells
        if not date:
            n_skipped += 1
            continue
        key = desc.strip().lower()
        if key in VITALS_SKIP:
            continue
        value, unit = split_value_unit(value_unit)
        if value is None:
            n_skipped += 1
            continue

        if key in VITALS_FIELD_MAP:
            by_date[date]["vitals"][VITALS_FIELD_MAP[key]] = value
        elif key in VITALS_AS_BIOMARKER:
            canonical = VITALS_AS_BIOMARKER[key]
            norm_unit, norm_value = normalize_unit(canonical, unit, value)
            ref_low, ref_high = get_fallback_refs(canonical)
            by_date[date]["biomarkers"].append({
                "name": canonical, "value": norm_value, "text_value": None,
                "unit": norm_unit, "ref_low": ref_low, "ref_high": ref_high,
                "flag": None,
            })
        else:
            n_skipped += 1
    return n_skipped, len(rows)


def infer_report_type(biomarkers):
    from biomarker_map import REGISTRY
    cat_by_name = {b.canonical_name: b.category for b in REGISTRY}
    cats = {cat_by_name.get(bm["name"]) for bm in biomarkers}
    if "Metabolic" in cats:
        return "Comprehensive"
    if "CBC" in cats or "CBC Differential" in cats:
        return "CBC"
    return "Other"


def process(file_name: str, person: str, dry_run: bool):
    path = RAW_DIR / person / file_name
    tree = ET.parse(path)
    root = tree.getroot()

    by_date = defaultdict(lambda: {"biomarkers": [], "vitals": {
        "weight_lbs": None, "height_in": None, "bmi": None,
        "bp_systolic": None, "bp_diastolic": None, "pulse": None,
        "temperature_f": None,
    }})

    results_sec = find_section(root, RESULTS_SECTION_CODE)
    vitals_sec = find_section(root, VITALS_SECTION_CODE)

    r_skipped = r_total = v_skipped = v_total = 0
    if results_sec is not None:
        r_skipped, r_total = parse_results(results_sec, by_date)
    if vitals_sec is not None:
        v_skipped, v_total = parse_vitals(vitals_sec, by_date)

    print(f"Results rows: {r_total} ({r_skipped} skipped as non-data/administrative)")
    print(f"Vitals rows: {v_total} ({v_skipped} skipped as untracked field)")
    print(f"Distinct visit dates found: {len(by_date)}")

    out_dir = PROC_DIR / person
    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for date, data in sorted(by_date.items()):
        report = {
            "report_date": date,
            "lab_name": DEFAULT_LAB_NAME,
            "report_type": infer_report_type(data["biomarkers"]),
            "biomarkers": data["biomarkers"],
            "vitals": data["vitals"],
            "source_file": f"{file_name}#{date}",
            "person_id": person,
        }
        out_path = out_dir / f"{Path(file_name).stem}_{date}.json"
        if dry_run:
            print(f"  [dry-run] would write {out_path.name} "
                  f"({len(data['biomarkers'])} biomarkers)")
        else:
            out_path.write_text(json.dumps(report, indent=2))
        written += 1

    print(f"{'Would write' if dry_run else 'Wrote'} {written} per-date report JSONs to {out_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a CCD/CDA XML export into per-date report JSONs")
    parser.add_argument("--file", required=True, help="XML filename in raw_pdfs/<PERSON>/")
    parser.add_argument("--person", required=True, choices=["AK", "RK"])
    parser.add_argument("--dry-run", action="store_true", help="Print what would be written without writing files")
    args = parser.parse_args()
    process(args.file, args.person, args.dry_run)
