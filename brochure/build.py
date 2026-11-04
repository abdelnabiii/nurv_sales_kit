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


# nurv. wordmark: the full stop (rightmost sub-path) takes the nurv. accent colour.
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
        f'<path fill="var(--accent)" d="{dot}"/></svg>')
JALOUR = strip(rd("assets/logo/jalour.svg")).replace("<svg ", '<svg role="img" aria-label="Jalour" ', 1)
MEADIS = strip(rd("assets/logo/meadis.svg")).replace("<svg ", '<svg role="img" aria-label="Meadis Group" ', 1)

html = rd("src/brochure.html")
pages = html.count('<section class="page')
HEADER = ('<div class="hdr"><span class="a">Jalour</span><span class="b">nurv</span>'
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
print("pages", pages, "footers", count)
