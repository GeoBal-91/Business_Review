from pathlib import Path
import sys,json
root=Path(__file__).resolve().parent;project=root.parents[1];sys.path.insert(0,'/Users/giorgibalarjishvili/Desktop/V9_Beta2')
from config import Settings
from analysis import run_analysis
from business_classification import classify
from triage_exports import export_triage
for case in json.loads((root/'generation.json').read_text()):
 name=case['case'];source=project/'validation/icon_integration/decks'/(name+'_input.xlsx')
 result=classify(run_analysis(Settings(input_file=source,partner_sbu=case['sbu'])))
 export_triage(result,root/'frozen_controls'/name);print(name,'frozen controls generated',flush=True)
