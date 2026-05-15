# Analyses Plan v2

**Date:** 2026-05-15
**Purpose:** Precise spec for each missing analysis before execution.

---

## Q4: Provider Quality Gradient

**What:** For each provider (OpenAI, Anthropic, Mistral, Qwen, Google), plot
the quality gradient from cheapest to most expensive model. X = input price/M,
Y = avg V2 score across 21 tasks. One line per provider.

**CSV fields:** model, score (V2). Price from MODEL_PRICES dict (not CSV column
— CSV has per-row prices that vary by task due to corrections).

**Output:** `provider_gradient.svg` + `provider_gradient.json`. One figure with
5 lines (one per provider). Shows whether paying more within a provider buys
quality.

**Time estimate:** 30 min (data prep 10 min, figure 15 min, manual label placement 5 min).

**Risk of revealing problems:** LOW. The data is clean. Possible surprise: a
provider's expensive model might score LOWER than its cheap model on V2
(e.g., if the expensive model is a reasoning model that V2 scores differently).
Not a data problem — a finding.

**Priority: NICE-TO-HAVE.** Interesting for the paper but doesn't affect any
core finding. Goes in appendix or discussion.

---

## Q9: Chinese vs American

**What:** Group models by country of origin. Compare avg V2 scores and avg
cost per query. Mann-Whitney test for quality difference.

**Classification criteria:**

| Origin | Models | Count |
|--------|--------|:-----:|
| Chinese | qwen/* (7), deepseek/* (2), bytedance-seed/* (3), kimi-k2.6 (1), MiniMax-M2.7 (1), seed-2-0-* (2) | 16 |
| American | gpt-* (10), claude-* (4), gemini-* (3), o3 (1), o4-mini (1), mistral-* (5), devstral (1), x-ai/* (3) | 28 |
| Other | meta-llama/* (3, American but open-weight from Meta), google/gemma (1), microsoft/phi (1), nvidia/nemotron (1) | 6 |

**Debatable:** Mistral is French, not American. Meta's Llama is American but
open-weight. Google's Gemma is American but open-weight. I'll use:
- "Western" (US + EU): OpenAI, Anthropic, Google, Mistral, xAI, Meta, Microsoft, NVIDIA = 32
- "Chinese": Qwen, DeepSeek, ByteDance, Kimi, MiniMax = 16

No — this is getting political. Better framing:
- "Direct-API providers" (models accessed via their own API): OpenAI, Anthropic, Google, Mistral, MiniMax, Moonshot, BytePlus
- "OpenRouter-only" (models accessed via OpenRouter): Qwen, DeepSeek, Llama, Grok, Gemma, Phi, Nemotron, ByteDance Seed

Actually that's confusing too. Simplest: **compare by provider** (Q4 already does this)
and skip the geopolitical framing entirely. If a reviewer asks "are Chinese models
competitive?", we point to Q4 (Qwen line is competitive with OpenAI line).

**CSV fields:** model, score (V2).

**Output:** `origin_comparison.json`. Table of avg score by origin group.
Skip the figure — the provider gradient (Q4) is more informative.

**Time estimate:** 15 min.

**Risk:** MEDIUM. The classification is debatable and invites attacks (see
FINDINGS_CRITIQUE F7). Any framing we choose will be wrong for someone.

**Priority: LOW.** Nice to have the numbers but don't put in the main paper.
Appendix table at most. The provider gradient (Q4) tells the same story
without the geopolitical framing.

---

## Q10: Open vs Closed

**What:** Group models by weight availability. Compare avg V2 scores.

**Classification:**

| Type | Models | Count |
|------|--------|:-----:|
| Open weights | llama-3.2-1b, llama-3.2-3b, llama-4-maverick, deepseek-v3.2, deepseek-v4-pro, qwen/* (7), gemma-4, phi-4, nemotron, ministral-3b | 17 |
| Closed | gpt-* (10), claude-* (4), gemini-* (3), o3, o4-mini, mistral-large, mistral-medium, devstral, grok-* (3), MiniMax, kimi, seed-* (3) | 30 |

**Debatable:** Devstral — open weight? Mistral Small — open? Qwen — open weights
but closed training data. DeepSeek — open weights. This classification is
messy and provider-dependent.

**CSV fields:** model, score (V2).

**Output:** `open_vs_closed.json`. Table + Mann-Whitney test.

**Time estimate:** 15 min.

**Risk:** LOW for data issues. MEDIUM for classification debates.

**Priority: LOW.** Same issue as Q9 — the classification is debatable.
Compute the numbers, put in appendix if interesting.

---

## Q11: Generational Delta

**What:** For 4 model pairs (same provider, different generation), compute
the V2 score delta per task. Shows whether upgrading generation matters.

**Pairs:**
1. GPT-4o (2024, $2.50/M) → GPT-5.4 (2026, $1.00/M) — newer AND cheaper
2. GPT-4o-mini (2024, $0.15/M) → GPT-5.4-mini (2026, $0.10/M) — newer AND cheaper
3. Claude Sonnet 4 (2025) → Claude Sonnet 4.6 (2026) — same price
4. DeepSeek V3.2 (2025) → DeepSeek V4 Pro (2026) — newer but more expensive

All 4 pairs have 21/21 tasks in V3 data. The comparison is: per-task V2 score
of old model vs new model.

**CSV fields:** model, task, score (V2).

**Output:** `generational_delta.json` + `generational_delta.svg` (4 small bar
charts or a table). For each pair: avg delta across 21 tasks, tasks where new
model wins vs loses.

**Time estimate:** 25 min.

**Risk:** LOW. The data exists and is clean. Possible surprise: Sonnet 4→4.6
might show zero improvement (they're very similar models). That's a finding,
not a problem.

**Priority: MEDIUM.** Interesting for the paper narrative ("is upgrading worth
it?"). Goes in Results or Appendix.

---

## Q12: Coverage Matrix (Optimal Routing Set)

**What:** Find the smallest set of models that achieves >= 4.5/5 on all 21
tasks at the lowest total cost. This is the "recommended routing configuration."

**Algorithm:** Greedy set cover. For each task, list models with score >= 4.5.
Pick the model that covers the most uncovered tasks at the lowest cost. Repeat
until all 21 tasks are covered.

**CSV fields:** task, model, score (V2), cost_usd.

**Output:** `coverage_matrix.json`. The optimal set (expected: 2-4 models),
total cost per query, which model handles which tasks.

**Time estimate:** 30 min (algorithm + verification).

**Risk:** LOW for data issues. The result might be "1 model covers everything"
(if Devstral or Qwen Turbo scores >= 4.5 on all 21 tasks), which would make
the analysis trivial. In that case the finding is: "you don't even need
routing — one Economy model handles everything."

**Priority: HIGH.** This is the most actionable output for practitioners.
Goes in Discussion 5.1.

---

## Q15: Per-Task Routing Savings

**What:** For each task separately: what's the cost of the cheapest adequate
model (>= 4.0) vs the cost of the best single model (o3). Shows which tasks
drive the aggregate 70% savings.

**CSV fields:** task, model, score (V2), cost_usd.

**Output:** `per_task_routing_savings.json` + figure. Bar chart: 21 tasks,
each bar = savings % from routing on that task.

**Time estimate:** 20 min.

**Risk:** LOW. Straightforward computation.

**Priority: HIGH.** Answers "where does routing help most?" Directly feeds
into Discussion 5.1 and strengthens F2 (routing saves money).

---

## NQ1: Ranking Flips V1→V2

**What:** For each task, count how many model-pair rankings flip between V1
and V2 judge scores. If model A > model B under V1 but B > A under V2, that's
a flip. Report: total flips / total pairs, and which models flip most.

**Data source:** Raw JSON files. Each file has both `score` (V1) and
`judge_v2_score` (V2) for LLM-judged tasks. Compute per-model avg under V1
and V2, then count pairwise flips.

**Output:** `ranking_flips.json`. Total flip rate (e.g., "18% of model-pair
rankings changed"), top flipping models, tasks with most flips.

**Time estimate:** 30 min (need to read all raw files, compute per-model avgs
under both judges, count flips).

**Risk:** MEDIUM. If flip rate is > 30%, it means our V1 findings were deeply
wrong — and by extension, all other benchmarks using generic LLM judges may
be wrong too. This is either a powerful finding or an uncomfortable revelation.
Either way, worth knowing.

**Priority: MUST-HAVE for the paper.** This quantifies the judge bias impact
in a way reviewers can grasp immediately. "18% of model rankings flip when you
fix the judge" is a punchline. Goes in Methodology 3.4.

---

## NQ2: Verbosity Correlation

**What:** For each model, compute: (a) avg response length in characters
across all LLM-judged tasks, (b) V1→V2 score delta. Plot (a) vs (b).
If verbose models rose more in V2, verbosity IS the confound.

**Data source:** Raw JSON files. `response` field for length, `score` for V1,
`judge_v2_score` for V2.

**Output:** `verbosity_correlation.json` + `verbosity_scatter.svg`. Scatter
plot: X = avg response length, Y = V1→V2 delta. Pearson r.

**Time estimate:** 25 min (read all raw files for response length, compute
per-model averages, scatter).

**Risk:** LOW. If r > 0.5, we have strong evidence of the mechanism. If r < 0.3,
the format bias is more subtle than pure verbosity (could be structural format
like markdown vs plain text, or use of code blocks, etc.). Either way, a result.

**Priority: MUST-HAVE.** Quantifies the mechanism behind the judge bias.
Without this, we say "format bias exists" but can't explain WHY. With this,
we say "verbose models were penalized, r=0.XX." Goes in Methodology 3.4.

---

## Priority Summary

| Priority | Analysis | Time | Paper section |
|----------|---------|:----:|---------------|
| **MUST-HAVE** | NQ1: Ranking flips | 30 min | Methodology 3.4 |
| **MUST-HAVE** | NQ2: Verbosity correlation | 25 min | Methodology 3.4 |
| **MUST-HAVE** | Q12: Coverage matrix | 30 min | Discussion 5.1 |
| **HIGH** | Q15: Per-task routing savings | 20 min | Results 4.5 |
| **MEDIUM** | Q11: Generational delta | 25 min | Results or Appendix |
| **MEDIUM** | Q4: Provider gradient | 30 min | Appendix |
| **LOW** | Q9: Chinese vs American | 15 min | Appendix (if interesting) |
| **LOW** | Q10: Open vs Closed | 15 min | Appendix (if interesting) |

**Total realistic time: 3-4 hours** (not 2.5h — each analysis needs verification,
and at least one will reveal something that needs investigation).

**Recommended execution order:** NQ1 → NQ2 → Q12 → Q15 → Q11 → Q4 → Q9/Q10.
Must-haves first, nice-to-haves last. Stop after Q15 if time runs out — the
first 4 cover the paper's needs.
