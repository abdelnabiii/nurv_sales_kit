# trace.py in.png out.svg [invert] [threshold] [crop x0,y0,x1,y1]
import sys, potrace, numpy as np
from PIL import Image
src,dst=sys.argv[1:3]; inv='invert' in sys.argv
thr=int(next((a for a in sys.argv[3:] if a.isdigit()),'128'))
im=Image.open(src).convert('L')
crop=next((a for a in sys.argv[3:] if a.count(',')==3),None)
if crop: im=im.crop(tuple(int(v) for v in crop.split(',')))
a=np.array(im)
bw = (a<thr) if inv else (a>=thr)          # True = ink
ys,xs=np.where(bw); x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
bw=bw[y0:y1+1,x0:x1+1]
bm=potrace.Bitmap(~bw if "flip" not in sys.argv else bw); path=bm.trace(turdsize=8,alphamax=1.0,opticurve=True,opttolerance=0.2)
parts=[]
for c in path:
    s=c.start_point; d=[f'M{s.x:.2f},{s.y:.2f}']
    for seg in c.segments:
        if seg.is_corner: d.append(f'L{seg.c.x:.2f},{seg.c.y:.2f}L{seg.end_point.x:.2f},{seg.end_point.y:.2f}')
        else: d.append(f'C{seg.c1.x:.2f},{seg.c1.y:.2f} {seg.c2.x:.2f},{seg.c2.y:.2f} {seg.end_point.x:.2f},{seg.end_point.y:.2f}')
    d.append('Z'); parts.append(''.join(d))
h,w=bw.shape
open(dst,'w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><path fill="currentColor" fill-rule="evenodd" d="{" ".join(parts)}"/></svg>')
print(dst,w,h,len(parts))
