# Extract vector paths with layer + CTM from AutoCAD PDF -> JSON
import sys, json, pypdf
from pypdf.generic import ContentStream
src,dst=sys.argv[1:3]
r=pypdf.PdfReader(src); pages=[]
def mul(a,b):
    return [a[0]*b[0]+a[1]*b[2], a[0]*b[1]+a[1]*b[3], a[2]*b[0]+a[3]*b[2], a[2]*b[1]+a[3]*b[3], a[4]*b[0]+a[5]*b[2]+b[4], a[4]*b[1]+a[5]*b[3]+b[5]]
for pi,page in enumerate(r.pages):
    props=page['/Resources'].get('/Properties',{}); H=float(page.mediabox.height)
    cs=ContentStream(page['/Contents'],r); ctm=[1,0,0,1,0,0]; st=[]; lw=1; lst=[]
    layers=[]; path=[]; cur=None; out=[]
    def T(x,y): return (ctm[0]*x+ctm[2]*y+ctm[4], H-(ctm[1]*x+ctm[3]*y+ctm[5]))
    for ops,op in cs.operations:
        if op==b'q': st.append((ctm[:],lw)); continue
        if op==b'Q': ctm,lw=st.pop() if st else (ctm,lw); continue
        if op==b'cm': ctm=mul([float(v) for v in ops],ctm); continue
        if op==b'w': lw=float(ops[0]); continue
        if op==b'BDC':
            nm=None
            if ops and ops[0]=='/OC':
                try: nm=str(props[ops[1]].get_object()['/Name'])
                except Exception: pass
            layers.append(nm); continue
        if op==b'BMC': layers.append(None); continue
        if op==b'EMC':
            if layers: layers.pop()
            continue
        if op==b'm': path.append(['M',*T(float(ops[0]),float(ops[1]))]); continue
        if op==b'l': path.append(['L',*T(float(ops[0]),float(ops[1]))]); continue
        if op==b'c':
            p=[float(v) for v in ops]; path.append(['C',*T(p[0],p[1]),*T(p[2],p[3]),*T(p[4],p[5])]); continue
        if op==b're':
            x,y,w_,h_=[float(v) for v in ops]
            path += [['M',*T(x,y)],['L',*T(x+w_,y)],['L',*T(x+w_,y+h_)],['L',*T(x,y+h_)],['Z']]; continue
        if op==b'h': path.append(['Z']); continue
        if op in (b'W',b'W*'): continue
        if op==b'n': path=[]; continue
        if op in (b'S',b's',b'f',b'F',b'f*',b'B',b'B*',b'b',b'b*'):
            if path:
                L=[s for s in layers if s]; lay=L[-1] if L else '0'
                xs=[v for seg in path for v in seg[1::2] if isinstance(v,float)]
                ys=[v for seg in path for v in seg[2::2] if isinstance(v,float)]
                sc=(abs(ctm[0])+abs(ctm[3]))/2
                out.append({'layer':lay,'op':op.decode(),'d':path,'lw':lw*sc,
                            'bbox':[min(xs),min(ys),max(xs),max(ys)],'n':len(path)})
            path=[]; continue
    pages.append({'w':float(page.mediabox.width),'h':H,'paths':out})
json.dump(pages,open(dst,'w'))
for i,p in enumerate(pages):
    from collections import Counter
    print(i+1, len(p['paths']), Counter(x['layer'] for x in p['paths']).most_common())
