# Final Check — Figures V3 vs Findings

**Date:** 2026-05-17
**Method:** Verified all numbers in FINAL_FINDINGS_v3.md against freshly
generated analysis_v3_final/ JSONs from the E2E reproduction test.

---

## Number Alignment

| Finding | Number in FINAL_FINDINGS_v3.md | Source JSON | JSON value | Match |
|:--------|:---:|:-----------|:---:|:---:|
| F1 Premium avg | 4.791 | stats_validation.json | 4.791 | OK |
| F1 Economy avg | 4.749 | stats_validation.json | 4.749 | OK |
| F1 gap | 0.042 | computed | 4.791 - 4.749 = 0.042 | OK |
| F2 savings | 99.7% | routing_savings.json | 99.7 | OK |
| F2 best single | o3 | routing_savings.json | o3 | OK |
| F3 intent spread | 3.20 | task_discriminativeness.json | 3.2 | OK |
| F9 models at 4.5 | 5 | q12_robustness.json | 5 | OK |
| F9 models at 4.7 | 0 | q12_robustness.json | 0 | OK |
| F10 GPT-4o→5.4 price | -60% | generational_delta.json | -60 | OK |
| F10 GPT-4o→5.4 delta | +0.089 | generational_delta.json | 0.089 | OK |
| F14 flip rate | 34.7% | ranking_flips.json | 34.7 | OK |
| F15 verbosity r | 0.217 | verbosity_correlation.json | 0.2174 | OK |

**All 12 checked numbers match.**

---

## Stale Document Check

| Document | Stale numbers? | Action |
|:---------|:-:|:---|
| FINAL_FINDINGS_v3.md | No | All numbers verified |
| PAPER_OUTLINE.md | No | References findings, not raw numbers |
| PAPER_STRATEGY.md | No | Strategy doc, no data claims |
| FINDINGS_COHERENCE_REVIEW.md | No | References findings by number |
| README.md | **Fixed** | Updated to 46 models, 51,580 rows |

---

## Verdict: PASS

All numbers in all documents align with the freshly generated analysis data.
No stale or inconsistent numbers detected.
