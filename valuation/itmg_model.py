"""ITMG integrated financial model and valuation workbook (Phase XVI).

    python -I -X utf8 valuation/itmg_model.py

Builds outputs/ITMG_model_valuation.xlsx with LIVE formulas (inputs in blue, scenario selector on 'Inputs'),
then evaluates every formula with valuation/xlsx_eval.py (no Excel/LibreOffice available in this environment),
runs Bear/Base/Bull, reverse DCF, consensus-implied Newcastle and sensitivity grids by overriding input cells,
writes those static result tables into the workbook, and saves data/reference/research/ITMG_valuation_results.json.

Evidence classes (kept separate, also labelled in the workbook):
  VALIDATED   - ITMG-C1 M2 (frozen) for the next-quarter ASP only (Q4 2026, provisional: data to 25 Nov 2026).
  BENCHMARK   - C2/C3 failed, so their strongest benchmarks are used: seasonal sales (q-4), last-quarter unit cost,
                last-quarter royalty rate. I1 (CONDITIONAL GO) structure for Q4 gross profit.
  ANALYST     - everything beyond one quarter (Newcastle deck, ASP/Newcastle ratio, cost-price relation, mine plans,
                licence extensions, capex, payout, discount rate). Not validated.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xlsx_eval import Evaluator  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "data" / "reference" / "research"
OUT = ROOT / "outputs" / "ITMG_model_valuation.xlsx"
YEARS = list(range(2026, 2051))
COL = {y: get_column_letter(3 + i) for i, y in enumerate(YEARS)}   # C=2026 ... AA=2050
F = "Arial"
BLUE, BLACK, GREEN = Font(name=F, color="0000FF"), Font(name=F, color="000000"), Font(name=F, color="008000")
BOLD = Font(name=F, bold=True)
YELLOW = PatternFill("solid", fgColor="FFFF00")
HDR = PatternFill("solid", fgColor="DCE6F1")
USD = '#,##0.0;(#,##0.0);"-"'
USD0 = '#,##0;(#,##0);"-"'
PCT = '0.0%;(0.0%);"-"'
MULT = '0.0"x"'


# --------------------------------------------------------------------------- data
def hist_data() -> dict:
    A = pd.read_csv(RES / "ITMG_financials_annual.csv", index_col=0) / 1000.0          # USD m
    fs = pd.read_csv(RES / "ITMG_fs_costs.csv", index_col=0); fs.index = pd.PeriodIndex(fs.index, freq="Q")
    vol = fs.groupby(fs.index.year).implied_sales_mt.sum()
    roy = fs.groupby(fs.index.year).royalty_q.sum() / 1000
    snap = json.loads((RES / "ITMG_market_snapshot.json").read_text(encoding="utf-8"))
    peers = pd.read_csv(RES / "coal_peers_snapshot.csv")
    m9 = fs[fs.index.year == 2026]
    return dict(A=A, vol=vol, roy=roy, snap=snap, peers=peers,
                vol9m26=float(m9.implied_sales_mt.sum()), roy9m26=float(m9.royalty_q.sum() / 1000))


# --------------------------------------------------------------------------- workbook
class Book:
    def __init__(self):
        self.wb = Workbook(); self.ref = {}

    def sheet(self, name):
        ws = self.wb.active if self.wb.active.title == "Sheet" else self.wb.create_sheet(name)
        ws.title = name
        return ws

    def put(self, ws, cell, v, fmt=None, key=None, note=None, inp=False, bold=False):
        c = ws[cell]; c.value = v
        if inp:
            c.font = BLUE
        elif isinstance(v, str) and v.startswith("="):
            c.font = GREEN if "!" in v else BLACK
        else:
            c.font = BOLD if bold else Font(name=F)
        if bold:
            c.font = Font(name=F, bold=True, color=c.font.color.rgb if c.font.color else "000000")
        if fmt:
            c.number_format = fmt
        if note:
            c.comment = Comment(note, "model")
        if key:
            self.ref[key] = f"'{ws.title}'!${cell[0:len(cell.rstrip('0123456789'))]}${cell[len(cell.rstrip('0123456789')):]}" if " " in ws.title else f"{ws.title}!${cell.rstrip('0123456789')}${cell[len(cell.rstrip('0123456789')):]}"
        return c


def build(H: dict):
    B = Book(); R = B.ref
    A, snap = H["A"], H["snap"]
    info = snap["itmg_info"]

    # ---------------- Cover
    ws = B.sheet("Cover")
    lines = ["PT Indo Tambangraya Megah Tbk (ITMG) - integrated model and valuation (USD m unless stated)",
             "Built by valuation/itmg_model.py on 2026-11-25. All forecast cells are live formulas driven by 'Inputs'.",
             "Legend: blue = hard-coded input; black = formula; green = link to another sheet; yellow fill = key assumption / scenario selector.",
             "Evidence classes: VALIDATED = frozen ITMG-C1 M2 (next-quarter ASP only); BENCHMARK = strongest benchmark of failed C2/C3 (volume, unit cost, royalty);",
             "ANALYST = all multi-year assumptions (Newcastle path, ASP ratio, cost-price relation, mine plans, licence extensions, capex, payout, discount rate) - NOT validated.",
             "Static tables on 'Scenarios' and 'Sensitivity' were computed by overriding inputs with the Python evaluator (re-run the script after changing inputs).",
             "Formulas were verified with valuation/xlsx_eval.py (no Excel/LibreOffice recalculation in the build environment); Excel recalculates on open.",
             "Sources: ITMG consolidated FS FY2018-9M26 and analyst decks (S-066), World Bank CMO (S-003), Yahoo/S&P consensus and prices (S-002/S-036), FRED DGS10 (S-074).",
             "Research only; not investment advice. ITMG-C1 is forecasting evidence, not proven trading alpha; ITMG-I1 remains CONDITIONAL."]
    for i, l in enumerate(lines):
        B.put(ws, f"A{i + 1}", l, bold=(i == 0))
    ws.column_dimensions["A"].width = 160

    # ---------------- Inputs
    ws = B.sheet("Inputs")
    B.put(ws, "A1", "Inputs and scenario levers", bold=True)
    B.put(ws, "A3", "Scenario selector (1 = Bear, 2 = Base, 3 = Bull)")
    c = B.put(ws, "B3", 2, inp=True, key="sel"); c.fill = YELLOW
    for col, h in zip("ABCDEFG", ["Scenario lever", "Live", "Bear", "Base", "Bull", "Unit", "Class / source"]):
        x = B.put(ws, f"{col}5", h, bold=True); x.fill = HDR
    scen = [
        ("newc27", "Newcastle FY2027", 100, 125, 145, "USD/t", "ANALYST: path from Jan-Oct 2026 avg USD 134/t (CMO) toward long run"),
        ("newc28", "Newcastle FY2028", 90, 110, 130, "USD/t", "ANALYST"),
        ("newclr", "Newcastle FY2029+ (long run, nominal)", 85, 105, 125, "USD/t", "ANALYST: base ~ median of 2016-2025 annual averages (USD 108/t, CMO); bear ~ 2016-2020 avg"),
        ("pesc", "Newcastle escalation per year from 2029 (nominal)", 0.0, 0.02, 0.025, "%", "ANALYST: base = flat real price at ~2% inflation; bear = flat nominal (real decline, energy transition)"),
        ("esc", "Cost escalation per year (opex, selling, G&A)", 0.025, 0.02, 0.02, "%", "ANALYST: base = flat real margins (same 2% as price); bear = real cost squeeze"),
        ("ratio", "ITMG ASP / Newcastle", 0.66, 0.69, 0.72, "x", "ANALYST: 2023-3Q26 quarterly median 0.685; 2018-3Q26 median 0.716 (first-reported ASP vs CMO)"),
        ("roy", "Effective royalty rate (on revenue)", 0.12, 0.115, 0.11, "%", "BENCHMARK-based: 9M26 11.1%, 2024-26 range 10.5-12.7% (FS royalty / coal revenue)"),
        ("iupk", "Extra royalty on IMM revenue after IUPK conversion (2028+)", 0.04, 0.03, 0.02, "pp", "ANALYST: PP 15/2022 progressive IUPK royalty (knowledge-only, not verified)"),
        ("immext", "IMM CCOW (expires Mar 2028) extended as IUPK? (1/0)", 0, 1, 1, "flag", "ANALYST: regulatory; decks give expiry only"),
        ("npr", "NPR production rate 2027+", 1.5, 2.5, 3.5, "Mt", "ANALYST: FY26e 0.4 Mt (3Q26 deck); ramp assumed from 2027 at half-rate"),
        ("gpk", "GPK production rate 2027+", 2.0, 2.5, 3.0, "Mt", "ANALYST: FY26e 2.0 Mt, earlier FY26 target 2.7 Mt (decks)"),
        ("traded", "Third-party (traded) coal sales", 2.5, 3.5, 4.5, "Mt", "ANALYST: FY25 sales 24.7 - production 21.2 = 3.5 Mt (4Q25 deck)"),
        ("uc27", "Unit cost ex-royalty FY2027", 59.0, 57.7, 55.0, "USD/t", "BENCHMARK: last-quarter unit cost (3Q26 57.7, C3 strongest benchmark; bear +2.3%, bull -4.7%), adjusted by b x (ASP2027 - 3Q26 ASP)"),
        ("costa", "Cost-price relation intercept shift (2028+)", 1.5, 0.0, -2.0, "USD/t", "ANALYST: shift to the 2019-3Q26 fit UC = a + b x ASP"),
    ]
    r = 6
    for k, lab, b_, m_, u_, unit, src in scen:
        B.put(ws, f"A{r}", lab)
        fmt = PCT if unit in ("%", "pp") else ("0.00" if unit == "x" else ("0" if unit == "flag" else USD))
        B.put(ws, f"B{r}", f"=INDEX(C{r}:E{r},1,$B$3)", fmt=fmt, key=k)
        for col, v in zip("CDE", (b_, m_, u_)):
            x = B.put(ws, f"{col}{r}", v, fmt=fmt, inp=True); x.fill = YELLOW
        B.put(ws, f"F{r}", unit); B.put(ws, f"G{r}", src)
        r += 1
    r += 1
    x = B.put(ws, f"A{r}", "Constants and calibration", bold=True); x.fill = HDR; r += 1
    m9 = A.loc["9M26"]
    da9 = 311.194 - 245.449          # deck EBITDA - operating income (3Q26 deck p23)
    consts = [
        ("price", "ITMG share price (IDR, 25 Nov 2026 close)", snap["itmg_last_close"]["close"], USD0, "Yahoo S-002"),
        ("shares", "Shares outstanding ex-treasury (m)", 1129.925 - 81.5, USD, "1,129.925m issued (FY25 FS) - 81.5m bought back by 4 Nov 2026 (3Q26 deck p5); assumes none resold"),
        ("fx", "USD/IDR (25 Nov 2026)", 18295.0, USD0, "Yahoo IDR=X close"),
        ("rf", "Risk-free (US 10y)", 0.0492, PCT, "FRED DGS10, 23 Nov 2026 (S-074)"),
        ("crp", "Indonesia country risk premium", 0.022, PCT, "ANALYST (Damodaran-style; not fetched)"),
        ("erp", "Mature-market equity risk premium", 0.05, PCT, "ANALYST"),
        ("beta", "Equity beta", 1.0, "0.00", "ANALYST (Yahoo beta -0.53 not meaningful); net-cash company so WACC = cost of equity"),
        ("tax", "Effective tax rate", 0.28, PCT, "FY23-9M26 effective 22-34%, mean 28% (FS)"),
        ("nci", "Non-controlling share of profit", 0.025, PCT, "FY25 1.9%, 9M26 2.7% (FS)"),
        ("payout", "Dividend payout ratio", 0.60, PCT, "FY25 final 60%, 2025 interim 55% (decks)"),
        ("finr", "Interest income on opening cash", 0.03, PCT, "9M26 finance income 25.8 on ~0.8bn cash (~4%); ANALYST lower"),
        ("fincost", "Finance costs per year", 6.0, USD, "9M26 5.3 (FS)"),
        ("nwc", "Net working capital % revenue", 0.07, PCT, "9M26 (AR+inventory-AP) 149 / TTM revenue 2,113 = 7.1%"),
        ("sell", "Selling expenses per tonne sold (2026 USD)", round(-m9.selling_exp / H["vol9m26"], 2), USD, "9M26 selling 134.8 / 18.7 Mt (FS)"),
        ("ga", "G&A per year (2026 USD m)", 56.5, USD, "9M26 42.4 annualised (FS)"),
        ("da", "D&A (ex stripping amortisation) per own tonne", round(da9 / 15.9, 2), USD, "9M26 EBITDA - op. income 65.7 / production 15.9 Mt (3Q26 deck)"),
        ("capexdev", "Capex FY2027-FY2030 per year", 85.0, USD, "ANALYST: FY24 budget 96.5, FY25 actual 76, 9M26 37 (decks)"),
        ("capexm", "Maintenance capex per own tonne (2031+)", 3.5, USD, "ANALYST"),
        ("closure", "Closure / rehabilitation outflow at end of production", 85.0, USD, "Mine rehab 79 + decommissioning ~5 provision (9M26/FY25 FS)"),
        ("ca", "Cost-price fit intercept a", 35.43, USD, "OLS 2019Q1-2026Q3 (n=31, R2 0.61): UC ex-royalty = 35.4 + 0.170 x ASP (descriptive)"),
        ("cb", "Cost-price fit slope b", 0.170, "0.000", "same fit"),
        ("newc26", "Newcastle 2026 Jan-Oct average", 134.0, USD, "World Bank CMO 'Coal, Australian' (S-003)"),
        # Q4 2026 bridge (VALIDATED / BENCHMARK)
        ("q4vol", "Q4 2026 sales volume", 6.8, USD, "BENCHMARK: seasonal (4Q25 6.8 Mt; C2 strongest). Guidance 27.2-27.6 Mt FY implies 8.5-8.9 Mt"),
        ("q4asp", "Q4 2026 ASP (frozen C1-M2, provisional)", 102.46, USD, "VALIDATED model: itmg_prospective_run.py dry run 25 Nov 2026, fallback mode, Oct-26 only; official run 10 Jan 2027"),
        ("q3asp", "3Q26 first-reported ASP", 94.8, USD, "3Q26 deck p19 (anchor for the FY2027 cost benchmark)"),
        ("q4uc", "Q4 2026 unit cost ex-royalty", 57.68, USD, "BENCHMARK: 3Q26 (C3 strongest = last quarter)"),
        ("q4roy", "Q4 2026 royalty rate", 0.111, PCT, "BENCHMARK: 3Q26 rate (I1 input)"),
        ("q4prod", "Q4 2026 own production", 5.6, USD, "3Q26 deck 4Q26 target"),
        ("q4capex", "Q4 2026 capex", 12.0, USD, "ANALYST (9M26 actual 37, FY25 76)"),
        ("q4bb", "Q4 2026 share buyback cash", 28.0, USD, "20.5m shares (81.5m total - 5.4% held at 30 Sep) x ~IDR 25,000 / 18,300"),
        ("q4fin", "Q4 2026 finance income", 7.8, USD, "3Q26 run-rate (deck p23)"),
    ]
    for k, lab, v, fmt, src in consts:
        B.put(ws, f"A{r}", lab); B.put(ws, f"B{r}", v, fmt=fmt, inp=True, key=k); B.put(ws, f"G{r}", src); r += 1
    B.put(ws, f"A{r}", "Cost of equity (= WACC, net cash)"); B.put(ws, f"B{r}", f"={R['rf']}+{R['crp']}+{R['beta']}*{R['erp']}", fmt=PCT, key="ke")
    B.put(ws, f"G{r}", "rf + CRP + beta x ERP"); r += 2
    # 9M26 actuals
    x = B.put(ws, f"A{r}", "9M26 actuals (USD m, FS S-066)", bold=True); x.fill = HDR; r += 1
    act = [("a_rev", "Revenue", m9.revenue), ("a_roy", "Royalty", H["roy9m26"]), ("a_cogs", "Cost of revenue (incl. royalty)", -m9.cost_of_revenue),
           ("a_sell", "Selling expenses", -m9.selling_exp), ("a_ga", "G&A", -m9.ga_exp), ("a_finc", "Finance costs", -m9.finance_costs),
           ("a_fini", "Finance income", m9.finance_income), ("a_oth", "Others, net (deck)", -12.294), ("a_tax", "Income tax", -m9.income_tax),
           ("a_ni", "Profit", m9.profit), ("a_nio", "Profit to owners", m9.profit_owners), ("a_da", "D&A ex stripping (deck)", da9),
           ("a_vol", "Sales volume (Mt, FS revenue / ASP)", H["vol9m26"]), ("a_cash", "Cash 30 Sep 2026", m9.cash),
           ("a_debt", "Bank loans + leases 30 Sep 2026", m9.st_bank_loans + m9.lt_loans_current + m9.lt_loans_noncurrent + m9.lease_current + m9.lease_noncurrent),
           ("a_nwc", "AR + inventory - AP 30 Sep 2026", m9.trade_receivables_3p + m9.trade_receivables_rp + m9.inventories - m9.trade_payables),
           ("a_mine", "PPE + deferred stripping + exploration 30 Sep 2026", m9.ppe + m9.deferred_stripping + m9.deferred_exploration),
           ("a_prov", "Mine rehabilitation provision 30 Sep 2026", m9.mine_rehab_provision),
           ("a_ta", "Total assets 30 Sep 2026", m9.total_assets), ("a_tl", "Total liabilities 30 Sep 2026", m9.total_liabilities),
           ("a_te", "Total equity 30 Sep 2026", m9.total_equity), ("a_ap", "Trade payables 30 Sep 2026", m9.trade_payables)]
    for k, lab, v in act:
        B.put(ws, f"A{r}", lab); B.put(ws, f"B{r}", round(float(v), 3), fmt=USD, inp=True, key=k); B.put(ws, f"G{r}", "ITMG 9M26 FS / 3Q26 deck"); r += 1
    ws.column_dimensions["A"].width = 58; ws.column_dimensions["G"].width = 110
    for col in "BCDEF":
        ws.column_dimensions[col].width = 12

    # ---------------- Mines
    ws = B.sheet("Mines")
    B.put(ws, "A1", "Mine-level production schedule (Mt) - reserves at 31 Dec 2025 (JORC, 3Q26 deck p24); ANALYST rates and licence assumptions", bold=True)
    hdr = ["Mine", "Reserves end-2025 (Mt)", "FY2026e prod (Mt)", "Rate 2027+ (Mt)", "Licence expiry (year)", "Fraction of expiry year", "Extended? (1/0)", "CV (kcal/kg GAR)", "Licence"]
    for i, h in enumerate(hdr):
        x = B.put(ws, f"{get_column_letter(1 + i)}3", h, bold=True); x.fill = HDR
    mines = [("IMM", "Indominco Mandiri", 31, 7.1, 7.0, 2028, 0.25, R["immext"], "5,600-6,200", "CCOW Gen I, exp. Mar 2028"),
             ("TCM", "Trubaindo Coal Mining", 71, 3.4, 3.4, 2035, 0.15, 1, "6,100-6,500", "CCOW Gen II, exp. Feb 2035"),
             ("BEK", "Bharinto Ekatama", 95, 8.0, 8.0, 2041, 0.45, 1, "6,100-6,500", "CCOW Gen III, exp. Jun 2041"),
             ("NPR", "Nusa Persada Resources", 77, 0.4, R["npr"], 2033, 0.4, 1, "5,500-6,100", "IUP, exp. May 2033"),
             ("GPK", "Graha Panca Karsa (70%)", 99, 2.0, R["gpk"], 2029, 0.7, 1, "3,900", "IUP, exp. Sep 2029"),
             ("TIS", "Tepian Indah Sukses", 7, 0.6, 0.6, 2029, 0.3, 1, "6,400", "IUP, exp. Apr 2029")]
    r = 4
    for code, name, res, p26, rate, exp, frac, ext, cv, lic in mines:
        B.put(ws, f"A{r}", f"{code} {name}")
        B.put(ws, f"B{r}", res, fmt=USD, inp=True, key=f"res_{code}")
        B.put(ws, f"C{r}", p26, fmt=USD, inp=True, key=f"p26_{code}")
        B.put(ws, f"D{r}", rate if isinstance(rate, (int, float)) else f"={rate}", fmt=USD, inp=isinstance(rate, (int, float)), key=f"rate_{code}")
        B.put(ws, f"E{r}", exp, fmt="0", inp=True, key=f"exp_{code}")
        B.put(ws, f"F{r}", frac, fmt="0.00", inp=True, key=f"frac_{code}")
        B.put(ws, f"G{r}", ext if isinstance(ext, int) else f"={ext}", fmt="0", inp=isinstance(ext, int), key=f"ext_{code}")
        B.put(ws, f"H{r}", cv); B.put(ws, f"I{r}", lic)
        r += 1
    B.put(ws, f"A{r}", "Note: licence extensions for TCM, BEK, NPR, GPK, TIS are ASSUMED in all scenarios (IUP/IUPK renewal); only IMM is flexed. JBG (2 Mt, inactive) and non-coal assets excluded.")
    r += 2
    yr_row = r
    B.put(ws, f"A{r}", "Year", bold=True)
    for y in YEARS:
        B.put(ws, f"{COL[y]}{r}", y, fmt="0", bold=True)
    r += 1
    prod_rows = {}
    for code, *_ in mines:
        pr, rr = r, r + 1
        B.put(ws, f"A{pr}", f"{code} production (Mt)"); B.put(ws, f"A{rr}", f"{code} remaining reserves (Mt)")
        for y in YEARS:
            c, p = COL[y], COL.get(y - 1)
            if y == 2026:
                B.put(ws, f"{c}{pr}", f"={R['p26_' + code]}", fmt=USD)
                B.put(ws, f"{c}{rr}", f"={R['res_' + code]}-{c}{pr}", fmt=USD)
            else:
                e = f"IF({R['ext_' + code]}=1,2100,{R['exp_' + code]})"
                B.put(ws, f"{c}{pr}", f"=MAX(0,MIN({R['rate_' + code]},{p}{rr}))*IF({c}${yr_row}<{e},1,IF({c}${yr_row}={e},{R['frac_' + code]},0))*Model!{c}@FLAG@", fmt=USD)
                B.put(ws, f"{c}{rr}", f"={p}{rr}-{c}{pr}", fmt=USD)
        prod_rows[code] = pr
        r += 2
    B.put(ws, f"A{r}", "Total own production (Mt)", bold=True)
    for y in YEARS:
        c = COL[y]
        B.put(ws, f"{c}{r}", "=" + "+".join(f"{c}{prod_rows[k]}" for k in prod_rows), fmt=USD, key=f"own_{y}")
    tot_row = r
    r += 1
    B.put(ws, f"A{r}", "Remaining reserves, all mines (Mt)")
    for y in YEARS:
        c = COL[y]
        B.put(ws, f"{c}{r}", "=" + "+".join(f"{c}{prod_rows[k] + 1}" for k in prod_rows), fmt=USD, key=f"rem_{y}")
    for y in YEARS:
        R[f"immprod_{y}"] = f"Mines!${COL[y]}${prod_rows['IMM']}"
    ws.column_dimensions["A"].width = 34
    for i in range(2, 30):
        ws.column_dimensions[get_column_letter(i)].width = 11

    # ---------------- Model
    ws = B.sheet("Model")
    B.put(ws, "A1", "Integrated model (USD m; FY2026E = 9M26 actual + Q4 bridge; FY2026 cash-flow and balance-sheet columns cover Q4 2026 only)", bold=True)
    B.put(ws, "A2", "Valuation horizon ends 2050 (no terminal value; reserves left at 2050 are given zero value).")
    row = {}
    lines = []

    def L(key, label, fmt, f26, fgen):
        lines.append((key, label, fmt, f26, fgen))

    I = R  # alias
    L("year", "Fiscal year", "0", None, None)
    L("hdr_ops", "OPERATIONS", None, None, None)
    L("own", "Own production (Mt)", USD, lambda c, p, y: f"=Mines!{c}{tot_row}", lambda c, p, y: f"=Mines!{c}{tot_row}")
    L("traded", "Third-party coal sold (Mt)", USD, lambda c, p, y: f"={c}{{sales}}-{c}{{own}}", lambda c, p, y: f"=IF({c}{{own}}>0,{I['traded']},0)")
    L("sales", "Sales volume (Mt)", USD, lambda c, p, y: f"={I['a_vol']}+{I['q4vol']}", lambda c, p, y: f"={c}{{own}}+{c}{{traded}}")
    L("newc", "Newcastle (USD/t)", USD, lambda c, p, y: f"={I['newc26']}",
      lambda c, p, y: f"={I['newc27']}" if y == 2027 else (f"={I['newc28']}" if y == 2028 else f"={I['newclr']}*(1+{I['pesc']})^({c}{{year}}-2028)"))
    L("asp", "Average selling price (USD/t)", USD, lambda c, p, y: f"={c}{{rev}}/{c}{{sales}}", lambda c, p, y: f"={I['ratio']}*{c}{{newc}}")
    L("uc", "Unit cost ex-royalty (USD/t)", USD, lambda c, p, y: f"={c}{{cogs}}/{c}{{sales}}",
      lambda c, p, y: f"={I['uc27']}+{I['cb']}*({c}{{asp}}-{I['q3asp']})" if y == 2027 else f"=({I['ca']}+{I['costa']}+{I['cb']}*{c}{{asp}})*(1+{I['esc']})^({c}{{year}}-2026)")
    L("flag", "Operating flag: 1 if prior-year volume x cash margin/t [ASP net of royalty - (unit cost - D&A) - selling] covers G&A + capex; else permanent closure", "0", lambda c, p, y: "=1",
      lambda c, p, y: f"=IF({p}{{own}}>0,IF(({c}{{asp}}*(1-{I['roy']})-({c}{{uc}}-{I['da']})-{I['sell']}*(1+{I['esc']})^({c}{{year}}-2026))*{p}{{own}}-{I['ga']}*(1+{I['esc']})^({c}{{year}}-2026)-IF({c}{{year}}<=2030,{I['capexdev']},{I['capexm']}*{p}{{own}})>0,1,0),0)")
    L("hdr_is", "INCOME STATEMENT", None, None, None)
    L("rev", "Revenue", USD, lambda c, p, y: f"={I['a_rev']}+{I['q4vol']}*{I['q4asp']}", lambda c, p, y: f"={c}{{sales}}*{c}{{asp}}")
    L("roy", "Royalty", USD, lambda c, p, y: f"={I['a_roy']}+{I['q4vol']}*{I['q4asp']}*{I['q4roy']}",
      lambda c, p, y: f"={c}{{rev}}*{I['roy']}+{I['iupk']}*{c}{{asp}}*{I['immprod_' + str(y)]}*IF({c}{{year}}>=2028,1,0)")
    L("cogs", "Cost of revenue ex-royalty", USD, lambda c, p, y: f"={I['a_cogs']}-{I['a_roy']}+{I['q4vol']}*{I['q4uc']}", lambda c, p, y: f"={c}{{sales}}*{c}{{uc}}")
    L("gp", "Gross profit", USD, lambda c, p, y: f"={c}{{rev}}-{c}{{roy}}-{c}{{cogs}}", lambda c, p, y: f"={c}{{rev}}-{c}{{roy}}-{c}{{cogs}}")
    L("selling", "Selling expenses", USD, lambda c, p, y: f"={I['a_sell']}+{I['q4vol']}*{I['sell']}",
      lambda c, p, y: f"={c}{{sales}}*{I['sell']}*(1+{I['esc']})^({c}{{year}}-2026)")
    L("ga", "General and administrative", USD, lambda c, p, y: f"={I['a_ga']}+{I['ga']}/4", lambda c, p, y: f"={I['ga']}*(1+{I['esc']})^({c}{{year}}-2026)*IF({c}{{own}}>0,1,0)")
    L("ebit", "Operating income (EBIT)", USD, lambda c, p, y: f"={c}{{gp}}-{c}{{selling}}-{c}{{ga}}", lambda c, p, y: f"={c}{{gp}}-{c}{{selling}}-{c}{{ga}}")
    L("da", "D&A ex stripping amortisation", USD, lambda c, p, y: f"={I['a_da']}+{I['q4prod']}*{I['da']}", lambda c, p, y: f"={c}{{own}}*{I['da']}")
    L("ebitda", "EBITDA (company definition)", USD, lambda c, p, y: f"={c}{{ebit}}+{c}{{da}}", lambda c, p, y: f"={c}{{ebit}}+{c}{{da}}")
    L("fini", "Finance income", USD, lambda c, p, y: f"={I['a_fini']}+{I['q4fin']}", lambda c, p, y: f"={I['finr']}*{p}{{cash}}")
    L("finc", "Finance costs", USD, lambda c, p, y: f"={I['a_finc']}+{I['fincost']}/4", lambda c, p, y: f"={I['fincost']}*IF({c}{{own}}>0,1,0)")
    L("oth", "Others, net", USD, lambda c, p, y: f"={I['a_oth']}", lambda c, p, y: "=0")
    L("pbt", "Profit before tax", USD, lambda c, p, y: f"={c}{{ebit}}+{c}{{fini}}-{c}{{finc}}+{c}{{oth}}", lambda c, p, y: f"={c}{{ebit}}+{c}{{fini}}-{c}{{finc}}+{c}{{oth}}")
    L("tax", "Income tax", USD, lambda c, p, y: f"={I['a_tax']}+MAX(0,{c}{{pbt}}-({I['a_ni']}+{I['a_tax']}))*{I['tax']}", lambda c, p, y: f"=MAX(0,{c}{{pbt}})*{I['tax']}")
    L("ni", "Profit for the year", USD, lambda c, p, y: f"={c}{{pbt}}-{c}{{tax}}", lambda c, p, y: f"={c}{{pbt}}-{c}{{tax}}")
    L("nci", "Non-controlling interests", USD, lambda c, p, y: f"=({I['a_ni']}-{I['a_nio']})+({c}{{ni}}-{I['a_ni']})*{I['nci']}", lambda c, p, y: f"={c}{{ni}}*{I['nci']}")
    L("nio", "Profit to owners", USD, lambda c, p, y: f"={c}{{ni}}-{c}{{nci}}", lambda c, p, y: f"={c}{{ni}}-{c}{{nci}}")
    L("eps", "EPS (USD)", "0.000", lambda c, p, y: f"={c}{{nio}}/{I['shares']}", lambda c, p, y: f"={c}{{nio}}/{I['shares']}")
    L("epsidr", "EPS (IDR)", USD0, lambda c, p, y: f"={c}{{eps}}*{I['fx']}", lambda c, p, y: f"={c}{{eps}}*{I['fx']}")
    L("dps", "DPS declared on the year (IDR)", USD0, lambda c, p, y: f"=MAX(0,{c}{{epsidr}}*{I['payout']})", lambda c, p, y: f"=MAX(0,{c}{{epsidr}}*{I['payout']})")
    L("hdr_cf", "CASH FLOW (FY2026 column = Q4 2026 only)", None, None, None)
    L("nwc", "Net working capital (AR + inventory - AP)", USD, lambda c, p, y: f"={c}{{rev}}*{I['nwc']}", lambda c, p, y: f"={c}{{rev}}*{I['nwc']}")
    L("dnwc", "Increase in net working capital", USD, lambda c, p, y: f"={c}{{nwc}}-{I['a_nwc']}", lambda c, p, y: f"={c}{{nwc}}-{p}{{nwc}}")
    L("cfo", "Operating cash flow", USD, lambda c, p, y: f"=({c}{{ni}}-{I['a_ni']})+{I['q4prod']}*{I['da']}-{c}{{dnwc}}", lambda c, p, y: f"={c}{{ni}}+{c}{{da}}-{c}{{dnwc}}")
    L("capex", "Capital expenditure", USD, lambda c, p, y: f"={I['q4capex']}", lambda c, p, y: f"=IF({c}{{own}}>0,IF({c}{{year}}<=2030,{I['capexdev']},{I['capexm']}*{c}{{own}}),0)")
    L("closure", "Closure and rehabilitation spend", USD, lambda c, p, y: "=0", lambda c, p, y: f"=IF(AND({c}{{own}}<=0,{p}{{own}}>0),{I['closure']},0)")
    L("fcfe", "Free cash flow to equity", USD, lambda c, p, y: f"={c}{{cfo}}-{c}{{capex}}-{c}{{closure}}", lambda c, p, y: f"={c}{{cfo}}-{c}{{capex}}-{c}{{closure}}")
    L("div", "Dividends paid", USD, lambda c, p, y: "=0", lambda c, p, y: f"=MAX(0,{c}{{nio}}*{I['payout']})")
    L("bb", "Share buybacks", USD, lambda c, p, y: f"={I['q4bb']}", lambda c, p, y: "=0")
    L("hdr_bs", "BALANCE SHEET (net of trade payables; debt held flat)", None, None, None)
    L("cash", "Cash and equivalents", USD, lambda c, p, y: f"={I['a_cash']}+{c}{{fcfe}}-{c}{{div}}-{c}{{bb}}", lambda c, p, y: f"={p}{{cash}}+{c}{{fcfe}}-{c}{{div}}-{c}{{bb}}")
    L("bs_nwc", "Net working capital", USD, lambda c, p, y: f"={c}{{nwc}}", lambda c, p, y: f"={c}{{nwc}}")
    L("mine", "Mining assets (PPE + stripping + exploration)", USD, lambda c, p, y: f"={I['a_mine']}+{c}{{capex}}-{I['q4prod']}*{I['da']}", lambda c, p, y: f"={p}{{mine}}+{c}{{capex}}-{c}{{da}}")
    L("otha", "Other assets (held constant)", USD, lambda c, p, y: f"={I['a_ta']}-{I['a_cash']}-({I['a_nwc']}+{I['a_ap']})-{I['a_mine']}", lambda c, p, y: f"={p}{{otha}}")
    L("ta", "Total assets (net of trade payables)", USD, lambda c, p, y: f"={c}{{cash}}+{c}{{bs_nwc}}+{c}{{mine}}+{c}{{otha}}", lambda c, p, y: f"={c}{{cash}}+{c}{{bs_nwc}}+{c}{{mine}}+{c}{{otha}}")
    L("debt", "Bank loans and leases", USD, lambda c, p, y: f"={I['a_debt']}", lambda c, p, y: f"={p}{{debt}}")
    L("prov", "Mine rehabilitation provision", USD, lambda c, p, y: f"={I['a_prov']}", lambda c, p, y: f"={p}{{prov}}-{c}{{closure}}")
    L("othl", "Other liabilities (held constant)", USD, lambda c, p, y: f"={I['a_tl']}-{I['a_ap']}-{I['a_debt']}-{I['a_prov']}", lambda c, p, y: f"={p}{{othl}}")
    L("tl", "Total liabilities (ex trade payables)", USD, lambda c, p, y: f"={c}{{debt}}+{c}{{prov}}+{c}{{othl}}", lambda c, p, y: f"={c}{{debt}}+{c}{{prov}}+{c}{{othl}}")
    L("eq", "Total equity", USD, lambda c, p, y: f"={I['a_te']}+({c}{{ni}}-{I['a_ni']})-{c}{{div}}-{c}{{bb}}", lambda c, p, y: f"={p}{{eq}}+{c}{{ni}}-{c}{{div}}-{c}{{bb}}")
    L("chk", "Balance check (assets - liabilities - equity)", USD, lambda c, p, y: f"={c}{{ta}}-{c}{{tl}}-{c}{{eq}}", lambda c, p, y: f"={c}{{ta}}-{c}{{tl}}-{c}{{eq}}")
    L("netcash", "Net cash (cash - loans - leases)", USD, lambda c, p, y: f"={c}{{cash}}-{c}{{debt}}", lambda c, p, y: f"={c}{{cash}}-{c}{{debt}}")
    L("hdr_dcf", "VALUATION LINES", None, None, None)
    L("fcff", "Unlevered FCF = EBIT x (1-t) + D&A - dNWC - capex - closure", USD, lambda c, p, y: "=0",
      lambda c, p, y: f"={c}{{ebit}}*(1-{I['tax']})+{c}{{da}}-{c}{{dnwc}}-{c}{{capex}}-{c}{{closure}}")
    L("df", "Discount factor (mid-year, from 31 Dec 2026)", "0.000", lambda c, p, y: "=0", lambda c, p, y: f"=1/(1+{I['ke']})^({c}{{year}}-2026-0.5)")
    L("pv", "PV of unlevered FCF", USD, lambda c, p, y: "=0", lambda c, p, y: f"={c}{{fcff}}*{c}{{df}}")
    L("pvdiv", "PV of dividends", USD, lambda c, p, y: "=0", lambda c, p, y: f"={c}{{div}}*{c}{{df}}")
    r = 4
    for key, *_ in lines:
        row[key] = r; r += 1
    for key, label, fmt, f26, fgen in lines:
        rr = row[key]
        x = B.put(ws, f"A{rr}", label, bold=key.startswith("hdr") or key in ("gp", "ebit", "nio", "fcfe", "chk"))
        if key.startswith("hdr"):
            x.fill = HDR; continue
        for y in YEARS:
            c, p = COL[y], COL.get(y - 1)
            if key == "year":
                B.put(ws, f"{c}{rr}", y, fmt="0", bold=True); continue
            f = (f26 if y == 2026 else fgen)(c, p, y)
            f = f.format(**{k: v for k, v in row.items()})
            B.put(ws, f"{c}{rr}", f, fmt=fmt, key=f"{key}_{y}")
    ws.column_dimensions["A"].width = 58
    for i in range(3, 30):
        ws.column_dimensions[get_column_letter(i)].width = 10
    ws.freeze_panes = "C5"
    for rowc in B.wb["Mines"].iter_rows():
        for cc in rowc:
            if isinstance(cc.value, str) and "@FLAG@" in cc.value:
                cc.value = cc.value.replace("@FLAG@", str(row["flag"]))

    # ---------------- Historical
    ws = B.sheet("Historical")
    B.put(ws, "A1", "Historical financial statements (USD m; parsed from ITMG consolidated FS, identities checked: ITMG_financials_checks.csv)", bold=True)
    per = ["FY2018", "FY2019", "FY2020", "FY2021", "FY2022", "FY2023", "FY2024", "FY2025", "9M25", "9M26"]
    for j, pname in enumerate(per):
        B.put(ws, f"{get_column_letter(2 + j)}3", pname, bold=True)
    items = [("revenue", "Revenue"), ("cost_of_revenue", "Cost of revenue"), ("gross_profit", "Gross profit"), ("selling_exp", "Selling expenses"),
             ("ga_exp", "G&A"), ("finance_income", "Finance income"), ("finance_costs", "Finance costs"), ("pbt", "Profit before tax"),
             ("income_tax", "Income tax"), ("profit", "Profit"), ("profit_owners", "Profit to owners"),
             ("cash", "Cash"), ("trade_receivables_3p", "Trade receivables (3rd party)"), ("inventories", "Inventories"), ("ppe", "PPE"),
             ("deferred_stripping", "Deferred stripping"), ("total_assets", "Total assets"), ("trade_payables", "Trade payables"),
             ("total_liabilities", "Total liabilities"), ("total_equity", "Total equity"),
             ("cfo", "Operating cash flow"), ("capex_ppe", "Purchase of PPE"), ("capex_exploration", "Exploration/development additions"),
             ("dividends_paid", "Dividends paid"), ("lease_payments", "Lease payments")]
    for i, (k, lab) in enumerate(items):
        rr = 4 + i
        B.put(ws, f"A{rr}", lab)
        for j, pname in enumerate(per):
            v = A.loc[pname, k] if k in A.columns else np.nan
            B.put(ws, f"{get_column_letter(2 + j)}{rr}", None if pd.isna(v) else round(float(v), 1), fmt=USD, inp=True)
    rr = 4 + len(items) + 1
    B.put(ws, f"A{rr}", "Sales volume (Mt; FS coal revenue / first-reported ASP)")
    for j, pname in enumerate(per[:8]):
        y = int(pname[2:])
        B.put(ws, f"{get_column_letter(2 + j)}{rr}", round(float(H["vol"].get(y, np.nan)), 2) if y >= 2019 else None, fmt=USD, inp=True)
    B.put(ws, f"A{rr + 1}", "Gross margin")
    for j in range(len(per)):
        cl = get_column_letter(2 + j)
        B.put(ws, f"{cl}{rr + 1}", f"={cl}6/{cl}4", fmt=PCT)
    B.put(ws, f"A{rr + 2}", "Net margin")
    for j in range(len(per)):
        cl = get_column_letter(2 + j)
        B.put(ws, f"{cl}{rr + 2}", f"={cl}13/{cl}4", fmt=PCT)
    B.put(ws, f"A{rr + 3}", "Dividend payout (paid / prior-year profit to owners)")
    for j in range(1, 8):
        cl, pl = get_column_letter(2 + j), get_column_letter(1 + j)
        B.put(ws, f"{cl}{rr + 3}", f"=-{cl}27/{pl}14", fmt=PCT)
    B.put(ws, f"A{rr + 5}", "FY2018 sales volume is not computed (incomplete quarterly FS set for 2018 in the volume series). 9M columns are year-to-date.")
    ws.column_dimensions["A"].width = 52
    R["hist_row_profit_owners"] = 14

    # ---------------- Valuation
    ws = B.sheet("Valuation")
    B.put(ws, "A1", "Valuation (live; scenario per Inputs!B3)", bold=True)
    y0, y1 = COL[2027], COL[2050]
    v = [
        ("ev", "PV of unlevered FCF 2027-2050 (USD m)", f"=SUM(Model!{y0}{row['pv']}:{y1}{row['pv']})", USD),
        ("nc26", "Net cash at 31 Dec 2026E (USD m)", f"=Model!{COL[2026]}{row['netcash']}", USD),
        ("eqv", "Equity value - mine-life DCF (USD m)", "={ev}+{nc26}", USD),
        ("fvu", "Fair value per share (USD)", f"={{eqv}}/{R['shares']}", "0.000"),
        ("fv", "Fair value per share - DCF (IDR)", f"={{fvu}}*{R['fx']}", USD0),
        ("ddm_pv", "PV of dividends 2027-2050 (USD m)", f"=SUM(Model!{y0}{row['pvdiv']}:{y1}{row['pvdiv']})", USD),
        ("ddm_res", "PV of residual net cash returned at end-2050 (USD m)",
         f"=(Model!{y1}{row['netcash']}-Model!{y1}{row['prov']})/(1+{R['ke']})^24", USD),
        ("ddm", "Fair value per share - finite DDM (IDR)", f"=({{ddm_pv}}+{{ddm_res}})/{R['shares']}*{R['fx']}", USD0),
        ("price", "Share price (IDR)", f"={R['price']}", USD0),
        ("mcap", "Market capitalisation (USD m)", f"={R['price']}*{R['shares']}/{R['fx']}", USD),
        ("evmkt", "Market EV = market cap - net cash end-2026E (USD m)", "={mcap}-{nc26}", USD),
        ("up", "Upside to DCF fair value", "={fv}/{price}-1", PCT),
        ("tr12", "Expected 12m total return if price converges (FV x (1+ke) / price - 1)", f"={{fv}}*(1+{R['ke']})/{{price}}-1", PCT),
        ("pe27", "P/E FY2027E at market (x; 0 if EPS <= 0)", f"=IF(Model!{COL[2027]}{row['epsidr']}>0,{{price}}/MAX(Model!{COL[2027]}{row['epsidr']},0.000001),0)", MULT),
        ("eveb27", "EV/EBITDA FY2027E at market (x; 0 if EBITDA <= 0)", f"=IF(Model!{COL[2027]}{row['ebitda']}>0,{{evmkt}}/MAX(Model!{COL[2027]}{row['ebitda']},0.000001),0)", MULT),
        ("dy27", "Dividend yield FY2027E (declared basis)", f"=Model!{COL[2027]}{row['dps']}/{{price}}", PCT),
        ("life", "Reserve-life proxy: 2027-2050 production / FY2027 production (years)", f"=SUM(Model!{y0}{row['own']}:{y1}{row['own']})/MAX(Model!{COL[2027]}{row['own']},0.000001)", "0.0"),
        ("rem2050", "Reserves left unvalued at end-2050 (Mt)", f"=Mines!{y1}{tot_row + 1}", USD),
    ]
    r = 3
    vrow = {}
    for k, lab, f, fmt in v:
        vrow[k] = r; r += 1
    for k, lab, f, fmt in v:
        B.put(ws, f"A{vrow[k]}", lab)
        B.put(ws, f"B{vrow[k]}", f.format(**{kk: f"B{vv}" for kk, vv in vrow.items()}), fmt=fmt, key=f"v_{k}")
    ws.column_dimensions["A"].width = 70; ws.column_dimensions["B"].width = 16
    r += 1
    # relative valuation
    B.put(ws, f"A{r}", "Relative valuation (peer medians from 'Peers'; applied to FY2027E)", bold=True); r += 1
    rel = r
    return B, row, vrow, tot_row, rel


def add_peers(B: Book, H: dict, row: dict, vrow: dict, rel: int):
    R = B.ref
    P = H["peers"]
    ws = B.sheet("Peers")
    B.put(ws, "A1", "Listed Indonesian coal peers - Yahoo snapshot 25 Nov 2026 (S-002/S-036). USD reporters: Yahoo divides IDR EV / price by USD EBITDA / book, so those ratios are divided by USD/IDR here.", bold=True)
    hdr = ["Ticker", "Name", "Price (IDR)", "Mkt cap (IDR bn)", "Fin. currency", "Trailing P/E (x)", "Dividend yield", "EV/EBITDA raw", "EV/EBITDA corrected (x)", "P/B raw", "P/B corrected (x)"]
    for i, h in enumerate(hdr):
        x = B.put(ws, f"{get_column_letter(1 + i)}3", h, bold=True); x.fill = HDR
    r = 4
    first = r
    for _, p in P.iterrows():
        B.put(ws, f"A{r}", p.ticker); B.put(ws, f"B{r}", p["name"])
        B.put(ws, f"C{r}", p.currentPrice, fmt=USD0, inp=True); B.put(ws, f"D{r}", (p.marketCap or 0) / 1e9, fmt=USD0, inp=True)
        B.put(ws, f"E{r}", p.financialCurrency, inp=True)
        B.put(ws, f"F{r}", None if pd.isna(p.trailingPE) else float(p.trailingPE), fmt=MULT, inp=True)
        B.put(ws, f"G{r}", None if pd.isna(p.dividendYield) else float(p.dividendYield) / 100, fmt=PCT, inp=True)
        B.put(ws, f"H{r}", None if pd.isna(p.enterpriseToEbitda) else float(p.enterpriseToEbitda), fmt="0.00", inp=True)
        B.put(ws, f"I{r}", f'=IF(E{r}="USD",H{r}/{R["fx"]},H{r})', fmt=MULT)
        B.put(ws, f"J{r}", None if pd.isna(p.priceToBook) else float(p.priceToBook), fmt="0.00", inp=True)
        B.put(ws, f"K{r}", f'=IF(E{r}="USD",J{r}/{R["fx"]},J{r})', fmt=MULT)
        r += 1
    last = r - 1
    ws.column_dimensions["B"].width = 36
    # medians excluding ITMG (row 'first' is ITMG) - computed in Python (MEDIAN not in evaluator), written as values with note
    peers = P[P.ticker != "ITMG"].copy()
    fx = 18295.0
    peers["eveb"] = np.where(peers.financialCurrency == "USD", peers.enterpriseToEbitda / fx, peers.enterpriseToEbitda)
    meds = {"pe": float(peers.trailingPE.median()), "eveb": float(peers.eveb.median()), "dy": float(peers.dividendYield.median() / 100)}
    B.put(ws, f"A{r + 1}", "Peer median ex-ITMG: trailing P/E"); B.put(ws, f"F{r + 1}", meds["pe"], fmt=MULT, inp=True, key="med_pe")
    B.put(ws, f"A{r + 2}", "Peer median ex-ITMG: EV/EBITDA (corrected)"); B.put(ws, f"I{r + 2}", meds["eveb"], fmt=MULT, inp=True, key="med_eveb")
    B.put(ws, f"A{r + 3}", "Peer median ex-ITMG: dividend yield"); B.put(ws, f"G{r + 3}", meds["dy"], fmt=PCT, inp=True, key="med_dy")
    B.put(ws, f"A{r + 4}", "Medians computed by the build script from the rows above (MEDIAN avoided for evaluator compatibility). Trailing P/E mixes fiscal periods; vendor data, unaudited.")
    # relative valuation rows on Valuation sheet
    wv = B.wb["Valuation"]
    c27 = COL[2027]
    items = [("rel_pe", "Implied value: peer P/E x FY2027E EPS (IDR)", f"={R['med_pe']}*Model!{c27}{row['epsidr']}"),
             ("rel_ev", "Implied value: peer EV/EBITDA x FY2027E EBITDA + net cash (IDR)",
              f"=({R['med_eveb']}*Model!{c27}{row['ebitda']}+B{vrow['nc26']})/{R['shares']}*{R['fx']}"),
             ("rel_dy", "Implied value: FY2027E DPS / peer dividend yield (IDR)", f"=Model!{c27}{row['dps']}/{R['med_dy']}")]
    for i, (k, lab, f) in enumerate(items):
        B.put(wv, f"A{rel + i}", lab); B.put(wv, f"B{rel + i}", f, fmt=USD0, key=k)
    return meds


# --------------------------------------------------------------------------- evaluation helpers
def cellref(full: str):
    s, c = full.split("!")
    return s.strip("'"), c.replace("$", "")


def val(E, B, key):
    return E.get(*cellref(B.ref[key]))


def setv(E, B, key, v):
    E.set(*cellref(B.ref[key]), v)


def scenario_inputs(B, E, n):
    setv(E, B, "sel", n)


def bisect(fn, lo, hi, target, it=60):
    flo = fn(lo) - target
    for _ in range(it):
        mid = (lo + hi) / 2; fm = fn(mid) - target
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2


def main() -> dict:
    H = hist_data()
    B, row, vrow, tot_row, rel = build(H)
    meds = add_peers(B, H, row, vrow, rel)
    E = Evaluator(B.wb)
    keys_years = [2026, 2027, 2028, 2029, 2030]
    lines = ["sales", "own", "newc", "asp", "uc", "rev", "roy", "gp", "selling", "ga", "ebit", "ebitda", "pbt", "tax", "ni", "nio", "eps", "epsidr", "dps",
             "cfo", "capex", "fcfe", "div", "cash", "debt", "netcash", "eq", "ta", "tl", "chk", "fcff"]
    res = {"scenarios": {}}
    names = {1: "Bear", 2: "Base", 3: "Bull"}
    for n in (1, 2, 3):
        E.clear(); scenario_inputs(B, E, n)
        proj = {y: {k: float(val(E, B, f"{k}_{y}")) for k in lines} for y in keys_years}
        maxchk = max(abs(float(val(E, B, f"chk_{y}"))) for y in YEARS)
        vals = {k: float(val(E, B, f"v_{k}")) for k in vrow}
        vals.update({k: float(val(E, B, k)) for k in ("rel_pe", "rel_ev", "rel_dy")})
        res["scenarios"][names[n]] = {"projection": proj, "valuation": vals, "max_balance_check": maxchk}
    # base-case analytics
    E.clear(); scenario_inputs(B, E, 2)
    price = float(val(E, B, "price"))
    ref_lr = B.ref["newclr"]; ref_27 = B.ref["newc27"]; ref_ke = B.ref["ke"]

    def fv_at(key, x):
        E.cache.clear(); setv(E, B, key, x); return float(val(E, B, "v_fv"))
    # reverse DCF 1: flat long-run Newcastle (2029+) consistent with price (2027/28 base)
    rev_lr = bisect(lambda x: fv_at("newclr", x), 40, 250, price)
    E.clear(); scenario_inputs(B, E, 2)
    # reverse DCF 2: one flat Newcastle from 2027 onward
    def fv_flat(x):
        E.cache.clear(); setv(E, B, "newc27", x); setv(E, B, "newc28", x); setv(E, B, "newclr", x); return float(val(E, B, "v_fv"))
    rev_flat = bisect(fv_flat, 40, 250, price)
    E.clear(); scenario_inputs(B, E, 2)
    # consensus-implied Newcastle FY2027 (EPS match)
    cons = {c["fy"]: c for c in H["snap"]["consensus"] if c["ticker"] == "ITMG"}
    eps27 = float(cons["FY27"]["eps_avg"])
    def eps_at(x):
        E.cache.clear(); setv(E, B, "newc27", x); return float(val(E, B, "eps_2027"))
    imp27 = bisect(eps_at, 40, 300, eps27)
    E.clear(); scenario_inputs(B, E, 2)
    # sensitivities: long-run Newcastle x cost of equity
    grid = {}
    for lr in (85, 95, 105, 115, 125):
        for ke in (0.10, 0.11, 0.12, 0.13, 0.14):
            E.clear(); scenario_inputs(B, E, 2); setv(E, B, "newclr", lr); setv(E, B, "ke", ke)
            grid[f"{lr}|{ke}"] = float(val(E, B, "v_fv"))
    grid2 = {}
    for ratio in (0.63, 0.66, 0.69, 0.72, 0.75):
        for ext in (0, 1):
            E.clear(); scenario_inputs(B, E, 2); setv(E, B, "ratio", ratio); setv(E, B, "immext", ext)
            grid2[f"{ratio}|{ext}"] = float(val(E, B, "v_fv"))
    tor = {}
    for k, lo, hi in [("newclr", 95, 115), ("ratio", 0.66, 0.72), ("costa", 3.0, -3.0), ("roy", 0.125, 0.105), ("immext", 0, 1),
                      ("npr", 1.5, 3.5), ("traded", 2.5, 4.5), ("ke", 0.13, 0.11), ("capexdev", 105.0, 65.0), ("payout", 0.5, 0.7)]:
        out = []
        for x in (lo, hi):
            E.clear(); scenario_inputs(B, E, 2); setv(E, B, k, x); out.append(float(val(E, B, "v_fv")))
        tor[k] = {"low_input": lo, "high_input": hi, "fv_low": out[0], "fv_high": out[1]}
    E.clear(); scenario_inputs(B, E, 2)
    res.update(price_idr=price, reverse_dcf_longrun_newc=rev_lr, reverse_dcf_flat_newc_from_2027=rev_flat,
               consensus=cons, consensus_implied_newc_2027=imp27, peer_medians=meds,
               sensitivity_lr_ke=grid, sensitivity_ratio_immext=grid2, tornado=tor,
               shares_m=float(val(E, B, "shares")), fx=float(val(E, B, "fx")), ke=float(val(E, B, "ke")))
    # write static result sheets
    ws = B.sheet("Scenarios")
    B.put(ws, "A1", "Scenario results (static; computed by valuation/itmg_model.py via the formula evaluator)", bold=True)
    hdr = ["Metric", "Bear", "Base", "Bull"]
    for i, h in enumerate(hdr):
        x = B.put(ws, f"{get_column_letter(1 + i)}3", h, bold=True); x.fill = HDR
    metr = [("DCF fair value (IDR/share)", lambda s: s["valuation"]["fv"], USD0), ("Finite DDM (IDR/share)", lambda s: s["valuation"]["ddm"], USD0),
            ("Upside to DCF", lambda s: s["valuation"]["up"], PCT), ("Expected 12m total return", lambda s: s["valuation"]["tr12"], PCT),
            ("FY2027E EPS (USD)", lambda s: s["projection"][2027]["eps"], "0.000"), ("FY2027E profit to owners (USD m)", lambda s: s["projection"][2027]["nio"], USD),
            ("FY2028E profit to owners (USD m)", lambda s: s["projection"][2028]["nio"], USD), ("FY2027E EBITDA (USD m)", lambda s: s["projection"][2027]["ebitda"], USD),
            ("FY2027E DPS (IDR)", lambda s: s["projection"][2027]["dps"], USD0), ("P/E FY2027E at market", lambda s: s["valuation"]["pe27"], MULT),
            ("Max |balance check| (USD m)", lambda s: s["max_balance_check"], "0.000000")]
    for i, (lab, fn, fmt) in enumerate(metr):
        B.put(ws, f"A{4 + i}", lab)
        for j, nme in enumerate(("Bear", "Base", "Bull")):
            B.put(ws, f"{get_column_letter(2 + j)}{4 + i}", fn(res["scenarios"][nme]), fmt=fmt, inp=True)
    r = 6 + len(metr)
    B.put(ws, f"A{r}", "Reverse DCF: long-run Newcastle (2029+) implied by the share price, base 2027-28 path"); B.put(ws, f"B{r}", rev_lr, fmt=USD, inp=True)
    B.put(ws, f"A{r + 1}", "Reverse DCF: single flat Newcastle from 2027 implied by the share price"); B.put(ws, f"B{r + 1}", rev_flat, fmt=USD, inp=True)
    B.put(ws, f"A{r + 2}", "Newcastle FY2027 implied by consensus FY2027 EPS (base otherwise)"); B.put(ws, f"B{r + 2}", imp27, fmt=USD, inp=True)
    ws.column_dimensions["A"].width = 80
    ws = B.sheet("Sensitivity")
    B.put(ws, "A1", "DCF fair value (IDR/share), base case; static grid computed by the build script", bold=True)
    B.put(ws, "A3", "Long-run Newcastle (rows) x cost of equity (columns)", bold=True)
    for j, ke in enumerate((0.10, 0.11, 0.12, 0.13, 0.14)):
        B.put(ws, f"{get_column_letter(2 + j)}4", ke, fmt=PCT, bold=True)
    for i, lr in enumerate((85, 95, 105, 115, 125)):
        B.put(ws, f"A{5 + i}", lr, fmt=USD0, bold=True)
        for j, ke in enumerate((0.10, 0.11, 0.12, 0.13, 0.14)):
            B.put(ws, f"{get_column_letter(2 + j)}{5 + i}", grid[f"{lr}|{ke}"], fmt=USD0, inp=True)
    B.put(ws, "A12", "ASP/Newcastle ratio (rows) x IMM extended (0 = no, 1 = yes)", bold=True)
    B.put(ws, "B13", 0, bold=True); B.put(ws, "C13", 1, bold=True)
    for i, ra in enumerate((0.63, 0.66, 0.69, 0.72, 0.75)):
        B.put(ws, f"A{14 + i}", ra, fmt="0.00", bold=True)
        for j, ext in enumerate((0, 1)):
            B.put(ws, f"{get_column_letter(2 + j)}{14 + i}", grid2[f"{ra}|{ext}"], fmt=USD0, inp=True)
    B.put(ws, "A21", "One-at-a-time ranges (base case)", bold=True)
    for i, (k, d) in enumerate(tor.items()):
        B.put(ws, f"A{22 + i}", f"{k}: {d['low_input']} -> {d['high_input']}")
        B.put(ws, f"B{22 + i}", d["fv_low"], fmt=USD0, inp=True); B.put(ws, f"C{22 + i}", d["fv_high"], fmt=USD0, inp=True)
    ws.column_dimensions["A"].width = 60
    # consensus sheet
    ws = B.sheet("Consensus")
    B.put(ws, "A1", "Market expectations - S&P consensus via Yahoo, retrieved 25 Nov 2026 (forward snapshot only; no historical consensus exists in this project)", bold=True)
    hdr = ["Item", "FY2026", "FY2027"]
    for i, h in enumerate(hdr):
        x = B.put(ws, f"{get_column_letter(1 + i)}3", h, bold=True); x.fill = HDR
    B.put(ws, "A4", "Consensus EPS (USD)"); B.put(ws, "B4", float(cons["FY26"]["eps_avg"]), fmt="0.000", inp=True); B.put(ws, "C4", float(cons["FY27"]["eps_avg"]), fmt="0.000", inp=True)
    B.put(ws, "A5", "Consensus EPS low-high (USD)"); B.put(ws, "B5", f"{cons['FY26']['eps_low']:.3f}-{cons['FY26']['eps_high']:.3f}"); B.put(ws, "C5", f"{cons['FY27']['eps_low']:.3f}-{cons['FY27']['eps_high']:.3f}")
    B.put(ws, "A6", "Number of analysts (EPS)"); B.put(ws, "B6", float(cons["FY26"]["n_analysts"]), inp=True); B.put(ws, "C6", float(cons["FY27"]["n_analysts"]), inp=True)
    B.put(ws, "A7", "Consensus revenue (USD m)"); B.put(ws, "B7", float(cons["FY26"]["rev_avg"]) / 1e6, fmt=USD, inp=True); B.put(ws, "C7", float(cons["FY27"]["rev_avg"]) / 1e6, fmt=USD, inp=True)
    B.put(ws, "A8", "Model EPS, live scenario (USD)"); B.put(ws, "B8", f"=Model!{COL[2026]}{row['eps']}", fmt="0.000"); B.put(ws, "C8", f"=Model!{COL[2027]}{row['eps']}", fmt="0.000")
    B.put(ws, "A9", "Model revenue, live scenario (USD m)"); B.put(ws, "B9", f"=Model!{COL[2026]}{row['rev']}", fmt=USD); B.put(ws, "C9", f"=Model!{COL[2027]}{row['rev']}", fmt=USD)
    B.put(ws, "A10", "EPS gap (model / consensus - 1)"); B.put(ws, "B10", "=B8/B4-1", fmt=PCT); B.put(ws, "C10", "=C8/C4-1", fmt=PCT)
    pt = H["snap"]["itmg_price_targets"]
    B.put(ws, "A12", "Analyst price targets (IDR): mean / median / high / low"); B.put(ws, "B12", f"{pt['mean']:,.0f} / {pt['median']:,.0f} / {pt['high']:,.0f} / {pt['low']:,.0f}")
    rec = H["snap"]["itmg_recommendations"][0]
    B.put(ws, "A13", "Recommendations (strong buy / buy / hold / sell / strong sell)"); B.put(ws, "B13", f"{rec['strongBuy']} / {rec['buy']} / {rec['hold']} / {rec['sell']} / {rec['strongSell']}")
    B.put(ws, "A14", "Note: consensus EPS share basis is not disclosed by the vendor; model EPS uses 1,048.4m shares ex-treasury.")
    ws.column_dimensions["A"].width = 60; ws.column_dimensions["B"].width = 40
    # sources sheet
    ws = B.sheet("Sources")
    src = [("S-066", "ITMG investor relations: consolidated FS FY2018-9M26 and analyst presentations 1Q18-3Q26", "https://www.itmg.co.id/files/investor/", "SHA-256 in ITMG_document_manifest.csv"),
           ("S-003", "World Bank Commodity Price Data (Pink Sheet), Coal Australian (Newcastle)", "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx", "vintages hashed"),
           ("S-002", "Yahoo Finance prices, market data, peer multiples", "https://finance.yahoo.com", "vendor data; currency mismatch corrected"),
           ("S-036", "S&P Global consensus via Yahoo", "https://finance.yahoo.com", "forward snapshot 2026-11-25"),
           ("S-074", "FRED DGS10 US 10-year Treasury yield", "https://fred.stlouisfed.org/series/DGS10", "4.92% on 2026-11-23"),
           ("S-071", "Coal regulations table (royalty, DMO, price caps)", "data/reference/coal_regulatory_regimes.csv", "several items knowledge-only")]
    for i, h in enumerate(["ID", "Source", "Location", "Note"]):
        x = B.put(ws, f"{get_column_letter(1 + i)}1", h, bold=True); x.fill = HDR
    for i, s in enumerate(src):
        for j, v in enumerate(s):
            B.put(ws, f"{get_column_letter(1 + j)}{2 + i}", v)
    ws.column_dimensions["B"].width = 80; ws.column_dimensions["C"].width = 90
    # order sheets
    order = ["Cover", "Inputs", "Valuation", "Scenarios", "Sensitivity", "Model", "Mines", "Historical", "Peers", "Consensus", "Sources"]
    B.wb._sheets = [B.wb[n] for n in order]
    for wsx in B.wb.worksheets:
        for rowc in wsx.iter_rows():
            for cc in rowc:
                if cc.font is None or cc.font.name != F:
                    cc.font = Font(name=F, bold=cc.font.bold if cc.font else False, color=cc.font.color if cc.font else None)
    B.wb.active = 2
    B.wb.save(OUT)
    # formula count and evaluation coverage (every formula cell evaluates without error)
    E.clear(); scenario_inputs(B, E, 2)
    n, bad = 0, []
    for wsx in B.wb.worksheets:
        for rowc in wsx.iter_rows():
            for cc in rowc:
                if isinstance(cc.value, str) and cc.value.startswith("="):
                    n += 1
                    try:
                        x = E.get(wsx.title, cc.coordinate)
                        if isinstance(x, float) and not np.isfinite(x):
                            bad.append(f"{wsx.title}!{cc.coordinate}")
                    except Exception as exc:  # noqa: BLE001
                        bad.append(f"{wsx.title}!{cc.coordinate}: {exc}")
    res["formula_check"] = {"formulas": n, "errors": bad[:20], "n_errors": len(bad)}
    (RES / "ITMG_valuation_results.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    return res


if __name__ == "__main__":
    r = main()
    print("formulas", r["formula_check"])
    for s, d in r["scenarios"].items():
        v = d["valuation"]
        print(s, {k: round(v[k], 3) for k in ("fv", "ddm", "up", "tr12", "eqv", "ev", "nc26", "pe27", "eveb27", "dy27", "life", "rem2050", "rel_pe", "rel_ev", "rel_dy")}, "chk", d["max_balance_check"])
        for y in (2026, 2027, 2028, 2030):
            p = d["projection"][y]
            print("  ", y, {k: round(p[k], 2) for k in ("sales", "asp", "uc", "rev", "ebitda", "nio", "eps", "dps", "fcfe", "cash")})
    print("reverse LR", round(r["reverse_dcf_longrun_newc"], 1), "flat", round(r["reverse_dcf_flat_newc_from_2027"], 1), "cons-implied N27", round(r["consensus_implied_newc_2027"], 1))
    print("peer medians", r["peer_medians"])
