# Filter AutoCAD PDF by OCG layer, per complete path object.
# Usage: oclayer.py in.pdf out.pdf keep|drop "L1|L2" [--noimg] [--notext] [--pages 2]
import sys, pypdf
from pypdf.generic import ContentStream, DecodedStreamObject, NameObject
src,dst,mode,names=sys.argv[1:5]; names=set(n for n in names.split('|') if n)
noimg='--noimg' in sys.argv; notext='--notext' in sys.argv
r=pypdf.PdfReader(src); w=pypdf.PdfWriter(clone_from=r)
PATH={b'm',b'l',b'c',b'v',b'y',b're',b'h'}
PAINT={b'S',b's',b'f',b'F',b'f*',b'B',b'B*',b'b',b'b*'}
TEXTOPS={b'Tj',b'TJ',b"'",b'"'}
for page in w.pages:
    props=page['/Resources'].get('/Properties',{})
    cs=ContentStream(page['/Contents'],w); out=[]; stack=[]; buf=[]
    def cur():
        l=[s for s in stack if s]; return l[-1] if l else '0'
    def ok(): return (cur() in names) if mode=='keep' else (cur() not in names)
    for operands,op in cs.operations:
        if op in PATH: buf.append((operands,op)); continue
        if op==b'W' or op==b'W*': buf.append((operands,op)); continue
        if op==b'n':
            out.extend(buf); out.append((operands,op)); buf=[]; continue  # clip paths always kept
        if op in PAINT:
            if ok(): out.extend(buf); out.append((operands,op))
            elif any(o in (b'W',b'W*') for _,o in buf):
                out.extend([b for b in buf]); out.append(([],b'n'))
            buf=[]; continue
        if op==b'BDC':
            nm=None
            if operands and operands[0]=='/OC':
                try: nm=str(props[operands[1]].get_object()['/Name'])
                except Exception: pass
            stack.append(nm)
        elif op==b'BMC': stack.append(None)
        elif op==b'EMC':
            if stack: stack.pop()
        if op==b'Do' and (noimg or not ok()): continue
        if op in TEXTOPS and (notext or not ok()): continue
        out.append((operands,op))
    cs.operations=out
    ref=w._add_object(DecodedStreamObject()); ref.get_object().set_data(cs.get_data())
    page[NameObject('/Contents')]=ref
w.write(dst)
