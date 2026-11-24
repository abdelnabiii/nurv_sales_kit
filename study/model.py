#!/usr/bin/env python3
"""Shorouk Mall investment study: buyer-side financial model (annual periods).

All inputs are in ASSUMPTIONS. Used by build_study.py (report) and build_xlsx.py (Excel).
Convention: year 0 = contract signing; handover at end of year 2; operating years 1-10
are model years 3-12; cash flows fall at year end except the down payment (year 0).
"""

ASSUMPTIONS = {
    "handover_year": 2,          # years from contract to handover (contractual)
    "operating_years": 10,       # years of operation modelled
    "net_ratio": 0.80,           # net income = gross rent less 20% (all costs)
    "growth_initial": 0.10,      # annual rent growth, first period
    "growth_initial_years": 5,   # operating years on the initial growth rate (years 1-5)
    "growth_later": 0.07,        # ASSUMPTION: market growth after the first period
    "value_uplift_to_handover": 0.50,  # value growth from contract to handover
    "value_growth_after": 0.10,        # annual value growth after handover
    "discount_rate": 0.16,
}

VARIANTS = {
    "G+2": {"list_price": 400.0, "rent_low": 35.0, "rent_high": 40.0},
    "G+3": {"list_price": 450.0, "rent_low": 50.0, "rent_high": 55.0},
}

# (name, discount, down payment share of price paid, instalment years)
OPTIONS = [
    ("Option 1 · Cash", 0.40, 1.00, 0),
    ("Option 2", 0.30, 0.30, 5),
    ("Option 3", 0.25, 0.25, 4),
    ("Option 4", 0.20, 0.20, 3),
]

# Rent basis: Street Side Mall asking rents, March 2026 (EGP per sqm per month), per client.
RENT_RATES = {"ground_indoor": 1500, "ground_outdoor": 750, "kiosk": 4000,
              "upper": 1000, "coworking": 2000, "rooftop_cafe": 1500}
# Leasable areas (sqm), as instructed by the client: the full 650 sqm floor plate per floor,
# 400 sqm of outdoor seating and a 300 sqm rooftop open-air cafe. Kiosk area from the drawings.
NLA = {"ground_indoor": 650.0, "kiosk": 27.8, "first": 650.0, "second": 650.0, "third": 650.0,
       "ground_outdoor": 400.0, "rooftop_cafe": 300.0}
ESCALATION_TO_HANDOVER_YEARS = 3   # March 2026 -> assumed handover Q1 2029


def rent_series(year1):
    a = ASSUMPTIONS
    out, r = [], year1
    for k in range(1, a["operating_years"] + 1):
        if k > 1:
            r *= 1 + (a["growth_initial"] if k <= a["growth_initial_years"] else a["growth_later"])
        out.append(r)
    return out


def irr(flows):
    lo, hi = -0.99, 5.0
    f = lambda r: sum(c / (1 + r) ** t for t, c in enumerate(flows))
    if f(lo) * f(hi) > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def npv(rate, flows):
    return sum(c / (1 + rate) ** t for t, c in enumerate(flows))


def payback(price, net):
    cum = 0.0
    for k, n in enumerate(net, 1):
        if cum + n >= price:
            return k - 1 + (price - cum) / n
        cum += n
    return None


def run(variant, year1_rent):
    a, v = ASSUMPTIONS, VARIANTS[variant]
    T = a["handover_year"] + a["operating_years"]
    gross = rent_series(year1_rent)
    net = [g * a["net_ratio"] for g in gross]
    value_handover = v["list_price"] * (1 + a["value_uplift_to_handover"])
    value = [value_handover * (1 + a["value_growth_after"]) ** k for k in range(1, a["operating_years"] + 1)]
    exit_value = value[-1]
    res = {"gross": gross, "net": net, "value_handover": value_handover, "value": value,
           "exit_value": exit_value, "exit_yield": net[-1] / exit_value, "options": []}
    for name, disc, down, yrs in OPTIONS:
        price = v["list_price"] * (1 - disc)
        pay = [0.0] * (T + 1)
        pay[0] = price * down
        for y in range(1, yrs + 1):
            pay[y] += price * (1 - down) / yrs
        inc = [0.0] * (T + 1)
        for k, n in enumerate(net, 1):
            inc[a["handover_year"] + k] = n
        flows_income = [inc[t] - pay[t] for t in range(T + 1)]
        flows = flows_income[:]
        flows[T] += exit_value
        res["options"].append({
            "name": name, "discount": disc, "down": down, "years": yrs, "price": price,
            "down_amount": price * down,
            "instalment_q": (price * (1 - down) / (yrs * 4)) if yrs else 0.0,
            "pay": pay, "flows": flows, "flows_income": flows_income,
            "yield_paid": net[0] / price, "yield_list": net[0] / v["list_price"],
            "payback": payback(price, net),
            "irr": irr(flows), "irr_income": irr(flows_income),
            "npv": npv(a["discount_rate"], flows),
            "npv_income": npv(a["discount_rate"], flows_income),
            "multiple": (sum(net) + exit_value) / price,
        })
    return res


def rent_build():
    r, n = RENT_RATES, NLA
    rows = [
        ("Ground floor, indoor", n["ground_indoor"], r["ground_indoor"]),
        ("Ground floor, outdoor seating", n["ground_outdoor"], r["ground_outdoor"]),
        ("Kiosks and sponsorship", n["kiosk"], r["kiosk"]),
        ("First floor", n["first"], r["upper"]),
        ("Second floor", n["second"], r["upper"]),
        ("Rooftop, open-air café", n["rooftop_cafe"], r["rooftop_cafe"]),
    ]
    third = ("Third floor, co-working (G+3)", n["third"], r["coworking"])
    f = 1.10 ** ESCALATION_TO_HANDOVER_YEARS
    def tot(rs):
        return sum(a * p * 12 for _, a, p in rs) / 1e6
    return {"rows": rows, "third": third, "factor": f,
            "g2_now": tot(rows), "g2_handover": tot(rows) * f,
            "third_now": tot([third]), "third_handover": tot([third]) * f}


if __name__ == "__main__":
    rb = rent_build()
    print("rent build G+2 now %.1f handover %.1f | third now %.1f handover %.1f" % (
        rb["g2_now"], rb["g2_handover"], rb["third_now"], rb["third_handover"]))
    for var, v in VARIANTS.items():
        for label, y1 in (("low", v["rent_low"]), ("mid", (v["rent_low"] + v["rent_high"]) / 2), ("high", v["rent_high"])):
            m = run(var, y1)
            print(var, label, "exit %.0f exit-yield %.1f%%" % (m["exit_value"], m["exit_yield"] * 100))
            for o in m["options"]:
                print("   %-16s price %6.1f yield %4.1f%% payback %4.1f IRR %4.1f%% (income-only %s) NPV %7.1f mult %.1fx" % (
                    o["name"], o["price"], o["yield_paid"] * 100, o["payback"] or -1, o["irr"] * 100,
                    "%.1f%%" % (o["irr_income"] * 100) if o["irr_income"] is not None else "n/a", o["npv"], o["multiple"]))
