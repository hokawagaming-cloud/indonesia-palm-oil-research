# Independent audit artefacts — GPT Astra (2026-11-24)

**Provenance.** Two untracked files were created by an external agent ("GPT Astra") in this working tree at 21:19–21:20 WIB on 2026-11-24, while a Claude Code session was running. The user approved reconciliation on 2026-11-24. The files are preserved **byte-for-byte** in `original/` (SHA-256 below). They were moved, not edited, from:

| Original path | Archived as | SHA-256 |
|---|---|---|
| `quant/tapg_pit_audit.py` | `original/tapg_pit_audit.py` | see `sha256.txt` |
| `data/reference/research/continuation_evidence.json` | `original/continuation_evidence.json` | see `sha256.txt` |

The archived script is **not executed** from here: its `ROOT` path assumes `quant/`. Its logic is integrated into `quant/pit_panel.py` as the strict vintage rule (D-017).

**Source-ID conflicts.** Astra's IDs S-034 to S-042 collide with this repository's S-034 to S-037. They are Astra-local IDs and must not be read as register IDs. The mapping to register IDs is in `id_map.csv`. Each item was independently verified (or not) as recorded there.
