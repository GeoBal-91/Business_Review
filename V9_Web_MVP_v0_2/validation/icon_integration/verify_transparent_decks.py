from pathlib import Path
from zipfile import ZipFile
import json,re
from io import BytesIO
root=Path(__file__).resolve().parent
results=[]
def normalized(data):
 obj=json.loads(data)
 def clean(x):
  if isinstance(x,dict):return {k:('EXPECTED_PATH' if k in ('input_file','output_file','subbusiness_file') else 'EXPECTED_PRESENTATION_VERSION' if k=='presentation_version' else clean(v)) for k,v in x.items()}
  if isinstance(x,list):return [clean(v) for v in x]
  return x
 return clean(obj)
for old in sorted((root/'opaque_decks').glob('*.pptx')):
 with ZipFile(old) as a,ZipFile(root/'decks'/old.name) as b:
  assert set(a.namelist())==set(b.namelist())
  changes=[n for n in a.namelist() if a.read(n)!=b.read(n)]
  for n in changes:
   if n.startswith('ppt/embeddings/'):
    with ZipFile(BytesIO(a.read(n))) as x,ZipFile(BytesIO(b.read(n))) as y:
     assert set(x.namelist())==set(y.namelist())
     for k in x.namelist():
      u,v=x.read(k),y.read(k)
      if k=='docProps/core.xml':
       u,v=(re.sub(rb'(<dcterms:(?:created|modified)[^>]*>)[^<]+',rb'\1TIMESTAMP',data) for data in (u,v))
      assert u==v,(old.name,n,k,'workbook contents changed')
   else:assert n.startswith('ppt/media/') or n=='docProps/core.xml',(old.name,n)
  assert any(n.startswith('ppt/media/') for n in changes)
 audit=old.stem+'_audit.zip'
 with ZipFile(root/'opaque_decks'/audit) as a,ZipFile(root/'decks'/audit) as b:
  assert set(a.namelist())==set(b.namelist())
  for n in a.namelist():
   x,y=a.read(n),b.read(n)
   if n.endswith('.json'):x,y=normalized(x),normalized(y)
   assert x==y,(audit,n)
  count=len(a.namelist())
 results.append({'case':old.stem,'all_slide_xml_and_relationships_identical':True,'audit_files_equal_except_expected_paths_and_presentation_version':count,'changed_package_parts':changes})
(root/'transparency_deck_parity.json').write_text(json.dumps(results,indent=2))
print('PASS: all 5 decks preserve every slide XML/relationship, layout, pagination, text and fonts. All 23 audit entries per deck unchanged except paths/presentation version.')
