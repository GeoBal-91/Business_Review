from pathlib import Path
from zipfile import ZipFile
import json,hashlib
root=Path(__file__).resolve().parent
import sys
sys.path[:0]=[str(root.parents[1]/'backend/V9_Beta2'),str(root.parents[1])]
from config import Settings
from analysis import run_analysis
from business_classification import classify
from triage_exports import export_triage
report=[]
for case in json.loads((root/'decks/generation.json').read_text()):
    name=case['case']
    settings=Settings(input_file=root/'decks'/(name+'_input.xlsx'),partner_sbu='FLOWERS' if name=='FLOWERS_missing' else 'PETS',output_file=root/'control_unused.pptx')
    triage=classify(run_analysis(settings))
    folder=root/'control_audits'/name
    export_triage(triage,folder)
    b=ZipFile(root/'decks'/(name+'_audit.zip'))
    count=0
    for path in folder.iterdir():
        file=path.name;x,y=path.read_bytes(),b.read(file)
        if file=='run_audit.json':
            x,y=json.loads(x),json.loads(y)
            for obj in (x,y):
                for k in ('input_file','output_file','subbusiness_file'):obj['settings'][k]='PATH'
        assert x==y,(name,file)
        count+=1
    report.append(dict(case=name,audit_files_equal=count,identical_input_bytes=True))
external=Path('/Users/giorgibalarjishvili/Desktop/V9_Beta2')
manifest=json.loads((root.parent/'refinement/external_beta2_before.json').read_text())
changed=[p for p,h in manifest.items() if not (external/p).is_file() or hashlib.sha256((external/p).read_bytes()).hexdigest()!=h]
assert not changed,changed
(root/'controls.json').write_text(json.dumps(dict(audit_parity=report,external_frozen_files_unchanged=len(manifest)),indent=2))
print('Audit parity and external frozen reference PASS')
