# DSNG Inventory Catalyst — Verification vs TAPG (preliminary)

_Date: 2026-11-24 · Audit finding D · Sources: S-037 (DSNG company updates 1H26 and 9M26, DSNG 9M26 financial statements, downloaded from dsn.co.id) · No rating, no valuation_

## Claim under test (GPT Astra, preliminary)

> DSNG's investor newsletter reported CPO inventory rising from about 23,000t to 52,000t because of delayed customer pickups.

## What the primary DSNG documents show

| Item | 1H26 | 9M26 | Q3 2026 (DERIVED: 9M − 1H) | Source |
|---|---|---|---|---|
| CPO production (kt) | 299 | 451 | **152** | Corporate Update 1H26 p6; Company Update 9M26 p5 (chart labels) |
| CPO sales (kt) | 319 | 446 | **127** | same |
| Production − sales (kt) | −20 | +5 | **+25** | derived |
| CPO ASP (IDR mn/t) | 14.9 | 15.1 | — | same |
| Total inventories (IDR bn, all segments) | — | 1,814.0 (Dec-25: 1,380.4) | — | 9M26 FS p4 |

The 9M26 deck says: "CPO sales volume declined by 3% YoY to 446.1 thousand tons, as shipment delays and vessel congestion slowed customer pickups, resulting in higher CPO inventories at the end of September 2026" (p5).

**Verdict: PARTIALLY VERIFIED.**
- **Verified from primary sources:** the cause (delayed pickups, vessel congestion) and the direction (higher CPO inventory at Sep-26).
- **Consistent with the claim:** a Q3 production surplus of about +25kt (derived), against the claimed +29kt (23k → 52k).
- **Not verified:** the 23k and 52k levels. They do not appear in the decks or the FS text in hand; a separate DSNG "investor newsletter" was not found.
- **Not separated:** the FS inventory increase (+IDR 434bn) also includes wood products and other segments.

## Preliminary comparison with TAPG

| | DSNG | TAPG |
|---|---|---|
| Evidence of unsold output | Company states the cause (pickup delays), which reads as transient. Q3 CPO build of ~25kt derived from company volumes. | Finished-goods inventory IDR 288bn → 664bn (FS, OBS). The cause is not stated by the company; a broker says "part of 9M26 output is still unsold". Tonnage unknown (A-020/A-021 estimates). |
| Scope quality | Production and sales are on the same consolidated scope in the deck | Quarterly production is group-wide (incl. associates); sales are consolidated. The inventory build cannot be converted to tonnes reliably. |
| Indicative Q4 revenue shift if released | ~25kt × IDR 15.1mn/t ≈ IDR 380bn (DERIVED, revenue, not profit) | ~IDR 307–639bn revenue in the base/bull scenarios (EST) |
| Profit effect | Not estimated: unit cost and margin not yet extracted | Included in the Q4 scenarios (base 1,268bn) |
| Market expectations | **Not yet gathered** | Yahoo consensus implies Q4 ~720bn (D-016) |
| Valuation / price-in | **Not yet assessed** | Event study done (`price_in_assessment.md`) |

## Conclusion (preliminary)

- DSNG's inventory evidence is **qualitatively stronger** than TAPG's: the company names a transient cause, and the volumes are on one scope.
- That does not make DSNG the better opportunity. Its expectations, margins, valuation and price reaction are not assessed yet, and a timing shift only matters if consensus did not already assume shipments normalise.
- **TAPG remains primary coverage.**
- STAA has not been started.

## Next steps

1. DSNG: dated consensus (Yahoo eps_trend), Q4 2025 base, unit margin from the 9M FS, event study with `quant/tapg_price_in.py` logic (peer index ex-DSNG).
2. Look for the DSNG investor newsletter with the 23k/52k figures, or confirm it does not exist.
3. STAA: the same light screen.
