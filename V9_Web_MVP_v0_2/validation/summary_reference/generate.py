from pathlib import Path
import sys
root=Path(__file__).resolve().parent;project=root.parents[1];sys.path.insert(0,str(project))
from web.services import invoke
source=project/'validation/icon_integration/decks';out=root/'decks';out.mkdir(exist_ok=True)
for name,sbu,partner in [('Actions_6','PETS','პეტფუდი — საერთაშორისო პარტნიორი და შინაური ცხოველების მომსახურების ცენტრი'),('Empty','PETS','PetFood')]:
 result=invoke('generate',(source/(name+'_input.xlsx')).read_bytes(),(project/'backend/V9_Beta2/Partner Logo.png').read_bytes(),sbu,partner_name=partner)
 assert result['ok'],result
 (out/(name+'.pptx')).write_bytes(result['pptx']);(out/(name+'_audit.zip')).write_bytes(result['audit']);print(name,'worker PASS',flush=True)
