# Reproducibility Review

**Date:** 2026-05-17
**Question:** Can a reviewer clone the repo and reproduce our results?

---

## 1. Structure Clarity

| Check | Status | Notes |
|:------|:------:|:------|
| README.md exists | OK | Updated with 47 models, 21 tasks, correct structure |
| README explains how to run | OK | Shows `run_batch.py`, `rebuild_csv.py`, `analyze_costs.py` |
| README explains project structure | OK | Directory tree included |
| METHODOLOGY.md exists | OK | 12 sections, comprehensive |
| LEARNINGS.md exists | OK | 19 sections, operational knowledge |

**Gap:** README says "47 complete models" but current count is 46 (after
nemotron fix). README numbers are stale from the last mass update. Need to
update to 46 complete, 51,580 rows.

---

## 2. Scripts Documentation

| Script | Purpose | Documented? | Runnable standalone? |
|:-------|:--------|:---:|:---:|
| `run_batch.py` | Main benchmark runner | YES (METHODOLOGY.md) | YES (needs .env) |
| `rebuild_csv.py` | Rebuild CSV from raw JSON | YES | YES |
| `analyze_costs.py` | V1 analysis (Pareto, heatmap) | YES | YES |
| `re_judge_failed_scores.py` | Re-judge crashed scores | Partially | YES (needs OpenAI key) |
| `rejudge_v2.py` | V2 re-judge (2 tasks) | Code comments only | YES (needs OpenAI key) |
| `rejudge_v2_full.py` | V2 re-judge (15 tasks) | Code comments only | YES (needs OpenAI key) |
| `humaneval_harness.py` | Code gen pass@1 evaluation | Code comments | YES |
| `rerun_cat_a.sh` | Category A re-run shell script | Inline comments | YES |
| `run_full_benchmark.py` | V1 legacy runner | YES (METHODOLOGY.md) | YES |

**Gap:** No single `reproduce_analysis.py` script that regenerates all
v3 analysis files from the CSV. The v3 analyses were done as inline Python
in the conversation, not as a committed script. A reviewer would need to
extract the analysis code from conversation history.

**Fix needed:** Create `scripts/analyze_v3.py` that reads the CSV and
generates all 20 JSON files in `analysis_v3_final/`.

---

## 3. Data Accessibility

| Data | Location | Public? | Size |
|:-----|:---------|:---:|:---:|
| CSV (main dataset) | `results/benchmark_results.csv` | YES (in repo) | ~8MB |
| V1 CSV backup | `results/benchmark_results_v1_judge.csv.bak` | YES | ~8MB |
| Raw JSON responses | `results/raw/*.json` | YES (51,705 files) | ~500MB |
| Datasets (JSONL) | `datasets/*.jsonl` | YES (24 files) | ~2MB |
| V3 analysis JSONs | `results/analysis_v3_final/*.json` | YES (20 files) | ~1MB |
| V2 analysis files | `results/analysis_v2_final/*` | YES (legacy) | ~5MB |
| Rejudge log | `results/rejudge_v2_log.jsonl` + `rejudge_v2_full_log.jsonl` | YES | ~3MB |
| Spend tracker | `results/spend_tracker.json` | YES | 1KB |

**Gap:** The .env file with API keys is not in the repo (correct — security).
But there's no `.env.example` showing which keys are needed. A reviewer can't
know they need `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `MISTRAL_API_KEY`, etc.

**Fix needed:** Create `.env.example` with all required keys listed (values blank).

---

## 4. Figure Reproducibility

| Figure | Can be regenerated? | From which script? |
|:-------|:---:|:------|
| Heatmap | NO | Was inline Python, not a script |
| Pareto plots | NO | Was inline Python |
| Tier comparison | NO | Was inline Python |
| Task discriminativeness | NO | Was inline Python |
| Verbosity scatter | NO | Was inline Python |
| Provider gradient | NO | Was inline Python |
| Per-task routing | NO | Was inline Python |
| Generational delta | NO | Was inline Python |
| Origin comparison | NO | Was inline Python |
| License comparison | NO | Was inline Python |

**All 10 figures were generated as inline code in the conversation, not as
committed scripts.** A reviewer cannot regenerate them.

**Fix needed:** Create `scripts/generate_figures.py` that produces all figures
from the CSV / JSON files.

---

## 5. Reproducibility Checklist

| Step | Can a reviewer do it? | What's missing? |
|:-----|:---:|:------|
| Clone repo | YES | — |
| Understand structure | YES | README is clear |
| Read raw data | YES | CSV + JSON all public |
| Rerun benchmark | PARTIAL | Needs .env with 9 API keys + credits |
| Rebuild CSV from raw | YES | `python3 scripts/rebuild_csv.py` |
| Regenerate V3 analyses | **NO** | No committed analysis script |
| Regenerate figures | **NO** | No committed figure script |
| Rerun V2 judge | PARTIAL | Needs OpenAI key + ~$60 |
| Rerun pass@1 harness | YES | `scripts/humaneval_harness.py` |
| Verify judge validation | **NO** | Validation was inline, not scripted |

---

## 6. Fixes Required Before Paper Submission

### Priority 1 (blocking)

1. **Create `scripts/analyze_v3.py`** — reads CSV, computes all 20 JSON files
   in `analysis_v3_final/`. Includes: tier comparison, task discriminativeness,
   routing savings, coverage matrix, generational delta, provider gradient,
   origin comparison, license comparison, bootstrap CIs, Mann-Whitney tests.

2. **Create `scripts/generate_figures.py`** — reads JSON files, produces all
   10 SVG figures. Uses the validated Pareto style from PARETO_STYLE_GUIDE.md.

3. **Regenerate 4 stale figures** (heatmap, Paretos, tier comparison,
   discriminativeness) on V3 data.

### Priority 2 (important)

4. **Create `.env.example`** with all required API key names.

5. **Update README.md** to 46 complete models, 51,580 rows, V2 judge.

6. **Add a `Makefile` or `reproduce.sh`** with commands:
   ```
   make rebuild     # rebuild CSV from raw JSON
   make analyze     # run analyze_v3.py
   make figures     # run generate_figures.py
   make validate    # run humaneval_harness.py for code gen validation
   ```

### Priority 3 (nice to have)

7. **Add `requirements.txt`** (numpy, scipy, matplotlib, sacrebleu, requests).

8. **Document the V2 judge prompts** in a machine-readable format (JSON or YAML)
   not just in JUDGE_PROMPTS_V2.md.
