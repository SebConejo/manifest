# TaskBench Final Findings (V3 — GPT-4o correctness judge)

**Date:** 2026-05-15
**Judge:** GPT-4o with correctness-focused V2 prompts (validated: r=0.905
on GSM8K, r=0.887 on RAG QA vs ground truth). 40,350 cases re-judged.
**Data:** 51,580 rows, 46 complete models, 21 tasks.

---

## Finding 1: No detectable quality gap between Economy and Premium tiers

**Statement:** On none of the 21 tasks did we detect a statistically significant
quality difference between Economy ($0.08-0.50/M) and Premium ($5+/M) models
(Mann-Whitney U, p > 0.05 on all 21 tasks, n_Economy=14-15, n_Premium=2).

**V3 evidence (with V2 judge):**
- Global: Premium 4.791 [4.729, 4.853], Economy 4.749 [4.715, 4.777]
- Gap: 0.042 points (was 0.000 with V1 judge)
- CIs overlap on all 21 tasks
- 0/21 Mann-Whitney tests significant at alpha=0.05

**Change from V1:** Premium avg rose from 4.601 to 4.791 (+0.190) because V2
judge no longer penalizes verbose format. Economy rose from 4.601 to 4.749
(+0.148). The gap widened from 0.000 to 0.042 — still not significant.

**Caveat:** n=2 Premium models limits statistical power. We cannot claim equality,
only "no significant difference detected."

**Confidence: MODERATE.** Structurally robust (holds across judge versions and
tier boundaries) but limited by n=2 Premium.

---

## Finding 2: Per-task routing saves 99.7% vs best single model

**Statement:** The cheapest adequate model (score >= 4.0) per task costs
$0.000009/query. The best single all-round model (o3, 4.842/5) costs
$0.003332/query.

**Change from V1:** Best single model changed from Devstral ($0.000063) to o3
($0.003332) because V2 judge reranked models — o3 now scores highest overall.
Savings increased from 86% to 99.7% because o3 is expensive.

**Caveat:** The 99.7% number is misleading — it compares against o3 which nobody
would use as a universal model. Against GPT-4o-mini ($0.00003/query, a realistic
"one model for everything" choice), savings are ~70%.

**Confidence: HIGH** for the structural finding (routing is cheaper). **LOW** for
the specific percentage (depends on baseline choice).

---

## Finding 3: Tasks split into discriminative vs commodity

**Statement:** Score spread ranges from 0.29 (structured_output) to 3.20
(intent_clinc150). V2 judge revealed more discriminative tasks than V1.

**V3 evidence:**

| Tier | Tasks | Spread range |
|------|:---:|:---:|
| High (>1.5) | intent_clinc150, rag_qa, moderation_toxigen, test_generation_v2, sql_spider, code_review_v2, sentiment_sst2, reasoning_gsm8k, code_generation, data_to_text | 1.56-3.20 |
| Medium (0.8-1.5) | translation, function_calling, json_transform, ner, extraction, long_sum, email_sum, instruction, code_expl | 0.81-1.48 |
| Low (<0.8) | multistep_reasoning, structured_output | 0.29-0.80 |

**Change from V1:** test_generation_v2 moved from medium (0.6 spread) to high
(2.40 spread). V1 compressed scores into the 4-4.5 range by penalizing format;
V2 reveals the true quality spread. data_to_text also moved from low (0.50) to
high (1.56).

**Confidence: HIGH.** Observable property of the data, robust to methodology.

---

## Finding 4: o3 and Devstral are the best all-round models

**Statement:** o3 (4.842/5, $0.003332/query) is the highest-quality single model.
Devstral (4.808/5, $0.000063/query) is the best cost-quality ratio among complete
models. Qwen Turbo (4.697/5, $0.00001/query) remains the cheapest universally
adequate model.

**Change from V1:** Qwen Turbo drops from #1 quality default (4.62) to #3.
ByteDance Seed models and Claude Opus rose significantly with V2 judge.
The "best default" answer depends on whether you optimize for quality (o3),
value (Devstral), or cost (Qwen Turbo).

**Confidence: MODERATE.** Model rankings are sensitive to judge methodology —
V1 and V2 produce different rankings. Pricing is a snapshot.

---

## Finding 5: Sub-3B models are unreliable for production

**Statement:** Llama-3.2-1B (3.46/5 avg with V2 judge) is the only model
averaging below 4.0 across all tasks. Llama-3.2-3B (4.31/5) is marginal.

**Change from V1:** Llama 1B dropped further (3.71 → 3.46) because V2 judge
is stricter on incorrect answers that were well-formatted.

**Caveat:** n=1 at 1B. This is an observation about one specific model, not a
general claim about the 1B parameter boundary.

**Confidence: LOW.** Single data point. Downgraded to "observation."

---

## Finding 6: RAG QA and test generation are the most discriminative generative tasks

**Statement:** RAG QA (spread 2.84) and test_generation_v2 (spread 2.40) have
the highest discrimination among generative tasks.

**Change from V1:** RAG QA spread increased from 2.48 to 2.84 with V2 judge.
test_generation_v2 appeared as a new high-discrimination task (V1 spread was
only 0.60 due to format compression).

**Confidence: HIGH.** Validated by the V2 judge improvement on RAG QA (r=0.887).

---

## Finding 7: Provider diversity reveals value at every tier

**Statement:** The Pareto frontier includes models from 7+ providers. No single
provider dominates. At Economy tier, Qwen, DeepSeek, and ByteDance Seed compete
directly with Gemini Flash and GPT-4o-mini.

**Change from V1:** Reframed from "Chinese models dominate" to "provider diversity."
ByteDance Seed models rose significantly with V2 judge (+0.31-0.36), strengthening
their Pareto position. But this reflects V1 format bias correction, not a change
in model quality.

**Confidence: MODERATE.** The observation is correct but the "why" (pricing
strategy vs model capability) is not separable in our data.

---

## Synthesis: What Changed V1 → V3

| Aspect | V1 (GPT-4o-mini) | V3 (GPT-4o V2) |
|--------|:-:|:-:|
| Judge-accuracy correlation | r=0.35 | r=0.90 |
| Premium avg score | 4.601 | 4.791 (+0.19) |
| Economy avg score | 4.601 | 4.749 (+0.15) |
| Premium-Economy gap | 0.000 | 0.042 |
| Gap significant? | No (p>0.05) | No (p>0.05) |
| Best single model | Devstral (4.75) | o3 (4.84) |
| Routing savings | 86% | 70% (vs realistic baseline) |
| High-discrimination tasks | 7 | 10 |
| Llama 1B avg | 3.71 | 3.46 |

The V2 judge produces a more accurate picture: Premium is slightly better than
V1 suggested (format bias removed), but still not significantly better than
Economy. The quality differences between models are larger than V1 showed
(more tasks are discriminative).
