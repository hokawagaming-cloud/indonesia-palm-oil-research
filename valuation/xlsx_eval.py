"""Minimal, dependency-free evaluator for the formula subset used in our openpyxl-built workbooks.

Supports: numbers, + - * / ^, comparisons (= <> < > <= >=), parentheses, cell and range references (optionally
sheet-qualified, $-anchored), and SUM, MIN, MAX, IF, AND, OR, ABS, INDEX(range,row,col).
Used to (a) verify the workbook's live formulas without Excel/LibreOffice and (b) run scenarios / goal seeks by
overriding input cells. Not a general Excel engine.
"""
from __future__ import annotations

import re

from openpyxl.utils import column_index_from_string, get_column_letter

REF = re.compile(r"(?:(?:'([^']+)'|([A-Za-z_][A-Za-z0-9_]*))!)?\$?([A-Z]{1,3})\$?(\d+)(?::\$?([A-Z]{1,3})\$?(\d+))?")


class Evaluator:
    def __init__(self, wb):
        self.wb, self.cache, self.over = wb, {}, {}

    def set(self, sheet: str, ref: str, value) -> None:
        self.over[(sheet, ref.replace("$", ""))] = value
        self.cache.clear()

    def clear(self) -> None:
        self.over.clear(); self.cache.clear()

    def get(self, sheet: str, ref: str):
        key = (sheet, ref.replace("$", ""))
        if key in self.over:
            return self.over[key]
        if key in self.cache:
            return self.cache[key]
        v = self.wb[sheet][key[1]].value
        if isinstance(v, str) and v.startswith("="):
            v = self._eval(v[1:], sheet)
        elif v is None:
            v = 0.0
        self.cache[key] = v
        return v

    def _range(self, sheet, c1, r1, c2, r2):
        a, b = column_index_from_string(c1), column_index_from_string(c2)
        return [[self.get(sheet, f"{get_column_letter(c)}{r}") for c in range(a, b + 1)] for r in range(int(r1), int(r2) + 1)]

    def _eval(self, f: str, sheet: str):
        env = {"R": self.get, "RG": self._range}
        out, i = [], 0
        # protect function names from the reference regex by scanning tokens
        for m in REF.finditer(f):
            s, e = m.span()
            q, n, c1, r1, c2, r2 = m.groups()
            if s > 0 and (f[s - 1].isalnum() or f[s - 1] in "_."):   # inside a name or a number
                continue
            if e < len(f) and (f[e].isalnum() or f[e] == "("):       # e.g. 'LOG10(' or 'A1B'
                continue
            sh = q or n or sheet
            out.append(f[i:s])
            out.append(f'RG("{sh}","{c1}",{r1},"{c2}",{r2})' if c2 else f'R("{sh}","{c1}{r1}")')
            i = e
        out.append(f[i:])
        py = "".join(out)
        py = re.sub(r"\bSUM\(", "_sum(", py); py = re.sub(r"\bMIN\(", "_min(", py); py = re.sub(r"\bMAX\(", "_max(", py)
        py = re.sub(r"\bIF\(", "_if(", py); py = re.sub(r"\bAND\(", "_and(", py); py = re.sub(r"\bOR\(", "_or(", py)
        py = re.sub(r"\bABS\(", "abs(", py); py = re.sub(r"\bINDEX\(", "_index(", py)
        py = py.replace("^", "**").replace("<>", "!=")
        py = re.sub(r"(?<![<>!=])=(?!=)", "==", py)

        def flat(a):
            for x in a:
                if isinstance(x, list):
                    yield from flat(x)
                else:
                    yield x
        env.update(_sum=lambda *a: sum(float(x) for x in flat(a) if isinstance(x, (int, float))),
                   _min=lambda *a: min(float(x) for x in flat(a)), _max=lambda *a: max(float(x) for x in flat(a)),
                   _if=lambda c, a, b=0.0: a if c else b, _and=lambda *a: all(flat(a)), _or=lambda *a: any(flat(a)),
                   _index=lambda rg, r, c=1: rg[int(r) - 1][int(c) - 1])
        return eval(py, {"__builtins__": {}}, env)  # noqa: S307 (formulas are our own)
