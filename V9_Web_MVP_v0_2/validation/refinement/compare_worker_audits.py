from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
import json,sys
root=Path(__file__).resolve().parent
source=Path('/Users/giorgibalarjishvili/Desktop/V9_Web_MVP_v0_2')
sys.path.insert(0,str(source))
from web.services import invoke
report=[]
for case in json.loads((root/'final/generation.json').read_text()):
    name=case['case']
    result=invoke('generate',(root/'final'/f'{name}_input.xlsx').read_bytes(),(source/'backend/V9_Beta2/Partner Logo.png').read_bytes(),case['sbu'],partner_name='PetFood' if name!='FLOWERS_missing' else 'ყვავილების სახლი')
    assert result['ok'],result
    (root/'before'/f'{name}.pptx').write_bytes(result['pptx'])
    (root/'before'/f'{name}_audit.zip').write_bytes(result['audit'])
    checks=[]
    before,after=ZipFile(BytesIO(result['audit'])),ZipFile(root/'final'/f'{name}_audit.zip')
    assert set(before.namelist())==set(after.namelist())
    for file in before.namelist():
        a,b=before.read(file),after.read(file)
        if file=='web_run.json':
            a,b=json.loads(a),json.loads(b)
            assert a.pop('presentation_version')=='2026-09-19.1'
            assert b.pop('presentation_version')=='2026-09-22.1'
        elif file=='run_audit.json':
            a,b=json.loads(a),json.loads(b)
            for obj in (a,b):
                for k in ('input_file','output_file','subbusiness_file'):
                    obj['settings'][k]=Path(obj['settings'][k]).name
        assert a==b,(name,file)
        checks.append(file)
    report.append({'case':name,'identical_uploaded_bytes':True,'audit_files_matched':len(checks),'normalized':['temporary/configured file paths in run_audit.json','presentation_version in web_run.json only'],'files':checks})
    print(name,'audit parity PASS',flush=True)
(root/'audit_parity.json').write_text(json.dumps(report,indent=2))
