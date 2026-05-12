# TaskBench

**Cost-Quality Tradeoffs Across Production LLM Tasks**

A benchmark measuring LLM cost vs quality across 21 production tasks and 47 models from 9 API providers. For each task, we identify which model delivers acceptable quality at the lowest cost.

## Scale

- **47 complete models** (21/21 tasks, >=40 cases each) + 9 partial
- **21 production tasks** (50 cases each): sentiment, intent, reasoning, moderation, translation, SQL, NER, function calling, code generation, code review, test generation, RAG QA, instruction following, structured output, and more
- **9 API providers**: Anthropic, OpenAI, Google, Mistral, MiniMax, Moonshot, BytePlus, OpenRouter, Azure
- **51,617 data points** in the CSV (51,705 raw response files)

## How It Works

A custom Python runner (`scripts/run_batch.py`) sends each test case to each model, records the response, and scores it using either exact-match (classification tasks) or an LLM judge (generative tasks). Cost per query is computed from token usage and hardcoded per-model pricing.

```bash
# Run a single task across all models
python3 scripts/run_batch.py --task sentiment_sst2 --skip-azure

# Rebuild CSV from raw JSON files (source of truth)
python3 scripts/rebuild_csv.py

# Generate analysis (Pareto plots, heatmaps)
python3 scripts/analyze_costs.py results/
```

## Project Structure

```
benchmark/
  datasets/                        # Input data (JSONL, one file per task)
  results/
    benchmark_results.csv          # All results (51,617 rows)
    spend_tracker.json             # Cumulative spend ($143.81)
    rejudge_log.jsonl              # Rejudge audit trail (6,170 entries)
    raw/                           # Per-case JSON with full response text (51,705 files)
    figures/                       # Generated plots
  scripts/
    run_batch.py                   # V2 runner (production)
    run_full_benchmark.py          # V1 runner (legacy, reference only)
    rebuild_csv.py                 # Rebuild CSV from raw JSON source of truth
    re_judge_failed_scores.py      # Re-judge script for fixing scoring errors
    analyze_costs.py               # Pareto plots, heatmaps, report generation
```

## Key Findings

1. Economy models ($0.10-0.15/M) match premium models ($5-15/M) on 12 of 16 task types
2. No single model wins everywhere -- the cheapest adequate model changes by task
3. Premium models are paradoxically worse on some simple tasks (overthinking)
4. The cost-quality curve has brutal diminishing returns above the Economy tier
5. A 3B-parameter model (Ministral-3B at $0.04/M) matches GPT-4o on basic reasoning

See FINDINGS.md for the complete list with evidence.

## Documentation

| File | Contents |
|------|----------|
| FINDINGS.md | All benchmark findings with evidence and stability ratings |
| METHODOLOGY.md | Every methodological decision, design rationale, reproducibility checklist |
| LIMITATIONS.md | 14 known limitations with honest impact assessments |
| LEARNINGS.md | Operational lessons learned (bugs, fixes, patterns) |
| QUESTIONS.md | Scope guard -- 15 questions the benchmark answers |
| RELATED_WORK.md | Positioning vs MMLU, LMSYS, RouterArena, FrugalGPT, etc. |
| SESSION_NOTES.md | Per-session operational notes |
| DATA_QUALITY_CHECK.md | Data quality verification |
| FINAL_VERIFICATION.md | Post-cleanup verification report |
| STATE_RECONCILIATION.md | Cross-document consistency audit |

## Budget

$143.81 tracked spend (61,594 API calls) of $250 hard cap. Real OpenAI spend was ~$180+ due to reasoning tokens not tracked by the spend tracker. See LIMITATIONS.md section 14.
