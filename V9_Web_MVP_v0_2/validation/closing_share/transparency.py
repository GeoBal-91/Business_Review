from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib
root=Path(__file__).resolve().parent
# Reuse only the tested neighbourhood helpers; no icon assets are processed.
source=(root.parent/'icon_integration/correct_transparency.py').read_text()
helpers=source[source.index('def morph'):source.index('stats={}')] 
exec(helpers)
original=root/'Thank_You_original.png';im=Image.open(original).convert('RGB');a=np.asarray(im).astype(float)
# This artwork contains only saturated yellow on a neutral checkerboard.
# Neutral areas include the opening inside the yellow pin, which is also background.
silhouette=np.ptp(a,axis=2)>20
core=morph(silhouette,2,False);band=morph(silhouette,3,True)&~core
ys,xs,F=nearest_values(a,core,band)
P=a[ys,xs]
# Neutral backgrounds have zero chroma: recover coverage without inheriting
# the varying grey/white luminance of the baked checkerboard.
Fc=F-F.mean(axis=1,keepdims=True);Pc=P-P.mean(axis=1,keepdims=True)
alpha=np.clip((Pc*Fc).sum(axis=1)/(Fc*Fc).sum(axis=1),0,1)
alpha[np.ptp(P,axis=1)<=5]=0;alpha[alpha<.02]=0;alpha[alpha>.99]=1
rgb=np.asarray(im).copy();A=core.astype('uint8')*255;A[ys,xs]=np.rint(alpha*255).astype('uint8')
partial=(alpha>0)&(alpha<1);rgb[ys[partial],xs[partial]]=np.rint(F[partial]).astype('uint8');rgb[A==0]=0
assert np.array_equal(rgb[A==255],np.asarray(im)[A==255])
assert np.all(A[np.ptp(a,axis=2)<=5]==0)
assert not ((A>0)&(np.ptp(rgb.astype(float),axis=2)<30)).any()
corrected=Image.fromarray(np.dstack((rgb,A)));corrected.save(root/'Thank_You.png')
stats={'dimensions':list(im.size),'alpha_range':[int(A.min()),int(A.max())],'transparent_pixels':int((A==0).sum()),'antialiased_pixels':int(((A>0)&(A<255)).sum()),'opaque_artwork_pixels_unchanged':int((A==255).sum()),'all_neutral_checkerboard_pixels_transparent':True,'original_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'corrected_sha256':hashlib.sha256((root/'Thank_You.png').read_bytes()).hexdigest()}
(root/'transparency.json').write_text(json.dumps(stats,indent=2));print(stats)
for label,bg in [('white','#ffffff'),('dark','#202b38')]:
 proof=Image.new('RGBA',im.size,bg);proof.alpha_composite(corrected);proof.convert('RGB').save(root/f'transparency_{label}.png')
