import sys
sys.path.insert(0, 'ingestion')
from biomarker_map import normalize_name, _NOISE
import re

tests = [
    'calcium, serum', 'ldl chol calc (nih)', 'white blood cell count', 'red blood cell count',
    'calcium', 'bilirubin, total', 'carbon dioxide, total', 'protein, total',
    'cholesterol, total', 'sodium lvl', 'neutro %', 'chol/hdlc ratio',
    't4, free', 'egfr if nonafricn am', 'hgb a1c glycosylated',
]
print("=== Noise-strip keys ===")
for t in tests:
    key = _NOISE.sub(" ", t).lower()
    key = re.sub(r"\s+", " ", key).strip().strip(",").strip()
    result = normalize_name(t)
    status = "OK" if result != t.strip().title() else "UNMAPPED"
    print(f"  [{status}] {t:35s} -> key=\"{key}\" -> {result}")
