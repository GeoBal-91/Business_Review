from pathlib import Path
import hashlib,json,zipfile,importlib.metadata,sys,shutil
p=Path.cwd(); out=p/'releases';out.mkdir(exist_ok=True)
stage=p/'validation/final_release/package_stage/V9_Web_MVP_v0_2';stage.mkdir(parents=True,exist_ok=True)
files=[p/n for n in ['app.py','web_style.css','web_config.toml','Start.command','requirements.txt','requirements-lock.txt','README.md','.streamlit/config.toml']]
files+=list((p/'web').glob('*.py'))
b=p/'backend/V9_Beta2'
files += [f for f in b.iterdir() if f.is_file() and (f.suffix in ('.py','.xlsx','.png') or f.name.startswith('requirements'))]
files += [f for f in (b/'assets').rglob('*') if f.is_file() and f.name!='.DS_Store']
for f in files:
 d=stage/f.relative_to(p);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,d)
lines=[];drift=[]
for line in (p/'requirements-lock.txt').read_text().splitlines():
 name,old=line.split('==');actual=importlib.metadata.version(name);lines.append(name+'=='+actual)
 if old!=actual:drift.append({'package':name,'historical_lock':old,'tested':actual})
(stage/'requirements-final-tested.txt').write_text('\n'.join(lines)+'\n')
(stage/'RELEASE_README.md').write_text('''# Final release — 6 October 2026

Only Cover and Thank You were redesigned. Analytical code and all other approved slides are preserved. Partner Share Evolution remains 20.0 cm wide.

## Run

Validation used Python 3.14.7. Use the matching tested dependency list:

```
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-final-tested.txt
.venv/bin/python -m streamlit run app.py
```

The retained original README/launcher mention the earlier Python 3.12 setup. This release note records the actual final validation environment. The historical lock is preserved; requirements-final-tested.txt records the installed versions used for validation. A fresh dependency installation has not been tested. Fonts Montserrat and Noto Sans Georgian must be available for matching rendering. PowerPoint rendering was not independently tested; visual QA used LibreOffice.

The application retains its existing localhost binding. Hosting configuration and deployment remain outside this presentation release.

All runtime Python modules, benchmark workbook, logos and approved transparent PNG assets are included. Development tests, frozen historical snapshots, generated presentations/audits, temporary renders and virtual environments are excluded. Full validation evidence remains in the source workspace under validation/final_release.

## Validation disposition

37/37 web/presentation/UI tests passed. Five actual worker decks passed presentation preservation, icons, dynamic fields and audit checks. All 110 analytical audit files matched the external engine on identical inputs and explicit SBU after normalizing temporary paths and the independently verified default-SBU-only config hash.

Historical suites: bundled backend 299/301 passed (two old logo hash expectations); external reference 295/301 passed (six historical config/sample snapshot expectations). These differences existed before this task. Neither baseline was modified to force these tests to pass. No new analytical regression was found.

SOURCE_MANIFEST_SHA256.json records SHA-256 for every packaged file except the manifest itself. Its own SHA-256 is recorded beside the ZIP in the release metadata.
''')
sha=lambda x:hashlib.sha256(x).hexdigest()
manifest={str(f.relative_to(stage)):sha(f.read_bytes()) for f in sorted(stage.rglob('*')) if f.is_file() and f.name!='SOURCE_MANIFEST_SHA256.json'}
(stage/'SOURCE_MANIFEST_SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
archive=out/'V9_Web_MVP_v0_2_FINAL_2026-10-06.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(stage.rglob('*')):
  if f.is_file():z.write(f,Path(stage.name)/f.relative_to(stage))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for name,h in manifest.items():assert sha(z.read(stage.name+'/'+name))==h
 assert not any(any(x in n.split('/') for x in ('__pycache__','.venv','tests','validation','reference')) for n in z.namelist())
 extract=p/'validation/final_release/package_extracted';z.extractall(extract)
h=sha(archive.read_bytes());(out/(archive.name+'.sha256')).write_text(h+'  '+archive.name+'\n')
metadata={'zip':str(archive),'zip_sha256':h,'source_manifest_sha256':sha((stage/'SOURCE_MANIFEST_SHA256.json').read_bytes()),'packaged_files':len(manifest),'python':sys.version,'dependency_lock_differences':drift,'archive_integrity':'PASS','manifest_integrity':'PASS'}
(out/'FINAL_RELEASE_METADATA.json').write_text(json.dumps(metadata,indent=2)+'\n');print(json.dumps(metadata,indent=2))
