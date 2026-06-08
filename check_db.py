import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, 'ingestion')
from biomarker_map import REGISTRY

canonical_names = {bm.canonical_name for bm in REGISTRY}
conn = sqlite3.connect('data/health.db')

print('=== 1. UNIT VARIANTS (should be 1 per biomarker) ===')
rows = conn.execute("""
    SELECT b.name, COUNT(DISTINCT b.unit) n, GROUP_CONCAT(DISTINCT b.unit) units
    FROM biomarkers b JOIN reports r ON b.report_id=r.id
    WHERE r.person_id='AK' AND b.value IS NOT NULL
    GROUP BY b.name HAVING n > 1 ORDER BY n DESC, b.name
""").fetchall()
if rows:
    for r in rows:
        print(f'  {r[0]:35s} {r[1]} units: {r[2]}')
else:
    print('  CLEAN - all biomarkers use a single unit.')

print()
print('=== 2. UNRECOGNIZED NAMES (not in canonical map) ===')
all_names = conn.execute("""
    SELECT b.name, COUNT(*) n FROM biomarkers b
    JOIN reports r ON b.report_id=r.id
    WHERE r.person_id='AK'
    GROUP BY b.name ORDER BY n DESC
""").fetchall()
unknowns = [(r[0], r[1]) for r in all_names if r[0] not in canonical_names]
if unknowns:
    for name, n in unknowns[:40]:
        print(f'  {name:50s} ({n}x)')
    if len(unknowns) > 40:
        print(f'  ... and {len(unknowns)-40} more')
else:
    print('  CLEAN - all names are canonical.')

print()
print('=== 3. DUPLICATE BIOMARKERS WITHIN SAME REPORT ===')
rows = conn.execute("""
    SELECT r.source_file, b.name, COUNT(*) n
    FROM biomarkers b JOIN reports r ON b.report_id=r.id
    WHERE r.person_id='AK'
    GROUP BY r.id, b.name HAVING n>1 ORDER BY n DESC
""").fetchall()
if rows:
    for r in rows:
        print(f'  {r[0]:45s} {r[1]} ({r[2]}x)')
else:
    print('  CLEAN - no duplicates.')

print()
print('=== 4. NUMERIC VALUES WITH NO UNIT ===')
rows = conn.execute("""
    SELECT b.name, COUNT(*) n FROM biomarkers b
    JOIN reports r ON b.report_id=r.id
    WHERE r.person_id='AK' AND b.value IS NOT NULL
      AND (b.unit IS NULL OR b.unit='')
    GROUP BY b.name ORDER BY n DESC
""").fetchall()
if rows:
    for r in rows:
        print(f'  {r[0]:40s} ({r[1]}x)')
else:
    print('  CLEAN - all numeric values have units.')

print()
print()
print('=== 5. REPORTS WITH MANY MISSING UNITS ===')
rows = conn.execute("""
    SELECT r.source_file,
           SUM(CASE WHEN b.unit IS NULL OR b.unit='' THEN 1 ELSE 0 END) no_unit,
           COUNT(*) total
    FROM biomarkers b JOIN reports r ON b.report_id=r.id
    WHERE r.person_id='AK' AND b.value IS NOT NULL
    GROUP BY r.id
    HAVING no_unit > 5
    ORDER BY no_unit DESC
""").fetchall()
if rows:
    for r in rows:
        print(f'  {r[0]:50s}  no_unit={r[1]}  total={r[2]}')
else:
    print('  CLEAN - no reports with many missing units.')

print()
print('=== 6. SUMMARY ===')
total_bm = conn.execute("SELECT COUNT(*) FROM biomarkers b JOIN reports r ON b.report_id=r.id WHERE r.person_id='AK'").fetchone()[0]
total_rp = conn.execute("SELECT COUNT(*) FROM reports WHERE person_id='AK'").fetchone()[0]
distinct_bm = conn.execute("SELECT COUNT(DISTINCT b.name) FROM biomarkers b JOIN reports r ON b.report_id=r.id WHERE r.person_id='AK'").fetchone()[0]
print(f'  Reports: {total_rp}  |  Biomarker rows: {total_bm}  |  Distinct biomarkers: {distinct_bm}')
conn.close()
