#!/usr/bin/env python3
"""Build the Shorouk Mall Investment Study (A4 report) as HTML: dark and light versions.

Numbers come from model.py; market data from the DAMAK market research (Dec 2024).
Render with: node ../brochure/render.js <out.pdf> "" <abs path to html>   (see build.sh)
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model as M

BRO = os.path.join(HERE, "..", "brochure")
A = M.ASSUMPTIONS


def rd(p):
    return open(p, encoding="utf-8").read()


JALOUR = re.sub(r"<!--.*?-->", "", rd(os.path.join(BRO, "assets/logo/jalour.svg")), flags=re.S).strip()

# ------------------------------------------------------------------ numbers
R = {}
for var, v in M.VARIANTS.items():
    R[var] = {k: M.run(var, y) for k, y in (("low", v["rent_low"]), ("mid", (v["rent_low"] + v["rent_high"]) / 2), ("high", v["rent_high"]))}
RB = M.rent_build()


def m(x, d=1):
    return f"{x:,.{d}f}"


def pct(x, d=1):
    return f"{x * 100:.{d}f}%"


def rng(lo, hi, f=m, sep="–"):
    a, b = f(lo), f(hi)
    if lo < 0 or hi < 0:
        sep = " to "
    return a if a == b else f"{a}{sep}{b}"


# ------------------------------------------------------------------ market data (DAMAK, Dec 2024)
COMPETITORS = [
    ("Le Monde Mall", "Dar Developments", "1,110", "Commercial and medical"),
    ("Rio Business Hub", "Rio Development", "1,440", "Ground commercial; offices and clinics above"),
    ("The Gate Mall", "Gate Group", "1,550", "G+1 commercial; offices and medical above"),
    ("Sedra Mall", "Alchemy Development", "1,725", "Educational, medical, commercial"),
    ("Orium Mall", "Z Group", "1,800", "G+1 shops; finished clinics; offices"),
    ("City Club", "Aswaq Development", "2,360", "All commercial"),
    ("Arena Mall", "Aswaq Development", "3,200", "G+1 commercial; offices; medical"),
    ("Mercado Mall", "Aswaq Development", "3,400", "All commercial, with hypermarket"),
    ("Town Center Mall", "Value Developments", "4,000", "Commercial, offices, clinics"),
    ("Eagle Hub", "Eagle Group", "5,000", "G+1 commercial; medical and offices"),
    ("Premier Mall", "Rio Development", "5,000", "Commercial; finished offices and clinics"),
    ("The Square Mall", "Value Developments", "5,300", "Commercial; offices and medical"),
    ("Jaya East", "Egyptian Developers", "6,000", "Commercial; medical; cinema and kids' area"),
    ("Eagle 85", "Eagle Group", "6,130", "G+1 shops; medical; offices"),
    ("Solaria Mall", "Aswaq Development", "6,400", "G+1 commercial; medical; offices"),
    ("Value Mall", "Value Developments", "6,666", "Commercial"),
    ("The Palace Mall", "Dar Developments", "12,600", "G+1 commercial; offices and medical"),
]
RETAIL_PSM = [  # primary retail, average asking price per sqm (EGP), Dec 2024
    ("Le Monde", 73900), ("Sedra", 75000), ("The Gate", 80000), ("Eagle 85", 94886), ("Arena (shell)", 100703),
    ("Town Center", 111374), ("Eagle Hub", 116857), ("Mercado", 117113), ("The Palace", 121968),
    ("City Club", 126894), ("Solaria", 130875), ("Jaya East", 145409), ("The Square", 153968),
    ("Premier", 160190), ("Orium", 166265), ("Rio Hub", 200000), ("Value Mall 1", 214492), ("Arena (finished)", 227613),
]
RENT_COMPS = [  # EGP per sqm per month, Dec 2024
    ("Value Mall 1", "Retail", "318–500"), ("Orium Mall", "Retail, fully finished", "759–798"),
    ("Eagle Mall 85", "Office", "333"), ("Town Center", "Clinic", "293"),
]
CONNECT = [("Madinaty", "5 km", "8 min"), ("Cairo–Suez Road", "2 km", "4 min"), ("Ring Road", "6 km", "9 min"),
           ("Cairo–Ismailia Road", "9 km", "12 min"), ("New Cairo", "24 km", "27 min"),
           ("Cairo International Airport", "31 km", "30 min"), ("New Administrative Capital", "19 km", "20 min")]

# ------------------------------------------------------------------ building blocks
PAGES = []


ZOOM = {"Executive summary": 1.17, "Rent basis": 1.13, "Price and payment options": 1.2, "Contact": 1.3, "Market: El Sherouk": 1.14, "Market: competition": 1.10, "Market: catchment and demand": 1.2, "The asset": 1.2,
        "Feasibility: results by payment option": 1.04, "Asset value and cash flow": 1.3, "Assumptions and risks": 1.2,
        "Market: pricing benchmarks": 1.2, "Concept": 1.24, "Returns": 1.2}


def page(title, body, num=True):
    PAGES.append((title, body, num))


def table(head, rows, cls="", align=None):
    align = align or ["l"] + ["r"] * (len(head) - 1)
    h = "".join(f'<th class="{a}">{c}</th>' for c, a in zip(head, align))
    b = "".join("<tr>" + "".join(f'<td class="{a}">{c}</td>' for c, a in zip(r, align)) + "</tr>" for r in rows)
    return f'<table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


def kpis(items, cols=None):
    cols = cols or len(items)
    return f'<div class="kpi" style="grid-template-columns:repeat({cols},1fr)">' + "".join(
        f"<div><b>{v}</b><span>{l}</span></div>" for v, l in items) + "</div>"


def bars(data, unit="", maxv=None, hl=None, w=300, rowh=13.5, labw=96, fmt=lambda v: f"{v:,.0f}"):
    maxv = maxv or max(v for _, v in data)
    H = len(data) * rowh + 4
    out = [f'<svg viewBox="0 0 {w} {H}" width="100%" class="bars">']
    for i, (lab, v) in enumerate(data):
        y = i * rowh + 2
        bw = (w - labw - 70) * v / maxv
        c = "var(--blue)" if (hl and lab in hl) else "var(--bar)"
        out.append(f'<text x="{labw - 6}" y="{y + 8.6}" text-anchor="end" class="bl">{lab}</text>')
        out.append(f'<rect x="{labw}" y="{y + 1}" width="{bw:.1f}" height="{rowh - 4}" fill="{c}"/>')
        out.append(f'<text x="{labw + bw + 5:.1f}" y="{y + 8.6}" class="bv">{fmt(v)}{unit}</text>')
    out.append("</svg>")
    return "".join(out)


def columns(series, w=500, h=150, fmt=lambda v: f"{v:,.0f}", labels=None, neg=True):
    """Simple column chart; series = list of (label, value)."""
    vals = [v for _, v in series]
    hi, lo = max(vals + [0]), min(vals + [0])
    span = (hi - lo) or 1
    pad_t, pad_b = 12, 16
    ph = h - pad_t - pad_b
    zero = pad_t + ph * hi / span
    bw = (w - 10) / len(series)
    out = [f'<svg viewBox="0 0 {w} {h}" width="100%" class="cols">',
           f'<line x1="0" x2="{w}" y1="{zero:.1f}" y2="{zero:.1f}" stroke="var(--rule2)" stroke-width="0.6"/>']
    for i, (lab, v) in enumerate(series):
        x = 5 + i * bw
        bh = ph * abs(v) / span
        y = zero - bh if v >= 0 else zero
        c = "var(--blue)" if v >= 0 else "var(--neg)"
        out.append(f'<rect x="{x + 2:.1f}" y="{y:.1f}" width="{bw - 4:.1f}" height="{bh:.1f}" fill="{c}"/>')
        ty = y - 3 if v >= 0 else y + bh + 8
        out.append(f'<text x="{x + bw / 2:.1f}" y="{ty:.1f}" text-anchor="middle" class="bv">{fmt(v)}</text>')
        out.append(f'<text x="{x + bw / 2:.1f}" y="{h - 3}" text-anchor="middle" class="bl">{lab}</text>')
    out.append("</svg>")
    return "".join(out)


DISC = ('<p class="disc">Projections only. Figures are estimates based on the assumptions stated in this study, are rounded, '
        'and are not guaranteed. This study is not an offer or a contract.</p>')

# ================================================================== PAGES
V = sys.argv[1] if len(sys.argv) > 1 else "G+2"
assert V in M.VARIANTS
G3 = V == "G+3"
rv, vv = R[V], M.VARIANTS[V]
midv = rv["mid"]
GFA_ABOVE = 2600 if G3 else 1950
GFA_TOTAL = "4,000" if G3 else "3,350"
COVERNAME = "cover-g3" if G3 else "cover"
XLSX = f"Shorouk_Mall_{V}_Financial_Model.xlsx"
MIXTXT = "dining, lifestyle retail, wellness and co-working" if G3 else "dining, lifestyle retail and wellness"
_n = M.NLA
_cells = [m(_n["ground_indoor"], 0), m(_n["kiosk"], 0), m(_n["first"], 0), m(_n["second"], 0)]
_tot = _n["ground_indoor"] + _n["kiosk"] + _n["first"] + _n["second"]
_heads = ["", "Ground, indoor", "Kiosks", "First", "Second"]
if G3:
    _cells.append(m(_n["third"], 0)); _heads.append("Third"); _tot += _n["third"]
NLA_TOTAL = _tot
NLA_NOTE = "; the third floor is assumed to match the second" if G3 else ""


def opt_range(var, key, f):
    lo, hi = R[var]["low"]["options"], R[var]["high"]["options"]
    vals = [o[key] for o in lo] + [o[key] for o in hi]
    return rng(min(vals), max(vals), f)


# ---- cover
page("cover", f"""
<div class="cover">
  <div class="conf">Confidential</div>
  <h1>Shorouk<br>Mall</h1>
  <div class="ct">Investment Study · {V}</div>
  <div class="cs">Concept · Market study · Returns · Feasibility</div>
  <img src="{BRO}/assets/img/{COVERNAME}.jpg" alt="Shorouk Mall">
  <div class="cb"><b>El Sherouk, Cairo</b><br>A mixed-use commercial development, offered as a whole building · {V} configuration<br>
  Developed by Jalour Developments, Al Jalal Holding · November 2026</div>
</div>""", num=False)

# ---- contents + executive summary
toc = ["Executive summary", "Concept", "The asset", "Market: El Sherouk", "Market: catchment and demand",
       "Market: competition", "Market: pricing benchmarks", "Rent basis", "Price and payment options",
       "Returns", "Feasibility: results by payment option", "Asset value and cash flow",
       "Assumptions and risks", "Contact"]
page("Executive summary", f"""
<div class="two">
<div>
<h3>Contents</h3>
<ol class="toc">{''.join(f'<li><span>{t}</span><i>{i + 2:02d}</i></li>' for i, t in enumerate(toc))}</ol>
</div>
<div>
<h3>The opportunity</h3>
<p>Shorouk Mall is a mixed-use commercial building in the Fourth District of El Sherouk, offered for sale as a whole building with its land (1,113 sqm). It is planned floor by floor ({MIXTXT}), with basement parking and a rooftop open-air café.</p>
<p>This study sets out the concept, the market evidence, the expected returns and a buyer-side feasibility for the {V} configuration.</p>
</div>
</div>
<h3>Headline figures</h3>
{table(["", V], [
    ["List price", f"EGP {m(vv['list_price'], 0)}M"],
    ["Price after discount (four payment options)", f"EGP {rng(midv['options'][0]['price'], midv['options'][-1]['price'])}M"],
    ["Expected rent, first year after handover", f"EGP {rng(vv['rent_low'], vv['rent_high'], lambda x: m(x, 0))}M"],
    ["Expected net income, first year (rent less 20%)", f"EGP {rng(rv['low']['net'][0], rv['high']['net'][0], lambda x: m(x, 0))}M"],
    ["Net yield, year 1, on price paid", opt_range(V, 'yield_paid', pct)],
    ["Payback from handover, on price paid", opt_range(V, 'payback', m) + " years"],
    ["IRR, 12 years, with resale", opt_range(V, 'irr', pct)],
    ["IRR, 12 years, rental income only", opt_range(V, 'irr_income', pct)],
    ["NPV at 16%, with resale", f"EGP {opt_range(V, 'npv', lambda x: m(x, 0))}M"],
], cls="big")}
<p class="note">Ranges cover the four payment options and the low-to-high rent range. Returns with resale depend mainly on the asset-value assumption (value up about 50% by handover, then about 10% a year); rental income alone returns less than the 16% discount rate. Both are shown throughout so the reader can judge each separately.</p>
{DISC}""")

# ---- concept
page("Concept", f"""
<p class="lead">An all-inclusive destination: everything a household needs in a week, in one building.</p>
<p>Shorouk Mall is conceived as a curated destination for dining, lifestyle, wellness and everyday retail: a place people choose to visit, not simply pass through. The building is planned floor by floor, so that each level has a clear purpose and the whole reads as one unified offer. The aim is to be as all-inclusive as possible, so that a single visit covers a meal, shopping, a pharmacy or bank errand, and exercise.</p>
{table(["Level", "Concept", "Role in the mix"], [
    ["Basement", "Parking and services", "Customer parking and building services, away from the customer entrance"],
    ["Ground floor", "The Dining Experience", "Restaurants and cafés with outdoor seating on the plaza; daily-needs units such as a pharmacy and a bank; kiosks"],
    ["First floor", "Lifestyle and Shopping", "Home comfort and lifestyle retail"],
    ["Second floor", "The Wellness Arena", "Fitness, treatment and wellbeing"],
    *([["Third floor", "Co-working", "Flexible workspace and meeting rooms, bringing a weekday community"]] if G3 else []),
    ["Rooftop", "Open-air café", "An open-air café on the roof; the building's landmark"],
], align=["l", "l", "l"])}
<div class="two" style="margin-top:14pt">
<div><h3>Design</h3><ul class="list">
<li>Predominantly glass curtain-wall façade</li><li>Outdoor plaza at the public frontage</li>
<li>Flexible structural grid: units can be combined or subdivided</li><li>Ground floor 5 m high; upper floors 4 m</li>
<li>Up to 11 shops per floor</li></ul></div>
<div><h3>Operation</h3><ul class="list">
<li>Managed by our retail and commercial expertise partners; the management contract is optional for the buyer</li>
<li>Planned tenant curation, floor by floor, led by a tenant mix consultant</li>
<li>Building-wide CCTV, 24/7 security, centralised waste management</li>
<li>Who it serves: the market study identifies families and teenagers as the main users of mixed-use space in El Sherouk</li></ul></div>
</div>
<p class="note">Tenant categories are a planned curation. No tenant is signed at the date of this study.</p>""")

# ---- asset
page("The asset", f"""
<div class="two">
<div>
{table(["Level", "Gross area (sqm)", "Height"], [
    ["Basement", "1,100", "4 m"], ["Ground floor", "650", "5 m"], ["First floor", "650", "4 m"], ["Second floor", "650", "4 m"],
    *([["Third floor", "650", "4 m"]] if G3 else []), ["Rooftop, open-air café", "300", "—"]])}
{kpis([("1,113 sqm", "Land area, included in the sale"), (GFA_TOTAL + " sqm", "Total gross area"), (f"{GFA_ABOVE:,} sqm", "Above-ground commercial gross area")])}
</div>
<div>
<img class="ph" src="{BRO}/assets/img/{COVERNAME}.jpg" alt="Shorouk Mall">
<p class="cap">The {V} configuration. Artist's impression.</p>
</div>
</div>
<div class="two" style="margin-top:10pt">
<div><h3>Location</h3><ul class="list">
<li>El Sherouk, Fourth District; coordinates 30.126386, 31.627335</li>
<li>Between El Sadat Road and the Orabi Road extension, the district's two arterial roads</li>
<li>Main-road visibility, approximately 30–40 m frontage</li>
<li>About 0.6 km to La Vista CASA; about 0.8 km to Street Side Mall</li></ul></div>
<div><h3>Handover and delivery</h3><ul class="list">
<li>Contractual handover within 2 years of contract signing</li>
<li>Core and shell, with façade, passenger elevator and fire safety systems</li>
<li>Finished outdoor plaza and parking</li>
<li>Sold as a whole building, land included; all floors commercial</li></ul></div>
</div>
<h3>Indicative net leasable area</h3>
{table(_heads + ["Total"], [["sqm"] + _cells + [m(NLA_TOTAL, 0)]])}
<p class="note">Leasable areas are as instructed by Jalour and equal the full 650 sqm floor plate of each floor. They exclude the outdoor seating and the rooftop café, and are subject to final design.</p>""")

# ---- market 1
page("Market: El Sherouk", f"""
<p class="lead">A third-generation city of more than 400,000 people, with almost all of its residential land already built.</p>
{kpis([("11,900 acres", "City area"), ("400,000+", "Population"), ("85.5%", "Residential land already constructed"), ("3.42%", "Share of the surveyed supply that is mixed-use")], 4)}
<div class="two" style="margin-top:12pt">
<div>
<p>El Sherouk is bordered by Badr City and the Regional Ring Road to the east, the Ring Road to the west, the Cairo–Ismailia Road to the north and the Cairo–Suez Road to the south. It has complete services (healthcare, education, sports, entertainment and commercial) and sits between Madinaty, New Heliopolis and Mostakbal City.</p>
<p>The market survey covered 30 residential projects and 17 mixed-use projects in the city. Mixed-use space is a small share of supply, which the study reads as room for further commercial investment. The study also reports annual price growth of around 12% for newly introduced projects in the city.</p>
<h3>Strengths and opportunities</h3><ul class="list"><li>Strategic location and modern infrastructure</li><li>Proximity to the New Administrative Capital</li><li>Population and economic growth; urban expansion</li></ul>
<h3>Weaknesses and threats</h3><ul class="list"><li>Competition from other new cities and from established developers</li><li>High initial investment costs</li><li>Economic instability and regulatory change</li></ul>
</div>
<div>
<h3>Connectivity</h3>
{table(["Destination", "Distance", "Drive time"], CONNECT)}
<img class="ph" style="margin-top:10pt" src="{BRO}/assets/img/map-google-wide.jpg" alt="Location map">
<p class="cap">Map: Google Maps (Map data ©2026 Google). The red marker shows the site.</p>
</div>
</div>
<p class="src">Source: DAMAK market research for Al Jalal Holding, El Sherouk City, December 2024 (ref. DMM-NR08-AAPO-ASC-MUP-1224, rev. 02). Data as of 15 December 2024.</p>""")

# ---- market 2
page("Market: catchment and demand", f"""
<p class="lead">About 22,000 residents in the surrounding districts are served by a single mixed-use building.</p>
{kpis([("22,000", "Residents in the immediate catchment, approximately"), ("5,340", "Residential units in the main catchment district"), ("1", "Mixed-use building currently serving it"), ("13,500 sqm", "Service space still needed, measured against the average code requirement, approximately")], 4)}
<div class="two" style="margin-top:12pt">
<div>
<h3>The site's district</h3>
<p>The site is in the Fourth District (L'azurde), surrounded by two arterial roads, El Sadat Road and the extension of Orabi Road, which make the district easy to reach. The surrounding housing is G+3 residential buildings with two to four units per floor.</p>
{table(["Catchment area", "Residential buildings", "Expected population"], [
    ["Main catchment district", "445", "21,360"], ["District 1", "85", "4,080"], ["District 2", "128", "6,144"],
    ["District 3", "132", "6,336"], ["District 4", "100", "4,800"]])}
<p class="note">Figures as reported in the market study; its district totals are presented on separate maps and are not additive.</p>
</div>
<div>
<h3>Supply gap</h3>
<p>Under Egyptian codes, the service area (retail, offices and clinics) required for this population is between 5,340 and 32,040 sqm. The one existing mixed-use building, Rio Business Hub (1,440 sqm of land), leaves about 13,500 sqm unmet when measured against the average of that range.</p>
<p>The study also identifies 11 nearby land plots that could become either expansion or direct competition, so the gap will not stay open indefinitely.</p>
<h3>Who uses mixed-use space</h3>
<p>The study's survey concludes that the users of mixed-use space in El Sherouk are primarily families and teenagers. Among services wanted beside a residential project, malls rank alongside schools, hospitals and clubs. This supports a dining, lifestyle, wellness and daily-needs mix.</p>
<h3>Nearby residential values</h3>
<p>Average asking prices in the nearest compounds range from about EGP 33,000 to EGP 103,000 per sqm (El Patio Casa: about EGP 73,500), against a city average of about EGP 71,000 across the surveyed projects.</p>
</div>
</div>
<p class="src">Source: DAMAK market research, December 2024.</p>""")

# ---- competition
page("Market: competition", f"""
<p class="lead">Seventeen mixed-use projects were surveyed. Most stack commercial below offices and clinics; few are curated as a single destination.</p>
{table(["Project", "Developer", "Land (sqm)", "Mix"], COMPETITORS, cls="sm", align=["l", "l", "r", "l"])}
<div class="two" style="margin-top:10pt">
<div><h3>What the survey shows</h3><ul class="list">
<li>Typical height is G+2 or G+3; Shorouk Mall's land (1,113 sqm) is at the small end of the range</li>
<li>44% of surveyed units were ready to move; 48% were due in 2027</li>
<li>Core and shell is the most common finish (196 of 335 units)</li>
<li>One retail operator runs most commercial projects in the city</li></ul></div>
<div><h3>Nearest competitors</h3><ul class="list">
<li><b>Rio Business Hub:</b> the only mixed-use building in the Fourth District service centre; the study notes a high selling price and few unique selling points</li>
<li><b>Street Side Mall:</b> about 0.8 km from the site; the source of the rent benchmarks used in this study (March 2026). It is not covered by the 2024 survey</li></ul></div>
</div>
<p class="src">Source: DAMAK market research, December 2024. Street Side Mall information: Jalour Developments, March 2026.</p>""")

# ---- pricing benchmarks
ours_cash = vv["list_price"] * 0.6 * 1e6 / GFA_ABOVE
ours_list = vv["list_price"] * 1e6 / GFA_ABOVE
chart = bars(RETAIL_PSM + [("Shorouk Mall, cash", ours_cash), ("Shorouk Mall, list", ours_list)],
             hl={"Shorouk Mall, cash", "Shorouk Mall, list"}, labw=92)
page("Market: pricing benchmarks", f"""
<div class="two">
<div>
<h3>Retail asking prices, primary market (EGP per sqm)</h3>
{chart}
<p class="note">Competitors: average asking price per sqm of retail units, December 2024. Shorouk Mall (blue): price divided by its {GFA_ABOVE:,} sqm of above-ground gross area; the price also includes the land, the basement and the rooftop. Competitor prices are for individual units two years earlier, so the comparison is indicative only.</p>
</div>
<div>
<h3>Rents used in this study (March 2026)</h3>
{table(["Space", "EGP / sqm / month"], [
    ["Ground floor, indoor", m(M.RENT_RATES['ground_indoor'], 0)], ["Ground floor, outdoor", m(M.RENT_RATES['ground_outdoor'], 0)],
    ["Kiosks and sponsorship", m(M.RENT_RATES['kiosk'], 0)], ["First and second floors", m(M.RENT_RATES['upper'], 0)],
    ["Rooftop, open-air café", m(M.RENT_RATES['rooftop_cafe'], 0)],
    *([["Third floor, co-working", m(M.RENT_RATES['coworking'], 0)]] if G3 else [])])}
<h3>Market payment norms</h3><ul class="list"><li>Most common plan: 20% down and 6 years</li><li>Other frequent plans: 15% or 25% down and 6 years; 40% down and 2 years</li><li>Shorouk Mall: 20–30% down over 3–5 years, with discounts of 20–40%</li></ul>
</div>
</div>
<p class="src">Source: DAMAK market research, December 2024; Jalour Developments (Street Side Mall rents, March 2026).</p>""")

# ---- rent basis
BU_NOW = RB["g2_now"] + (RB["third_now"] if G3 else 0)
BU_HO = RB["g2_handover"] + (RB["third_handover"] if G3 else 0)
_mid = (vv["rent_low"] + vv["rent_high"]) / 2
BU_LEAD = ("At Street Side Mall's rates, the building's leasable area supports more rent than Jalour's expected figure." if BU_HO > vv["rent_high"]
           else "The expected rent reconciles with the building's leasable area at Street Side Mall's rates.")
BU_TXT = ("The bottom-up result sits " + ("below" if BU_HO < vv["rent_low"] else "above" if BU_HO > vv["rent_high"] else "within")
          + " Jalour's expected range" + (", close to its low end." if vv["rent_low"] <= BU_HO < _mid else "."))
rb_rows = [[lab, m(a, 0), m(p, 0), m(a * p * 12 / 1e6), m(a * p * 12 / 1e6 * RB["factor"])] for lab, a, p in RB["rows"]]
t3 = RB["third"]
page("Rent basis", f"""
<p class="lead">{BU_LEAD}</p>
<p>Jalour expects total rent of EGP {m(vv['rent_low'], 0)}–{m(vv['rent_high'], 0)} million in the first year after handover. The table tests that figure from the bottom up: indicative leasable areas multiplied by the March 2026 rates, then raised by 10% a year to handover.</p>
{table(["Component", "Area (sqm)", "EGP/sqm/month", "Rent, March 2026 (EGP M)", "Rent at handover (EGP M)"],
       rb_rows + ([[t3[0].replace(" (G+3)", ""), m(t3[1], 0), m(t3[2], 0), m(RB['third_now']), m(RB['third_handover'])]] if G3 else [])
       + [["<b>Total</b>", "", "", f"<b>{m(BU_NOW)}</b>", f"<b>{m(BU_HO)}</b>"]])}
{kpis([(f"EGP {m(BU_HO)}M", "Bottom-up rent at handover"),
       (f"EGP {m(vv['rent_low'], 0)}–{m(vv['rent_high'], 0)}M", "Jalour's expected rent, first year after handover"),
       (f"{BU_HO / ((vv['rent_low'] + vv['rent_high']) / 2) * 100:.0f}%", "Bottom-up result as a share of the expected midpoint")])}
<h3>What this rests on</h3>
<ul class="list">
<li>Rates are March 2026 asking rents at Street Side Mall, the nearest competitor, supplied by Jalour</li>
<li>Escalation of 10% a year for {M.ESCALATION_TO_HANDOVER_YEARS} years to an assumed handover in early 2029 (factor {RB['factor']:.2f})</li>
<li>Leasable areas as instructed by Jalour: the full 650 sqm floor plate on each floor, {m(M.NLA['ground_outdoor'], 0)} sqm of outdoor seating and a {m(M.NLA['rooftop_cafe'], 0)} sqm rooftop open-air café</li>
<li>Full occupancy from the first year, as instructed. A slower lease-up would reduce first-year income</li>
<li>Sponsorship income is included in the kiosk line at the same rate</li>
</ul>
<p class="note">{BU_TXT} The return calculations that follow use Jalour's expected ranges, not the bottom-up figure.</p>
{DISC}""")

# ---- price and payment
def pay_rows(var):
    rows = []
    for o in R[var]["mid"]["options"]:
        rows.append([o["name"], pct(o["discount"], 0), f"{m(o['price'])}",
                     f"{m(o['down_amount'])} ({pct(o['down'], 0)})",
                     f"{o['years'] * 4} × {m(o['instalment_q'], 2)}" if o["years"] else "—",
                     f"{o['years']} years" if o["years"] else "On contract"])
    return rows
ph = ["Option", "Discount", "Price paid", "Down payment", "Quarterly instalments", "Term"]
page("Price and payment options", f"""
{kpis([(f"EGP {m(vv['list_price'], 0)}M", f"List price, {V}, whole building with land"), (f"EGP {rng(midv['options'][0]['price'], midv['options'][-1]['price'])}M", "Price after discount, across the four options")], 2)}
<h3>Payment options</h3>
{table(ph, pay_rows(V), cls="nw")}
<div class="two" style="margin-top:12pt">
<div><h3>Terms</h3><ul class="list">
<li>Instalments are quarterly and equal, starting after the down payment</li>
<li>The down payment is a share of the discounted price</li>
<li>Contractual handover within 2 years of contract signing</li>
<li>Sold as a whole building, land included</li></ul></div>
<div><h3>How the options compare</h3><ul class="list">
<li>Cash carries the largest discount and the lowest price, so the highest yield and the shortest payback</li>
<li>Options 2–4 trade a smaller discount for payments spread over 3–5 years; under Options 2 and 3, part of the price is paid after rent begins</li>
<li>The feasibility pages show the return for each option</li></ul></div>
</div>
<p class="note">Prices in EGP millions. Instalment amounts are the price balance divided equally by the number of quarters.</p>""")

# ---- returns pages
def returns_page(var):
    lo, mid, hi = R[var]["low"], R[var]["mid"], R[var]["high"]
    v = M.VARIANTS[var]
    rows, cl, ch = [], 0.0, 0.0
    for k in range(A["operating_years"]):
        cl += lo["net"][k]; ch += hi["net"][k]
        g = "—" if k == 0 else pct(A["growth_initial"] if k < A["growth_initial_years"] else A["growth_later"], 0)
        rows.append([f"Year {k + 1}", g, rng(lo["gross"][k], hi["gross"][k]), rng(lo["net"][k], hi["net"][k]), rng(cl, ch), m(mid["value"][k], 0)])
    chart = columns([(f"Y{k + 1}", mid["net"][k]) for k in range(A["operating_years"])], h=120, fmt=lambda x: f"{x:,.0f}")
    page("Returns", f"""
<p class="lead">Expected rent of EGP {m(v['rent_low'], 0)}–{m(v['rent_high'], 0)} million in the first year after handover, rising 10% a year for the first five years.</p>
{kpis([(f"EGP {rng(lo['net'][0], hi['net'][0], lambda x: m(x, 0))}M", "Net income, year 1"),
       (opt_range(var, 'yield_paid', pct), "Net yield, year 1, on price paid"),
       (opt_range(var, 'payback', m) + " yrs", "Payback from handover, on price paid"),
       (f"EGP {rng(sum(lo['net']), sum(hi['net']), lambda x: m(x, 0))}M", "Net income over 10 years")], 4)}
<h3>Ten operating years from handover (EGP millions)</h3>
{table(["Operating year", "Rent growth", "Total rent", "Net income", "Cumulative net income", "Asset value (basis)"], rows)}
<h3>Net income by year, base case (EGP millions)</h3>
{chart}
<p class="note">Ranges show the low and high rent cases; the chart and the asset value use the midpoint. Net income is total rent less 20%, which covers management, maintenance, vacancy and all other costs. Rent growth is 10% a year for operating years 2–5 and an assumed {pct(A['growth_later'], 0)} a year afterwards; growth after the first period will follow the market. Operating year 1 begins at handover, 2 years after contract signing.</p>
{DISC}""")

returns_page(V)

# ---- feasibility
def feas_rows(var):
    lo, mid, hi = R[var]["low"]["options"], R[var]["mid"]["options"], R[var]["high"]["options"]
    rows = []
    for a, b, c in zip(lo, mid, hi):
        rows.append([b["name"], m(b["price"]), rng(a["yield_paid"], c["yield_paid"], pct), rng(c["payback"], a["payback"], m),
                     rng(a["irr"], c["irr"], pct), rng(a["irr_income"], c["irr_income"], pct),
                     rng(a["npv"], c["npv"], lambda x: m(x, 0))])
    return rows
fh = ["Option", "Price paid", "Net yield, yr 1", "Payback (yrs)", "IRR, with resale", "IRR, income only", "NPV, with resale"]
page("Feasibility: results by payment option", f"""
<p class="lead">With the resale value, every option clears the 16% discount rate.</p>
{table(fh, feas_rows(V), cls="sm nw")}
<div class="two" style="margin-top:12pt">
<div><h3>How to read this</h3><ul class="list">
<li><b>Net yield:</b> first-year net income divided by the price paid</li>
<li><b>Payback:</b> years from handover until cumulative net income equals the price paid</li>
<li><b>IRR and NPV:</b> over 12 years from contract (2 to handover, 10 of operation), on annual cash flows; NPV at a 16% discount rate</li>
<li><b>With resale:</b> assumes a sale at the end of year 12 at the asset-value basis on the next page</li></ul></div>
<div><h3>Findings</h3><ul class="list">
<li>Cash gives the highest yield and shortest payback; Option 2 gives the highest IRR and NPV with resale, because less capital is tied up before rent starts</li>
<li>Options 2 and 3 are still being paid when rent begins, so early income helps fund the later instalments</li>
<li>The case for buying rests on both income and capital growth. A buyer who expects lower value growth should weight the income-only column</li></ul></div>
</div>
<p class="note">Price and NPV in EGP millions. Ranges show the low and high rent cases.</p>
{DISC}""")

# ---- value and cash flow
def flow_chart(var, idx):
    o = R[var]["mid"]["options"][idx]
    T = A["handover_year"] + A["operating_years"]
    return columns([(f"Y{t}", o["flows_income"][t]) for t in range(T + 1)], h=118, fmt=lambda x: f"{x:,.0f}")

page("Asset value and cash flow", f"""
<div class="two">
<div>
<h3>Asset-value basis</h3>
<p>As instructed by Jalour, the study assumes the building's value rises by about 50% between contract and handover, and by about 10% a year afterwards, starting from the list price.</p>

</div>
<div>
<h3>Asset value (EGP millions)</h3>
{table(["", "EGP M"], [
    ["List price at contract", m(vv['list_price'], 0)],
    ["Value at handover (+50%)", m(midv['value_handover'], 0)],
    ["Value after 5 operating years", m(midv['value'][4], 0)],
    ["Value after 10 operating years (resale)", m(midv['exit_value'], 0)]])}
</div>
</div>
<h3>Annual net cash flow before resale, base case (EGP millions)</h3>
<div class="two">
<div><p class="cap2">Option 1, cash</p>{flow_chart(V, 0)}</div>
<div><p class="cap2">Option 2, 30% down and 5 years</p>{flow_chart(V, 1)}</div>
</div>
<div class="two">
<div><p class="cap2">Option 3, 25% down and 4 years</p>{flow_chart(V, 2)}</div>
<div><p class="cap2">Option 4, 20% down and 3 years</p>{flow_chart(V, 3)}</div>
</div>
<p class="note">Y0 is contract signing; rent begins in Y3, the first year after handover. Quarterly instalments are shown as annual totals. Resale proceeds at the end of Y12 are excluded from the charts.</p>
{DISC}""")

APPROVAL_TXT = ("The G+3 configuration and the 2-year handover depend on approvals and construction progress" if G3
                else "The 2-year handover depends on approvals and construction progress")
# ---- assumptions and risks
page("Assumptions and risks", f"""
<div class="two">
<div>
<h3>Assumptions</h3>
{table(["Item", "Basis"], [
    ["List price", f"EGP {m(vv['list_price'], 0)}M ({V})"],
    ["Payment options", "Four options; discounts of 20–40%"],
    ["Handover", "2 years from contract (contractual)"],
    ["First-year rent", f"EGP {m(vv['rent_low'], 0)}–{m(vv['rent_high'], 0)}M"],
    ["Occupancy", "100% from the first year"],
    ["Costs", "20% of rent, covering everything"],
    ["Rent growth", f"10% a year, operating years 2–5; then {pct(A['growth_later'], 0)} (conservative study assumption)"],
    ["Asset value", "+50% to handover; +10% a year after"],
    ["Horizon", "12 years: 2 to handover, 10 operating"],
    ["Discount rate", "16%"],
    ["Timing", "Annual cash flows; down payment at contract"],
    ["Taxes and financing", "Not modelled; unleveraged, before tax"],
], align=["l", "l"])}
<p class="note">Jalour supplied all inputs except the rent growth after year 5 and the assumed handover date, which are assumptions of this study.</p>
</div>
<div>
<h3>Risks a buyer should weigh</h3>
<ul class="list">
<li><b>Rent level.</b> The rates used are asking rents at one competitor. Achieved rents may be lower. <b>Mitigation:</b> with the operator's expertise, these rents can be achieved</li>
<li><b>Lease-up.</b> Full occupancy in the first year is assumed. No tenant is signed; a slower lease-up delays income. <b>Mitigation:</b> with the operator's expertise, full occupancy in the first year can be achieved</li>
<li><b>Resale value.</b> The with-resale returns depend on value growing faster than rent. Income-only returns are below the discount rate</li>
<li><b>Market data.</b> The market survey dates from December 2024; prices, supply and rents have moved since</li>
<li><b>New supply.</b> Eleven nearby plots could become competing projects</li>
<li><b>Costs.</b> The 20% deduction is a single allowance, not a costed budget</li>
<li><b>Approvals and delivery.</b> {APPROVAL_TXT}. <b>Mitigation:</b> contractual penalties compensate the buyer for any delay in delivery</li>
<li><b>Economy.</b> Inflation, interest rates and currency affect rents, values and the appropriate discount rate</li>
<li><b>Taxes.</b> Rental and capital gains taxes are not modelled</li>
</ul>
<h3>Recommended before commitment</h3>
<ul class="list"><li>Verify current achieved rents and occupancy at Street Side Mall</li><li>Obtain a measured leasable-area schedule</li><li>Take independent legal, tax and valuation advice</li></ul>
</div>
</div>""")

# ---- notice + contact
page("Contact", f"""
<h3>Accompanying file</h3>
<p>The Excel workbook <b>{XLSX}</b> contains the full model with live formulas: assumptions, the rent basis, and year-by-year cash flows, IRR and NPV for each payment option.</p>
<div class="contact">
<div><b>Abdelnabi</b><br>Head of Business Development<br>Jalour Developments, Al Jalal Holding</div>
<div class="r">abdelnabi@aljalalholding.com<br>+20 100 077 5002</div>
</div>""")

# ================================================================== HTML
CSS = """
@font-face{font-family:"Inter Tight";font-weight:300;src:url(%(B)s/fonts/inter-tight-300.woff2) format("woff2")}
@font-face{font-family:"Inter Tight";font-weight:400;src:url(%(B)s/fonts/inter-tight-400.woff2) format("woff2")}
@font-face{font-family:"Inter Tight";font-weight:500;src:url(%(B)s/fonts/inter-tight-500.woff2) format("woff2")}
@font-face{font-family:"Inter Tight";font-weight:600;src:url(%(B)s/fonts/inter-tight-600.woff2) format("woff2")}
:root{--bg:#000;--fg:#fff;--body:#C9CDD3;--mute:#8B929C;--faint:#6A717B;--rule:#272B31;--rule2:#3A4048;--blue:#4282BC;--bar:#3A4048;--neg:#7A828C;--panel:#0B0D10}
@page{size:A4;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:var(--bg)}
body{font-family:"Inter Tight",sans-serif;color:var(--fg);-webkit-font-smoothing:antialiased}
.page{width:595.28pt;height:841.89pt;position:relative;overflow:hidden;background:var(--bg);padding:26pt 34pt 0;break-after:page}
.page:last-child{break-after:auto}
.hdr{display:flex;justify-content:space-between;font-size:7pt;letter-spacing:.08em;text-transform:uppercase;color:var(--fg)}
.hdr span:nth-child(2){margin-right:auto;margin-left:60pt}
h2{font-size:25pt;font-weight:400;letter-spacing:.04em;text-transform:uppercase;line-height:1;margin:20pt 0 14pt}
h3{font-size:7.4pt;letter-spacing:.14em;text-transform:uppercase;color:var(--blue);font-weight:500;padding-bottom:5pt;border-bottom:1px solid var(--rule2);margin:12pt 0 0}
p{font-size:8.6pt;line-height:1.5;color:var(--body);font-weight:300;margin-top:6pt}
p b,li b{font-weight:500;color:var(--fg)}
p.lead{font-size:12.5pt;line-height:1.3;color:var(--fg);font-weight:400;margin:0 0 4pt}
p.note{font-size:7.2pt;line-height:1.45;color:var(--mute);margin-top:7pt}
p.src{font-size:6pt;color:var(--faint);margin-top:8pt}
p.disc{font-size:6.6pt;color:var(--faint);margin-top:8pt}
p.cap,p.cap2{font-size:6.8pt;color:var(--mute);margin-top:4pt}
p.cap2{letter-spacing:.06em;text-transform:uppercase;margin:8pt 0 2pt}
.two{display:grid;grid-template-columns:1fr 1fr;gap:0 22pt}
.two>div>h3:first-child{margin-top:0}
table{width:100%%;border-collapse:collapse;margin-top:2pt}
th{font-size:6.4pt;letter-spacing:.08em;text-transform:uppercase;color:var(--mute);font-weight:400;padding:6pt 0 4pt;border-bottom:1px solid var(--rule2);vertical-align:bottom;line-height:1.25}
td{font-size:8.2pt;padding:4.4pt 0;border-bottom:1px solid var(--rule);color:var(--body);font-weight:300;vertical-align:top;line-height:1.35}
td:first-child{color:var(--fg);font-weight:400}
th.r,td.r{text-align:right;padding-left:8pt;white-space:nowrap}
th.l,td.l{text-align:left;padding-right:8pt}
table th+th.l,table td+td.l{padding-left:10pt !important}
table.nw td:first-child{white-space:nowrap;padding-right:8pt}
table.sm td{font-size:7.4pt;padding:3.2pt 0}
table.big td{font-size:9pt;padding:5.6pt 0}
ul.list{list-style:none}
ul.list li{font-size:8.2pt;line-height:1.4;padding:3.8pt 0;border-bottom:1px solid var(--rule);color:var(--body);font-weight:300}
ol.toc{list-style:none}
ol.toc li{display:flex;justify-content:space-between;font-size:8.2pt;padding:3.4pt 0;border-bottom:1px solid var(--rule);color:var(--body);font-weight:300}
ol.toc i{font-style:normal;color:var(--mute)}
.kpi{display:grid;gap:0 14pt;margin-top:10pt}
.kpi div{border-top:1px solid var(--rule2);padding-top:6pt}
.kpi b{display:block;font-size:15pt;font-weight:400;color:var(--fg);line-height:1.1}
.kpi span{display:block;font-size:6.8pt;color:var(--mute);line-height:1.35;margin-top:3pt}
img.ph{display:block;width:100%%;object-fit:cover}
svg.bars .bl,svg.cols .bl{font:6.4px "Inter Tight",sans-serif;fill:var(--mute)}
svg.bars .bv,svg.cols .bv{font:6.4px "Inter Tight",sans-serif;fill:var(--fg)}
svg.bars{margin-top:6pt}
.ftr{position:absolute;left:34pt;right:34pt;bottom:14pt;display:flex;gap:12pt;align-items:center;font-size:5.8pt;color:var(--mute)}
.ftr .logo svg{height:8pt;width:auto;display:block;color:var(--fg)}
.ftr .t{flex:1}.ftr .pg{font-size:7pt;color:var(--fg);letter-spacing:.06em}
.cover{position:absolute;inset:0;padding:60pt 34pt 0}
.cover .conf{font-size:7.5pt;letter-spacing:.2em;text-transform:uppercase;color:var(--blue);font-weight:500}
.cover h1{font-size:64pt;line-height:.92;font-weight:500;letter-spacing:-.01em;margin-top:26pt}
.cover .ct{font-size:20pt;margin-top:20pt;font-weight:400}
.cover .cs{font-size:9pt;letter-spacing:.14em;text-transform:uppercase;color:var(--mute);margin-top:8pt}
.cover img{display:block;width:100%%;height:298pt;object-fit:cover;margin-top:30pt}
.cover .cb{font-size:9pt;line-height:1.6;color:var(--body);font-weight:300;margin-top:22pt}
.cover .cb b{color:var(--fg);font-weight:500}
.contact{display:flex;justify-content:space-between;align-items:flex-end;border-top:1px solid var(--rule2);margin-top:26pt;padding-top:12pt;font-size:9pt;line-height:1.5;color:var(--body);font-weight:300}
.contact b{font-size:12pt;color:var(--fg);font-weight:500}.contact .r{text-align:right;color:var(--fg)}
""" % {"B": BRO}

LIGHT = """
:root{--bg:#F6F4F0;--fg:#111316;--body:#3B4047;--mute:#6A7079;--faint:#8D939B;--rule:#DDD9D2;--rule2:#C9C4BB;--bar:#C9C4BB;--neg:#9AA0A8;--panel:#ECE9E3}
"""

total = len(PAGES)
html_pages = []
for i, (title, body, num) in enumerate(PAGES, 1):
    if title == "cover":
        inner = body
    else:
        inner = (f'<div class="hdr"><span>Jalour</span><span>Shorouk Mall {V} · Investment Study</span><span>Confidential · 2026</span></div>'
                 f'<h2>{title}</h2><div class="content" style="zoom:{ZOOM.get(title, 1.26)}">{body}</div>')
    ftr = (f'<div class="ftr"><span class="logo">{JALOUR}</span><span class="t">Confidential. Projections only; not guaranteed. '
           f'Not an offer or a contract.</span><span class="pg">{i:02d} / {total:02d}</span></div>')
    html_pages.append(f'<section class="page">{inner}{ftr}</section>')

doc = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Shorouk Mall {V} — Investment Study</title>'
       f"<style>{CSS}</style>__THEME__</head><body>{''.join(html_pages)}</body></html>")
os.makedirs(os.path.join(HERE, "build"), exist_ok=True)
open(os.path.join(HERE, "build", f"study-{V}.html"), "w", encoding="utf-8").write(doc.replace("__THEME__", ""))
open(os.path.join(HERE, "build", f"study-{V}-light.html"), "w", encoding="utf-8").write(doc.replace("__THEME__", f"<style>{LIGHT}</style>"))
print(V, "pages", total)
