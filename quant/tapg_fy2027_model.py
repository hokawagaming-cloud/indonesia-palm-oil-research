"""TAPG FY2027 quarterly operating and earnings model (Phase III, priority 3). EXPLORATORY.

Transparent driver model, consolidated scope, IDR bn. Every input is tagged in INPUTS
(OBS/BRK/GUID/DER/EST). Three scenarios (bear/base/bull) span the uncertainty; no
probabilities are attached.

Production
  FY26 group CPO = 9M actual 756.8kt (BRK, S-029) + Q4 (GUID-implied 259kt) -> 1,016kt.
  FY27 change: bull 0% / base -7.5% / bear -12% (management guidance -5 to -10% via
  Indo Premier, S-045, secondary; 2026 JJAS rainfall -65% vs normal in Central
  Kalimantan, CHIRPS S-007; ONI 2.46 in ASO 2026; after the 2023 El Nino TAPG nucleus
  FFB fell 3.4% in 2024).
  Consolidated share of group CPO = 68.4% (PE25 FY2025, S-032).
  Quarterly seasonality = 2025 group CPO shares (KBV, S-028): 24.3 / 26.7 / 23.3 / 25.7%.
Price / netback (quant/levy_duty.py, quant/cpo_netback.py)
  Realised ASP (IDR/kg) = (world price - levy - duty) x USDIDR / 1000 + basis.
  Basis calibrated on Q3 2026: WB avg 1,148 USD/t, charges 273.2, USDIDR 17,846
  gives 15,618 vs realised 15,565, so basis = -53 IDR/kg (DER). HRef = 0.873 x WB
  (Q3 2026 ratio, DER). Levy/duty use the current PMK 9/2026 and PMK 68/2025 schedules.
  World price (USD/t): bear 1,000 / base 1,100 / bull 1,200 (EST). USDIDR 18,000 (EST).
Revenue = CPO + PK (15.7% of CPO revenue, Q3 2026 DER) + other (7.3%) + Q1 sale of the part of the
  9M26 finished-goods build not released in the matching Q4 scenario (bear 100%, base 50%, bull 0%).
  The FY26 base used for scaling excludes the Q4 base inventory release (one-off).
Costs
  FY26 COGS = 9M 5,330 (OBS) + Q4 base 2,179 (nowcast base). FY26 fertiliser estimated
  at 692bn = 0.77 x (0.75 x 800bn FY25 broker estimate, S-031) + 230bn Q4 base (EST).
  FY27 fertiliser = FY26 x 1.25 (management guidance via S-045, secondary).
  Non-fertiliser COGS scales with consolidated volume, 50% pass-through of the price change
  (purchased FFB) and 4% cost inflation (EST).
JV/associates: FY26 = 918.9 (9M, OBS) + 310 (Q4 base) = 1,229; FY27 scales with the
  percentage change in TAPG gross profit (same crop, region and prices; EST).
Other: selling scales with volume; G&A +5%; other operating items -100bn/yr; finance net
  +80bn/yr; tax 21.6% of PBT ex-JV; NCI 3.9% (Q3 2026 DER).

Output: data/reference/research/TAPG_fy2027_quarterly.csv, research/company/TAPG/fy2027_model.md
Usage:  python -I -X utf8 quant/tapg_fy2027_model.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from levy_duty import duty_usd_t, levy_usd_t  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
SEAS = [231 / 952, 254 / 952, 222 / 952, 245 / 952]
FY26 = dict(group_cpo_kt=1016.0, cons_share=652 / 953, cpo_sales_kt=None, revenue=9446.6 + 3701.7,
            cogs=5330.0 + 2179.0, fert=0.77 * 0.75 * 800 + 230, jv=918.9 + 310, gp=4116.6 + 1522.6,
            selling=-256.2 - 90.0, ga=-427.5 - 152.3, np=4714.7)
BASIS = -53.0
HREF_RATIO = 0.873
SCEN = {
    "bear": dict(inv27=1.0, prod=-0.12, wb=1000, fx=18000, fert_mult=1.25, infl=0.05, other_op=-150, label="production -12%, world CPO USD 1,000/t, fertiliser +25%, cost inflation 5%"),
    "base": dict(inv27=0.5, prod=-0.075, wb=1100, fx=18000, fert_mult=1.25, infl=0.04, other_op=-100, label="production -7.5%, USD 1,100/t, fertiliser +25%, inflation 4%"),
    "bull": dict(inv27=0.0, prod=0.0, wb=1200, fx=18000, fert_mult=1.10, infl=0.03, other_op=-60, label="production flat, USD 1,200/t, fertiliser +10%, inflation 3%"),
}


def realised_asp(wb: float, fx: float, date: str = "2027-06-15") -> tuple[float, float, float]:
    href = wb * HREF_RATIO
    lv, _ = levy_usd_t(date, href)
    dt, _ = duty_usd_t(date, href)
    return (wb - lv - dt) * fx / 1000 + BASIS, lv, dt


def run(s: dict) -> pd.DataFrame:
    asp, lv, dt = realised_asp(s["wb"], s["fx"])
    asp26 = 15157 * 0.75 + (15565 * 0.945) * 0.25  # 9M ASP and Q4 base ASP (DER/EST)
    cons_cpo27 = FY26["group_cpo_kt"] * (1 + s["prod"]) * FY26["cons_share"]
    cons_cpo26 = FY26["group_cpo_kt"] * FY26["cons_share"]
    vol = cons_cpo27 / cons_cpo26
    pchg = asp / asp26 - 1
    rev_cpo = cons_cpo27 * asp / 1e3
    # inventory: the part of the 9M26 build NOT released in the matching Q4 scenario is sold in Q1 2027
    inv_cost = 375.8 * s["inv27"]
    inv_rev = inv_cost / (9000 / 15565) * (asp / 15565)
    rev_prod = rev_cpo * (1 + 0.157 + 0.073)
    rev = rev_prod + inv_rev
    fert = FY26["fert"] * s["fert_mult"]
    # FY26 base for scaling EXCLUDES the Q4 base inventory release (rev 307.3, carrying cost 187.9)
    cogs26_ex_release = FY26["cogs"] - 187.9
    cogs_ex = (cogs26_ex_release - FY26["fert"]) * vol * (1 + 0.5 * pchg) * (1 + s["infl"])
    cogs = cogs_ex + fert + inv_cost
    gp = rev - cogs
    gp26_ex_release = FY26["gp"] - (307.3 - 187.9)
    jv = FY26["jv"] * ((gp - (inv_rev - inv_cost)) / gp26_ex_release)
    selling, ga = FY26["selling"] * vol, FY26["ga"] * 1.05
    pbt = gp + selling + ga + s["other_op"] + 80 + jv
    np_ = (pbt - 0.216 * (pbt - jv)) * (1 - 0.039)
    rows = []
    for qi, w in enumerate(SEAS, start=1):
        # fertiliser front-loaded into H1 (catch-up continues in Q1 per management, BRK S-028)
        fw = [0.32, 0.26, 0.20, 0.22][qi - 1]
        q_rev = rev_prod * w + (inv_rev if qi == 1 else 0.0)
        q_cogs = cogs_ex * w + fert * fw + (inv_cost if qi == 1 else 0.0)
        q_gp = q_rev - q_cogs
        q_jv = jv * w
        q_pbt = q_gp + selling * w + ga / 4 + s["other_op"] / 4 + 20 + q_jv
        rows.append({"quarter": f"2027Q{qi}", "cons_cpo_sales_kt": cons_cpo27 * w, "asp_idr_kg": asp, "revenue": q_rev,
                     "gross_profit": q_gp, "jv_assoc": q_jv, "pbt": q_pbt,
                     "net_profit_owners": (q_pbt - 0.216 * (q_pbt - q_jv)) * (1 - 0.039)})
    q = pd.DataFrame(rows)
    q.attrs.update(fy_np=np_, fy_rev=rev, asp=asp, levy=lv, duty=dt, vol=vol, fert=fert, jv=jv, gp=gp)
    return q


def main() -> int:
    exp = pd.read_csv(REF / "TAPG_expectations_snapshots.csv")
    cons27 = float(exp[(exp.metric == "FY27 EPS") & exp.source.str.startswith("Yahoo")].value.iloc[0]) * 19852.54 / 1000
    out, md = [], ["# TAPG — FY2027 Quarterly Model (exploratory)", "",
                   "_Generated by `quant/tapg_fy2027_model.py`. Consolidated scope, IDR bn. Inputs are tagged in the module docstring. Not validated._", "",
                   f"FY2026 base reference: net profit {FY26['np']:,.0f}bn (9M actual + Q4 base nowcast).", "",
                   "| Scenario | Assumptions | Realised CPO ASP (IDR/kg) | Levy + duty (USD/t) | Revenue | Gross profit | JV | **FY27 net profit** | vs FY26 base | vs consensus FY27 |",
                   "|---|---|---|---|---|---|---|---|---|---|"]
    for k, s in SCEN.items():
        q = run(s)
        q.insert(0, "scenario", k)
        out.append(q)
        a = q.attrs
        md.append(f"| {k} | {s['label']} | {a['asp']:,.0f} | {a['levy'] + a['duty']:,.0f} | {a['fy_rev']:,.0f} | {a['gp']:,.0f} | {a['jv']:,.0f} | **{a['fy_np']:,.0f}** | {a['fy_np'] / FY26['np'] - 1:+.0%} | {a['fy_np'] / cons27 - 1:+.0%} |")
    Q = pd.concat(out)
    Q.to_csv(REF / "research" / "TAPG_fy2027_quarterly.csv", index=False, float_format="%.1f")
    piv = Q.pivot(index="quarter", columns="scenario", values="net_profit_owners")[["bear", "base", "bull"]]
    md += ["", f"Consensus FY27 (S&P via Yahoo/StockAnalysis, 2026-11-24): EPS 225.3, i.e. about **{cons27:,.0f}bn** (+6% vs consensus FY26). Other FY27 points: KB Valbury 4,075bn (29 Oct, under review); Ajaib 4,430bn (May); Indo Premier 4,980bn (7 Oct, pre-results; it flagged 5–13% downside risk).", "",
           "## Quarterly net profit (IDR bn)", "", "| Quarter | Bear | Base | Bull |", "|---|---|---|---|"]
    md += [f"| {i} | {r.bear:,.0f} | {r.base:,.0f} | {r.bull:,.0f} |" for i, r in piv.iterrows()]
    md += ["", "## Reading", "",
           "- **Our base sees FY27 below FY26.** Volume falls (El Niño lag), fertiliser rises (+25% guided) and the price is lower. Consensus instead expects about +6% growth.",
           "- So the expectations gap may have opposite signs in the two years: our FY26 is above consensus (Q4), but our FY27 base is below it.",
           "- The share-price weakness after 9M26 is consistent with the market looking through a strong FY26 to a weaker FY27. That is a hypothesis, not a finding.",
           "- **Largest uncertainties:**",
           "  - World CPO price: every USD 100/t is about IDR 1,800/kg of realised ASP before second-round levy/duty effects.",
           "  - The size of the El Niño volume hit.",
           "  - The fertiliser base level (FY25 fertiliser is a broker estimate, not disclosed).",
           "- Quarterly phasing follows 2025 seasonality, with fertiliser front-loaded into H1 (catch-up continuing into Q1 2027 per management, via KBV). The timing of the El Niño lag within FY27 is not modelled separately."]
    (ROOT / "research" / "company" / "TAPG" / "fy2027_model.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
