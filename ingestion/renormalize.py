"""
Re-normalize existing extracted JSONs without re-calling the API.
Applies the latest biomarker_map (names, units, refs) to all saved JSONs.

Usage:
    python ingestion/renormalize.py --person AK
    python ingestion/renormalize.py --person RK
    python ingestion/renormalize.py          # both
"""

import json
import argparse
from pathlib import Path

from rich.console import Console
from biomarker_map import normalize_name, normalize_unit, get_fallback_refs, REGISTRY

console = Console()
ROOT     = Path(__file__).parent.parent
PROC_DIR = ROOT / "data" / "processed"

# Canonical unit for each canonical biomarker name (for backfilling missing units)
_CANONICAL_UNIT = {bm.canonical_name: bm.canonical_unit for bm in REGISTRY}

# Map from % biomarker names to their Abs counterparts (for unit-based disambiguation)
_PCT_TO_ABS = {
    "Neutrophils %":            "Neutrophils Abs",
    "Lymphocytes %":            "Lymphocytes Abs",
    "Monocytes %":              "Monocytes Abs",
    "Eosinophils %":            "Eosinophils Abs",
    "Basophils %":              "Basophils Abs",
    "Immature Granulocytes %":  "Immature Granulocytes Abs",
}

# Units that indicate an absolute cell count (not a percentage)
_ABS_UNITS = {"x10e3/ul", "10³/µl", "k/ul", "k/µl", "10^3/ul", "thous/mcl",
              "x10(3)/mcl", "thou/ul", "×10³/µl", "10⁹/l"}


def renormalize_person(person: str):
    person_dir = PROC_DIR / person
    if not person_dir.exists():
        console.print(f"[yellow]No processed data for {person}[/yellow]")
        return

    jsons = sorted(person_dir.glob("*.json"))
    updated = 0

    for jf in jsons:
        data = json.loads(jf.read_text(encoding="utf-8"))
        changed = False

        for bm in data.get("biomarkers", []):
            old_name  = bm.get("name", "")
            old_unit  = bm.get("unit", "") or ""
            old_value = bm.get("value")

            # Step 1: Normalize name
            new_name = normalize_name(old_name)

            # Step 2: If a %-differential has an absolute-count unit, rename to Abs
            if new_name in _PCT_TO_ABS and old_unit.lower() in _ABS_UNITS:
                new_name = _PCT_TO_ABS[new_name]

            # Step 3: Normalize unit + convert value
            new_unit, new_value = normalize_unit(new_name, old_unit, old_value)

            # Step 4: Backfill unit from canonical registry if still empty
            if (not new_unit) and new_name in _CANONICAL_UNIT:
                canonical = _CANONICAL_UNIT[new_name]
                if canonical:
                    new_unit = canonical

            # Step 5: Backfill ref range from registry if both are null
            if bm.get("ref_low") is None and bm.get("ref_high") is None:
                bm["ref_low"], bm["ref_high"] = get_fallback_refs(new_name)

            if new_name != old_name or new_unit != old_unit or new_value != old_value:
                bm["name"]  = new_name
                bm["unit"]  = new_unit
                bm["value"] = new_value
                changed = True

        # Step 6: Deduplicate — within a JSON, keep the first occurrence of each name.
        # This handles eGFR (non-African-Am vs African-Am) and any other lab doubles.
        seen = set()
        deduped = []
        for bm in data.get("biomarkers", []):
            name = bm.get("name", "")
            if name not in seen:
                seen.add(name)
                deduped.append(bm)
        if len(deduped) < len(data.get("biomarkers", [])):
            data["biomarkers"] = deduped
            changed = True

        if changed:
            jf.write_text(json.dumps(data, indent=2), encoding="utf-8")
            updated += 1

    console.print(f"[green]{person}:[/green] {updated}/{len(jsons)} JSONs updated")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--person", choices=["AK", "RK"])
    args = parser.parse_args()
    persons = [args.person] if args.person else ["AK", "RK"]
    for p in persons:
        renormalize_person(p)
