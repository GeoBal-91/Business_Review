"""Verify every byte of the uploaded frozen baseline, including assets/history."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
manifest = json.loads((root/'baseline_manifest.json').read_text())
base = root/'backend'/'V9_Beta2'
errors = []
for name, expected in manifest['files'].items():
    path = base/name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        errors.append(name)
extras = [str(p.relative_to(base)) for p in base.rglob('*') if p.is_file()
          and '__pycache__' not in p.parts and p.suffix != '.pyc'
          and str(p.relative_to(base)) not in manifest['files']]
if errors or extras:
    print('Baseline integrity FAILED:', ', '.join(errors + extras))
    sys.exit(1)
print(f"PASS: all {len(manifest['files'])} baseline files match the uploaded V9_Beta2.zip exactly.")
