"""ITMG prospective evaluation (Phase XIV, D-042). Run after ITMG publishes the quarter:

    python -I -X utf8 quant/itmg_prospective_eval.py 2026Q4 [--dry-run]

1. Downloads the quarter's analyst presentation and the YTD FS from itmg.co.id (official; same naming scheme as
   ITMG_document_manifest.csv, including the singular 'Statement' variant), hashing each file.
   If either is not yet published -> prints 'not yet published' and changes nothing.
2. Extracts the FIRST-REPORTED ASP (quant/itmg_extract.py) and FS standalone gross profit on the coal-revenue basis
   (quant/itmg_ops_extract.py; Q4 = 12M - 9M).
3. Compares with every forecast record in data/reference/prospective/ITMG_<q>_forecast_*.json (non-dry-run),
   writes ITMG_<q>_evaluation_<ts>.json and APPENDS resolution rows to the forecast journal.
   No model is re-estimated; nothing historical is edited. A single quarter is NOT a test of skill: the
   pre-registered prospective tests need >= 8 (interim) / 12 (final) resolved quarters.
"""
from __future__ import annotations

import hashlib
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import itmg_extract as ie  # noqa: E402
import itmg_ops_extract as oe  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference"
RAW = ROOT / "data" / "raw" / "coal" / "ITMG"
BASE = "https://www.itmg.co.id/files/investor/"


def fetch(names: list[str]) -> Path | None:
    for n in names:
        f = RAW / n.replace(" ", "_")
        if f.exists() and f.read_bytes()[:4] == b"%PDF":
            return f
        try:
            b = urllib.request.urlopen(urllib.request.Request(BASE + urllib.parse.quote(n), headers={"User-Agent": "Mozilla/5.0 (research client)"}), timeout=180).read()
            if b[:4] == b"%PDF":
                f.write_bytes(b); return f
        except Exception:  # noqa: BLE001
            continue
    return None


def run(quarter: str, dry: bool) -> dict:
    q = pd.Period(quarter, "Q"); tag = f"{q.quarter}Q{str(q.year)[2:]}"; ytd = {1: "3M", 2: "6M", 3: "9M", 4: "12M"}[q.quarter]
    deck = fetch([f"ITM Analyst Presentation {tag}.pdf"])
    fs = fetch([f"ITM Consolidated Financial Statements {ytd}{str(q.year)[2:]}.pdf", f"ITM Consolidated Financial Statement {ytd}{str(q.year)[2:]}.pdf"])
    if deck is None or fs is None:
        return {"quarter": quarter, "status": "not yet published", "deck": bool(deck), "fs": bool(fs)}
    asp = float(ie.extract(tag)["asp_usd_t"])
    cur = oe.fs_costs(fs)
    prevq = q - 1
    man = pd.read_csv(REF / "research" / "ITMG_document_manifest.csv")
    prev_file = man[(man.kind == "fs") & (man.period == str(prevq))].file
    if q.quarter == 1:
        gp = (cur["coal_revenue"] - cur["cost_of_revenue"]) / 1000
    else:
        pv = oe.fs_costs(Path(prev_file.iloc[0]))
        gp = ((cur["coal_revenue"] - pv["coal_revenue"]) - (cur["cost_of_revenue"] - pv["cost_of_revenue"])) / 1000
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    recs = sorted((REF / "prospective").glob(f"ITMG_{quarter}_forecast_*.json"))
    out = {"quarter": quarter, "evaluated_utc": ts, "actual_first_reported_asp": asp, "actual_gp_usd_m": gp,
           "documents": {"deck": {"file": deck.name, "sha256": hashlib.sha256(deck.read_bytes()).hexdigest()},
                         "fs": {"file": fs.name, "sha256": hashlib.sha256(fs.read_bytes()).hexdigest()}},
           "forecasts": []}
    for r in recs:
        f = json.loads(r.read_text(encoding="utf-8"))
        out["forecasts"].append({"record": r.name, "mode": f["mode"],
                                 "M2_err": f["C1"]["M2_asp"] - asp, "B4_err": f["C1"]["B4_asp"] - asp,
                                 "M2_in_10_90": f["C1"]["M2_interval_10_90"][0] <= asp <= f["C1"]["M2_interval_10_90"][1],
                                 "I1_err": f["I1"]["I1_gp_usd_m"] - gp, "G3_err": f["I1"]["G3_gp_usd_m"] - gp,
                                 "I1_in_10_90": f["I1"]["I1_interval_10_90"][0] <= gp <= f["I1"]["I1_interval_10_90"][1]})
    out["note"] = "One resolved quarter is not evidence of skill; prospective tests require >= 8/12 quarters (frozen specs)."
    d = REF / "prospective" / ("dry_run" if dry else ""); d.mkdir(parents=True, exist_ok=True)
    (d / f"ITMG_{quarter}_evaluation_{ts}.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    if not dry and out["forecasts"]:
        J = pd.read_csv(REF / "forecast_journal.csv")
        made = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"
        new = []
        for fr in out["forecasts"]:
            for t, s, e in [("first-reported ASP (USD/t)", "C1-M2", fr["M2_err"]), ("first-reported ASP (USD/t)", "B4", fr["B4_err"]),
                            ("gross profit coal basis (USD m)", "I1", fr["I1_err"]), ("gross profit coal basis (USD m)", "G3", fr["G3_err"])]:
                new.append(dict(made_on=made, model_commit="resolution", target=f"ITMG {quarter} {t}", scenario=f"RESOLVED {s} ({fr['mode']})",
                                value_idr_bn=np.nan, status="resolved", resolves_with=fr["record"], note=f"error {e:+.3f}; actual ASP {asp:.2f}, GP {gp:.1f}"))
        pd.concat([J, pd.DataFrame(new)], ignore_index=True).to_csv(REF / "forecast_journal.csv", index=False)
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    print(json.dumps(run(args[0] if args else "2026Q4", "--dry-run" in sys.argv), indent=1, default=float))
