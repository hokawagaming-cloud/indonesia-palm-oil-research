"""Phase XI Workstream 1: final audit of the MVP-B1 data layer and secondary results.
Original MVP-B1 outputs are NOT modified; findings are written to MVP_B1_audit.json / MVP_B1_audit_*.csv.

(a) Impairment sign: re-read raw PDFs without abs(); classify each negative raw impairment as
    'sign convention' (salaries/personnel expense line also negative in the same document) or
    'possible genuine reversal' (salaries positive). Also report negative STANDALONE monthly impairments
    (YTD differences), which abs() on YTD values does not remove.
(b) PBT-as-operating-profit: for documents flagged op_from_pbt, check NII + net non-interest operational result
    == PBT (the layout has no non-operating section).
(c) Timestamp reliability: compare BBCA filename dates and BBRI IR posting dates with the earliest
    Internet Archive (Wayback) capture of the same PDF URL (independent upper-bound evidence of public availability).
(d) Multiplicity: the T2 'information value' claim compared the BEST of 4 IM rules with the BEST of 4
    unconditional rules, chosen ex post. Re-test all 16 IM x U pairs per bank with Holm, then Bonferroni x4
    for (2 banks x 2 targets).

Usage: python -I -X utf8 quant/bank_audit_b1.py [--wayback]
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bank_extract as be  # noqa: E402
import bank_mvp_b1 as b1  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "reference" / "research"
RAW = ROOT / "data" / "raw" / "banking"
IMP = (r"(?:\(IMPAIRMENT\)|(?:LOSS )?IMPAIRMENT (?:LOSSES? )?(?:ON|OF|FOR) (?:FINANCIAL )?ASSETS|"
       r"PENURUNAN NILAI ASET KEUANGAN \(IMPAIRMENT\))(?= \(?\d)")
SAL = r"(?:SALARIES AND EMPLOYEE BENEFITS|PERSONNEL EXPENSES|BEBAN TENAGA KERJA)(?= \(?\d)"


def _text(f: Path) -> str:
    return " ".join(" ".join(p.get_text() for p in pymupdf.open(f)).split()).upper()


def audit_impairment() -> tuple[pd.DataFrame, dict]:
    man = pd.read_csv(RAW / "download_manifest.csv").dropna(subset=["file"])
    rows = []
    for r in man.itertuples():
        t = _text(Path(r.file)); k = 1 if r.kind == "M" else 4
        pl = max(be.find(t, r"NET INTEREST INCOME|PENDAPATAN \(BEBAN\) BUNGA BERSIH"), 0)
        q = be.find(t, IMP, pl); s = be.find(t, SAL, pl)
        imp = be.nums_after(t, q, k) if q > 0 else None
        sal = be.nums_after(t, s, k) if s > 0 else None
        if imp and imp[0] < 0:
            rows.append({"bank": r.bank, "kind": r.kind, "title": r.title, "raw_impairment": imp[0], "salaries": sal[0] if sal else np.nan,
                         "class": "sign convention" if (sal and sal[0] < 0) else "possible genuine reversal"})
    D = pd.DataFrame(rows)
    M = pd.read_csv(OUT / "bank_monthly_extract.csv")
    M["per"] = pd.PeriodIndex(M.period, freq="M")
    neg_standalone = []
    for bank, g in M.groupby("bank"):
        g = g.set_index("per").sort_index()
        for p in g.index:
            if p.month == 1 or (p - 1) not in g.index:
                continue
            v = g.loc[p, "bo_impairment"] - g.loc[p - 1, "bo_impairment"]
            if v < 0:
                neg_standalone.append({"bank": bank, "month": str(p), "standalone_impairment_bn": v / 1e3})
    summ = {"negative_raw_documents": len(D), "by_class": D["class"].value_counts().to_dict() if len(D) else {},
            "negative_standalone_months_preserved": neg_standalone}
    return D, summ


def audit_pbt_substitution() -> dict:
    man = pd.read_csv(RAW / "download_manifest.csv").dropna(subset=["file"])
    res = []
    for r in man.itertuples():
        k = 1 if r.kind == "M" else 4
        t = _text(Path(r.file))
        if re.search(r"NON[ -]OPERA(?:TING|TIONAL|SIONAL)", t):
            continue
        v = be.extract_doc(Path(r.file), k)
        if not v.get("op_from_pbt"):
            continue
        q = be.find(t, r"NET OPERATIONAL INCOME \(EXPENSES\) OTHER THAN INTEREST|PENDAPATAN \(BEBAN\) OPERASIONAL SELAIN BUNGA BERSIH")
        net_other = be.nums_after(t, q, k) if q > 0 else None
        if net_other and v["nii"] and v["pbt"]:
            gap = v["nii"][0] + net_other[0] - v["pbt"][0]
            res.append({"bank": r.bank, "kind": r.kind, "title": r.title, "gap": gap, "pbt": v["pbt"][0]})
    D = pd.DataFrame(res)
    return {"documents_using_pbt": int(len(D)), "reconciled_within_0.1pct": int((D.gap.abs() <= 0.001 * D.pbt.abs()).sum()) if len(D) else 0,
            "max_abs_gap_mn": float(D.gap.abs().max()) if len(D) else None}


def wayback_first(url: str) -> pd.Timestamp | None:
    api = "https://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode({"url": url, "limit": "1", "output": "json", "fl": "timestamp"})
    try:
        req = urllib.request.Request(api, headers={"User-Agent": "research-client"})
        j = json.loads(urllib.request.urlopen(req, timeout=40).read().decode() or "[]")
        return pd.to_datetime(j[1][0], format="%Y%m%d%H%M%S") if len(j) > 1 else None
    except Exception:  # noqa: BLE001
        return None


def audit_timestamps(sample: int = 40) -> pd.DataFrame:
    import urllib.parse  # noqa: F401
    M = pd.read_csv(OUT / "bank_monthly_extract.csv", parse_dates=["avail_verified"])
    man = pd.read_csv(RAW / "download_manifest.csv").dropna(subset=["file"])
    man["source"] = man.file.apply(lambda f: Path(f).name)
    D = M.merge(man[["source", "url"]], on="source").dropna(subset=["avail_verified"])
    D = D[D.period >= "2020-01"].groupby("bank", group_keys=False).apply(lambda g: g.sample(min(len(g), sample // 2), random_state=7))
    out = []
    for r in D.itertuples():
        w = wayback_first(r.url); time.sleep(1.0)
        out.append({"bank": r.bank, "period": r.period, "claimed_date": r.avail_verified.date(), "wayback_first": w.date() if w is not None else None,
                    "days_capture_minus_claimed": (w.normalize() - r.avail_verified).days if w is not None else None})
    return pd.DataFrame(out)


def audit_multiplicity() -> pd.DataFrame:
    F = pd.read_csv(OUT / "MVP_B1_forecasts_primary.csv")
    F["excluded"] = F.excluded.fillna("")
    rows = []
    for bank in ("BBCA", "BBRI"):
        for tgt in ("T1", "T2"):
            cols = [f"{tgt}|{m}" for m in b1.IM + b1.UNC]
            D = F[(F.bank == bank) & (F.excluded == "")].dropna(subset=cols + [f"actual_{tgt}"])
            a = D[f"actual_{tgt}"].to_numpy()
            ps = {}
            for im in b1.IM:
                for u in b1.UNC:
                    dm, p = b1.dm_test(D[f"{tgt}|{im}"].to_numpy() - a, D[f"{tgt}|{u}"].to_numpy() - a)
                    ps[(im, u)] = p
            hp = b1.holm({f"{i}|{u}": p for (i, u), p in ps.items()})
            for (i, u), p in ps.items():
                rows.append({"bank": bank, "target": tgt, "IM": i, "U": u, "n": len(a), "p_raw": p, "p_holm16": hp[f"{i}|{u}"],
                             "p_holm16_bonf4": min(1.0, hp[f"{i}|{u}"] * 4)})
    return pd.DataFrame(rows)


def main() -> int:
    D, imp = audit_impairment()
    pbt = audit_pbt_substitution()
    mult = audit_multiplicity()
    ts = audit_timestamps() if "--wayback" in sys.argv else pd.DataFrame()
    D.to_csv(OUT / "MVP_B1_audit_impairment_signs.csv", index=False)
    mult.to_csv(OUT / "MVP_B1_audit_multiplicity.csv", index=False, float_format="%.4f")
    if len(ts):
        ts.to_csv(OUT / "MVP_B1_audit_wayback.csv", index=False)
    t2 = mult[mult.target == "T2"]
    best = t2.sort_values("p_raw").groupby("bank").head(3)
    summary = {"impairment": imp, "pbt_substitution": pbt,
               "T2_pairs_significant_after_holm16_bonf4": t2[t2.p_holm16_bonf4 <= 0.05].groupby("bank").size().to_dict(),
               "T2_best_pairs": best[["bank", "IM", "U", "p_raw", "p_holm16", "p_holm16_bonf4"]].to_dict("records"),
               "wayback": ({"n": int(ts.days_capture_minus_claimed.notna().sum()),
                            "captures_before_claimed_date": int((ts.days_capture_minus_claimed < 0).sum()),
                            "median_days_after": float(ts.days_capture_minus_claimed.median())} if len(ts) else "not run")}
    (OUT / "MVP_B1_audit.json").write_text(json.dumps(summary, indent=1, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
