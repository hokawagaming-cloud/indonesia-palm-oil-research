"""Parse TAPG IDX announcement listings mirrored by jejaksaham.id (S-027) into a table of
disclosure timestamps (local time, WIB).

The listing gives, for each IDX announcement: date, time, title and category. This is
a SECONDARY mirror of the IDX e-reporting feed: it gives timestamps where IDX itself
is blocked to scripts.

Input:  data/raw/company/TAPG/external/jejaksaham/p*.html (git-ignored)
Output: data/reference/TAPG_idx_announcements.csv
Usage:  python -I quant/parse_idx_announcements.py
"""
import glob
import html
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MONTHS = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "Mei": 5, "Jun": 6, "Jul": 7, "Agu": 8, "Agt": 8,
          "Sep": 9, "Okt": 10, "Nov": 11, "Des": 12}
DAY = r"(?:Senin|Selasa|Rabu|Kamis|Jumat|Sabtu|Minggu), (\d{1,2}) (\w{3}) (\d{4}) \d+ pengumuman"


def main() -> int:
    rows = []
    for f in sorted(glob.glob(str(ROOT / "data/raw/company/TAPG/external/jejaksaham/p*.html"))):
        t = open(f, encoding="utf-8", errors="ignore").read()
        x = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
        x = html.unescape(re.sub(r"<[^>]+>", " ", x))
        x = re.sub(r"\s+", " ", x)
        parts = re.split(DAY, x)
        # parts: [pre, d, m, y, body, d, m, y, body, ...]
        for k in range(1, len(parts) - 3, 4):
            d, m, y, body = parts[k], parts[k + 1], parts[k + 2], parts[k + 3]
            if m not in MONTHS:
                continue
            date = pd.Timestamp(int(y), MONTHS[m], int(d))
            for it in re.finditer(r"TAPG (.+?) (\d{2}:\d{2}) ([A-Z][a-z&,\s]+?)(?= TAPG |$| [A-Z][a-z]+, \d)", body):
                rows.append({"date": date.date(), "time_wib": it.group(2), "title": it.group(1).strip(),
                             "category": it.group(3).strip(), "source_page": Path(f).name})
    out = pd.DataFrame(rows).drop_duplicates(["date", "time_wib", "title"]).sort_values(["date", "time_wib"])
    out.to_csv(ROOT / "data" / "reference" / "TAPG_idx_announcements.csv", index=False)
    print(len(out), "announcements", out.date.min(), "->", out.date.max())
    fin = out[out.title.str.contains("Laporan Keuangan|Public Expose|Laporan Tahunan|Dividen|RUPS|Newsletter|Presentasi|Analyst", case=False)]
    print(fin.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
