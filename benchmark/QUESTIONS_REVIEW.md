# Questions Review

**Date:** 2026-05-15
**Purpose:** Audit the 15 original scope-guard questions against actual data
and findings after the V2 judge correction.

---

## Original 15 Questions: Status

| # | Question | Status | Finding | Confidence | Gap |
|---|---------|:------:|---------|:----------:|-----|
| Q1 | Best model per task at lowest cost? | **ANSWERED** | Pareto frontiers (21 tasks), top-5 tables | HIGH | Paretos need regenerating with V2 scores (only RAG QA v8 style exists) |
| Q2 | Economy match Premium on simple tasks? | **ANSWERED** | F1: no significant gap (MW p>0.05, 21/21) | MODERATE | n=2 Premium caveat. Need to split "simple" vs "all" more clearly |
| Q3 | Reasoning models justify cost? | **PARTIALLY** | Data exists but no dedicated analysis | LOW | Need: reasoning-tier cost-per-correct on GSM8K/RAG QA with V2 scores. Is o3 at $0.003/query worth it vs gpt-4o-mini at $0.00003? |
| Q4 | Provider quality gradient? | **NOT COMPUTED** | Data exists (OpenAI 10 models, Qwen 7, Mistral 5) | — | Need: per-provider price-vs-quality curve. Not in any findings file. |
| Q5 | Same tier, which model wins? | **PARTIALLY** | top5_per_task.json has rankings | MODERATE | Need: explicit within-tier comparison table. Currently mixed across tiers. |
| Q6 | Commodity vs discriminative tasks? | **ANSWERED** | F3: 10 high, 9 medium, 2 low discrimination | HIGH | V2 changed the split (more tasks now discriminative). Update in findings. |
| Q7 | Cost per correct answer? | **PARTIALLY** | cost_per_correct.json computed on V1 scores | LOW | Need to recompute on V2 scores for LLM-judged tasks. Exact-match unchanged. |
| Q8 | Quality floor (min viable model)? | **ANSWERED** | F5: Llama 1B at 3.46/5 is only model below 4.0 | LOW | n=1 at 1B. Observation, not finding. |
| Q9 | Chinese vs American competitive? | **NOT COMPUTED** | Data exists (13 Chinese, ~15 American) | — | Need: boxplot or table of avg scores by origin, per task. |
| Q10 | Open vs closed competitive? | **NOT COMPUTED** | Data exists | — | Need: same analysis by license type. |
| Q11 | 2026 gen vs 2024 gen? | **NOT COMPUTED** | 4 comparable pairs exist | — | Need: before/after comparison (gpt-4o vs 5.4, etc.) |
| Q12 | Optimal 3-4 model routing set? | **NOT COMPUTED** | routing_savings.json has single vs routed cost | — | Need: coverage matrix. "Pick Qwen Turbo + Devstral + o3 = covers all 21 tasks at what total cost?" |
| Q13 | Top 5 models per use case? | **ANSWERED** | top5_per_task.json, top5_per_task.md | HIGH | Already computed. Needs V2 recompute (done in v3). |
| Q14 | Routing saves money? | **ANSWERED** | F2: 70% savings (vs realistic baseline) | HIGH | Sensitivity analysis at different thresholds still needed. |
| Q15 | Where does routing add most value? | **PARTIALLY** | Implied by F3 (discriminative tasks) | MODERATE | Need explicit: routing savings PER TASK, not just aggregate. |

### Summary

| Status | Count | Questions |
|--------|:-----:|-----------|
| Fully answered | 5 | Q1, Q2, Q6, Q13, Q14 |
| Partially answered | 4 | Q3, Q5, Q7, Q15 |
| Not computed | 5 | Q4, Q9, Q10, Q11, Q12 |
| Answered but weak | 1 | Q8 |

**5 of 15 questions have no analysis at all.** These are all analyses we said
we could do (the data exists) but never actually computed.

---

## Analysis: What's Missing and How Hard to Fix

### Easy to compute (< 30 min each, no new data needed)

**Q4: Provider quality gradient.** For OpenAI (10 models), Qwen (7), Mistral (5),
Anthropic (4), Google (3): plot avg V2 score vs input price per model, one line
per provider. Shows whether paying more within a provider buys quality.

**Q9: Chinese vs American.** Group models by origin. Boxplot of avg V2 scores.
Mann-Whitney test. Chinese: Qwen (7), DeepSeek (2), ByteDance (3), Kimi (1),
MiniMax (1) = 14. American: OpenAI (10), Anthropic (4), Google (3), Mistral (5),
xAI (3) = 25. Meta (2) is American. Google (3) is American.

**Q10: Open vs Closed.** Open-weight: Llama (3), DeepSeek (2), Qwen (7), Gemma (1),
Phi (1), Nemotron (1), Ministral (1) = 16. Closed: GPT (10), Claude (4), Gemini (3),
Grok (3), MiniMax (1), Kimi (1), Mistral-large/medium (2), Seed (3), Devstral (1) = 28.
Some classifications are debatable (Qwen, DeepSeek: open weights but closed training).

**Q11: Generational delta.** 4 pairs: gpt-4o→5.4 (same tier), gpt-4o-mini→5.4-mini,
Sonnet 4→4.6, DeepSeek V3.2→V4 Pro. Plot before/after per task.

**Q15: Per-task routing savings.** For each task: cost of cheapest adequate (>=4.0)
vs cost of best single model on that task. Shows which tasks drive the 70% savings.

### Medium effort (1-2 hours)

**Q3: Reasoning model ROI.** Compute cost-per-correct on GSM8K and RAG QA (where
we have ground truth + V2 judge) for reasoning vs non-reasoning models. Is o3's
$0.003/query justified by higher accuracy?

**Q7: Cost-per-correct with V2.** Recompute for LLM-judged tasks using V2 scores.
Define "correct" = score >= 4 (V2 judge). Compare across tiers.

**Q12: Coverage matrix.** Greedy set cover: what's the smallest set of models that
achieves >= 4.5/5 on all 21 tasks? What's the total cost? This is the "recommended
routing configuration."

---

## New Questions from the Judge Bias Discovery

The V1→V2 judge transition opens questions nobody has asked before:

### NQ1: How much does judge methodology affect benchmark rankings?

We can now compute: how many model rankings flip between V1 and V2?
If model A > model B under V1 but B > A under V2, that's a ranking flip.
Count flips across all task × model-pair combinations.

**Why it matters:** If judge choice changes 20%+ of rankings, all existing
LLM-as-judge benchmarks (MT-Bench, AlpacaEval, WildBench) may have systematic
errors. This is a finding about the field, not just our benchmark.

### NQ2: Does format bias correlate with model verbosity?

For each model, compute: avg response length (chars) and V1→V2 delta.
If verbose models systematically rose in V2, verbosity IS the confound.
Plot it.

**Why it matters:** Confirms the mechanism. Turns an observation into a
quantified, reproducible finding.

### NQ3: Would a different judge model produce different results?

We have V1 (GPT-4o-mini) and V2 (GPT-4o) with different prompts. We can't
separate the model effect from the prompt effect. But we CAN note that the
prompt change alone on the same model (GPT-4o-mini with V2 prompts) would
be an interesting experiment. Not doing it now, but noting for future work.

---

## Questions NOT Worth Answering

**Q8 (quality floor at 1B):** n=1, can't be strengthened without more sub-3B
models. Keep as observation, don't promote to finding.

**Q9/Q10 (Chinese vs American / Open vs Closed):** Answerable but adds
geopolitical framing that draws attacks (see FINDINGS_CRITIQUE.md F7).
Compute the analysis (it takes 10 min) but present neutrally: "models from
diverse providers are competitive" rather than "Chinese dominate."

---

## Recommendation: Compute the 5 Missing + 2 New Before Writing

| Analysis | Question | Effort | Paper section |
|----------|---------|--------|---------------|
| Provider gradient | Q4 | 20 min | Results 4.x or Appendix |
| Chinese vs American | Q9 | 10 min | Appendix (neutral framing) |
| Open vs Closed | Q10 | 10 min | Appendix |
| Generational delta | Q11 | 20 min | Results 4.x or Appendix |
| Coverage matrix | Q12 | 30 min | Discussion 5.1 |
| Per-task routing savings | Q15 | 15 min | Results 4.5 |
| Ranking flip count (NQ1) | NEW | 30 min | Methodology 3.4 (judge bias) |
| Verbosity correlation (NQ2) | NEW | 15 min | Methodology 3.4 |

**Total: ~2.5 hours of computation.** All use existing data, no new API calls.

Once computed, ALL 15 original questions + 2 new ones will have answers.
Then we can finalize the outline with confidence that the paper covers
everything we set out to answer.
