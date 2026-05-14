# Analysis Plan

**Date:** 2026-05-14
**Status:** Pareto v8 template validated on RAG QA. Pending propagation and remaining analyses.

---

## 1. What's Done

| Deliverable | Status | Files |
|------------|--------|-------|
| Task-model aggregates | Done | `task_model_aggregates.json` |
| Pareto frontiers (21 tasks) | 1/21 (RAG QA v8 validated) | `pareto_rag_qa_v8.svg` |
| Heatmap (model x task) | Draft v2 (needs review) | `heatmap_model_task_v2.svg` |
| Top 5 per task | Done | `top5_per_task.json`, `top5_per_task.md` |
| Tier comparison | Done | `tier_comparison.svg`, `tier_comparison.json` |
| Task discriminativeness | Done | `task_discriminativeness.svg`, `task_discriminativeness.json` |
| Cost-per-correct (exact-match) | Done | `cost_per_correct.json` |
| Routing savings | Done | `routing_savings.json` |
| FINAL_FINDINGS.md | Draft (7 findings) | `FINAL_FINDINGS.md` |

## 2. What Remains

### 2a. Propagate Pareto v8 template to 20 remaining tasks

Same dual-panel layout. For each task, hardcode 3-5 labels on the most
informative models. This requires looking at each task's data to pick:
- Pareto winner (cheapest at top quality)
- Worst model (bottom of the chart)
- 1 interesting outlier per panel

Estimated work: ~1 hour (generate, pick labels per task, verify).

### 2b. Heatmap publication-ready

Current v2 heatmap has 48 models x 21 tasks with score text in each cell.
Needs review for:
- Readability of 5-point font scores
- Color scale clarity (red-yellow-green)
- Model ordering (currently by avg score; could group by tier)
- Whether to include partial models or only the 46 complete

### 2c. Paper figures selection

Not all 21 Paretos go in the paper. Select 4-6 representative ones:
- 1 high-discrimination (RAG QA or intent_clinc150)
- 1 medium-discrimination (code_review or translation)
- 1 commodity (data_to_text or long_summarization)
- 1 exact-match (moderation_toxigen or sentiment_sst2)
- The heatmap (overview)
- Routing savings bar chart (if we make one)

The rest go in an appendix or supplementary material.

### 2d. Additional analyses not yet generated

| Analysis | What it answers | Priority |
|----------|----------------|----------|
| Per-provider quality curve | Q4: within one provider, quality gradient cheap→expensive | Medium |
| Chinese vs American boxplot | Q9: are Chinese-origin models competitive? | Medium |
| Open vs closed boxplot | Q10: are open-weight models competitive? | Low |
| Generational delta (GPT-4o vs 5.4) | Q11: does 2026 gen improve over 2024? | Medium |
| Coverage matrix | Q12: which 3-4 models cover all tasks? | High |
| Routing savings bar chart | Q14: visual version of the 86% finding | High |

### 2e. FINAL_FINDINGS.md revision

Current draft has 7 findings. After all analyses complete, revise:
- Validate each finding against final data
- Add evidence from new analyses (provider curves, generational delta)
- Sharpen confidence ratings
- Add 1-2 findings if new analyses reveal something

---

## 3. Preliminary Findings (what the data already shows)

### Finding 1: Economy = Premium (HIGH confidence)

Economy tier achieves 97-105% of Premium quality across all 21 tasks.
On 7 tasks, Economy actually outperforms Premium. The gap is never more
than 6% in Premium's favor. This is the central finding of the paper.

Evidence: tier_comparison.json — every task computed.

### Finding 2: Routing saves 86% (HIGH confidence)

Cheapest adequate model (score >= 4.0) per task costs $0.000009/query.
Best single model (Devstral, 4.75/5) costs $0.000063/query. Delta: 86%.

Evidence: routing_savings.json.

Caveat: this uses our CSV cost_usd which underestimates reasoning model
costs. The real saving % might be different if we use corrected prices.
But the structural finding (routing is cheaper) holds regardless.

### Finding 3: 7 discriminative vs 5 commodity tasks (HIGH confidence)

Score spread ranges from 0.49 (structured_output) to 3.20 (intent_clinc150).
On commodity tasks, any model works. On discriminative tasks, model choice
is the difference between 1.5/5 and 4.7/5.

Evidence: task_discriminativeness.json.

### Finding 4: Qwen Turbo = best default model (HIGH confidence)

$0.05/M input, 4.62/5 avg across 21 tasks, $0.00001/query. Cheapest
model that never scores below 4.0 on any task. The "if you don't know
what model to use, use this one" answer.

### Finding 5: 1B parameter cliff (HIGH confidence)

Llama-3.2-1B is the only model averaging below 4.0 (3.60/5). The jump
from 1B to 3B doubles quality on classification tasks. Below 3B, models
are unreliable for production use.

### Finding 6: RAG QA is the hardest task (HIGH confidence)

Spread 2.48, many strong models fail. Tests whether models hallucinate
vs answer strictly from context. Most discriminative generative task.

### Finding 7: Chinese models dominate Pareto (MEDIUM confidence)

Qwen, DeepSeek, and ByteDance Seed models appear consistently on or near
the Pareto frontier. MEDIUM because we have fewer Chinese models at the
Premium tier, so the comparison is not symmetric.

### Potential additional findings (to verify)

- GPT-5.4 Nano beats GPT-4o-mini on hard tasks (generational leap)
- Reasoning models are overkill for classification (thinking tax)
- Devstral (Mistral coding model) is the best single all-round model
- Content moderation has the most surprising results (Premium worst)

---

## 4. Methodological Assumptions

These are choices we made that affect results. Each should be stated
in the paper's methodology section.

### 4a. Inclusion threshold: >= 40 cases per task

A model needs >= 40 valid (non-empty) cases on a task to be included
in the analysis for that task. This excludes models with too much
missing data to be statistically meaningful.

Why 40 and not 50: Two tasks have fewer than 50 cases in the dataset
(code_explanation: 48, structured_output: 41). Setting the threshold
at 50 would exclude all models from structured_output. 40 is the
highest threshold that includes all tasks.

Impact: 46 models qualify on 21/21 tasks. 2 more qualify on 19-20.
The remaining 8 are Azure legacy doublons with 1-2 tasks.

### 4b. LLM judge: GPT-4o-mini

All generative tasks scored by GPT-4o-mini on a 1-5 scale with
task-specific rubrics. Temperature 0.

Known bias: may favor GPT-family output style. We document this as
a limitation. The dual-metric validation on 4 exact-match tasks shows
judge scores correlate with native accuracy, but diverge on verbose
reasoning (Opus gets 98% accuracy but 3.5/5 from judge on GSM8K).

Cost: ~$0.0001/call, total ~$4 for all judge calls.

Alternative considered: Claude Haiku as second judge. Not done due to
budget. Could be added as a robustness check for ~$2.

### 4c. Scoring scale: 1-5

Not 1-10 or 1-100. LLMs cluster around round numbers on fine-grained
scales, making extra precision illusory. 1-5 with clear anchors
(1=fail, 3=acceptable, 5=perfect) produces consistent ratings.

Exact-match tasks use binary scoring: 5 if correct, 0 if wrong. This
creates a bimodal distribution on classification tasks (all 0 or 5).

### 4d. Cost measurement: hardcoded prices

Per-query cost computed from token counts * hardcoded $/M prices.
Prices set at benchmark time (April-May 2026).

CRITICAL CAVEAT: reasoning model costs are underestimated 3-10x in
the CSV. GPT-5.5 Pro, o3, o4-mini consume invisible thinking tokens
charged by OpenAI but not reflected in completion_tokens. The paper
must either:
- (A) Use corrected prices for reasoning models (from provider billing)
- (B) Document this as a limitation and note that reasoning model
  cost_usd values are lower bounds
- (C) Exclude reasoning models from cost comparisons

Recommendation: option (B). The structural findings (Economy vs Premium)
still hold because reasoning models are all in the Standard/Premium tier.

### 4e. Temperature: 0 for all models that support it

Makes results deterministic and reproducible. Exception: reasoning models
that reject temperature=0 (DeepSeek-R1, Kimi K2.6, Opus 4.7). Their
outputs have run-to-run variance.

### 4f. Token budget: 8192 for reasoning models

effective_max_tokens returns max(requested, 8192) for models in
REASONING_MODELS. Non-reasoning models get the task's native max
(20-1000 tokens). This gives reasoning models room for invisible
thinking tokens.

### 4g. Provider diversity vs comparability

Models are accessed via 9 different API providers. The same model
weights accessed via different providers (e.g., DeepSeek via OpenRouter
vs Azure) may produce slightly different results due to infrastructure
differences. We use one provider per model and document which.

### 4h. 50 cases per task

95% CI of approximately +/-0.2 on the 1-5 scale. Sufficient for
1+ point gaps (Economy vs Micro), marginal for 0.3-point within-tier
differences. The paper should avoid claims about differences smaller
than 0.3 points.

---

## 5. Execution Order

1. Validate this plan (you are here)
2. Propagate Pareto v8 to 20 tasks (hardcoded labels per task)
3. Review and finalize heatmap
4. Generate remaining analyses (provider curves, routing bar chart, coverage matrix)
5. Revise FINAL_FINDINGS.md with all evidence
6. Select 4-6 paper figures
7. Write the paper

Each step needs explicit validation before moving to the next.
