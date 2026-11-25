"""Phase XVII LSIP: engineering tests (data identities, cohort mechanics, workbook structure, no double counting).
These are NOT evidence of forecasting skill or investment edge."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "data" / "reference" / "research"
sys.path.insert(0, str(ROOT / "valuation"))
from xlsx_eval import Evaluator  # noqa: E402

WB = ROOT / "outputs" / "LSIP_model_valuation.xlsx"


def test_lsip_financial_identities_and_restatements():
    c = pd.read_csv(RES / "LSIP_financials_checks.csv").dropna()
    ident = c[~c.check.str.startswith("restatement")]
    assert len(ident) >= 40 and (ident.difference.abs() < 1.5).all()
    rest = c[c.check.str.startswith("restatement") & (c.difference.abs() > 1.5)]
    # only the disclosed FY2021 restatement (AR2022, PSAK 24) and an FY2022 CFO/CFI reclassification are allowed
    assert set(rest.period) <= {"FY2021", "FY2022"}
    assert rest.difference.abs().max() < 30000           # IDR mn


def test_cogs_components_sum():
    k = pd.read_csv(RES / "LSIP_cogs_breakdown.csv", index_col=0)
    parts = ["indirect", "ffb_purchases", "harvesting", "upkeep_fertiliser", "depreciation", "manufacturing"]
    assert ((k[parts].sum(axis=1) - k.total_production_cost).abs() < 2).all()
    fin = pd.read_csv(RES / "LSIP_financials_annual.csv", index_col=0)
    for p in ("FY2023", "FY2024", "FY2025", "9M26"):
        assert abs(k.loc[p, "cogs"] + fin.loc[p, "cogs"]) < 2


def test_age_profile_and_ops():
    a = pd.read_csv(RES / "LSIP_age_profile.csv").dropna(subset=["total"])
    assert ((a[["immature", "a4_6", "a7_20", "gt20"]].sum(axis=1) - a.total).abs() <= 1).all()
    a23 = a[a.date == "2023-12-31"].iloc[0]
    assert abs(a23.gt20_share - 0.41) < 0.005 and a23.total == 91759
    o = pd.read_csv(RES / "LSIP_operational_annual.csv", index_col=0)
    assert abs(o.loc["FY2025", "yield_nucleus_t_ha"] - 1139 / 84.744) < 1e-3   # CSV stores 4 decimals
    assert (o.loc[[f"FY{y}" for y in range(2017, 2026)], "op_mature"] + o.loc[[f"FY{y}" for y in range(2017, 2026)], "op_immature"]
            == o.loc[[f"FY{y}" for y in range(2017, 2026)], "oil_palm"]).all()


def test_cohort_roll_conserves_area_and_removes_oldest():
    import lsip_cohort as LC
    s = pd.Series(0.0, index=np.arange(LC.MAXAGE + 1)); s[[5, 25, 30]] = [100.0, 50.0, 40.0]
    k = pd.Series(1.0, index=s.index)
    s2, _ = LC.roll(s, plant=60.0, remove_total=60.0, kmult_state=k, k_new=1.2)
    assert abs(s2.sum() - s.sum()) < 1e-9
    assert s2[31] == 0 and abs(s2[26] - 30.0) < 1e-9 and s2[0] == 60.0 and s2[6] == 100.0


def test_cohort_scenarios_area_and_rates():
    sc = pd.read_csv(RES / "LSIP_cohort_scenarios.csv")
    assert np.allclose(sc.area_ha, 89331.0, atol=1e-3)
    assert (sc.ffb_nucleus_kt > 0).all()
    summ = json.loads((RES / "LSIP_cohort_summary.json").read_text())
    assert abs(summ["steady_state"]["B_accelerated"]["cycle_years"] - 25) < 1e-9
    assert summ["hist_planting_rate_2017_2025_ha"] < summ["sustainable_rate_ha_25y"]
    b = sc[sc.scenario == "B_accelerated"].set_index("year")
    assert b.loc[2030, "replant_ha"] == summ["sustainable_rate_ha_25y"]


def test_workbook_verified_and_balanced():
    r = json.loads((RES / "LSIP_valuation_results.json").read_text())
    assert r["n_errors"] == 0 and r["formulas"] > 1500
    for k, d in r["detail"].items():
        assert max(abs(v) for v in d["check"].values()) < 1e-6, k


def test_value_ordering_and_ddm_below_dcf():
    r = json.loads((RES / "LSIP_valuation_results.json").read_text())
    for s in ("A_historical", "B_accelerated", "C_deferred", "D_intensive"):
        v = [r["grid"][f"{s}|{c}"]["ps"] for c in ("bear", "base", "bull")]
        assert v[0] < v[1] < v[2]
        assert r["grid"][f"{s}|base"]["ddm_ps"] < r["grid"][f"{s}|base"]["ps"]
    sens = r["sensitivity"]
    lr = [sens["plrm"][k]["ps"] for k in sorted(sens["plrm"], key=float)]
    rpc = [sens["rpc"][k]["ps"] for k in sorted(sens["rpc"], key=float)]
    assert all(np.diff(lr) > 0) and all(np.diff(rpc) < 0)
    pay = [sens["pay"][k]["ddm_ps"] for k in sorted(sens["pay"], key=float)]
    assert all(np.diff(pay) > 0)


def test_interest_income_not_in_operating_value():
    """Changing the deposit yield must not change operating value (FCFF excludes interest); cash is added once."""
    wb = openpyxl.load_workbook(WB)
    inp = {wb["Inputs"][f"A{r}"].value: f"B{r}" for r in range(3, 120) if wb["Inputs"][f"A{r}"].value}
    dy = inp["Pre-tax deposit yield"]
    val = {wb["Valuation"][f"A{r}"].value: f"B{r}" for r in range(10, 45) if wb["Valuation"][f"A{r}"].value}
    ops = val["Operating enterprise value (plantations, ex cash)"]
    E = Evaluator(wb); base = E.get("Valuation", ops)
    E.set("Inputs", dy, 0.10)
    assert abs(E.get("Valuation", ops) - base) < 1e-6


def test_q4_v1_preserved_and_v2_separate():
    v1 = pd.read_csv(RES / "LSIP_q4_2026_nowcast.csv", index_col=0)
    assert abs(v1.loc["base", "q4_np_owners"] - 468.11) < 0.01
    v2 = pd.read_csv(RES / "LSIP_q4_2026_nowcast_v2.csv", index_col=0)
    assert v2.loc["bear", "q4_np_owners"] < v2.loc["base", "q4_np_owners"] < v2.loc["bull", "q4_np_owners"]


def test_itmg_frozen_artifacts_untouched():
    frozen = ["data/reference/research/ITMG_C1_preregistration.json", "data/reference/research/ITMG_I1_preregistration.json",
              "data/reference/research/DR_preregistration.json", "data/reference/forecast_journal.csv"]
    out = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", *frozen], cwd=ROOT)
    assert out.returncode == 0
