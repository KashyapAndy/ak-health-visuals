import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
conn = sqlite3.connect('data/health.db')

print('=== Biomarkers appearing only ONCE (AK) ===')
rows = conn.execute("""
    SELECT b.name, COUNT(DISTINCT r.id) n
    FROM biomarkers b JOIN reports r ON b.report_id=r.id
    WHERE r.person_id='AK'
    GROUP BY b.name HAVING n = 1
    ORDER BY b.name
""").fetchall()
for r in rows:
    print(f'  {r[0]}')

print()
print('=== 2018-11 reports ===')
rows = conn.execute("SELECT id, source_file, report_date, lab_name FROM reports WHERE report_date LIKE '2018-11%'").fetchall()
for r in rows:
    print(f'  id={r[0]}  {r[2]}  {r[1]}  {r[3]}')

print()
print('=== Biomarkers with >= 2 occurrences (AK) ===')
rows = conn.execute("""
    SELECT b.name, COUNT(DISTINCT r.id) n
    FROM biomarkers b JOIN reports r ON b.report_id=r.id
    WHERE r.person_id='AK'
    GROUP BY b.name HAVING n >= 2
    ORDER BY n DESC, b.name
""").fetchall()
print(f'  Total: {len(rows)}')
for r in rows:
    print(f'  {r[0]:40s} {r[1]}x')
conn.close()
