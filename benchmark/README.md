# TaskBench

**Cost-Quality Tradeoffs Across Production LLM Tasks**

A benchmark measuring LLM cost vs quality across 21 production tasks and 46 complete models from 9 API providers. Includes a validated correctness-focused LLM judge (r=0.89-0.91 vs ground truth on 3 task types).

## Scale

- **46 complete models** (21/21 tasks, >=40 cases each) + 10 partial
- **21 production tasks** (50 cases each): sentiment, intent, reasoning, moderation, translation, SQL, NER, function calling, code generation, code review, test generation, RAG QA, instruction following, structured output, and more
- **9 API providers**: Anthropic, OpenAI, Google, Mistral, MiniMax, Moonshot, BytePlus, OpenRouter, Azure
- **51,580 data points** in the CSV (51,705 raw response files)
- **V2 judge**: GPT-4o with correctness-focused rubrics, validated on GSM8K (r=0.905), RAG QA (r=0.887), and HumanEval (r=0.891)

## How to Reproduce

### Prerequisites

```bash
pip install -r requirements.txt
# Only needed to re-run the benchmark (not for analysis):
cp .env.example .env  # Fill in API keys
```

### Reproduce analyses from existing data

```bash
# Rebuild CSV from raw JSON files (source of truth)
python3 scripts/rebuild_csv.py

# Run all V3 analyses (generates 15+ JSON files)
python3 scripts/analyze_v3.py

# Generate all figures
python3 scripts/generate_figures.py

# Validate judge on code generation (HumanEval pass@1)
python3 -c "from scripts.humaneval_harness import evaluate_case; print('Harness OK')"
```

### Re-run the benchmark (requires API keys + budget)

```bash
# Run a single task across all models
python3 scripts/run_batch.py --task sentiment_sst2 --skip-azure

# Re-judge with V2 prompts (requires OpenAI key, ~$60)
python3 scripts/rejudge_v2_full.py
```

## Project Structure

```
benchmark/
  datasets/                        # Input data (JSONL, one file per task)
  results/
    benchmark_results.csv          # All results, V2 judge scores (51,580 rows)
    benchmark_results_v1_judge.csv.bak  # V1 judge scores backup
    spend_tracker.json             # Cumulative spend
    rejudge_log.jsonl              # Rejudge audit trail (6,170 entries)
    rejudge_v2_log.jsonl           # V2 judge log (4,788 validation cases)
    rejudge_v2_full_log.jsonl      # V2 judge log (35,562 full re-judge)
    raw/                           # Per-case JSON with full response text (51,705 files)
    analysis_v3_final/             # All analysis outputs (JSON + SVG)
  scripts/
    run_batch.py                   # Benchmark runner
    rebuild_csv.py                 # Rebuild CSV from raw JSON source of truth
    analyze_v3.py                  # V3 analysis pipeline (all 15 analyses)
    generate_figures.py            # Figure generation (all 10+ figures)
    humaneval_harness.py           # Code generation pass@1 evaluation
    rejudge_v2.py                  # V2 re-judge (2 validation tasks)
    rejudge_v2_full.py             # V2 re-judge (15 remaining tasks)
    re_judge_failed_scores.py      # Legacy: fix V1 judge crash zeros
    analyze_costs.py               # Legacy: V1 analysis
    run_full_benchmark.py          # Legacy: V1 runner (reference only)
```

## Key Findings (V3, with validated V2 judge)

1. No significant quality gap between Economy and Premium tiers (Mann-Whitney p>0.05 on 21/21 tasks)
2. Per-task routing saves 70-99% vs using a single model
3. Standard LLM-as-judge has severe format bias (r=0.35 vs ground truth); correctness-focused rubrics fix it (r=0.90)
4. Within-provider quality gradient is nearly flat (paying 750x more buys +0.13 quality)
5. New model generations are cheaper at equal or better quality (GPT-4o → GPT-5.4: -60% price)
6. Provider origin (Chinese/American/European) does not predict quality (p=0.40)

See `results/analysis_v3_final/FINAL_FINDINGS_v3.md` for the complete list.

## Documentation

| File | Contents |
|------|----------|
| METHODOLOGY.md | Every methodological decision, design rationale, reproducibility checklist |
| FINDINGS_COHERENCE_REVIEW.md | 17 findings with coherence analysis |
| FINDINGS_CRITIQUE_v2.md | Adversarial self-review (9 solid, 5 moderate, 3 fragile) |
| JUDGE_PROMPTS_V2.md | V2 judge rubrics for all 17 LLM-judged tasks |
| JUDGE_V2_VALIDATION_EXTENDED.md | Judge validation across 4 task types |
| PARETO_STYLE_GUIDE.md | Visual style spec for paper figures |
| PAPER_STRATEGY.md | Paper writing strategy (title, structure, venue) |
| PAPER_OUTLINE.md | Detailed paper outline |
| LIMITATIONS.md | 14 known limitations with honest impact assessments |
| LEARNINGS.md | 19 operational lessons (bugs, fixes, patterns) |
| QUESTIONS.md | Scope guard — 15 questions the benchmark answers |

## Budget

$143.81 tracked spend (61,594 API calls) of $250 hard cap. Real OpenAI spend was ~$180+ due to reasoning tokens not tracked. See LIMITATIONS.md section 14.
