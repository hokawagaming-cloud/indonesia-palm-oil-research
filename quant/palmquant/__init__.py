"""palmquant: a point-in-time quantamental research framework for Indonesian listed palm oil companies.

Design rules enforced in code (see context/RESEARCH_CONTEXT.md §8 and context/CLAUDE_CODE_TASKS.md):
  * every stored value carries an observation date AND a publication timestamp;
  * every stored value carries a source_id from quant/config/sources.yaml;
  * nothing is fabricated: missing data stays missing and is reported by the audit;
  * analysis functions only see data published at or before the decision time;
  * rankings and strategy outputs are locked until the quality gates pass.
"""

__version__ = "0.1.0"
