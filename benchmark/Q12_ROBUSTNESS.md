# Q12 Robustness: Coverage Matrix

**Date:** 2026-05-15

---

## Check 1: Coverage at different thresholds

| Threshold | Models covering 21/21 | Cheapest |
|:---------:|:---------------------:|:---------|
| >= 4.0 | 37 | Qwen Turbo ($0.05/M) |
| >= 4.5 | 5 | Seed 2.0 Lite ($0.075/M) |
| >= 4.7 | 0 | None |

At >= 4.0, nearly every non-tiny model covers all tasks. At >= 4.5, only 5
models qualify. At >= 4.7, no single model covers all 21 — several tasks
have no model scoring that high.

**The threshold matters enormously.** The "one model does everything" finding
is true at 4.5 but breaks at 4.7.

---

## Check 2: Seed 2.0 Lite per-task scores

| Status | Tasks | Details |
|:------:|:-----:|:--------|
| TIGHT (margin < 0.2) | 4/21 | rag_qa (4.50), instruction_following (4.54), moderation_toxigen (4.60), ner_extraction (4.62) |
| OK (margin >= 0.2) | 17/21 | All others, highest: sentiment/multistep/code_review/long_sum/data_to_text at 5.00 |

Average score: **4.836/5**. Average cost: **$0.00094/query**.

Seed 2.0 Lite barely crosses the 4.5 threshold on RAG QA (exactly 4.50) and
instruction_following (4.54). A small fluctuation could push these below
threshold. The model is not dominant on hard tasks — it's just barely adequate
everywhere.

---

## Check 3: Seed 2.0 Lite alone vs routing

| Strategy | Avg cost/query | Avg quality |
|:---------|:--------------:|:-----------:|
| Seed 2.0 Lite alone | $0.000936 | 4.84 |
| Cheapest per task (>= 4.5) | $0.000011 | varies |
| **Routing saves** | **98.8%** | |

Routing saves 98.8% vs using Seed Lite for everything. The savings come
from the fact that GPT-5.4 Nano ($0.02/M) handles 16/21 tasks at >= 4.5
with much lower per-query cost than Seed Lite ($0.075/M).

**The finding is NOT "you don't need routing."** The finding is: "a single
$0.075/M model can cover everything at adequate quality, but routing to
cheaper models per task saves 99% more."

---

## Check 4: All 5 models covering 21/21 at >= 4.5

| Model | Input $/M | Avg $/query | Avg score |
|:------|:---------:|:-----------:|:---------:|
| Grok 4 Fast | $0.60 | $0.00043 | 4.841 |
| Seed 2.0 Mini | $0.15 | $0.00061 | 4.834 |
| GPT-5.4 | $1.00 | $0.00072 | 4.812 |
| **Seed 2.0 Lite** | **$0.075** | **$0.00094** | **4.836** |
| o3 | $2.00 | $0.00333 | 4.842 |

**Seed 2.0 Lite has the lowest input price ($0.075/M) but NOT the lowest
per-query cost.** Grok 4 Fast ($0.00043/query) is cheaper per query because
it produces shorter responses (fewer output tokens). Seed Lite generates
longer output, costing more per query despite the lower per-M price.

The cheapest single-model strategy is actually **Grok 4 Fast** ($0.00043/query),
not Seed Lite.

---

## Summary for the paper

The "one model covers everything" finding holds at threshold >= 4.5 but:
1. Only 5 models qualify (out of 46)
2. The cheapest (Seed Lite) barely passes on 4 tasks (margin < 0.2)
3. At threshold >= 4.7, no single model covers all 21 tasks
4. Routing to the cheapest adequate model per task saves 99% more than
   using any single model

**Paper framing:** "At the 4.5/5 quality threshold, 5 Economy models cover
all 21 tasks. But per-task routing to the cheapest adequate model reduces
cost by 99% further, driven by Micro-tier models ($0.02-0.05/M) that
handle most tasks individually."
