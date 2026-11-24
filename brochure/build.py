#!/usr/bin/env python3
"""Assemble the nurv investor brochure.

Inlines the SVG assets (logos, plans, map) into src/brochure.html and writes
build/brochure.html, adding the identical running header and footer
(Jalour logo, legal line, page number) to every page.

Run:  python3 build.py && node render.js
"""
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
LEGAL = ("For information only. Not an offer or a contract. Visuals are artist's impressions; "
         "plans, areas and specifications are indicative and subject to change.")


def rd(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()


def strip(svg):
    return re.sub(r"<!--.*?-->", "", svg, flags=re.S).strip()


# nurv. wordmark (all white per client; the full stop is kept as its own sub-path).
nurv = strip(rd("assets/logo/nurv.svg"))
d = re.search(r' d="([^"]+)"', nurv).group(1)
subs = [s.strip() for s in re.split(r"(?=M)", d) if s.strip()]


def minx(s):
    return min(float(v) for v in re.findall(r"(-?\d+\.?\d*),", s))


dot = max(subs, key=minx)
letters = " ".join(s for s in subs if s is not dot)
vb = re.search(r'viewBox="([^"]+)"', nurv).group(1)
NURV = (f'<svg viewBox="{vb}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="nurv.">'
        f'<path fill="currentColor" fill-rule="evenodd" d="{letters}"/>'
        f'<path fill="currentColor" d="{dot}"/></svg>')
JALOUR = strip(rd("assets/logo/jalour.svg")).replace("<svg ", '<svg role="img" aria-label="Jalour" ', 1)
MEADIS = strip(rd("assets/logo/meadis.svg")).replace("<svg ", '<svg role="img" aria-label="Meadis Group" ', 1)

html = rd("src/brochure.html")
pages = html.count('<section class="page')
HEADER = ('<div class="hdr"><span class="a">Jalour</span><span class="b">Shorouk Mall</span>'
          '<span class="c">2026</span></div>')
html = html.replace("{{HEADER}}", HEADER)

count = 0


def footer(_):
    global count
    count += 1
    return (f'<div class="ftr"><span class="logo">{JALOUR}</span><span class="legal">{LEGAL}</span>'
            f'<span class="pg">{count:02d} / {pages:02d}</span></div>')


html = re.sub(r"\{\{FOOTER\}\}", footer, html)
html = html.replace("{{NURV_LOGO}}", NURV).replace("{{JALOUR_LOGO}}", JALOUR).replace("{{MEADIS_LOGO}}", MEADIS)
html = html.replace("{{MAP}}", strip(rd("src/map.svg")))
for i in range(1, 6):
    html = html.replace("{{PLAN%d}}" % i, strip(rd(f"assets/plans/plan{i}.svg")))

assert "{{" not in html, "unreplaced token"
assert count == pages, "every page needs a footer"
os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
open(os.path.join(ROOT, "build", "brochure.html"), "w", encoding="utf-8").write(html)
# Colour variants: same document plus a colour theme (colours only).
for name in ("light", "grey", "blue"):
    themed = html.replace("</head>", "<style>\n" + rd(f"src/{name}.css") + "</style>\n</head>", 1)
    open(os.path.join(ROOT, "build", f"brochure-{name}.html"), "w", encoding="utf-8").write(themed)
print("pages", pages, "footers", count)

# One-page fact sheet (A4), in the same four colour themes.
for src_name, out in (("factsheet.html", "factsheet"), ("factsheet-ar.html", "factsheet-ar")):
    fs = rd(f"src/{src_name}").replace("{{JALOUR_LOGO}}", JALOUR)
    assert "{{" not in fs
    open(os.path.join(ROOT, "build", f"{out}.html"), "w", encoding="utf-8").write(fs)
    for name in ("light", "grey", "blue"):
        themed = fs.replace("</head>", "<style>\n" + rd(f"src/{name}.css") + "</style>\n</head>", 1)
        open(os.path.join(ROOT, "build", f"{out}-{name}.html"), "w", encoding="utf-8").write(themed)

# G+3 variant (brochure + fact sheet), dark and light only.
g3 = rd("src/brochure-g3.html")
g3 = g3.replace("{{HEADER}}", HEADER)
g3_pages = g3.count('<section class="page')
_n = 0
def _g3footer(_):
    global _n
    _n += 1
    return (f'<div class="ftr"><span class="logo">{JALOUR}</span><span class="legal">{LEGAL}</span>'
            f'<span class="pg">{_n:02d} / {g3_pages:02d}</span></div>')
g3 = re.sub(r"\{\{FOOTER\}\}", _g3footer, g3)
g3 = g3.replace("{{NURV_LOGO}}", NURV).replace("{{JALOUR_LOGO}}", JALOUR).replace("{{MEADIS_LOGO}}", MEADIS)
g3 = g3.replace("{{MAP}}", strip(rd("src/map.svg")))
for i in range(1, 6):
    g3 = g3.replace("{{PLAN%d}}" % i, strip(rd(f"assets/plans/plan{i}.svg")))
assert "{{" not in g3
fs3 = rd("src/factsheet-g3.html").replace("{{JALOUR_LOGO}}", JALOUR)
assert "{{" not in fs3
for out, doc in (("brochure-g3", g3), ("factsheet-g3", fs3)):
    open(os.path.join(ROOT, "build", f"{out}.html"), "w", encoding="utf-8").write(doc)
    lt = doc.replace("</head>", "<style>\n" + rd("src/light.css") + "</style>\n</head>", 1)
    open(os.path.join(ROOT, "build", f"{out}-light.html"), "w", encoding="utf-8").write(lt)
print("g3 pages", g3_pages)
