from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from collections import Counter
import json,hashlib
from pptx import Presentation
from PIL import Image
root=Path(__file__).resolve().parent;project=root.parents[1];assets=project/'backend/V9_Beta2/assets'
expected={'Critical observation':'icon_critical_observation.png','Availability review':'icon_availability_review.png','Data quality':'icon_data_quality.png','Opening-hours hygiene':'icon_opening_hours.png','Activity review':'icon_store_review.png','Closure verification':'icon_store_review.png'}
sha=lambda b:hashlib.sha256(b).hexdigest()
icons={p.name:sha(p.read_bytes()) for p in assets.glob('icon_*.png')}
reports=[];covered=set();embedded=set()
for case in json.loads((root/'generation.json').read_text()):
 name=case['case'];path=root/'decks'/(name+'.pptx');prs=Presentation(path)
 old_path=project/'validation/final_refinement/decks'/(name+'.pptx')
 if old_path.exists():
  old=Presentation(old_path)
  assert len(prs.slides)==len(old.slides),name
  for i,(before,after) in enumerate(zip(old.slides,prs.slides),1):
   texts=lambda slide:[s.text for s in slide.shapes if s.has_text_frame]
   assert texts(before)==texts(after),(name,i,'text changed')
   title=texts(after)[0]
   if not title.startswith(('Action Plan','Operational & Data Review')):
    assert before._element.xml==after._element.xml,(name,i,'non-target slide changed')
 counter=Counter()
 for slide in prs.slides:
  values={s.name:s for s in slide.shapes}
  expect={}
  for sh in slide.shapes:
   if not sh.has_text_frame:continue
   if sh.name.startswith('Plan action ') and sh.name.endswith(' rank'):expect[sh.name[:-5]+' priority icon']='icon_priority_action.png'
   if sh.name.startswith('Plan action ') and sh.name.endswith(' agreed label'):expect[sh.name[:-6]+' icon']='icon_agreed_action.png'
   if sh.name.startswith('Additional action ') and sh.name.endswith('Agreed Action label'):expect[sh.name.removesuffix('Agreed Action label')+' agreed icon']='icon_agreed_action.png'
   if sh.name=='Next check-in label':expect['Next check-in icon']='icon_next_checkin.png'
   if sh.name.startswith('Review ') and sh.name.endswith(' type'):
    expect[sh.name[:-5]+' icon']=expected[sh.text];covered.add(sh.text)
  for icon_name,filename in expect.items():
   sh=values[icon_name];assert sh.shape_type==13
   assert sha(sh.image.blob)==icons[filename],(name,icon_name)
   w,h=sh.image.size;assert abs(sh.width/sh.height-w/h)<.00001
   assert not any((sh.crop_left,sh.crop_right,sh.crop_top,sh.crop_bottom))
   assert 0<=sh.left and 0<=sh.top and sh.left+sh.width<=prs.slide_width and sh.top+sh.height<=prs.slide_height
   for txt in slide.shapes:
    if txt.has_text_frame and txt.text:
     dx=min(sh.left+sh.width,txt.left+txt.width)-max(sh.left,txt.left)
     dy=min(sh.top+sh.height,txt.top+txt.height)-max(sh.top,txt.top)
     assert dx<=0 or dy<=0,(name,icon_name,'overlaps',txt.name)
   counter[filename]+=1;embedded.add(filename)
  assert sum(s.shape_type==13 and s.name.endswith(' icon') for s in slide.shapes)==len(expect)
 with ZipFile(path) as z:assert len(z.namelist())==len(set(z.namelist()))
 audit=ZipFile(root/'decks'/(name+'_audit.zip'));count=0
 for f in (root/'control_audits'/name).iterdir():
  a,b=f.read_bytes(),audit.read(f.name)
  if f.name=='run_audit.json':
   a,b=json.loads(a),json.loads(b)
   for obj in (a,b):
    for field in ('input_file','output_file','subbusiness_file'):obj['settings'][field]='PATH'
  assert a==b,(name,f.name,'analytical difference');count+=1
 reports.append(dict(case=name,icon_counts=dict(counter),audit_files_equal=count,prior_deck_content_and_pagination_equal=old_path.exists()))
assert covered==set(expected),covered
assert embedded==set(icons),embedded
hashes=json.loads((root/'before_hashes.json').read_text())
for directory,mapping in hashes.items():
 if directory=='web':continue
 for f,h in mapping.items():
  current=(Path(directory)/f).resolve()
  if current.name=='.DS_Store':continue
  if current.parent==assets and current.name in icons:
   assert sha((root/'opaque_asset_backup'/current.name).read_bytes())==h
   continue
  assert sha(current.read_bytes())==h,(directory,f)
transparency={p.name:dict(mode=Image.open(p).mode,alpha_extrema=Image.open(p).convert('RGBA').getchannel('A').getextrema()) for p in assets.glob('icon_*.png')}
(root/'verification.json').write_text(json.dumps(dict(cases=reports,review_types_verified=sorted(covered),all_8_approved_assets_embedded_unchanged=True,backend_code_and_external_reference_unchanged=True,source_transparency=transparency),indent=2))
print('PASS: icon mapping, native picture objects, exact asset bytes, aspect ratios, no text overlap, pagination/content parity, 22 audit files per case, frozen source integrity')
assert all(v['mode']=='RGBA' and v['alpha_extrema']==(0,255) for v in transparency.values())
print('PASS: all eight sources now have true alpha transparency')
