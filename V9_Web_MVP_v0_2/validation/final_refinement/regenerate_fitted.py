"""Regenerate only decks containing fitted opportunity titles, on saved identical inputs."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parent;project=root.parents[1]
sys.path.insert(0,str(project))
from web.services import invoke
for name in ['Actions_1','Actions_2','Actions_6','Zero_Zero']:
 display='პეტფუდი — საერთაშორისო პარტნიორი და შინაური ცხოველების მომსახურების ცენტრი' if name=='Actions_6' else 'PetFood'
 r=invoke('generate',(root/'decks'/(name+'_input.xlsx')).read_bytes(),(project/'backend/V9_Beta2/Partner Logo.png').read_bytes(),'PETS',partner_name=display)
 assert r['ok'],r
 (root/'decks'/(name+'.pptx')).write_bytes(r['pptx']);(root/'decks'/(name+'_audit.zip')).write_bytes(r['audit'])
 print(name,'actual worker PASS',flush=True)
