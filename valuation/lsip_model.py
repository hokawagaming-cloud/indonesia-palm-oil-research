"""LSIP integrated financial model and valuation workbook (Phase XVII).

    python -I -X utf8 valuation/lsip_model.py      (after quant/lsip_fs_extract.py, quant/lsip_ops_dataset.py,
                                                     valuation/lsip_cohort.py, quant/lsip_market_snapshot.py)

Builds outputs/LSIP_model_valuation.xlsx with LIVE formulas (Inputs -> Cohort -> Model -> Valuation), verifies every
formula with the repository's independent evaluator (valuation/xlsx_eval.py; no Excel/LibreOffice here), and runs
scenarios, sensitivities, reverse valuations and the 12-month return/entry analysis by overriding input cells.

Conventions: IDR bn unless stated; FFB/CPO in '000 t; prices IDR/kg; nominal terms. FY2025A is the audited base;
FY2026E uses reported 9M26 plus a Q4 estimate (production override); FY2027E-FY2050E are model years; FY2051 is the
steady-state terminal year (sustainable 25-year replacement cycle, no ageing benefit carried forward).
Interest income is EXCLUDED from operating free cash flow and cash is added once in the equity bridge.
Replanting capex is inside FCFF only; no separate replanting reserve is deducted from cash (no double count).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter as L

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "data" / "reference" / "research"
OUTX = ROOT / "outputs" / "LSIP_model_valuation.xlsx"
sys.path.insert(0, str(ROOT / "valuation"))
from xlsx_eval import Evaluator  # noqa: E402

YEARS = list(range(2026, 2051))
C0 = 3                                   # column C = 2026
COL = {y: L(C0 + i) for i, y in enumerate(YEARS)}
TV = L(C0 + len(YEARS))                  # steady-state terminal column (2051)
SCN = ["A_historical", "B_accelerated", "C_deferred", "D_intensive"]
BLUE, GREEN = Font(name="Arial", color="0000FF", size=9), Font(name="Arial", color="008000", size=9)
BLACK, BOLD = Font(name="Arial", size=9), Font(name="Arial", size=9, bold=True)
YEL = PatternFill("solid", fgColor="FFFF00")

FIN = pd.read_csv(RES / "LSIP_financials_annual.csv", index_col=0)
OPS = pd.read_csv(RES / "LSIP_operational_annual.csv", index_col=0)
COGS = pd.read_csv(RES / "LSIP_cogs_breakdown.csv", index_col=0)
COH = pd.read_csv(RES / "LSIP_cohort_scenarios.csv")
CSUM = json.loads((RES / "LSIP_cohort_summary.json").read_text())
SNAP = json.loads((RES / "LSIP_market_snapshot.json").read_text(encoding="utf-8"))
RPC = pd.read_csv(RES / "LSIP_related_party_cash.csv", index_col=0)

f25, o25, c25 = FIN.loc["FY2025"] / 1000, OPS.loc["FY2025"], COGS.loc["FY2025"].drop("source") / 1000
PRICE = float(SNAP["lsip_last_close"]["close"])
SHARES = 6819.963965

# ---------------------------------------------------------------- inputs: (key, label, value, unit, source, fmt)
INPUTS = [
    ("scen", "Replanting scenario (1 A historical, 2 B accelerated, 3 C deferred, 4 D intensive)", 1, "#", "selector", "0"),
    ("pcase", "CPO price case (1 bear, 2 base, 3 bull)", 2, "#", "selector", "0"),
    (None, "PRICES (realised, IDR/kg CPO; PK priced as a ratio)", None, None, None, None),
    ("p26", "Realised CPO price FY2026E", 15200, "IDR/kg", "9M26 palm revenue / CPO-equivalent volume = 15.3k (DER); Q4 lower (HRef Nov -6%)", "#,##0"),
    ("p27b", "FY2027E realised CPO - bear", 12500, "IDR/kg", "ANALYST", "#,##0"),
    ("p27m", "FY2027E realised CPO - base", 14600, "IDR/kg", "ANALYST (2025 realised 14.6k DER; 2026 15.2k)", "#,##0"),
    ("p27u", "FY2027E realised CPO - bull", 16500, "IDR/kg", "ANALYST", "#,##0"),
    ("plrb", "Long-run (FY2029) realised CPO - bear", 12000, "IDR/kg", "ANALYST", "#,##0"),
    ("plrm", "Long-run (FY2029) realised CPO - base", 14000, "IDR/kg", "ANALYST: below 2025-26 realised (levy/B50 uncertainty)", "#,##0"),
    ("plru", "Long-run (FY2029) realised CPO - bull", 16500, "IDR/kg", "ANALYST", "#,##0"),
    ("pesc", "Nominal price escalation after FY2029", 0.025, "%/yr", "ANALYST (~0% real)", "0.0%"),
    ("pkr", "PK products price / CPO price", 0.80, "x", "Calibrated FY2025 (DER)", "0.00"),
    ("oth", "Other revenue (seeds, rubber, cocoa, tea) / palm revenue", 0.05, "%", "Calibrated FY2025 (DER)", "0.0%"),
    (None, "OPERATIONS", None, None, None, None),
    ("ffb26", "FY2026E nucleus FFB (9M actual 850 + Q4E)", 1180, "kt", "9M26 highlights + Q4E (Q4/Q3 2025 seasonality)", "#,##0"),
    ("oer", "CPO extraction rate", 0.220, "%", "FY25 21.9%, 9M26 22.4% (highlights)", "0.0%"),
    ("ker", "PK extraction rate", 0.061, "%", "FY25 6.1% (highlights)", "0.0%"),
    ("ext", "External FFB purchased (plasma + third party)", 200, "kt", "FY25 204kt; 9M26 166kt", "#,##0"),
    ("ffbp", "External FFB price / CPO price", 0.235, "x", "FY25 FFB purchases 672bn / 204kt / 14.0k (DER)", "0.000"),
    (None, "COSTS (FY2025 base, escalated)", None, None, None, None),
    ("ind", "Indirect / estate overhead (fixed)", round(c25.indirect, 1), "IDR bn", "FY25 COGS note", "#,##0.0"),
    ("hrv", "Harvesting cost per t nucleus FFB", round(c25.harvesting / o25.ffb_nucleus * 1000, 1), "IDR '000/t", "FY25 COGS note / nucleus FFB", "#,##0.0"),
    ("upk", "Upkeep & fertiliser per mature ha", round(c25.upkeep_fertiliser / o25.op_mature * 1000, 3), "IDR m/ha", "FY25 COGS note / mature ha", "0.000"),
    ("fert", "Fertiliser/upkeep intensity multiplier", 1.0, "x", "sensitivity", "0.00"),
    ("mill", "Milling cost per t FFB processed", round(c25.manufacturing / o25.ffb_total * 1000, 1), "IDR '000/t", "FY25 COGS note", "#,##0.0"),
    ("sell", "Selling & distribution / revenue", round(f25.selling / f25.revenue * -1, 4), "%", "FY25 FS", "0.0%"),
    ("ga", "General & administrative (fixed)", round(-f25.ga, 1), "IDR bn", "FY25 FS", "#,##0.0"),
    ("cesc", "Cost escalation", 0.030, "%/yr", "ANALYST", "0.0%"),
    (None, "CAPEX", None, None, None, None),
    ("rpc", "Replanting cost per ha (land prep to maturity, 2025 IDR)", 100.0, "IDR m/ha", "Calibrated: immature additions FY23-25 avg 193bn / ~1.6k ha planted, ~80% oil palm (DER)", "0.0"),
    ("sp0", "Share of replanting cost in planting year", 0.40, "%", "ANALYST", "0%"),
    ("mcx", "Maintenance capex (mills, buildings, vehicles)", 255.0, "IDR bn", "FY25 capex 433 - immature bearer additions 178", "#,##0"),
    ("r23", "Planted FY2023 (reconstructed)", 1351.0, "ha", "cohort reconstruction", "#,##0"),
    ("r24", "Planted FY2024 (reconstructed)", 1664.0, "ha", "cohort reconstruction", "#,##0"),
    ("r25", "Planted FY2025 (reconstructed)", 1861.0, "ha", "cohort reconstruction", "#,##0"),
    (None, "TAX, FINANCE, WORKING CAPITAL", None, None, None, None),
    ("tax", "Corporate tax rate", 0.22, "%", "statutory", "0%"),
    ("dy", "Pre-tax deposit yield", 0.040, "%", "9M26 finance income 239bn / avg cash (DER); notes 3.15-6.50%", "0.0%"),
    ("ftx", "Final tax on interest", 0.20, "%", "statute", "0%"),
    ("dar", "D&A / opening net fixed assets", 0.075, "%", "FY25 (DER)", "0.0%"),
    ("nwc", "Operating working capital / revenue", 0.08, "%", "ANALYST (inventory + bio assets + receivables - payables)", "0.0%"),
    ("np9m", "Profit to owners 9M26 (reported)", 1744.886, "IDR bn", "9M26 FS", "#,##0.0"),
    ("q4e", "Q4 2026E profit to owners (nowcast v2 base)", round(float(pd.read_csv(RES / "LSIP_q4_2026_nowcast_v2.csv", index_col=0).loc["base", "q4_np_owners"]), 1), "IDR bn", "quant/lsip_phase17_analysis.py (set by script)", "#,##0.0"),
    ("othlr", "Other operating income net, normal (FY2027+ pre-tax, 2025 IDR)", 60.0, "IDR bn", "ANALYST (FY24-25 ex impairment ~60-130)", "#,##0"),
    (None, "CAPITAL RETURN", None, None, None, None),
    ("pay", "Dividend payout (of prior-year profit)", 0.30, "%", "FY24-25 30%; FY21-23 35% (company)", "0%"),
    ("div26", "Dividend paid FY2026 (FY25 final, Rp83)", 566.057, "IDR bn", "9M26 FS note (Rp83/share)", "#,##0"),
    ("bb", "Share buyback executed (Oct-Dec 2026)", 0.0, "IDR bn", "UNVERIFIED: up to 750bn authorised; base = 0 executed", "#,##0"),
    ("bbp", "Buyback price", PRICE, "IDR/share", "price 25 Nov 2026", "#,##0"),
    ("sh", "Shares outstanding", SHARES, "mn", "FS: 6,819,963,965", "#,##0.0"),
    ("px", "Share price (25 Nov 2026)", PRICE, "IDR", "Yahoo S-002", "#,##0"),
    (None, "VALUATION", None, None, None, None),
    ("rf", "Risk-free (10y SBN)", 0.0774, "%", "S-052 (7.735%)", "0.00%"),
    ("beta", "Beta (relevered, sector)", 0.90, "x", "Phase VII market beta 0.74, sector beta ~1 (ANALYST blend)", "0.00"),
    ("erp", "Equity risk premium", 0.060, "%", "ANALYST (Indonesia)", "0.0%"),
    ("g", "Terminal nominal growth (0% real)", 0.025, "%", "equal to price escalation; ANALYST", "0.0%"),
    ("cash26", "Cash at 30 Sep 2026", round(FIN.loc["9M26", "cash_end"] / 1000, 1), "IDR bn", "9M26 FS", "#,##0"),
    ("mincash", "Minimum operating cash (~2 months cash costs)", 592.0, "IDR bn", "9M26 cash costs 2,664bn / 9 x 2 (DER)", "#,##0"),
    ("seas", "Seasonal working-capital buffer", 300.0, "IDR bn", "ANALYST: FG inventory swing 9M26 (+172bn) and Q3 build", "#,##0"),
    ("eb", "Employee benefits liability (debt-like)", round(FIN.loc["9M26", "employee_benefits_lt"] / 1000, 1), "IDR bn", "9M26 FS", "#,##0"),
    ("taxp", "Taxes payable and accrued (debt-like, net)", 209.0, "IDR bn", "FY25 FS taxes payable", "#,##0"),
    ("rp", "Cash at related-party bank (Bank Ina Perdana)", round(RPC.loc["9M26", "bank_ina_perdana"] / 1000, 1), "IDR bn", "9M26 FS note", "#,##0"),
    ("rph", "Haircut on related-party cash", 0.0, "%", "sensitivity", "0%"),
    ("cr", "Credit for distributable surplus cash (minority realisation)", 0.8, "x", "ANALYST base 80% (governance: 30% payout, 63% sales to parent, related-party deposits, buyback unverified); sensitivity 60-100%", "0%"),
    ("yld", "FFB yield multiplier on cohort production FY2027+ (k sensitivity)", 1.0, "x", "sensitivity", "0.00"),
    ("tvp", "Terminal sustainable productivity multiplier (steady state)", 1.0, "x", "sensitivity", "0.00"),
    ("fxm", "USD/IDR multiplier on realised CPO price FY2027+ (1.10 = IDR 10% weaker)", 1.0, "x", "sensitivity; levy/duty second-round effects ignored", "0.00"),
    ("hur", "Investment hurdle (12-month expected total return)", 0.175, "%", "D-030 / A-024; proposed restatement 18.1% (A-049, not adopted)", "0.0%"),
]
KEY = {}


def build() -> openpyxl.Workbook:
    wb = openpyxl.Workbook()
    ws = wb.active; ws.title = "Cover"
    ws["A1"] = "PT PP London Sumatra Indonesia Tbk (LSIP) - integrated model and valuation"; ws["A1"].font = Font(name="Arial", bold=True, size=12)
    notes = ["Phase XVII, 25 Nov 2026. IDR bn unless stated. Blue = input, black = formula, green = link to another sheet.",
             "Flow: Inputs -> Cohort (production from valuation/lsip_cohort.py, values) -> Model (FY2026E-FY2050E integrated statements) -> Valuation.",
             "Select scenario in Inputs!B3 (1-4) and price case in Inputs!B4 (1-3).",
             "Historical sheet: audited FY2020-FY2025 and 9M26 (quant/lsip_fs_extract.py; identities pass).",
             "Recalculation: built with openpyxl; verified with valuation/xlsx_eval.py (no Excel/LibreOffice in the build environment).",
             "The yield curve is an analyst assumption scaled to LSIP (k); it is not an empirically validated LSIP age-yield relationship.",
             "Not investment advice."]
    for i, t in enumerate(notes, 3):
        ws[f"A{i}"] = t; ws[f"A{i}"].font = BLACK
    ws.column_dimensions["A"].width = 130

    I = wb.create_sheet("Inputs")
    I["A1"] = "Inputs"; I["A1"].font = BOLD
    for c, h in zip("ABCD", ["Item", "Value", "Unit", "Source / basis"]):
        I[f"{c}2"] = h; I[f"{c}2"].font = BOLD
    r = 3
    for key, lab, val, unit, src, fmt in INPUTS:
        I[f"A{r}"] = lab; I[f"A{r}"].font = BOLD if key is None else BLACK
        if key:
            I[f"B{r}"] = val; I[f"B{r}"].font = BLUE; I[f"B{r}"].number_format = fmt
            I[f"C{r}"] = unit; I[f"D{r}"] = src
            KEY[key] = f"Inputs!$B${r}"
            if key in ("scen", "pcase"):
                I[f"B{r}"].fill = YEL
        r += 1
    # derived inputs
    I[f"A{r}"] = "Cost of equity = rf + beta x ERP (ungeared; no debt)"; I[f"B{r}"] = f"={KEY['rf']}+{KEY['beta']}*{KEY['erp']}"
    I[f"B{r}"].number_format = "0.00%"; KEY["ke"] = f"Inputs!$B${r}"; r += 1
    I[f"A{r}"] = "FY2027E price (selected case)"; I[f"B{r}"] = f"=INDEX({KEY['p27b']}:{KEY['p27u'].split('!')[1]},{KEY['pcase']},1)"
    I[f"B{r}"].number_format = "#,##0"; KEY["p27"] = f"Inputs!$B${r}"; r += 1
    I[f"A{r}"] = "Long-run FY2029 price (selected case)"; I[f"B{r}"] = f"=INDEX({KEY['plrb']}:{KEY['plru'].split('!')[1]},{KEY['pcase']},1)"
    I[f"B{r}"].number_format = "#,##0"; KEY["plr"] = f"Inputs!$B${r}"; r += 1
    for c, w in zip("ABCD", (62, 12, 11, 95)):
        I.column_dimensions[c].width = w

    # ---------------------------------------------------------------- Cohort sheet (values from the Python model)
    Co = wb.create_sheet("Cohort")
    Co["A1"] = "Production by replanting scenario - values from valuation/lsip_cohort.py (ensemble base member); 2051 = steady state"
    Co["A1"].font = BOLD
    for y in YEARS:
        Co[f"{COL[y]}2"] = y; Co[f"{COL[y]}2"].font = BOLD
    Co[f"{TV}2"] = "2051 SS"; Co[f"{TV}2"].font = BOLD
    k_new = CSUM["k_hist_2021_2025_base"] * 1.15
    ss_ffb = CSUM["steady_state_yield_per_planted_ha_k1"] * k_new * 89331 / 1000
    ss_mature = 89331 * 22 / 25
    rows = {}
    fields = [("ffb_nucleus_kt", "nucleus FFB (kt)"), ("replant_ha", "replanting (ha)"), ("mature_ha", "mature area (ha)"),
              ("immature_ha", "immature area (ha)"), ("avg_age", "average age (yrs)"), ("gt20_ha", "area >20 yrs (ha)")]
    r = 3
    for si, s in enumerate(SCN):
        g = COH[COH.scenario == s].set_index("year")
        for f, lab in fields:
            Co[f"A{r}"] = f"{s} - {lab}"
            for y in YEARS:
                Co[f"{COL[y]}{r}"] = round(float(g.loc[y, f]), 3); Co[f"{COL[y]}{r}"].font = BLUE
            ss = CSUM["steady_state"][s][f]
            Co[f"{TV}{r}"] = round(ss, 3); Co[f"{TV}{r}"].font = BLUE
            rows[(si, f)] = r
            r += 1
        r += 1
    Co[f"A{r + 1}"] = ("Steady state (col 2051): each scenario's long-run planting rate held forever (A/C historical ~1,840 ha/yr = "
                       "~49-yr cycle; B/D sustainable 3,573 ha/yr = 25-yr cycle); uniform ages; all area on replanted material (k x 1.15).")
    Co.column_dimensions["A"].width = 42
    # selected-scenario block
    sel = {}
    r += 3
    Co[f"A{r}"] = "SELECTED SCENARIO (Inputs!B3)"; Co[f"A{r}"].font = BOLD; r += 1
    for f, lab in fields:
        Co[f"A{r}"] = f"selected - {lab}"
        for c in [COL[y] for y in YEARS] + [TV]:
            rr = [rows[(si, f)] for si in range(4)]
            Co[f"{c}{r}"] = (f"=IF({KEY['scen']}=1,{c}{rr[0]},IF({KEY['scen']}=2,{c}{rr[1]},IF({KEY['scen']}=3,{c}{rr[2]},{c}{rr[3]})))")
        sel[f] = r; r += 1

    # ---------------------------------------------------------------- Model sheet
    M = wb.create_sheet("Model")
    M["A1"] = "Integrated model (IDR bn unless stated)"; M["A1"].font = BOLD
    M["B2"] = "FY2025A"; M["B2"].font = BOLD
    for y in YEARS:
        M[f"{COL[y]}2"] = f"FY{y}E"; M[f"{COL[y]}2"].font = BOLD
    M[f"{TV}2"] = "FY2051 SS"; M[f"{TV}2"].font = BOLD
    R = {}
    order = ["year", "ffb_n", "replant", "mature", "ffb_ext", "ffb_proc", "cpo", "pk", "price", "rev_cpo", "rev_pk", "rev_oth", "revenue",
             "idx", "c_ind", "c_hrv", "c_upk", "c_mill", "c_ffb", "c_prod", "selling", "ga", "ebitda", "da", "ebit", "fin_inc", "pbt", "tax",
             "oth_at", "ni", "div", "bb", "cx_rep", "cx_mnt", "capex", "nwc", "dnwc", "cfo", "fcfe_pre", "cash_open", "cash", "fa", "other", "assets",
             "eb", "equity", "check", "shares", "eps", "dps", "fcff", "ebitda_m"]
    labels = {"year": "Year", "ffb_n": "Nucleus FFB (kt)", "replant": "Replanting (ha)", "mature": "Mature area (ha)",
              "ffb_ext": "External FFB (kt)", "ffb_proc": "FFB processed (kt)", "cpo": "CPO produced/sold (kt)", "pk": "PK produced/sold (kt)",
              "price": "Realised CPO price (IDR/kg)", "rev_cpo": "Revenue - CPO", "rev_pk": "Revenue - PK products", "rev_oth": "Revenue - other",
              "revenue": "Revenue", "idx": "Cost index (2025 = 1)", "c_ind": "Indirect / estate overhead", "c_hrv": "Harvesting",
              "c_upk": "Upkeep & fertiliser", "c_mill": "Milling", "c_ffb": "External FFB purchases", "c_prod": "Cash production cost",
              "selling": "Selling & distribution", "ga": "General & administrative", "ebitda": "EBITDA (ex FV of biological assets)",
              "da": "Depreciation & amortisation", "ebit": "EBIT (operating)", "fin_inc": "Finance income (deposits)", "pbt": "Profit before tax",
              "tax": "Tax (22% operating; 20% final on interest)", "oth_at": "Other items after tax (FY26: FV, FX, other income -> reconciles to 9M + Q4E)", "ni": "Net profit to owners", "div": "Dividends paid (cash)",
              "bb": "Share buyback", "cx_rep": "Replanting capex", "cx_mnt": "Maintenance capex", "capex": "Total capex",
              "nwc": "Operating working capital", "dnwc": "Change in working capital", "cfo": "Cash flow from operations",
              "fcfe_pre": "Free cash flow (CFO - capex)", "cash_open": "Opening cash", "cash": "Closing cash", "fa": "Net fixed assets (incl. bearer plants)",
              "other": "Other net assets (constant, FY25 plug)", "assets": "Net assets (cash + NWC + FA + other)", "eb": "Employee benefits liability",
              "equity": "Equity", "check": "Balance check (net assets - EB - equity)", "shares": "Shares outstanding (mn)", "eps": "EPS (IDR)",
              "dps": "DPS paid in year (IDR)", "fcff": "Operating FCFF (ex interest)", "ebitda_m": "EBITDA margin"}
    for i, k in enumerate(order, start=3):
        R[k] = i; M[f"A{i}"] = labels[k]
    M.column_dimensions["A"].width = 42
    K = KEY
    # FY2025A column (audited / reported)
    hist = {"ffb_n": o25.ffb_nucleus, "mature": o25.op_mature, "ffb_ext": o25.ffb_total - o25.ffb_nucleus, "ffb_proc": o25.ffb_total,
            "cpo": o25.cpo, "pk": o25.pk, "revenue": f25.revenue, "ebitda": 2451.72, "ni": f25.profit_owners if "profit_owners" in f25 else 1887.756,
            "cash": f25.cash_end, "fa": f25.fixed_assets_net, "equity": f25.total_equity, "eb": f25.employee_benefits_lt, "shares": SHARES,
            "capex": -f25.capex, "div": -f25.dividends_paid, "fin_inc": f25.finance_income}
    for k, v in hist.items():
        M[f"B{R[k]}"] = round(float(v), 3); M[f"B{R[k]}"].font = BLUE
    M[f"B{R['ni']}"] = 1887.756
    M[f"B{R['nwc']}"] = f"=B{R['revenue']}*{K['nwc']}"
    M[f"B{R['other']}"] = f"=B{R['equity']}+B{R['eb']}-B{R['cash']}-B{R['nwc']}-B{R['fa']}"
    M[f"B{R['replant']}"] = f"={K['r25']}"
    cols = [COL[y] for y in YEARS]
    for i, y in enumerate(YEARS):
        c = COL[y]; p = "B" if i == 0 else COL[y - 1]
        cell = lambda k: f"{c}{R[k]}"  # noqa: E731
        prev = lambda k: f"{p}{R[k]}"  # noqa: E731
        M[cell("year")] = y
        M[cell("ffb_n")] = f"={K['ffb26']}" if y == 2026 else f"=Cohort!{c}{sel['ffb_nucleus_kt']}*{K['yld']}"
        M[cell("replant")] = f"=Cohort!{c}{sel['replant_ha']}"
        M[cell("mature")] = f"=Cohort!{c}{sel['mature_ha']}"
        M[cell("ffb_ext")] = f"={K['ext']}"
        M[cell("ffb_proc")] = f"={cell('ffb_n')}+{cell('ffb_ext')}"
        M[cell("cpo")] = f"={cell('ffb_proc')}*{K['oer']}"
        M[cell("pk")] = f"={cell('ffb_proc')}*{K['ker']}"
        if y == 2026:
            M[cell("price")] = f"={K['p26']}"
        elif y == 2027:
            M[cell("price")] = f"={K['p27']}*{K['fxm']}"
        elif y == 2028:
            M[cell("price")] = f"=({K['p27']}+{K['plr']})/2*{K['fxm']}"
        elif y == 2029:
            M[cell("price")] = f"={K['plr']}*{K['fxm']}"
        else:
            M[cell("price")] = f"={prev('price')}*(1+{K['pesc']})"
        M[cell("rev_cpo")] = f"={cell('cpo')}*{cell('price')}/1000"
        M[cell("rev_pk")] = f"={cell('pk')}*{cell('price')}*{K['pkr']}/1000"
        M[cell("rev_oth")] = f"=({cell('rev_cpo')}+{cell('rev_pk')})*{K['oth']}"
        M[cell("revenue")] = f"={cell('rev_cpo')}+{cell('rev_pk')}+{cell('rev_oth')}"
        M[cell("idx")] = f"=(1+{K['cesc']})^({y}-2025)"
        M[cell("c_ind")] = f"={K['ind']}*{cell('idx')}"
        M[cell("c_hrv")] = f"={cell('ffb_n')}*{K['hrv']}/1000*{cell('idx')}"
        M[cell("c_upk")] = f"={cell('mature')}*{K['upk']}/1000*{cell('idx')}*{K['fert']}"
        M[cell("c_mill")] = f"={cell('ffb_proc')}*{K['mill']}/1000*{cell('idx')}"
        M[cell("c_ffb")] = f"={cell('ffb_ext')}*{cell('price')}*{K['ffbp']}/1000"
        M[cell("c_prod")] = f"={cell('c_ind')}+{cell('c_hrv')}+{cell('c_upk')}+{cell('c_mill')}+{cell('c_ffb')}"
        M[cell("selling")] = f"={cell('revenue')}*{K['sell']}"
        M[cell("ga")] = f"={K['ga']}*{cell('idx')}"
        M[cell("ebitda")] = f"={cell('revenue')}-{cell('c_prod')}-{cell('selling')}-{cell('ga')}"
        M[cell("ebitda_m")] = f"=IF({cell('revenue')}>0,{cell('ebitda')}/{cell('revenue')},0)"
        M[cell("da")] = f"={prev('fa')}*{K['dar']}"
        M[cell("ebit")] = f"={cell('ebitda')}-{cell('da')}"
        M[cell("fin_inc")] = f"={prev('cash')}*{K['dy']}"
        M[cell("pbt")] = f"={cell('ebit')}+{cell('fin_inc')}"
        M[cell("tax")] = f"=MAX(0,{cell('ebit')})*{K['tax']}+{cell('fin_inc')}*{K['ftx']}"
        if y == 2026:
            M[cell("oth_at")] = f"={K['np9m']}+{K['q4e']}-({cell('pbt')}-{cell('tax')})"
        else:
            M[cell("oth_at")] = f"={K['othlr']}*{cell('idx')}*(1-{K['tax']})"
        M[cell("ni")] = f"={cell('pbt')}-{cell('tax')}+{cell('oth_at')}"
        M[cell("div")] = f"={K['div26']}" if y == 2026 else f"=MAX(0,{prev('ni')}*{K['pay']})"
        M[cell("bb")] = f"={K['bb']}" if y == 2026 else "=0"
        # replanting capex: sp0 in planting year, (1-sp0)/3 in each of the next three years
        r1 = f"{K['r25']}" if y == 2026 else prev("replant")
        r2 = f"{K['r24']}" if y == 2026 else (f"{K['r25']}" if y == 2027 else f"{COL[y - 2]}{R['replant']}")
        r3 = f"{K['r23']}" if y == 2026 else (f"{K['r24']}" if y == 2027 else (f"{K['r25']}" if y == 2028 else f"{COL[y - 3]}{R['replant']}"))
        M[cell("cx_rep")] = (f"={K['rpc']}/1000*{cell('idx')}*({K['sp0']}*{cell('replant')}+(1-{K['sp0']})/3*({r1}+{r2}+{r3}))")
        M[cell("cx_mnt")] = f"={K['mcx']}*{cell('idx')}"
        M[cell("capex")] = f"={cell('cx_rep')}+{cell('cx_mnt')}"
        M[cell("nwc")] = f"={cell('revenue')}*{K['nwc']}"
        M[cell("dnwc")] = f"={cell('nwc')}-{prev('nwc')}"
        M[cell("cfo")] = f"={cell('ni')}+{cell('da')}-{cell('dnwc')}"
        M[cell("fcfe_pre")] = f"={cell('cfo')}-{cell('capex')}"
        M[cell("cash_open")] = f"={prev('cash')}"
        M[cell("cash")] = f"={cell('cash_open')}+{cell('cfo')}-{cell('capex')}-{cell('div')}-{cell('bb')}"
        M[cell("fa")] = f"={prev('fa')}+{cell('capex')}-{cell('da')}"
        M[cell("other")] = f"={prev('other')}"
        M[cell("assets")] = f"={cell('cash')}+{cell('nwc')}+{cell('fa')}+{cell('other')}"
        M[cell("eb")] = f"={prev('eb')}"
        M[cell("equity")] = f"={prev('equity')}+{cell('ni')}-{cell('div')}-{cell('bb')}"
        M[cell("check")] = f"={cell('assets')}-{cell('eb')}-{cell('equity')}"
        M[cell("shares")] = f"={prev('shares')}-{cell('bb')}*1000/{K['bbp']}"
        M[cell("eps")] = f"={cell('ni')}*1000/{cell('shares')}"
        M[cell("dps")] = f"={cell('div')}*1000/{prev('shares')}"
        M[cell("fcff")] = f"={cell('ebit')}*(1-{K['tax']})+{cell('da')}-{cell('capex')}-{cell('dnwc')}"
    M[f"B{R['other']}"].font = BLACK
    # steady-state terminal column (FY2051): sustainable replanting, capex = D&A, no NWC growth beyond inflation
    c, p = TV, COL[2050]
    M[f"{c}{R['ffb_n']}"] = f"=Cohort!{c}{sel['ffb_nucleus_kt']}*{K['yld']}*{K['tvp']}"
    M[f"{c}{R['replant']}"] = f"=Cohort!{c}{sel['replant_ha']}"
    M[f"{c}{R['mature']}"] = f"=Cohort!{c}{sel['mature_ha']}"
    M[f"{c}{R['ffb_ext']}"] = f"={K['ext']}"
    M[f"{c}{R['ffb_proc']}"] = f"={c}{R['ffb_n']}+{c}{R['ffb_ext']}"
    M[f"{c}{R['cpo']}"] = f"={c}{R['ffb_proc']}*{K['oer']}"
    M[f"{c}{R['pk']}"] = f"={c}{R['ffb_proc']}*{K['ker']}"
    M[f"{c}{R['price']}"] = f"={p}{R['price']}*(1+{K['pesc']})"
    for k in ("rev_cpo", "rev_pk", "rev_oth", "revenue", "c_ind", "c_hrv", "c_upk", "c_mill", "c_ffb", "c_prod", "selling", "ga", "ebitda"):
        M[f"{c}{R[k]}"] = M[f"{p}{R[k]}"].value.replace(p, c)
    M[f"{c}{R['idx']}"] = f"=(1+{K['cesc']})^(2051-2025)"
    M[f"{c}{R['cx_rep']}"] = f"={K['rpc']}/1000*{c}{R['idx']}*{c}{R['replant']}"
    M[f"{c}{R['cx_mnt']}"] = f"={K['mcx']}*{c}{R['idx']}"
    M[f"{c}{R['capex']}"] = f"={c}{R['cx_rep']}+{c}{R['cx_mnt']}"
    M[f"{c}{R['da']}"] = f"={c}{R['capex']}"
    M[f"{c}{R['ebit']}"] = f"={c}{R['ebitda']}-{c}{R['da']}"
    M[f"{c}{R['nwc']}"] = f"={c}{R['revenue']}*{K['nwc']}"
    M[f"{c}{R['dnwc']}"] = f"={c}{R['nwc']}-{p}{R['nwc']}"
    M[f"{c}{R['fcff']}"] = f"={c}{R['ebit']}*(1-{K['tax']})+{c}{R['da']}-{c}{R['capex']}-{c}{R['dnwc']}"
    M[f"{c}{R['ni']}"] = f"={c}{R['ebit']}*(1-{K['tax']})"
    for row in M.iter_rows(min_row=3, max_row=60, min_col=2, max_col=C0 + len(YEARS)):
        for x in row:
            if x.value is not None and x.font != BLUE:
                x.font = GREEN if isinstance(x.value, str) and "Cohort!" in x.value else (x.font if x.font == BLUE else BLACK)
                x.number_format = "#,##0;(#,##0);-"
    for k in ("ebitda_m",):
        for cc in cols + [TV]:
            M[f"{cc}{R[k]}"].number_format = "0.0%"
    for cc in ["B"] + cols + [TV]:
        M[f"{cc}{R['idx']}"].number_format = "0.000"
        M[f"{cc}{R['year']}"].number_format = "0"
    for cc in cols + [TV]:
        M.column_dimensions[cc].width = 9

    # ---------------------------------------------------------------- Valuation sheet
    V = wb.create_sheet("Valuation")
    V["A1"] = "Valuation at 31 Dec 2026 (IDR bn; per-share IDR). Discounting: FY2027 = 1 year."; V["A1"].font = BOLD
    V["A3"] = "Cost of equity (= WACC, no debt)"; V["B3"] = f"={K['ke']}"
    for i, y in enumerate(YEARS[1:], start=0):
        cc = COL[y]
        V[f"{cc}5"] = y
        V[f"{cc}6"] = f"=1/(1+$B$3)^({y}-2026)"
        V[f"{cc}7"] = f"=Model!{cc}{R['fcff']}*{cc}6"
        V[f"{cc}8"] = f"=Model!{cc}{R['div']}*{cc}6"
    V["A5"] = "Year"; V["A6"] = "Discount factor"; V["A7"] = "PV operating FCFF"; V["A8"] = "PV dividends paid"
    first, last = COL[2027], COL[2050]
    lines = [
        ("pv_fcff", "Sum PV FCFF FY2027-FY2050", f"=SUM({first}7:{last}7)"),
        ("tv", "Terminal value at 2050 (steady state FY2051 FCFF / (ke - g))", f"=Model!{TV}{R['fcff']}/($B$3-{K['g']})"),
        ("pv_tv", "PV terminal value", f"=B11*{last}6"),
        ("ev", "Operating enterprise value (plantations, ex cash)", "=B10+B12"),
        ("cash", "Cash at 31 Dec 2026 (model)", f"=Model!{COL[2026]}{R['cash']}"),
        ("opcash", "less minimum operating cash and seasonal buffer", f"=-({K['mincash']}+{K['seas']})"),
        ("rphc", "less haircut on related-party cash", f"=-{K['rp']}*{K['rph']}"),
        ("surplus", "Distributable surplus cash (before realisation credit)", "=B14+B15+B16"),
        ("credit", "x realisation credit", f"=B17*{K['cr']}"),
        ("debt", "less debt-like items (employee benefits, taxes payable)", f"=-({K['eb']}+{K['taxp']})"),
        ("eq", "Equity value (FCFF DCF + surplus cash)", "=B13+B18+B19"),
        ("ps", "Equity value per share (IDR)", f"=B20*1000/Model!{COL[2026]}{R['shares']}"),
        ("ops_ps", "  of which plantation operations per share", f"=(B13+B19)*1000/Model!{COL[2026]}{R['shares']}"),
        ("cash_ps", "  of which surplus cash per share", f"=B18*1000/Model!{COL[2026]}{R['shares']}"),
        ("ddm_pv", "DDM: PV dividends FY2027-FY2050", f"=SUM({first}8:{last}8)"),
        ("ddm_tv", "DDM: terminal (FY2051 dividend = payout x SS profit + cash yield) / (ke - g)",
         f"=({K['pay']}*(Model!{TV}{R['ni']}+Model!{last}{R['cash']}*{K['dy']}*(1-{K['ftx']})))/($B$3-{K['g']})*{last}6"),
        ("ddm_ps", "DDM value per share (minority cash receipts only; IDR)", f"=(B24+B25)*1000/Model!{COL[2026]}{R['shares']}"),
        ("trapped", "Value gap: DCF+cash minus DDM, per share (IDR)", "=B21-B26"),
        ("ev_ha", "Operating EV per planted oil-palm ha (IDR m)", "=B13*1000/89331"),
        ("pe27", "P/E FY2027E at current price", f"={K['px']}/Model!{COL[2027]}{R['eps']}"),
        ("ev_ebitda27", "Market EV / EBITDA FY2027E (EV = mcap - surplus cash + debt-like)",
         f"=({K['px']}*{K['sh']}/1000-B17-B19)/Model!{COL[2027]}{R['ebitda']}"),
        ("tp12", "12-month target price (value rolled 11 months at ke, less FY2027 DPS)",
         f"=B21*(1+$B$3)^(11/12)-Model!{COL[2027]}{R['dps']}"),
        ("dps27", "DPS paid FY2027E (IDR)", f"=Model!{COL[2027]}{R['dps']}"),
        ("tr12", "Expected 12-month total return at current price", f"=(B31+B32)/{K['px']}-1"),
        ("entry", "Entry price that meets the hurdle (IDR)", f"=(B31+B32)/(1+{K['hur']})"),
        ("ps_full", "Equity value per share at 100% cash credit (IDR)", f"=(B13+B17+B19)*1000/Model!{COL[2026]}{R['shares']}"),
    ]
    for i, (k, lab, f) in enumerate(lines, start=10):
        V[f"A{i}"] = lab; V[f"B{i}"] = f; KEY["v_" + k] = f"Valuation!$B${i}"
        V[f"B{i}"].number_format = "#,##0;(#,##0)"
    for k in ("pe27", "ev_ebitda27"):
        V[KEY["v_" + k].split("!")[1].replace("$", "")].number_format = "0.0x"
    V[KEY["v_tr12"].split("!")[1].replace("$", "")].number_format = "0.0%"
    V["B3"].number_format = "0.00%"
    V.column_dimensions["A"].width = 70
    return wb


def add_history(wb) -> None:
    H = wb.create_sheet("Historical")
    H["A1"] = "Audited / reported history (IDR bn; operating in ha, '000 t). Sources: quant/lsip_fs_extract.py, quant/lsip_ops_dataset.py"
    H["A1"].font = BOLD
    per = ["FY2020", "FY2021", "FY2022", "FY2023", "FY2024", "FY2025", "9M25", "9M26"]
    items = ["revenue", "cogs", "gross_profit", "fv_bio", "operating_profit", "finance_income", "pbt", "tax", "profit", "cfo", "capex",
             "dividends_paid", "cash_end", "total_assets", "total_liabilities", "total_equity", "employee_benefits_lt"]
    for j, p in enumerate(per):
        H[f"{L(2 + j)}3"] = p; H[f"{L(2 + j)}3"].font = BOLD
    r = 4
    for it in items:
        H[f"A{r}"] = it
        for j, p in enumerate(per):
            v = FIN.loc[p, it] if p in FIN.index and it in FIN.columns else np.nan
            if pd.notna(v):
                H[f"{L(2 + j)}{r}"] = round(float(v) / 1000, 1); H[f"{L(2 + j)}{r}"].number_format = "#,##0.0;(#,##0.0)"
        r += 1
    r += 1
    for it in ["oil_palm", "op_mature", "op_immature", "ffb_nucleus", "ffb_total", "cpo", "pk", "yield_nucleus_t_ha", "oer_derived"]:
        H[f"A{r}"] = it
        for j, p in enumerate(["FY2020", "FY2021", "FY2022", "FY2023", "FY2024", "FY2025", "9M25", "9M26"]):
            if p in OPS.index and pd.notna(OPS.loc[p, it]):
                H[f"{L(2 + j)}{r}"] = round(float(OPS.loc[p, it]), 2)
        r += 1
    r += 1
    for it in ["indirect", "ffb_purchases", "harvesting", "upkeep_fertiliser", "depreciation", "manufacturing", "total_production_cost"]:
        H[f"A{r}"] = f"COGS note: {it}"
        for j, p in enumerate(per):
            if p in COGS.index and pd.notna(COGS.loc[p, it]):
                H[f"{L(2 + j)}{r}"] = round(float(COGS.loc[p, it]) / 1000, 1)
        r += 1
    H.column_dimensions["A"].width = 34


def evaluate(wb, overrides: dict | None = None) -> dict:
    E = Evaluator(wb)
    for k, v in (overrides or {}).items():
        sh, ref = KEY[k].replace("$", "").split("!")
        E.set(sh, ref, v)
    g = lambda k: float(E.get(*KEY[k].replace("$", "").split("!")))  # noqa: E731
    out = {k[2:]: g(k) for k in KEY if k.startswith("v_")}
    return out, E


def model_rows(E, rows=("ffb_n", "revenue", "ebitda", "ni", "eps", "dps", "capex", "cx_rep", "fcff", "fcfe_pre", "cash", "check", "price", "mature", "replant")):
    return {r: {y: float(E.get("Model", f"{COL[y]}{ROWS[r]}")) for y in YEARS} for r in rows}


ROWS = {}


def main():
    wb = build(); add_history(wb)
    # recover row map from the Model sheet labels
    ws = wb["Model"]
    lab2key = {}
    from itertools import count  # noqa: F401
    for r in range(3, 60):
        v = ws[f"A{r}"].value
        if v:
            lab2key[v] = r
    keys = ["year", "ffb_n", "replant", "mature", "ffb_ext", "ffb_proc", "cpo", "pk", "price", "rev_cpo", "rev_pk", "rev_oth", "revenue",
            "idx", "c_ind", "c_hrv", "c_upk", "c_mill", "c_ffb", "c_prod", "selling", "ga", "ebitda", "da", "ebit", "fin_inc", "pbt", "tax",
            "oth_at", "ni", "div", "bb", "cx_rep", "cx_mnt", "capex", "nwc", "dnwc", "cfo", "fcfe_pre", "cash_open", "cash", "fa", "other", "assets",
            "eb", "equity", "check", "shares", "eps", "dps", "fcff", "ebitda_m"]
    for i, k in enumerate(keys, start=3):
        ROWS[k] = i
    OUTX.parent.mkdir(exist_ok=True)
    wb.save(OUTX)
    wb = openpyxl.load_workbook(OUTX)
    # 1. formula verification: evaluate every formula cell under every scenario x price case
    nform, errs = 0, []
    for sc in (1, 2, 3, 4):
        for pc in (1, 2, 3):
            E = Evaluator(wb); E.set("Inputs", KEY["scen"].split("!")[1].replace("$", ""), sc)
            E.set("Inputs", KEY["pcase"].split("!")[1].replace("$", ""), pc)
            for ws in wb.worksheets:
                for row in ws.iter_rows():
                    for x in row:
                        if isinstance(x.value, str) and x.value.startswith("="):
                            if sc == 1 and pc == 1:
                                nform += 1
                            try:
                                v = E.get(ws.title, x.coordinate)
                                if not np.isfinite(float(v)):
                                    errs.append((sc, pc, ws.title, x.coordinate, "non-finite"))
                            except Exception as exc:  # noqa: BLE001
                                errs.append((sc, pc, ws.title, x.coordinate, repr(exc)[:60]))
            chk = [abs(float(E.get("Model", f"{COL[y]}{ROWS['check']}"))) for y in YEARS]
            if max(chk) > 1e-6:
                errs.append((sc, pc, "Model", "check", max(chk)))
    results = {"formulas": nform, "formula_errors": errs[:20], "n_errors": len(errs), "price": PRICE}
    # 2. scenario x price-case grid
    grid, detail = {}, {}
    for si, s in enumerate(SCN, start=1):
        for pc, pn in ((1, "bear"), (2, "base"), (3, "bull")):
            v, E = evaluate(wb, {"scen": si, "pcase": pc})
            grid[f"{s}|{pn}"] = v
            if pn == "base" or si == 1:
                detail[f"{s}|{pn}"] = model_rows(E)
    results["grid"] = grid; results["detail"] = detail
    # 3. sensitivities on base (scenario A historical, base price)
    base = {"scen": 1, "pcase": 2}
    sens = {}
    for k, vals in {"plrm": [11000, 12500, 14000, 15500, 17000], "rpc": [70, 85, 100, 120, 140], "fert": [0.8, 0.9, 1.0, 1.1, 1.2],
                    "beta": [0.7, 0.8, 0.9, 1.0, 1.1], "pay": [0.3, 0.5, 0.7, 0.9, 1.0],
                    "g": [0.0, 0.01, 0.025], "bb": [0.0, 375.0, 750.0], "ext": [100, 200, 300], "oer": [0.21, 0.22, 0.23],
                    "yld": [0.85, 0.9, 1.0, 1.1, 1.15], "tvp": [0.8, 0.9, 1.0, 1.1], "fxm": [0.9, 0.95, 1.0, 1.05, 1.1],
                    "cr": [0.4, 0.6, 0.8, 1.0], "rph": [0.0, 0.5, 1.0]}.items():
        sens[k] = {str(x): evaluate(wb, base | {k: x})[0] for x in vals}
    results["sensitivity"] = sens
    # joint grid: scenario x price case x cash credit -> value, 12m return
    joint = {}
    for si, sname in enumerate(SCN, start=1):
        for pc, pn in ((1, "bear"), (2, "base"), (3, "bull")):
            for crv in (0.6, 0.8, 1.0):
                v = evaluate(wb, {"scen": si, "pcase": pc, "cr": crv})[0]
                joint[f"{sname}|{pn}|{crv}"] = {k: v[k] for k in ("ps", "ops_ps", "cash_ps", "ddm_ps", "tp12", "tr12", "entry")}
    results["joint"] = joint
    # LR price x ke grid (scenario A, credit 0.8) for the heat map
    results["grid_lr_beta"] = {f"{lr}|{b}": evaluate(wb, base | {"plrm": lr, "beta": b})[0]["ps"]
                               for lr in (11000, 12500, 14000, 15500, 17000) for b in (0.6, 0.75, 0.9, 1.05, 1.2)}
    # yield (k) and USD/IDR proxies: production x factor via ffb26-independent multiplier on all scenario rows is not an
    # input; FX enters through the realised IDR price (a 10% IDR depreciation ~ +10% realised price before levy effects).
    # 4. reverse valuations (bisection on base A scenario)
    def solve(key, lo, hi, target=PRICE, field="ps", over=None):
        f = lambda x: evaluate(wb, base | (over or {}) | {key: x})[0][field] - target  # noqa: E731
        flo, fhi = f(lo), f(hi)
        if flo * fhi > 0:
            return None
        for _ in range(40):
            mid = (lo + hi) / 2; fm = f(mid)
            if flo * fm <= 0:
                hi, fhi = mid, fm
            else:
                lo, flo = mid, fm
        return (lo + hi) / 2
    rev = {"implied_long_run_cpo_idr_kg": solve("plrm", 5000, 25000),
           "implied_long_run_cpo_full_cash_credit": solve("plrm", 5000, 25000, over={"cr": 1.0}),
           "implied_yield_multiplier": solve("yld", 0.2, 3.0),
           "implied_cash_credit_at_base_ops": solve("cr", -2.0, 2.0),
           "implied_cash_credit_bear_ops": solve("cr", -2.0, 3.0, over={"pcase": 1}),
           "implied_cost_of_equity_beta": solve("beta", 0.2, 4.0),
           "implied_replant_cost_m_per_ha": solve("rpc", 0, 600),
           "implied_fert_multiplier": solve("fert", 0.2, 3.0)}
    rev["implied_ke"] = None if rev["implied_cost_of_equity_beta"] is None else 0.0774 + rev["implied_cost_of_equity_beta"] * 0.06
    # DDM-implied payout that justifies the price
    rev["implied_payout_ddm"] = solve("pay", 0.0, 1.5, field="ddm_ps")
    results["reverse"] = rev
    (RES / "LSIP_valuation_results.json").write_text(json.dumps(results, indent=1, default=float), encoding="utf-8")
    print("formulas", nform, "errors", len(errs), errs[:5])
    show = pd.DataFrame({k: {f: v[f] for f in ("ps", "ps_full", "ops_ps", "cash_ps", "ddm_ps", "pe27", "ev_ebitda27", "tp12", "tr12", "entry")} for k, v in grid.items()}).T
    print(show.round(2).to_string())
    print(json.dumps(rev, indent=1))
    d = detail["A_historical|base"]
    print(pd.DataFrame(d).loc[[2026, 2027, 2028, 2030, 2035, 2040, 2050]].round(1).to_string())


if __name__ == "__main__":
    main()
