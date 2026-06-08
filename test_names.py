import sys
sys.path.insert(0, 'ingestion')
from biomarker_map import normalize_name, _NOISE
import re

tests = [
    'White Blood Cells', 'Red Blood Cells', 'Globulin, Total',
    'Glucose Lvl Random', 'Folate (Folic Acid), Serum',
    'Ld, Serum', 'Mean Glucose Est (Calc)', 'Occult Blood',
    'Vitamin D,25-Oh,Total', 'Vitamin D,25-Oh,Total,Ia',
    'Vitamin D,25-Oh, D3', 'Vitamin D,25-Oh, D2',
]
for t in tests:
    key = _NOISE.sub(' ', t).lower()
    key = re.sub(r'\s+', ' ', key).strip().strip(',').strip()
    result = normalize_name(t)
    status = 'MAPPED' if result != t.strip().title() else 'UNMAPPED'
    print(f'[{status}] {t:45s}  key="{key}"  -> {result}')
