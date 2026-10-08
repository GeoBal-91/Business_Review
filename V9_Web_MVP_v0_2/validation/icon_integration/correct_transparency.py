"""Recover exterior alpha only; never edit enclosed artwork or resize images."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import json,shutil,hashlib
root=Path(__file__).resolve().parent
assets=root.parents[1]/'backend/V9_Beta2/assets'
backup=root/'opaque_asset_backup';backup.mkdir(exist_ok=True)
out=root/'transparent_candidates';out.mkdir(exist_ok=True)
def morph(mask,r,expand):
 return np.asarray(Image.fromarray(mask.astype('uint8')*255).filter((ImageFilter.MaxFilter if expand else ImageFilter.MinFilter)(2*r+1)))>0
def nearest_values(a, source, target, radius=10):
 ys,xs=np.where(target); result=np.zeros((len(ys),3),dtype=float);done=np.zeros(len(ys),bool)
 for dy,dx in sorted(((dy,dx) for dy in range(-radius,radius+1) for dx in range(-radius,radius+1)),key=lambda d:d[0]**2+d[1]**2):
  yy=np.clip(ys+dy,0,a.shape[0]-1);xx=np.clip(xs+dx,0,a.shape[1]-1)
  take=(~done)&source[yy,xx];result[take]=a[yy[take],xx[take]];done[take]=True
  if done.all():break
 assert done.all()
 return ys,xs,result
stats={}
for file in sorted(assets.glob('icon_*.png')):
 original=backup/file.name
 if not original.exists():shutil.copy2(file,original)
 image=Image.open(original).convert('RGB');a=np.asarray(image).astype(float)
 # Only neutral, light pixels connected to the image perimeter may be background.
 candidate=(np.ptp(a,axis=2)<=14)&(a.min(axis=2)>=165)
 flood=Image.fromarray(candidate.astype('uint8')*255).copy();ImageDraw.floodfill(flood,(0,0),128)
 exterior=np.asarray(flood)==128;assert exterior.sum()>500000;silhouette=~exterior
 core=morph(silhouette,2,False)
 band=morph(silhouette,3,True)&~core
 ys,xs,F=nearest_values(a,core,band)
 clean_bg=exterior&~morph(silhouette,2,True)
 _,_,B=nearest_values(a,clean_bg,band)
 P=a[ys,xs];direction=F-B
 alpha=np.clip(np.sum((P-B)*direction,axis=1)/np.sum(direction*direction,axis=1),0,1)
 # Eliminate neutral checker texture in the exterior band. Real exterior contours
 # are dark navy or saturated colors; internal neutral artwork is protected.
 alpha[(np.ptp(P,axis=1)<=14)&(P.min(axis=1)>=165)]=0
 alpha[alpha<.035]=0
 alpha[alpha>.985]=1
 rgb=np.asarray(image).copy();A=core.astype('uint8')*255
 A[ys,xs]=np.rint(alpha*255).astype('uint8')
 partial=(alpha>0)&(alpha<1)
 # Partial coverage pixels contain baked background. Replace that contamination
 # with the nearest solid contour color, preserving coverage as true alpha.
 rgb[ys[partial],xs[partial]]=np.rint(F[partial]).astype('uint8')
 rgb[A==0]=0
 rgba=np.dstack((rgb,A));Image.fromarray(rgba).save(out/file.name)
 internal_light=core&(np.ptp(a,axis=2)<16)&(a.min(axis=2)>160)
 assert np.array_equal(rgb[core],a[core].astype('uint8'))
 assert (A[internal_light]==255).all()
 assert (A[~morph(silhouette,3,True)]==0).all()
 stats[file.name]={'dimensions':list(image.size),'alpha_range':[int(A.min()),int(A.max())], 'transparent_pixels':int((A==0).sum()),'partial_alpha_pixels':int(((A>0)&(A<255)).sum()),'unchanged_core_pixels':int(core.sum()),'preserved_internal_light_pixels':int(internal_light.sum()),'original_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'corrected_sha256':hashlib.sha256((out/file.name).read_bytes()).hexdigest()}
 print(file.name,stats[file.name],flush=True)
(root/'transparency_verification.json').write_text(json.dumps(stats,indent=2))
# Proof sheet: originals and corrected artwork at the same scale on light/dark.
files=sorted(out.glob('*.png'));sheet=Image.new('RGB',(1200,1600),'white');draw=ImageDraw.Draw(sheet)
for i,f in enumerate(files):
 for j,bg in enumerate(('#ffffff','#202b38','#fff8dd')):
  icon=Image.open(f).convert('RGBA');icon.thumbnail((290,175),Image.Resampling.LANCZOS)
  x=j*400;y=i*200;tile=Image.new('RGBA',(400,180),bg);tile.alpha_composite(icon,((400-icon.width)//2,0));sheet.paste(tile.convert('RGB'),(x,y));draw.text((x+10,y+181),f.name,fill='black')
sheet.save(root/'transparency_proof.png')
