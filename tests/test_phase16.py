"""Phase XVI ITMG model: engineering tests (data identities, formula evaluation, model structure). Not evidence of skill."""
import json
import sys
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "data" / "reference" / "research"
sys.path.insert(0, str(ROOT / "valuation"))
from xlsx_eval import Evaluator  # noqa: E402

WB = ROOT / "outputs" / "ITMG_model_valuation.xlsx"


def test_financial_statement_identities():
    k = pd.read_csv(RES / "ITMG_financials_checks.csv", index_col=0)
    assert (k.bs_balance.abs() < 1).all() and (k.gp_identity.abs() < 1).all() and (k.profit_identity.abs() < 1).all()
    assert (k.max_abs_restatement_next_year.dropna() < 1).all()


def test_evaluator_basic():
    wb = openpyxl.Workbook(); a = wb.active; a.title = "S"; b = wb.create_sheet("T")
    a["B1"] = 2; a["C1"] = 5; b["AB12"] = 3
    b["A1"] = "=S!$B$1*AB12+SUM(S!B1:C1)-MAX(1,2)^2+IF(AB12>=3,10,0)+INDEX(S!B1:C1,1,2)"
    assert Evaluator(wb).get("T", "A1") == 2 * 3 + 7 - 4 + 10 + 5


def test_workbook_formulas_evaluate_and_balance():
    r = json.loads((RES / "ITMG_valuation_results.json").read_text(encoding="utf-8"))
    assert r["formula_check"]["n_errors"] == 0 and r["formula_check"]["formulas"] > 1000
    for s in ("Bear", "Base", "Bull"):
        assert r["scenarios"][s]["max_balance_check"] < 1e-6


def test_scenarios_ordered_and_no_terminal_value():
    r = json.loads((RES / "ITMG_valuation_results.json").read_text(encoding="utf-8"))
    fv = [r["scenarios"][s]["valuation"]["fv"] for s in ("Bear", "Base", "Bull")]
    assert fv[0] < fv[1] < fv[2]
    wb = openpyxl.load_workbook(WB)
    txt = " ".join(str(c.value) for row in wb["Valuation"].iter_rows() for c in row if c.value)
    assert "terminal" not in txt.lower() or "no terminal" in txt.lower()


def test_sensitivity_monotonic_in_long_run_price():
    g = json.loads((RES / "ITMG_valuation_results.json").read_text(encoding="utf-8"))["sensitivity_lr_ke"]
    for ke in ("0.1", "0.12", "0.14"):
        vals = [g[f"{lr}|{ke}"] for lr in (85, 95, 105, 115, 125)]
        assert all(b >= a - 1e-6 for a, b in zip(vals, vals[1:]))


def test_c1_used_only_for_next_quarter():
    wb = openpyxl.load_workbook(WB)
    ws = wb["Inputs"]
    labels = {ws[f"A{r}"].value: ws[f"G{r}"].value for r in range(1, 120) if ws[f"A{r}"].value}
    c1 = [k for k, v in labels.items() if v and "VALIDATED" in str(v)]
    assert c1 == ["Q4 2026 ASP (frozen C1-M2, provisional)"]


def test_scenario_selector_changes_value():
    wb = openpyxl.load_workbook(WB); E = Evaluator(wb)
    ref = None
    for r in range(1, 40):
        if wb["Valuation"][f"A{r}"].value == "Fair value per share - DCF (IDR)":
            ref = f"B{r}"
    E.set("Inputs", "B3", 2); base = E.get("Valuation", ref)
    E.set("Inputs", "B3", 3); bull = E.get("Valuation", ref)
    assert bull > base
