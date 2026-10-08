from pathlib import Path
import sys,json
root=Path(__file__).resolve().parent;project=root.parents[1];sys.path.insert(0,str(project))
from web.services import invoke
for case in json.loads((root/'generation.json').read_text()):
 name=case['case'];out=root/'decks'
 result=invoke('generate',(out/(name+'_input.xlsx')).read_bytes(),(project/'backend/V9_Beta2/Partner Logo.png').read_bytes(),case['sbu'],partner_name=case['partner_name'])
 assert result['ok'],result
 (out/(name+'.pptx')).write_bytes(result['pptx']);(out/(name+'_audit.zip')).write_bytes(result['audit'])
 print(name,'actual worker regenerated with transparent approved icons',flush=True)
