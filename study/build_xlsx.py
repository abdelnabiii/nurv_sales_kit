#!/usr/bin/env python3
"""Write the Shorouk Mall financial model as a formula-driven Excel workbook."""
import os
import sys
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model as M

VAR = sys.argv[1]
assert VAR in M.VARIANTS
G3 = VAR == "G+3"
OUT = sys.argv[2]
A = M.ASSUMPTIONS
T = A["handover_year"] + A["operating_years"]

BLUE = Font(color="0000FF")            # inputs
BOLD = Font(bold=True)
HEAD = Font(bold=True, color="FFFFFF")
HFILL = PatternFill("solid", fgColor="0B0A0B")
SFILL = PatternFill("solid", fgColor="DCE6F1")
thin = Side(style="thin", color="BBBBBB")

wb = Workbook()

# ---------------- Assumptions ----------------
ws = wb.active
ws.title = "Assumptions"
ws["A1"] = f"Shorouk Mall {VAR} — Financial Model (buyer side)"; ws["A1"].font = Font(bold=True, size=14)
ws["A2"] = "EGP millions unless stated. Blue cells are inputs; all other cells are formulas. Annual periods: year 0 = contract, handover at end of year 2."
rows = [
    ("Years from contract to handover", A["handover_year"], "0"),
    ("Net income as share of gross rent", A["net_ratio"], "0%"),
    ("Annual rent growth, first period", A["growth_initial"], "0%"),
    ("Operating years on first-period growth", A["growth_initial_years"], "0"),
    ("Annual rent growth afterwards (assumption)", A["growth_later"], "0%"),
    ("Value uplift from contract to handover", A["value_uplift_to_handover"], "0%"),
    ("Annual value growth after handover", A["value_growth_after"], "0%"),
    ("Discount rate", A["discount_rate"], "0%"),
]
ws["A4"] = "General"; ws["A4"].font = BOLD
ref = {}
names = ["handover", "net", "g1", "g1yrs", "g2", "uplift", "vgrow", "disc"]
for i, ((lab, val, fmt), nm) in enumerate(zip(rows, names)):
    r = 5 + i
    ws.cell(r, 1, lab); c = ws.cell(r, 2, val); c.font = BLUE; c.number_format = fmt
    ref[nm] = f"Assumptions!$B${r}"
ws["A14"] = "Configuration"; ws["B14"] = VAR
for c in ("A14", "B14"):
    ws[c].font = BOLD
vrows = [("List price", "list_price"), ("Year-1 rent, low", "rent_low"), ("Year-1 rent, high", "rent_high")]
for i, (lab, key) in enumerate(vrows):
    r = 15 + i
    ws.cell(r, 1, lab)
    for j, var in enumerate((VAR,)):
        c = ws.cell(r, 2 + j, M.VARIANTS[var][key]); c.font = BLUE; c.number_format = "#,##0.0"
ws["A18"] = "Year-1 rent, base (midpoint)"
ws["B18"] = "=AVERAGE(B16:B17)"
ws["A19"] = "Year-1 rent, bottom-up case (from Rent basis)"; ws["B19"] = "='Rent basis'!E12"; ws["B19"].number_format = "#,##0.0"
ws["A20"] = "Payment option"; ws["B20"] = "Discount"; ws["C20"] = "Down payment"; ws["D20"] = "Instalment years"
for c in ("A20", "B20", "C20", "D20"):
    ws[c].font = BOLD
for i, (nm, d, dp, y) in enumerate(M.OPTIONS):
    r = 21 + i
    ws.cell(r, 1, nm)
    for j, (v, fmt) in enumerate(((d, "0%"), (dp, "0%"), (y, "0"))):
        c = ws.cell(r, 2 + j, v); c.font = BLUE; c.number_format = fmt
ws["A26"] = "Notes"; ws["A26"].font = BOLD
notes = [
    "Rent and price figures are the client's. Rent growth after the first period (7%) is a modelling assumption.",
    "Instalments are quarterly; the model aggregates them to year-end cash flows. The down payment falls at year 0.",
    "Asset value: list price x (1 + uplift) at handover, then growing annually. Resale assumed at the end of operating year 10.",
    "Projections only. Not guaranteed.",
]
for i, n in enumerate(notes):
    ws.cell(27 + i, 1, n)
ws.column_dimensions["A"].width = 46
for col in "BCD":
    ws.column_dimensions[col].width = 16

# ---------------- Rent build ----------------
rb = wb.create_sheet("Rent basis")
rb["A1"] = "Rent basis — Street Side Mall asking rents, March 2026"; rb["A1"].font = Font(bold=True, size=13)
hdr = ["Component", "Net leasable area (sqm)", "Rent (EGP/sqm/month)", "Annual rent, March 2026 (EGP M)", "Annual rent at handover (EGP M)"]
for j, h in enumerate(hdr):
    c = rb.cell(3, 1 + j, h); c.font = HEAD; c.fill = HFILL; c.alignment = Alignment(wrap_text=True)
build = M.rent_build()
third = (build["third"][0].replace(" (G+3)", ""),) + build["third"][1:]
allrows = build["rows"] + ([third] if G3 else [])
rb["A14"] = "Years of 10% escalation to handover"; rb["B14"] = M.ESCALATION_TO_HANDOVER_YEARS; rb["B14"].font = BLUE
for i, (lab, area, rate) in enumerate(allrows):
    r = 4 + i
    rb.cell(r, 1, lab)
    a = rb.cell(r, 2, area); a.font = BLUE; a.number_format = "#,##0.0"
    p = rb.cell(r, 3, rate); p.font = BLUE; p.number_format = "#,##0"
    rb.cell(r, 4, f"=B{r}*C{r}*12/1000000").number_format = "#,##0.0"
    rb.cell(r, 5, f"=D{r}*(1+{ref['g1']})^$B$14").number_format = "#,##0.0"
rb["A12"] = "Total"; rb["A12"].font = BOLD
_last = 3 + len(allrows)
rb["D12"] = f"=SUM(D4:D{_last})"; rb["E12"] = f"=SUM(E4:E{_last})"
for c in ("D12", "E12"):
    rb[c].number_format = "#,##0.0"; rb[c].font = BOLD
rb["A16"] = "Leasable areas as instructed by Jalour: the full 650 sqm floor plate per floor, 400 sqm of outdoor seating and a 300 sqm rooftop open-air cafe."
rb.column_dimensions["A"].width = 40
for col in "BCDE":
    rb.column_dimensions[col].width = 22

# ---------------- Variant sheets ----------------
def variant_sheet(name, vcol, rent_row=18, label="expected rent case"):
    s = wb.create_sheet(name)
    s["A1"] = f"Shorouk Mall {VAR} — cash flows (EGP M), {label}"; s["A1"].font = Font(bold=True, size=13)
    first = 2                                    # column of year 0
    col = lambda t: L(first + t)
    s.cell(3, 1, "Model year").font = BOLD
    s.cell(4, 1, "Operating year")
    s.cell(5, 1, "Gross rent")
    s.cell(6, 1, "Net income")
    s.cell(7, 1, "Cumulative net income")
    s.cell(8, 1, "Asset value")
    for t in range(T + 1):
        c = col(t)
        h = s[f"{c}3"]; h.value = t; h.font = HEAD; h.fill = HFILL; h.alignment = Alignment(horizontal="center")
        s[f"{c}4"] = f"=MAX({c}3-{ref['handover']},0)"
        if t == 0:
            s[f"{c}5"] = 0
        else:
            p = col(t - 1)
            s[f"{c}5"] = (f"=IF({c}4=0,0,IF({c}4=1,Assumptions!${vcol}${rent_row},"
                          f"{p}5*(1+IF({c}4<={ref['g1yrs']},{ref['g1']},{ref['g2']}))))")
        s[f"{c}6"] = f"={c}5*{ref['net']}"
        s[f"{c}7"] = f"=SUM(${col(0)}6:{c}6)"
        s[f"{c}8"] = (f"=IF({c}4=0,\"\",Assumptions!${vcol}$15*(1+{ref['uplift']})*(1+{ref['vgrow']})^{c}4)")
        for r in (5, 6, 7, 8):
            s[f"{c}{r}"].number_format = "#,##0.0"
    last = col(T)
    r = 10
    summary = []
    for i, (nm, _, _, _) in enumerate(M.OPTIONS):
        ar = 21 + i                               # row on Assumptions
        s.cell(r, 1, nm).font = BOLD
        for c in range(1, first + T + 1):
            s.cell(r, c).fill = SFILL
        s.cell(r + 1, 1, "Price paid"); s.cell(r + 1, 2, f"=Assumptions!${vcol}$15*(1-Assumptions!$B${ar})")
        s.cell(r + 2, 1, "Payments")
        s.cell(r + 3, 1, "Net cash flow, income only")
        s.cell(r + 4, 1, "Net cash flow, with resale")
        for t in range(T + 1):
            c = col(t)
            if t == 0:
                s[f"{c}{r+2}"] = f"=$B${r+1}*Assumptions!$C${ar}"
            else:
                s[f"{c}{r+2}"] = (f"=IF(AND(Assumptions!$D${ar}>0,{c}$3<=Assumptions!$D${ar}),"
                                  f"$B${r+1}*(1-Assumptions!$C${ar})/Assumptions!$D${ar},0)")
            s[f"{c}{r+3}"] = f"={c}$6-{c}{r+2}"
            s[f"{c}{r+4}"] = f"={c}{r+3}" + (f"+{c}$8" if t == T else "")
            for rr in (r + 2, r + 3, r + 4):
                s[f"{c}{rr}"].number_format = "#,##0.0;[Red]-#,##0.0"
        s.cell(r + 1, 2).number_format = "#,##0.0"
        s.cell(r + 5, 1, "Net yield, year 1, on price paid"); s.cell(r + 5, 2, f"={col(A['handover_year']+1)}$6/$B${r+1}").number_format = "0.0%"
        s.cell(r + 6, 1, "Payback from handover (years)")
        rng = f"${col(A['handover_year']+1)}$7:${last}$7"
        nrng = f"${col(A['handover_year']+1)}$6:${last}$6"
        s.cell(r + 6, 2, (f"=COUNTIF({rng},\"<\"&$B${r+1})+($B${r+1}-IF(COUNTIF({rng},\"<\"&$B${r+1})=0,0,"
                          f"INDEX({rng},COUNTIF({rng},\"<\"&$B${r+1}))))/INDEX({nrng},COUNTIF({rng},\"<\"&$B${r+1})+1)")).number_format = "0.0"
        s.cell(r + 7, 1, "IRR, with resale"); s.cell(r + 7, 2, f"=IRR({col(0)}{r+4}:{last}{r+4})").number_format = "0.0%"
        s.cell(r + 8, 1, "IRR, income only"); s.cell(r + 8, 2, f"=IRR({col(0)}{r+3}:{last}{r+3})").number_format = "0.0%"
        s.cell(r + 9, 1, "NPV at discount rate, with resale")
        s.cell(r + 9, 2, f"={col(0)}{r+4}+NPV({ref['disc']},{col(1)}{r+4}:{last}{r+4})").number_format = "#,##0.0;[Red]-#,##0.0"
        summary.append((nm, r))
        r += 11
    s.column_dimensions["A"].width = 36
    for t in range(T + 1):
        s.column_dimensions[col(t)].width = 11
    s.freeze_panes = "B4"
    return summary

variant_sheet("Cash flows", "B")
variant_sheet("Cash flows, bottom-up", "B", 19, "bottom-up rent case")
wb.save(OUT)
print("wrote", OUT)
