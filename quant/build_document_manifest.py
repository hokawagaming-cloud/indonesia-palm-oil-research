"""Build data/reference/document_manifest.csv: one row per unique source document
(by SHA-256) with every local copy, its reporting period, source URL and Git status.
PDFs are kept local only (.gitignore); this manifest is the tracked record.

Usage: python -I quant/build_document_manifest.py
"""
import hashlib
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
META = {  # filename -> (document, reporting period, source URL as known)
    "AR 2021.pdf": ("TAPG Annual Report 2021", "FY2021 (Jan-Dec 2021)", "not recorded - user download"),
    "AR_2022.pdf": ("TAPG Annual Report 2022", "FY2022", "not recorded - user download"),
    "AR_2023.pdf": ("TAPG Annual Report 2023", "FY2023", "https://admin-web.tap-agri.com/storage/files/1/AR/AR_2023.pdf"),
    "AR_2024.pdf": ("TAPG Annual Report 2024", "FY2024", "https://admin-web.tap-agri.com/storage/files/1/AR/AR_2024.pdf"),
    "TAPG_-_AR_2025.pdf": ("TAPG Annual Report 2025", "FY2025", "https://financialfilings.com/filings/pt-triputra-agro-persada-tbk/annual-report/2026/57434983/ (per user)"),
    "FinancialStatement-2026-I-TAPG.pdf": ("TAPG interim financial statements Q1 2026 (IDX XBRL)", "Q1 2026 (Jan-Mar)", "not recorded - user download (IDX filing)"),
    "FinancialStatement-2026-II-TAPG.pdf": ("TAPG interim financial statements H1 2026 (IDX XBRL)", "H1 2026 (Jan-Jun)", "not recorded - user download (IDX filing)"),
    "FinancialStatement-2026-III-TAPG.pdf": ("TAPG interim financial statements 9M 2026 (IDX XBRL)", "9M 2026 (Jan-Sep)", "https://financialfilings.com/filings/pt-triputra-agro-persada-tbk/interim-quarterly-report/2026/74818409/ (per user)"),
    "kbvalbury_tapg_3q26_261030.pdf": ("KB Valbury TAPG company report (broker)", "3Q26 / 9M26 (published 2026-10-29)", "https://www.kbvalbury.com/cfind/source/files/tapg-3q26---261030.pdf"),
    "aldiracita_TAPG_9M26_EarningsFlash.pdf": ("Aldiracita TAPG 9M26 Earnings Flash (broker)", "9M26 (published 2026-10-29)", "https://aldiracita.com/wp-content/uploads/2026/10/TAPG_9M26_EarningsFlash.pdf"),
    "ajaib_TAPG_company_update_20260505.pdf": ("Ajaib TAPG Company Update (broker)", "1Q26 (published 2026-05-05)", "https://storage.googleapis.com/storage-ajaib-prd-platform-pdf/Company%20Update%20-%20TAPG%20%2820260505%29.pdf"),
    "phintraco_TAPG_initiation_20250708.pdf": ("Phintraco TAPG initiation (broker)", "FY2024 base (published 2025-07-08)", "https://phintracosekuritas.com/wp-content/uploads/2025/07/PHINTAS-Initiate-Report-TAPG_20250708-EN.pdf"),
    "idx_public_expose_FY2025_20260316.pdf": ("TAPG Public Expose FY2025 (IDX filing)", "FY2021-FY2025, FY2026F", "https://www.idx.co.id/StaticData/NewsAndAnnouncement/ANNOUNCEMENTSTOCK/From_EREP/202603/d03bdcd902_0ec945e3ed.pdf"),
    "LSIP_bilingual_30_Sep_2026_Released.pdf": ("LSIP interim FS 30 Sep 2026 (bilingual)", "9M 2026", "user download (londonsumatra.com / IDX); IDX 2026-10-30 19:45"),
    "LSIP_bilingual_30_Jun_2026_Released.pdf": ("LSIP interim FS 30 Jun 2026 (bilingual)", "H1 2026", "user download; IDX 2026-07-31 16:22"),
    "LSIP_bilingual_31 des_2025_released.pdf": ("LSIP audited FS 31 Dec 2025 (bilingual)", "FY2025", "user download; IDX 2026-02-27"),
    "pp london sumatra indonesia_bilingual_31 des_2024_released.pdf": ("LSIP audited FS 31 Dec 2024 (bilingual)", "FY2024", "user download; IDX 2025-02-28"),
    "Lonsum Highlights 9M26.pdf": ("LSIP 9M26 highlights", "9M 2026", "user download; IDX 2026-10-30 20:01"),
    "Lonsum Highlights 1Q2026.pdf": ("LSIP 1Q26 highlights", "Q1 2026", "user download; IDX 2026-04-30 20:00"),
    "Lonsum Highlights FY25.pdf": ("LSIP FY25 highlights", "FY2025", "user download; IDX 2026-02-27 16:31"),
    "Lonsum Highlights FY24.pdf": ("LSIP FY24 highlights", "FY2024", "user download; IDX 2025-02-28 17:19"),
    "LSIP_KI_Rencana Pembelian Kembali Saham 2026.pdf": ("LSIP buyback disclosure (POJK 13/2023)", "Oct-Dec 2026 programme", "user download; IDX 2026-10-23 18:51"),
    "Sustainability Report LSIP 2025.pdf": ("LSIP Sustainability Report 2025", "FY2025", "user download; IDX 2026-04-30 19:50 (with AR)"),
}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    pdfs = sorted(p for p in ROOT.rglob("*.pdf") if ".git" not in p.parts)
    tracked = set(subprocess.run(["git", "ls-files", "*.pdf"], cwd=ROOT, capture_output=True,
                                 text=True).stdout.splitlines())
    rows = {}
    for p in pdfs:
        rel = p.relative_to(ROOT).as_posix()
        h = sha256(p)
        r = rows.setdefault(h, {"sha256": h, "filename": p.name, "bytes": p.stat().st_size,
                                "document": META.get(p.name, ("unknown", "", ""))[0],
                                "reporting_period": META.get(p.name, ("", "unknown", ""))[1],
                                "source_url": META.get(p.name, ("", "", "unknown"))[2],
                                "local_paths": [], "tracked_in_git_now": False})
        r["local_paths"].append(rel)
        r["tracked_in_git_now"] |= rel in tracked
    out = pd.DataFrame(rows.values())
    out["local_paths"] = out["local_paths"].map("; ".join)
    hist = set(subprocess.run(["git", "log", "--all", "--name-only", "--format="], cwd=ROOT, capture_output=True,
                              text=True).stdout.splitlines())
    out["in_git_history"] = out["filename"].map(lambda n: any(h.endswith("/" + n) or h == n for h in hist))
    out.to_csv(ROOT / "data" / "reference" / "document_manifest.csv", index=False)
    print(out[["filename", "reporting_period", "bytes", "tracked_in_git_now", "in_git_history"]].to_string(index=False))
    print("copies per document:", out["local_paths"].str.count(";").add(1).tolist())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
