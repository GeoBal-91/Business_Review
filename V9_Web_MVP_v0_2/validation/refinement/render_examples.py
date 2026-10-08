from pathlib import Path
import subprocess,json,os
root=Path(__file__).resolve().parent
bin=Path('/Users/giorgibalarjishvili/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override')
previews=root/'previews';previews.mkdir(exist_ok=True)
for case in json.loads((root/'final/generation.json').read_text()):
    name=case['case'];pdf=previews/(name+'.pdf');pptx=root/'final'/(name+'.pptx')
    if True:
        subprocess.run([str(bin/'soffice'),'--headless','--convert-to','pdf','--outdir',str(previews),str(pptx)],env=dict(os.environ,FONTCONFIG_FILE=str(root/'fonts.conf')),check=True)
    for item in case['affected']:
        n=item['page'];dest=previews/f'{name}-{n}'
        if dest.with_suffix('.png').exists() and dest.with_suffix('.png').stat().st_mtime>pdf.stat().st_mtime:continue
        subprocess.run([str(bin/'pdftoppm'),'-f',str(n),'-l',str(n),'-scale-to','1600','-png','-singlefile',str(pdf),str(dest)],check=True)
    print('Rendered',name,flush=True)
