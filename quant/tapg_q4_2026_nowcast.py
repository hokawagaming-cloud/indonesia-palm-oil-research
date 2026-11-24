"""EXPLORATORY Q4 2026 earnings scenarios for TAPG (bear / base / bull).

Not a validated forecast and not a rating (D-010). Every input is tagged:
  OBS   observed in an official filing (S-021/S-025) or the 9M26 FS
  BRK   broker-reported figure (S-028..S-031), secondary
  GUID  company guidance (Public Expose FY2025, S-032)
  DER   derived arithmetically from the above
  EST   an explicit scenario assumption (judgement), with the reasoning noted

Structure (consolidated scope, IDR bn):
  revenue = CPO vol x CPO ASP + PK vol x PK ASP + other palm/rubber revenue
  COGS    = (Q3 COGS ex-fertiliser) x volume factor x purchased-FFB price adj + Q4 fertiliser
  PBT     = GP - selling - G&A + other operating net + finance net + JV/associate share
  NP      = (PBT - tax on PBT ex-JV) x (1 - NCI share)
The script also solves for the fertiliser catch-up that alone would bring Q4 net
profit down to the ~IDR 612bn implied by KB Valbury's 29 Oct FY26F.

Output: data/reference/research/TAPG_q4_2026_scenarios.csv, research/company/TAPG/q4_2026_nowcast.md
Usage:  python -I -X utf8 quant/tapg_q4_2026_nowcast.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"


def q(item, quarter):
    d = pd.read_csv(REF / "TAPG_quarterly_derived.csv")
    r = d[(d["item"] == item) & (d.quarter == quarter)]["value_idr_mn"]
    return float(r.iloc[0]) / 1e3 if len(r) else float("nan")


# ---------------------------------------------------------------- observed anchors
Q3 = {k: q(k, "2026Q3") for k in ["revenue", "cost_of_sales", "gross_profit", "selling_marketing_exp", "general_admin_exp",
                                    "finance_income", "finance_costs", "share_of_profit_jv", "share_of_profit_associates",
                                    "profit_before_tax", "income_tax_expense", "profit_for_year", "profit_attrib_owners"]}
Q4_25 = {k: q(k, "2025Q4") for k in ["revenue", "cost_of_sales", "gross_profit", "profit_before_tax", "profit_attrib_owners"]}
jv_q3 = Q3["share_of_profit_jv"] + Q3["share_of_profit_associates"]
other_op_q3 = Q3["profit_before_tax"] - (Q3["gross_profit"] + Q3["selling_marketing_exp"] + Q3["general_admin_exp"]
                                         + Q3["finance_income"] + Q3["finance_costs"] + jv_q3)
NM9 = 3505.620  # 9M26 profit to owners (OBS, 9M26 FS)
INPUTS = [  # name, value, tag, note
    ("q3_cpo_sales_kt", 187.5, "BRK", "KBV p1"), ("q3_cpo_asp", 15565, "BRK", "KBV p1"),
    ("q3_pk_sales_kt", 34.2, "BRK", "KBV p1"), ("q3_pk_asp", 13402, "BRK", "KBV p1"),
    ("q3_fertilizer_bn", 75, "BRK", "KBV p1"),
    ("q3_other_revenue_bn", Q3["revenue"] - 187.5 * 15565 / 1e3 - 34.2 * 13402 / 1e3, "DER", "revenue - CPO - PK (PKO, PKM, FFB, rubber)"),
    ("q3_jv_assoc_bn", jv_q3, "OBS", "9M26 - H1 26 FS"), ("q3_other_operating_net_bn", other_op_q3, "DER", "PBT residual"),
    ("q3_tax_rate_ex_jv", -Q3["income_tax_expense"] / (Q3["profit_before_tax"] - jv_q3), "DER", "tax / (PBT - JV share)"),
    ("q3_nci_share", 1 - Q3["profit_attrib_owners"] / Q3["profit_for_year"], "DER", "1 - owners / profit"),
    ("fg_inventory_build_bn", 663.960 - 288.121, "OBS", "finished goods Sep-26 vs Dec-25, 9M26 FS p66"),
    ("fg_cost_per_kg_proxy", 9000, "EST", "≈ 9M26 COGM 5,652bn / ~630kt subsidiary CPO+PK output (PE25 2025 subsidiary share 68%); rough"),
    ("guidance_cpo_2026_total_kt", 1016, "GUID", "PE25 p9 (incl. associates)"),
    ("cpo_9m26_groupwide_kt", 756.8, "BRK", "ALD p2"),
]
I = {n: v for n, v, _, _ in INPUTS}
inv_kt = I["fg_inventory_build_bn"] * 1e3 / I["fg_cost_per_kg_proxy"]  # IDR bn / (IDR/kg) -> kt
INPUTS.append(("fg_inventory_build_kt_equiv", inv_kt, "DER/EST", "inventory build / cost proxy; CPO-equivalent, very rough"))
INPUTS.append(("guidance_implied_q4_cpo_groupwide_kt", 1016 - 756.8, "DER", "FY26F guidance minus 9M actual (guidance from Mar-26)"))

SCEN = {  # all EST unless stated
    "bear": dict(cpo_vol_vs_q3=0.95, inv_release=0.0, asp_vs_q3=-0.10, pk_asp_vs_q3=-0.12, fert_q4=340, ffb_price_pass=0.5,
                 jv_assoc=240, note="harvest down QoQ; no inventory release; CPO ASP -10% (Nov KPBN tender ~13,850 vs Q3 ASP 15,565); full fertiliser catch-up; JV back to the Q4'25 level"),
    "base": dict(cpo_vol_vs_q3=1.00, inv_release=0.5, asp_vs_q3=-0.04, pk_asp_vs_q3=-0.05, fert_q4=230, ffb_price_pass=0.5,
                 jv_assoc=310, note="flat harvest; half of the 9M inventory build sold; ASP -4% (WB Oct palm oil -2% vs Q3 avg, softer Nov tenders); fertiliser catch-up ~+155bn QoQ"),
    "bull": dict(cpo_vol_vs_q3=1.05, inv_release=1.0, asp_vs_q3=0.00, pk_asp_vs_q3=0.00, fert_q4=150, ffb_price_pass=0.5,
                 jv_assoc=360, note="guidance-consistent harvest; full inventory release; ASP flat (lower Nov export duty 124 vs 178 USD/t supports domestic price); moderate catch-up"),
}


def run(s: dict) -> dict:
    cpo_kt = I["q3_cpo_sales_kt"] * s["cpo_vol_vs_q3"] + s["inv_release"] * inv_kt
    vol_factor = cpo_kt / I["q3_cpo_sales_kt"]
    asp = I["q3_cpo_asp"] * (1 + s["asp_vs_q3"])
    pk_asp = I["q3_pk_asp"] * (1 + s["pk_asp_vs_q3"])
    rev = cpo_kt * asp / 1e3 + I["q3_pk_sales_kt"] * vol_factor * pk_asp / 1e3 + I["q3_other_revenue_bn"] * vol_factor * (1 + s["asp_vs_q3"])
    cogs_ex_fert_q3 = -Q3["cost_of_sales"] - I["q3_fertilizer_bn"]
    # purchased FFB is priced off CPO: pass part of the ASP change into non-fertiliser cost
    cogs = cogs_ex_fert_q3 * vol_factor * (1 + s["ffb_price_pass"] * s["asp_vs_q3"]) + s["fert_q4"]
    gp = rev - cogs
    selling = Q3["selling_marketing_exp"] * vol_factor
    pbt = gp + selling + Q3["general_admin_exp"] + I["q3_other_operating_net_bn"] + Q3["finance_income"] + Q3["finance_costs"] + s["jv_assoc"]
    tax = I["q3_tax_rate_ex_jv"] * (pbt - s["jv_assoc"])
    np_ = (pbt - tax) * (1 - I["q3_nci_share"])
    return {"cpo_sales_kt": cpo_kt, "cpo_asp": asp, "revenue": rev, "cogs": cogs, "gross_profit": gp, "gpm": gp / rev,
            "jv_assoc": s["jv_assoc"], "pbt": pbt, "net_profit_owners": np_, "fy26_net_profit": NM9 + np_}


def main() -> int:
    res = {k: run(v) for k, v in SCEN.items()}
    R = pd.DataFrame(res).T
    # break-even fertiliser: Q4 fertiliser that alone takes the base case to KBV's implied 612bn
    lo, hi = 0.0, 3000.0
    for _ in range(60):
        mid = (lo + hi) / 2
        v = run({**SCEN["base"], "fert_q4": mid})["net_profit_owners"]
        lo, hi = (mid, hi) if v > 612 else (lo, mid)
    be_fert = (lo + hi) / 2
    # also: break-even ASP change (base otherwise)
    lo, hi = -0.6, 0.2
    for _ in range(60):
        mid = (lo + hi) / 2
        v = run({**SCEN["base"], "asp_vs_q3": mid})["net_profit_owners"]
        lo, hi = (mid, hi) if v < 612 else (lo, mid)
    be_asp = (lo + hi) / 2
    out = R.copy()
    out.to_csv(REF / "research" / "TAPG_q4_2026_scenarios.csv", float_format="%.2f")
    pd.DataFrame(INPUTS, columns=["input", "value", "tag", "note"]).to_csv(REF / "research" / "TAPG_q4_2026_inputs.csv", index=False)

    md = ["# TAPG — Exploratory Q4 2026 Earnings Scenarios", "",
          "_Generated by `quant/tapg_q4_2026_nowcast.py`. **Exploratory. Not validated, not a forecast of record, no rating.** Tags: OBS = filing, BRK = broker, GUID = company guidance, DER = derived, EST = scenario assumption._", "",
          "## Reference points", "",
          f"- Q4 2025 actual (OBS, FY − 9M): revenue {Q4_25['revenue']:,.0f}bn, gross profit {Q4_25['gross_profit']:,.0f}bn, profit to owners **{Q4_25['profit_attrib_owners']:,.0f}bn**.",
          f"- Q3 2026 actual (OBS): revenue {Q3['revenue']:,.0f}bn, profit to owners **{Q3['profit_attrib_owners']:,.0f}bn**, JV+associates {jv_q3:,.0f}bn.",
          "- **Forecasts in hand:**",
          "  - KB Valbury, 29 Oct 2026: FY26F 4,118bn, so implied Q4 = 612bn. KBV itself calls this 'unrealistically weak' and says it is under review.",
          "  - Bloomberg consensus via Aldiracita, 29 Oct 2026: FY26F 4,122bn, so implied Q4 about 617bn.",
          "  - Indo Premier, 7 Oct 2026 (before the 9M results): FY26F 4,750bn, so Q4 about 1,244bn given 9M actual 3,506bn.",
          "  - **No forecast revised after the results was found.**", "",
          "## Inputs", "", "| Input | Value | Tag | Note |", "|---|---|---|---|"]
    md += [f"| {n} | {v:,.3f} | {t} | {no} |" if abs(v) < 10 else f"| {n} | {v:,.1f} | {t} | {no} |" for n, v, t, no in INPUTS]
    md += ["", "## Scenarios (IDR bn, consolidated)", "", "| | Bear | Base | Bull |", "|---|---|---|---|"]
    for col, fmt in [("cpo_sales_kt", "{:,.1f}"), ("cpo_asp", "{:,.0f}"), ("revenue", "{:,.0f}"), ("cogs", "{:,.0f}"), ("gross_profit", "{:,.0f}"),
                     ("gpm", "{:.1%}"), ("jv_assoc", "{:,.0f}"), ("pbt", "{:,.0f}"), ("net_profit_owners", "{:,.0f}"), ("fy26_net_profit", "{:,.0f}")]:
        md.append(f"| {col} | " + " | ".join(fmt.format(R.loc[s, col]) for s in ["bear", "base", "bull"]) + " |")
    md += ["", "Scenario assumptions (all EST):"]
    for k, s in SCEN.items():
        md.append(f"- **{k}**: CPO volume ×{s['cpo_vol_vs_q3']:.2f} of Q3; inventory release {s['inv_release']:.0%} of ~{inv_kt:.0f}kt; CPO ASP {s['asp_vs_q3']:+.0%} vs Q3; fertiliser {s['fert_q4']}bn (Q3: 75); JV+associates {s['jv_assoc']}bn; purchased-FFB cost pass-through 50% of the ASP change. {s['note']}.")
    md += ["", "## Can the implied ~612bn Q4 be justified?", "",
           f"- Holding the other base inputs, Q4 fertiliser would need to be about **{be_fert:,.0f}bn** (vs 75bn in Q3 2026) to bring Q4 profit to 612bn.",
           f"- Alternatively, CPO ASP would need to fall about **{be_asp:+.0%}** vs Q3 with base fertiliser (230bn).",
           "- Neither is ruled out by the data in hand. Fertiliser levels are known only for Q3 2026 (75bn) and as YoY changes (9M −23%). One broker estimated FY24 fertiliser at about 790bn (Phintraco, secondary), and management guides 2027 fertiliser +25% YoY (Indo Premier, 7 Oct). So the plausible size of the catch-up is uncertain.",
           "- The implied ~612bn requires a combination of a large fertiliser catch-up, falling CPO prices and lower JV income. The base case here (about "
           f"{R.loc['base','net_profit_owners']:,.0f}bn) sits between the KBV/consensus-implied figure and Indo Premier's pre-results figure.", "",
           "## What this does NOT show", "",
           "- Nothing about predictive accuracy: the structure has not been back-tested. Only 7 quarters of filings exist, and quarterly operational data begin at 3Q24 and were first seen in a 29 Oct 2026 report (D-011).",
           "- No earnings-surprise opportunity is claimed:",
           "  - The 'consensus' used is pre-results or stale, and no revised post-results forecasts were found.",
           "  - The stock price reaction since 29 Oct has not been analysed.",
           "  - The main swing factors (fertiliser timing, inventory release, Q4 CPO price) are not observed until the FY2026 filing (expected by about end-March 2027)."]
    (ROOT / "research" / "company" / "TAPG" / "q4_2026_nowcast.md").write_text("\n".join(md), encoding="utf-8")
    print(R[["cpo_sales_kt", "revenue", "gross_profit", "gpm", "pbt", "net_profit_owners", "fy26_net_profit"]].round(2).to_string())
    print(f"break-even fertiliser {be_fert:,.0f}bn; break-even ASP change {be_asp:+.1%}; inventory kt equiv {inv_kt:.1f}")
    print({k: round(v, 3) for k, v in I.items() if k.startswith("q3_")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
