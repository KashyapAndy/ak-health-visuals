import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
conn = sqlite3.connect('data/health.db')

print('=== REPORTS ===')
rows = conn.execute('SELECT source_file, report_date, lab_name, person_id FROM reports ORDER BY report_date').fetchall()
for r in rows:
    print(f'  {r[1]}  {str(r[2]):35s}  {r[3]}')

print()
print('=== VITALS (non-null rows only) ===')
rows = conn.execute('''
    SELECT r.report_date, v.weight_lbs, v.bmi, v.bp_systolic, v.bp_diastolic, v.pulse
    FROM vitals v JOIN reports r ON v.report_id=r.id
    WHERE v.weight_lbs IS NOT NULL OR v.bp_systolic IS NOT NULL
    ORDER BY r.report_date
''').fetchall()
for r in rows:
    print(f'  {r[0]}  wt={r[1]}  bmi={r[2]}  bp={r[3]}/{r[4]}  pulse={r[5]}')

print()
latest = conn.execute('SELECT id, source_file FROM reports ORDER BY report_date DESC LIMIT 1').fetchone()
print(f'=== SAMPLE BIOMARKERS (latest report: {latest[1]}) ===')
rows = conn.execute(
    'SELECT name, value, unit, ref_low, ref_high, flag FROM biomarkers WHERE report_id=? ORDER BY name',
    (latest[0],)
).fetchall()
for r in rows:
    flag = f'  [{r[5]}]' if r[5] else ''
    print(f'  {r[0]:35s} {str(r[1]):10s} {str(r[2]):15s} ref={r[3]}-{r[4]}{flag}')

conn.close()
