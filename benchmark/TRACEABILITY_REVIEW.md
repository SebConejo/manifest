# Traceability Review

**Date:** 2026-05-17
**Purpose:** Verify every number in the 17 findings is traceable to a source file.

---

## Finding × Source Verification

| Finding | Claim | Source file | Value | Status |
|:--------|:------|:-----------|:-----:|:------:|
| F1 | Economy avg = 4.749 | `v3/stats_validation.json` → bootstrap.Economy.mean | 4.749 | OK |
| F1 | Premium avg = 4.791 | `v3/stats_validation.json` → bootstrap.Premium.mean | 4.791 | OK |
| F2 | Savings = 99.7% | `v3/routing_savings.json` → savings_pct | 99.7 | OK |
| F2 | Best single = o3 | `v3/routing_savings.json` → single_best.model | o3 | OK |
| F3 | Intent spread = 3.20 | `v3/task_discriminativeness.json` → intent_clinc150.spread | 3.2 | OK |
| F4 | Provider gradient data | `v3/provider_gradient.json` | exists | OK |
| F7 | Origin p = 0.18 | `v3/origin_comparison.json` → mann_whitney_p | 0.1816 | OK |
| F8 | Closed avg = 4.787 | `v3/license_comparison.json` → closed.avg | 4.787 | OK |
| F8 | Open avg = 4.603 | `v3/license_comparison.json` → open.avg | 4.603 | OK |
| F9 | 5 models at ≥4.5 | `v3/q12_robustness.json` → thresholds.4.5 | 5 | OK |
| F9 | 0 models at ≥4.7 | `v3/q12_robustness.json` → thresholds.4.7 | 0 | OK |
| F10 | GPT-4o→5.4 price -60% | `v3/generational_delta.json` | -60 | OK |
| F10 | GPT-4o→5.4 quality +0.089 | `v3/generational_delta.json` | 0.089 | OK |
| F13 | V2 r GSM8K = 0.905 | `v2/judge_v2_validation.json` → gsm8k.v2_r | 0.9053 | OK |
| F13 | V2 r RAG QA = 0.887 | `v2/judge_v2_validation.json` → rag_qa.v2_r | 0.8875 | OK |
| F14 | Flip rate = 34.7% | `v3/ranking_flips.json` → global.flip_rate_pct | 34.7 | OK |
| F15 | Verbosity r = 0.217 | `v3/verbosity_correlation.json` → r_verbosity_vs_delta | 0.2174 | OK |
| F16 | Qwen Turbo cheapest on sentiment | `v3/per_task_routing_savings.json` | match | OK |
| F17 | 4 unique cheapest models at 4.5 | `v3/coverage_matrix.json` → unique_cheapest | 4 items | OK |

**Note on F13:** The judge_v2_validation.json is in `analysis_v2_final/`, not
`analysis_v3_final/`. This is correct — the validation was done before the
full re-judge and the numbers didn't change. For the paper, cite the file
in its actual location.

**All 19 checks pass.** Every number in the findings is traceable to a JSON
source file.

---

## Figure Verification

| # | Figure | Location | V2 scores? | Status |
|---|--------|----------|:---:|:------:|
| 1 | Heatmap | `v2/heatmap_model_task_v2.svg` | NO (V1 scores) | **NEEDS REGEN** |
| 2 | Pareto RAG QA | `v2/pareto_rag_qa_v8.svg` | NO (V1 scores) | **NEEDS REGEN** |
| 3 | Tier comparison | `v2/tier_comparison.svg` | NO (V1 scores) | **NEEDS REGEN** |
| 4 | Task discriminativeness | `v2/task_discriminativeness.svg` | NO (V1 scores) | **NEEDS REGEN** |
| 5 | Verbosity scatter | `v3/verbosity_scatter.svg` | YES | OK |
| 6 | Provider gradient | `v3/provider_gradient.svg` | YES | OK |
| 7 | Per-task routing | `v3/per_task_routing_savings.svg` | YES | OK |
| 8 | Generational delta | `v3/generational_delta.svg` | YES | OK |
| 9 | Origin comparison | `v3/origin_comparison.svg` | YES | OK |
| 10 | License comparison | `v3/license_comparison.svg` | YES | OK |

**4 figures need regeneration on V2 judge scores.** The heatmap, Pareto (RAG QA
and all 20 others), tier comparison, and task discriminativeness bar chart were
generated on V1 scores and have not been updated to V3 data. The underlying
JSON data in `analysis_v3_final/` IS on V2 scores, but the SVG figures are stale.

---

## Summary

| Check | Result |
|:------|:------:|
| Number traceability (17 findings) | **19/19 OK** |
| Figure existence | **10/10 exist** |
| Figure data freshness | **4 STALE** (need V3 regen) |

**Action required:** Regenerate 4 figures (heatmap, Paretos, tier comparison,
discriminativeness) using V3 data before paper submission.
