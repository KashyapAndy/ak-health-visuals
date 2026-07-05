"""
Health Dashboard — FastAPI backend
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pathlib import Path

app = FastAPI(title="Health Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

DB_PATH = Path(__file__).parent.parent / "data" / "health.db"

# Exclude: reports with bad/unreliable data, and clinical categories not useful for trending
EXCLUDED_DATES = ("2018-11",)          # BADDATE_SunriseMedical — unreliable panel
EXCLUDED_CATEGORIES = {"Drug Screen"}  # not useful for health trending

# Minimum number of reports a biomarker must appear in to be shown
MIN_REPORTS = 2


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def excluded_date_clause() -> str:
    clauses = [f"r.report_date NOT LIKE '{d}%'" for d in EXCLUDED_DATES]
    return " AND ".join(clauses)


# ---------------------------------------------------------------------------
# Registry helpers (category lookup)
# ---------------------------------------------------------------------------

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "ingestion"))
from biomarker_map import REGISTRY

_NAME_TO_CAT = {bm.canonical_name: bm.category for bm in REGISTRY}

CATEGORY_ORDER = [
    "CBC", "CBC Differential", "Metabolic", "Lipids",
    "Thyroid", "Vitamins", "Iron Studies", "Hormones",
    "Urinalysis", "Infectious Disease", "Pulmonary", "Other",
]


# ---------------------------------------------------------------------------
# Persons
# ---------------------------------------------------------------------------

@app.get("/api/persons")
def list_persons():
    conn = get_db()
    rows = conn.execute(
        "SELECT DISTINCT person_id FROM reports ORDER BY person_id"
    ).fetchall()
    conn.close()
    return [r["person_id"] for r in rows]


# ---------------------------------------------------------------------------
# Categories + biomarker names (filtered)
# ---------------------------------------------------------------------------

@app.get("/api/categories")
def list_categories(person: str = Query("AK")):
    exc = excluded_date_clause()
    conn = get_db()
    rows = conn.execute(f"""
        SELECT b.name, COUNT(DISTINCT r.id) AS n
        FROM biomarkers b
        JOIN reports r ON b.report_id = r.id
        WHERE r.person_id = ? AND {exc}
        GROUP BY b.name
        HAVING n >= {MIN_REPORTS}
        ORDER BY b.name
    """, (person,)).fetchall()
    conn.close()

    cat_map: dict[str, list[str]] = {}
    for row in rows:
        name = row["name"]
        cat = _NAME_TO_CAT.get(name, "Other")
        if cat in EXCLUDED_CATEGORIES:
            continue
        cat_map.setdefault(cat, []).append(name)

    result = []
    for cat in CATEGORY_ORDER:
        if cat in cat_map:
            result.append({"category": cat, "biomarkers": sorted(cat_map[cat])})
    # append any categories not in the preferred order
    for cat, names in cat_map.items():
        if cat not in CATEGORY_ORDER:
            result.append({"category": cat, "biomarkers": sorted(names)})
    return result


# ---------------------------------------------------------------------------
# Biomarker time-series (filtered)
# ---------------------------------------------------------------------------

# Ratios that should be computed from constituents rather than read raw.
# Format: ratio_name -> (numerator_name, denominator_name, unit, ref_low, ref_high)
COMPUTED_RATIOS: dict[str, tuple] = {
    "A/G Ratio": ("Albumin", "Globulin", "", 1.1, 2.5),
    # HDL/LDL is cardioprotective — higher is better
    "HDL/LDL Ratio": ("HDL Cholesterol", "LDL Cholesterol", "", 0.3, None),
    "LDL/HDL Ratio": ("LDL Cholesterol", "HDL Cholesterol", "", None, 3.5),
}

# Globulin isn't stored directly — it's Total Protein - Albumin
DERIVED_MARKERS: dict[str, tuple[str, str, str]] = {
    "Globulin": ("Total Protein", "Albumin", "subtract"),
}


def _fetch_marker_series(conn, person: str, name: str, exc: str) -> dict[str, float]:
    """Return {report_date: value} for a marker, computing derived ones if needed."""
    if name in DERIVED_MARKERS:
        a_name, b_name, op = DERIVED_MARKERS[name]
        a_rows = conn.execute(f"""
            SELECT r.report_date, b.value FROM biomarkers b
            JOIN reports r ON b.report_id = r.id
            WHERE r.person_id = ? AND b.name = ? AND b.value IS NOT NULL AND {exc}
        """, (person, a_name)).fetchall()
        b_rows = conn.execute(f"""
            SELECT r.report_date, b.value FROM biomarkers b
            JOIN reports r ON b.report_id = r.id
            WHERE r.person_id = ? AND b.name = ? AND b.value IS NOT NULL AND {exc}
        """, (person, b_name)).fetchall()
        a_map = {r["report_date"]: r["value"] for r in a_rows}
        b_map = {r["report_date"]: r["value"] for r in b_rows}
        result = {}
        for date in set(a_map) & set(b_map):
            if op == "subtract":
                result[date] = round(a_map[date] - b_map[date], 3)
        return result

    rows = conn.execute(f"""
        SELECT r.report_date, b.value FROM biomarkers b
        JOIN reports r ON b.report_id = r.id
        WHERE r.person_id = ? AND b.name = ? AND b.value IS NOT NULL AND {exc}
    """, (person, name)).fetchall()
    return {r["report_date"]: r["value"] for r in rows}


@app.get("/api/biomarker")
def biomarker_history(name: str = Query(...), person: str = Query("AK")):
    exc = excluded_date_clause()
    conn = get_db()

    # ── Computed ratio ────────────────────────────────────────────────────────
    if name in COMPUTED_RATIOS:
        num_name, den_name, unit, ref_low, ref_high = COMPUTED_RATIOS[name]
        num_map = _fetch_marker_series(conn, person, num_name, exc)
        den_map = _fetch_marker_series(conn, person, den_name, exc)
        conn.close()
        dates = sorted(set(num_map) & set(den_map))
        if not dates:
            raise HTTPException(status_code=404, detail=f"No data to compute {name}")
        data = []
        for date in dates:
            denom = den_map[date]
            value = round(num_map[date] / denom, 3) if denom else None
            data.append({"date": date, "value": value, "text_value": None, "flag": None})
        return {"name": name, "unit": unit, "ref_low": ref_low, "ref_high": ref_high, "data": data}

    # ── Raw stored marker ─────────────────────────────────────────────────────
    rows = conn.execute(f"""
        SELECT r.report_date, b.value, b.text_value, b.unit,
               b.ref_low, b.ref_high, b.flag
        FROM biomarkers b
        JOIN reports r ON b.report_id = r.id
        WHERE r.person_id = ? AND b.name = ? AND {exc}
        ORDER BY r.report_date
    """, (person, name)).fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No data for {name}")

    ref_lows  = [r["ref_low"]  for r in rows if r["ref_low"]  is not None]
    ref_highs = [r["ref_high"] for r in rows if r["ref_high"] is not None]
    ref_low  = min(ref_lows)  if ref_lows  else None
    ref_high = max(ref_highs) if ref_highs else None

    return {
        "name": name,
        "unit": rows[0]["unit"],
        "ref_low":  ref_low,
        "ref_high": ref_high,
        "data": [
            {
                "date":       r["report_date"],
                "value":      r["value"],
                "text_value": r["text_value"],
                "flag":       r["flag"],
            }
            for r in rows
        ],
    }


# ---------------------------------------------------------------------------
# Vitals time-series (filtered)
# ---------------------------------------------------------------------------

@app.get("/api/vitals")
def vitals_history(person: str = Query("AK")):
    exc = excluded_date_clause()
    conn = get_db()
    rows = conn.execute(f"""
        SELECT r.report_date, v.weight_lbs, v.height_in, v.bmi,
               v.bp_systolic, v.bp_diastolic, v.pulse, v.temperature
        FROM vitals v
        JOIN reports r ON v.report_id = r.id
        WHERE r.person_id = ? AND {exc}
          AND (v.weight_lbs IS NOT NULL OR v.bp_systolic IS NOT NULL)
        ORDER BY r.report_date
    """, (person,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Latest values summary
# ---------------------------------------------------------------------------

@app.get("/api/latest")
def latest_values(person: str = Query("AK")):
    exc = excluded_date_clause()
    conn = get_db()

    # Biomarkers that meet the min-reports threshold
    eligible = {
        row["name"]
        for row in conn.execute(f"""
            SELECT b.name, COUNT(DISTINCT r.id) AS n
            FROM biomarkers b JOIN reports r ON b.report_id=r.id
            WHERE r.person_id=? AND {exc}
            GROUP BY b.name HAVING n >= {MIN_REPORTS}
        """, (person,)).fetchall()
    }

    rows = conn.execute(f"""
        SELECT b.name, b.value, b.text_value, b.unit,
               b.ref_low, b.ref_high, b.flag, r.report_date
        FROM biomarkers b
        JOIN reports r ON b.report_id = r.id
        WHERE r.person_id = ? AND {exc}
        ORDER BY b.name, r.report_date DESC
    """, (person,)).fetchall()
    conn.close()

    seen: dict[str, list] = {}
    for r in rows:
        name = r["name"]
        if name not in eligible:
            continue
        cat = _NAME_TO_CAT.get(name, "Other")
        if cat in EXCLUDED_CATEGORIES:
            continue
        if name not in seen:
            seen[name] = []
        if len(seen[name]) < 2:
            seen[name].append(dict(r))

    result = []
    for name, readings in seen.items():
        latest = readings[0]
        prev   = readings[1] if len(readings) > 1 else None
        delta  = None
        if prev and latest["value"] is not None and prev["value"] is not None:
            delta = round(latest["value"] - prev["value"], 4)
        result.append({
            "name":       name,
            "value":      latest["value"],
            "text_value": latest["text_value"],
            "unit":       latest["unit"],
            "ref_low":    latest["ref_low"],
            "ref_high":   latest["ref_high"],
            "flag":       latest["flag"],
            "date":       latest["report_date"],
            "delta":      delta,
            "prev_value": prev["value"]      if prev else None,
            "prev_date":  prev["report_date"] if prev else None,
        })

    return sorted(result, key=lambda x: x["name"])
