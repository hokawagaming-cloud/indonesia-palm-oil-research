"""Extract per-page text from PDFs so values can be cited by page number.

Writes <out_dir>/<pdf stem>.txt with '=== PAGE n ===' markers (n = 1-based PDF page
index, i.e. the page number in a PDF viewer, not the printed folio), plus a
<pdf stem>.meta.json holding the PDF metadata and page count.

Usage:  python -I quant/pdf_to_text.py <pdf_dir> <out_dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pymupdf


def main(src: str, out: str) -> int:
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    for pdf in sorted(Path(src).glob("*.pdf")):
        doc = pymupdf.open(pdf)
        stem = pdf.stem.replace(" ", "_")
        chars = 0
        with open(out_dir / f"{stem}.txt", "w", encoding="utf-8") as fh:
            for i, page in enumerate(doc, start=1):
                text = page.get_text("text")
                chars += len(text)
                fh.write(f"\n=== PAGE {i} ===\n{text}")
        meta = {"file": pdf.name, "pages": doc.page_count, "chars": chars,
                "metadata": doc.metadata}
        (out_dir / f"{stem}.meta.json").write_text(json.dumps(meta, indent=1, default=str))
        print(f"{pdf.name}: {doc.page_count} pages, {chars} chars, "
              f"created {doc.metadata.get('creationDate')}, mod {doc.metadata.get('modDate')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:3]))
