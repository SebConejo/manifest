# Judge V2 Full Results

**Date:** 2026-05-15
**Scope:** 35,562 cases re-judged across 15 generative tasks + 4,788 from
the initial validation (reasoning_gsm8k, rag_qa). Total: 40,350 cases.
**Judge:** GPT-4o, correctness-focused V2 prompts. 0 errors.

---

## 1. Score Distribution: V1 vs V2

| Task | V1 avg | V2 avg | Delta | Direction |
|:-----|:------:|:------:|:-----:|:---------:|
| test_generation_v2 | 4.20 | 4.71 | **+0.50** | V1 under-scored |
| code_review_v2 | 4.45 | 4.89 | **+0.44** | V1 under-scored |
| extraction_hard_v2 | 4.44 | 4.86 | **+0.42** | V1 under-scored |
| code_generation | 4.24 | 4.65 | **+0.40** | V1 under-scored |
| instruction_following | 4.38 | 4.78 | **+0.39** | V1 under-scored |
| json_transform_v2 | 4.44 | 4.72 | +0.28 | V1 under-scored |
| translation_enfr | 4.56 | 4.82 | +0.26 | V1 under-scored |
| function_calling | 4.42 | 4.62 | +0.20 | V1 under-scored |
| reasoning_gsm8k | 4.64 | 4.84 | +0.20 | V1 under-scored |
| ner_extraction | 4.50 | 4.60 | +0.11 | V1 under-scored |
| structured_output | 4.86 | 4.97 | +0.11 | V1 under-scored |
| rag_qa | 4.23 | 4.31 | +0.07 | Stable |
| code_explanation | 4.91 | 4.94 | +0.03 | Stable |
| data_to_text | 4.98 | 4.94 | -0.03 | Stable |
| email_summary_v2 | 4.94 | 4.86 | -0.07 | Slight V2 stricter |
| sql_spider | 4.48 | 4.40 | -0.08 | Slight V2 stricter |
| long_summarization | 4.94 | 4.56 | **-0.38** | V2 stricter |

### Pattern

V2 scores are **higher** on tasks where V1 penalized format (test_gen +0.50,
code_review +0.44, extraction +0.42). These tasks produce long, structured
output where format diversity is high. V1 punished non-standard formats.

V2 scores are **lower** on long_summarization (-0.38) and slightly on
email_summary (-0.07) and SQL (-0.08). The V2 "factual completeness" rubric
is stricter than V1's "good summary" rubric — V2 checks if specific facts
are present, V1 rewarded general coherence.

---

## 2. Models That Move Most

### Biggest risers (V2 > V1)

| Model | V1 avg | V2 avg | Delta | Why |
|:------|:------:|:------:|:-----:|:----|
| bytedance-seed/seed-2.0-mini | 4.50 | 4.85 | +0.36 | Non-standard format was penalized by V1 |
| bytedance-seed/seed-2.0-lite | 4.51 | 4.84 | +0.33 | Same |
| claude-opus-4-7 | 4.48 | 4.79 | +0.31 | Verbose reasoning penalized by V1 |
| bytedance-seed/seed-1.6-flash | 4.52 | 4.83 | +0.31 | Format bias |
| x-ai/grok-4-fast | 4.53 | 4.84 | +0.31 | Format bias |
| gemini-2.0-flash | 4.51 | 4.81 | +0.30 | Format bias |
| gemini-2.5-pro | 4.46 | 4.72 | +0.26 | Verbose reasoning penalized by V1 |

**Pattern:** ByteDance Seed models and reasoning models (Opus, Gemini Pro)
rise the most. These models produce correct but non-standard output that V1
penalized.

### Biggest fallers (V2 < V1)

| Model | V1 avg | V2 avg | Delta | Why |
|:------|:------:|:------:|:-----:|:----|
| meta-llama/llama-3.2-1b-instruct | 3.71 | 3.46 | -0.25 | V1 was lenient on short wrong answers |
| meta-llama/llama-3.2-3b-instruct | 4.41 | 4.31 | -0.09 | Same |

**Pattern:** Only the smallest models fall. V1 gave them credit for
producing well-formatted wrong answers. V2 evaluates correctness more
strictly.

Note: almost all models RISE. The median delta is +0.20. V1 was
systematically harsher than V2 because format penalties dominated
correctness evaluation.

---

## 3. Impact on Key Findings

### F1 (Economy = Premium)

V2 moves **both** tiers up, but Premium rises more (+0.31 for Opus) than
Economy average (+0.15). This NARROWS the gap slightly but does not reverse
the finding. Economy is still within 0.3 points of Premium.

### F4 (Qwen Turbo best default)

Qwen Turbo: V1=4.66 → V2=4.70 (+0.04). Minimal change. Still among the
best defaults. But ByteDance Seed models now score higher (4.83-4.85)
and may challenge for the top spot.

### F6 (RAG QA hardest)

RAG QA V2 avg=4.31 (was 4.23). The task is still discriminative but less
"hard" than V1 suggested. long_summarization (V2=4.56, was 4.94) is now
lower — V2 is stricter on factual completeness for summaries.

### New pattern: test_generation_v2 was the most under-scored task

The biggest V1→V2 jump is test_generation_v2 (+0.50). V1 gave 70% of cases
score 4 (the "good but not great" zone). V2 gives 75% score 5. The V1
judge was penalizing test style/naming rather than evaluating coverage.

---

## 4. Next Steps

1. **Rebuild CSV** with V2 scores as the primary score column
2. **Recompute all analyses** (Pareto, heatmap, tier comparison, etc.)
3. **Reformulate findings** based on V2 scores
4. **Document dual-judge methodology** in the paper
