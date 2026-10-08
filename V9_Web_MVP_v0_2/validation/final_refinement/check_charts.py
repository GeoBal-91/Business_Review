from pathlib import Path
from zipfile import ZipFile
import json
root=Path(__file__).resolve().parent
report=[]
for name in ['Actions_1','Actions_2','Actions_6','FLOWERS_missing','Empty']:
 a=ZipFile(root.parent/'refinement/final'/(name+'.pptx'));b=ZipFile(root/'decks'/(name+'.pptx'))
 charts=lambda z:sorted(z.read(n) for n in z.namelist() if n.startswith('ppt/charts/chart') and n.endswith('.xml'))
 assert charts(a)==charts(b),name
 report.append(dict(case=name,unchanged_native_charts=len(charts(a))))
(root/'chart_parity.json').write_text(json.dumps(report,indent=2));print('All native chart XML unchanged in five before/after cases')
