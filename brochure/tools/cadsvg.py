# Render filtered CAD paths to clean SVG. Usage: cadsvg.py cad.json page out.svg [debug]
import json,sys
J=json.load(open(sys.argv[1])); pi=int(sys.argv[2]); outf=sys.argv[3]; debug=len(sys.argv)>4
PG=J[pi-1]; H=PG['h']; ROT = pi in (1,3,4)   # /Rotate 270
def tp(x,y): return (y, -x) if ROT else (x,y)
P=[]
for p in PG['paths']:
    d=[]; xs=[]; ys=[]
    for seg in p['d']:
        if seg[0]=='Z': d.append(['Z']); continue
        v=seg[1:]; nv=[]
        for i in range(0,len(v),2):
            a,b=tp(v[i],v[i+1]); nv+= [a,b]; xs.append(a); ys.append(b)
        d.append([seg[0]]+nv)
    q=dict(p); q['d']=d; q['bbox']=[min(xs),min(ys),max(xs),max(ys)]; P.append(q)
KEEP={'I-SECT-HTCH','WAL-1','I-SECT-DIMS','NEW WALLS','CLOM','Stairs','I-STRS-HRAL','walls','A-DOR','A-Door','A-Flor-Pfix','THIET-BI','A-FURN-FIXD','A-ELEV-BACK','I-COLS-CONC','0'}
nw=[p for p in P if p['layer']=='NEW WALLS']
bx=[min(p['bbox'][0] for p in nw),min(p['bbox'][1] for p in nw),max(p['bbox'][2] for p in nw),max(p['bbox'][3] for p in nw)]
X0,Y0,X1,Y1=bx; W=X1-X0; Hh=Y1-Y0; small=max(W,Hh)*0.012
def keep(p):
    if p['layer'] not in KEEP: return False
    b=p['bbox']
    if not (b[0]>=X0-1 and b[2]<=X1+1 and b[1]>=Y0-1 and b[3]<=Y1+1): return False
    sz=max(b[2]-b[0],b[3]-b[1])
    # arrows: small closed 3-4 vertex shapes on Stairs/0 layers
    if p['layer']!='CLOM' and sz<small*0.5: return False
    # SHX dimension/label strokes: tiny open polylines on generic layers
    if p['layer'] in ('0','walls') and sz<small*0.9: return False
    if p['layer']=='I-SECT-DIMS' and sz<small*1.2: return False
    return True
ps=[p for p in P if keep(p)]
# drop small isolated clusters (parking arrows, stray marks) on annotation-prone layers
def clusters(items,tol):
    par=list(range(len(items)))
    def f(i):
        while par[i]!=i: par[i]=par[par[i]]; i=par[i]
        return i
    bb=[p['bbox'] for p in items]
    order=sorted(range(len(items)),key=lambda i:bb[i][0])
    for a_i,a in enumerate(order):
        for b in order[a_i+1:]:
            if bb[b][0]>bb[a][2]+tol: break
            if bb[b][1]<=bb[a][3]+tol and bb[a][1]<=bb[b][3]+tol: par[f(a)]=f(b)
    g={}
    for i in range(len(items)): g.setdefault(f(i),[]).append(i)
    return g.values()
cand=[p for p in ps if p['layer'] in ('Stairs','0','walls','I-SECT-DIMS')]
drop=set()
for g in clusters(cand, small*0.35):
    xs0=min(cand[i]['bbox'][0] for i in g); xs1=max(cand[i]['bbox'][2] for i in g)
    ys0=min(cand[i]['bbox'][1] for i in g); ys1=max(cand[i]['bbox'][3] for i in g)
    if max(xs1-xs0,ys1-ys0)<small*2.2: drop.update(id(cand[i]) for i in g)
ps=[p for p in ps if id(p) not in drop]
COL={'WAL-1':'#0cf','I-SECT-DIMS':'#fa0','NEW WALLS':'#fff','CLOM':'#f00','Stairs':'#0f0','I-STRS-HRAL':'#0ff','walls':'#ff0','A-DOR':'#f0f','A-Door':'#f80','A-Flor-Pfix':'#8f8','THIET-BI':'#f88','A-FURN-FIXD':'#88f','0':'#c66','I-COLS-CONC':'#faa','A-ELEV-BACK':'#afa'}
def D(p): return ' '.join('Z' if s[0]=='Z' else s[0]+' '.join('%.2f'%x for x in s[1:]) for s in p['d'])
pad=W*0.02
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{X0-pad:.1f} {Y0-pad:.1f} {W+2*pad:.1f} {Hh+2*pad:.1f}" width="1400" height="{1400*(Hh+2*pad)/(W+2*pad):.0f}" style="--plan-wall:#E8E8E8;--plan-thin:#7C828C;--plan-hatch:#3A3F47;--plan-plot:#5A6070;background:#000" fill-rule="evenodd" stroke-linejoin="round" stroke-linecap="round">']
u=W/1000.0
def style(p):
    b=p['bbox']; full=(b[2]-b[0])>W*0.6 and (b[3]-b[1])>Hh*0.6
    L=p['layer']; filled=p['op'] in ('f','F','f*','b','B','b*','B*')
    if full: return 'plot', 'none', 'var(--plan-plot)', 0.9*u, f' stroke-dasharray="{6*u:.2f} {4*u:.2f}"'
    if L=='CLOM': return 'col', 'none','var(--plan-wall)',1.1*u,''
    if L in ('NEW WALLS','walls','Stairs','WAL-1'): return 'wall', 'none','var(--plan-wall)',1.1*u,''
    if L in ('I-STRS-HRAL','I-SECT-HTCH'): return 'hatch','none','var(--plan-hatch)',0.5*u,''
    return 'thin','none','var(--plan-thin)',0.6*u,''
for p in ps:
    if debug:
        c=COL.get(p['layer'],'#fff'); fill=c if p['op'] in ('f','F','f*','b','B','b*','B*') else 'none'
        svg.append(f'<path d="{D(p)}" fill="{fill}" stroke="{c}" stroke-width="{max(p["lw"],W/1400*0.6):.3f}"/>'); continue
    cls,fill,stroke,sw,extra=style(p)
    svg.append(f'<path class="{cls}" d="{D(p)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.3f}"{extra}/>')
svg.append('</svg>'); open(outf,'w').write('\n'.join(svg)); print(pi,len(ps),'W,H',round(W,1),round(Hh,1))
