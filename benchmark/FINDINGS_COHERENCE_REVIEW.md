# Findings Coherence Review

**Date:** 2026-05-17
**Purpose:** Check all 17 findings for internal consistency before paper writing.

---

## 1. The 17 Findings

| # | Finding | Evidence | Confidence |
|---|---------|----------|:---:|
| F1 | No significant quality gap between Economy and Premium tiers (Mann-Whitney p>0.05, 21/21 tasks) | stats_validation.json | HIGH |
| F2 | Per-task routing saves 99% vs best single model (o3), ~70% vs realistic single model | routing_savings.json, per_task_routing_savings.json | HIGH (structure), LOW (specific %) |
| F3 | 10 high-discrimination tasks (spread >1.5), 9 medium, 2 low | task_discriminativeness.json | HIGH |
| F4 | Paying more within a provider buys minimal quality. Anthropic: Haiku ≈ Opus. Google: Flash ≈ Pro. OpenAI: 750x price = +0.13 quality | provider_gradient.json, BATCH_2_REVIEW.md | HIGH |
| F5 | Sub-3B models unreliable. Llama 1B only model below 4.0 avg (3.46) | task_model_aggregates.json | LOW (n=1) |
| F6 | RAG QA and test_generation_v2 are the most discriminative generative tasks | task_discriminativeness.json | HIGH |
| F7 | Provider origin (Chinese/American/European) does not predict quality (Kruskal-Wallis p=0.40) | origin_comparison.json | HIGH |
| F8 | Closed-source models marginally better than open-weight (4.79 vs 4.60, p<0.001), gap 0.066 without sub-3B | license_comparison.json | MODERATE |
| F9 | 5 Economy models cover all 21 tasks at ≥4.5. Seed 2.0 Lite ($0.075/M) is cheapest. At ≥4.7, no single model covers all tasks | coverage_matrix.json, q12_robustness.json | HIGH |
| F10 | GPT-5.4 is 60% cheaper than GPT-4o at equal or better quality. New gen = cheaper, not just better | generational_delta.json | HIGH |
| F11 | RAG QA shows the biggest generational quality leap (+0.38 to +1.48 across providers) | generational_delta.json | HIGH |
| F12 | Premium models better on language/generation tasks (+0.11), worse on classification/code (-0.09) vs Economy | BATCH_2_REVIEW.md | MODERATE |
| F13 | LLM-as-judge with generic rubrics has severe format bias (r=0.35 vs ground truth). Correctness-focused rubrics fix it (r=0.90) | judge_reliability.json, judge_v2_validation.json | HIGH |
| F14 | Judge bias changes 34.7% of model-pair rankings. V1 rankings are unreliable | ranking_flips.json | HIGH |
| F15 | Verbosity is NOT the primary driver of judge format bias (r=0.22, non-significant) | verbosity_correlation.json | MODERATE |
| F16 | Qwen Turbo ($0.05/M) is cheapest adequate model on 17/21 tasks at ≥4.0 threshold | per_task_routing_savings.json | HIGH |
| F17 | GPT-5.4 Nano ($0.02/M) is cheapest adequate on 16/21 tasks at ≥4.5 threshold | coverage_matrix.json | HIGH |

---

## 2. Coherence Check: Pairwise

### F1 (Economy ≈ Premium) vs F2 (routing saves 99%)

**Coherent.** F1 says Economy quality matches Premium. F2 says routing to the
cheapest adequate model per task saves money. These reinforce each other:
if Economy matches Premium in quality, then routing to Economy instead of
Premium saves cost with no quality loss.

No contradiction.

### F1 (Economy ≈ Premium) vs F8 (closed > open by 0.066)

**Potentially confusing but coherent.** F1 compares by PRICE TIER (Economy vs
Premium). F8 compares by LICENSE (open vs closed). These are orthogonal axes:

- Some Economy models are closed (ByteDance Seed, Kimi)
- Some Economy models are open (Qwen, DeepSeek)
- Premium is all closed (Opus, GPT-5.5 Pro)

F1 says "cheap matches expensive." F8 says "closed marginally better than open."
Both can be true simultaneously: a cheap closed model (Seed 2.0 Lite at $0.075/M)
can match an expensive closed model (Opus at $15/M).

**Paper note:** Must make clear these are different comparison axes. A reader
might think "Economy ≈ Premium" contradicts "closed > open" because they
assume Economy = open and Premium = closed. That assumption is wrong in our data.

### F4 (provider gradient ≈ flat) vs F10 (new gen cheaper and better)

**Coherent.** F4 says within the SAME GENERATION, paying more buys little.
F10 says ACROSS GENERATIONS, the new model is cheaper AND better. These
complement each other:

- Within OpenAI 2026: GPT-5.4 Nano ($0.02/M) ≈ GPT-5.5 Pro ($15/M). Price ROI ≈ 0.
- Across OpenAI gens: GPT-5.4 ($1/M) > GPT-4o ($2.50/M) AND cheaper.

The lesson: upgrade generations (free quality), don't upgrade tiers (waste money).

### F4 (provider gradient flat) vs F12 (Premium better on language)

**Mild tension.** F4 says paying more buys nothing. F12 says Premium IS marginally
better on language tasks. These coexist because F4 reports the AVERAGE across
all tasks (flat), while F12 reports the per-category breakdown (Premium wins on
language, loses on classification). The aggregate hides the pattern.

**Paper note:** Present both. "On average, paying more buys nothing (F4). But
the average masks a task-type effect: Premium models add value on open-ended
language tasks and lose value on classification (F12)."

### F2 (routing 99%) vs F9 (1 model covers all)

**Tension.** F2 says routing saves 99%. F9 says one model (Seed Lite) covers
everything at ≥4.5. If one model works for everything, why route?

**Resolution (from Q12_ROBUSTNESS):** Seed Lite costs $0.00094/query. The
cheapest-per-task routing costs $0.000011/query. Routing saves 98.8% vs Seed
Lite. The answer: Seed Lite covers all tasks adequately, but routing to
even cheaper models per task saves 99% more. Both are valid strategies at
different points on the simplicity-cost tradeoff.

**Paper note:** Present as a spectrum: "A single Economy model provides
universal adequate quality. Per-task routing reduces cost by a further 99%
at the expense of operational complexity."

### F13 (judge bias) vs all quality findings

**Critical dependency.** Every quality finding (F1, F3, F4, F6, F8, F12) depends
on the V2 judge being correct. F13 shows V1 was wrong (r=0.35). If V2 is also
wrong (we validated on 3 tasks, not all 17), ALL quality findings could shift.

This is the paper's biggest vulnerability. We mitigate by:
1. Reporting the validation (r=0.89-0.91 on 3 tasks)
2. Reporting the ranking flip analysis (34.7% of V1 rankings changed)
3. Acknowledging the limitation (15 tasks validated by mechanism, not ground truth)

### F16 (Qwen Turbo cheapest at 4.0) vs F17 (GPT-5.4 Nano cheapest at 4.5)

**Coherent but confusing.** Different thresholds produce different "winners."
At ≥4.0, Qwen Turbo wins (cheapest per query). At ≥4.5, GPT-5.4 Nano wins
(cheapest per M tokens, and scores higher).

**Paper note:** Present both and let the reader choose their quality threshold.
Don't crown a single "best model."

---

## 3. Reinforcement Structure

### The thesis (mutually reinforcing findings)

F1 + F4 + F10 + F12 form the core thesis:

> "Paying more for LLMs is not worth it. Economy models match Premium on
> most tasks (F1). Within a provider, the quality gradient is nearly flat
> (F4). New generations are cheaper AND better (F10). The only exception:
> Premium adds marginal value on open-ended language tasks (F12)."

F2 + F9 + F16 + F17 form the practical recommendation:

> "Use per-task routing (F2) with cheap models (F16, F17). A single Economy
> model can cover everything (F9), but routing saves 99% more."

### Independent findings (neither support nor contradict the thesis)

- F3, F6 (task discriminativeness) — describes the landscape, doesn't argue for/against the thesis
- F5 (sub-3B floor) — an observation about small models
- F7 (origin doesn't matter) — diversity observation
- F8 (closed > open) — orthogonal to price tier comparison
- F11 (RAG QA generational leap) — specific observation

### Methodological findings (support credibility, not the thesis)

- F13 (judge bias, r=0.35→0.90)
- F14 (34.7% ranking flips)
- F15 (verbosity ≠ primary bias factor)

---

## 4. Fragile Findings

| Finding | Vulnerability | Survival odds |
|:--------|:-------------|:---:|
| F1 (Econ ≈ Premium) | n=2 Premium. Low power. Could flip with 5+ Premium models | 70% |
| F5 (sub-3B floor) | n=1 at 1B. Observation, not finding | 50% |
| F8 (closed > open) | Driven by small open models. Practically negligible gap (0.066) | 80% |
| F12 (Premium better on language) | Marginal deltas (<0.2), within noise per task | 60% |
| F15 (verbosity ≠ bias) | Weak r (0.22). Mechanism unclear. Honest but not compelling | 90% (can't be attacked — it IS weak) |

Most robust: F2, F3, F4, F6, F7, F9, F10, F13, F14, F16, F17. These have
strong data, large effects, or are definitional (not claimable).

---

## 5. Classification: Core / Supporting / Caveats

### Core findings (abstract + intro)

| # | Finding | Why core |
|---|---------|----------|
| F1 | Economy ≈ Premium (no significant gap) | The headline finding |
| F13 | LLM-judge format bias (r=0.35→0.90) | The methodological contribution |
| F4 | Provider gradient is flat (paying more ≠ better) | Strongest per-provider evidence for F1 |
| F2 | Routing saves 70-99% | The practical implication |

### Supporting findings (results sections)

| # | Finding | Where |
|---|---------|-------|
| F3 | Task discriminativeness (10 high, 9 medium, 2 low) | Results: landscape |
| F6 | RAG QA / test gen most discriminative | Results: landscape |
| F9 | 5 models cover all tasks at ≥4.5 | Results: coverage |
| F10 | New gen cheaper and better (GPT-4o→5.4) | Results: generational |
| F12 | Premium better on language, worse on classification | Results: tier nuance |
| F14 | 34.7% ranking flips V1→V2 | Results: judge validation |
| F16/F17 | Cheapest adequate models (Qwen Turbo, GPT-5.4 Nano) | Results: routing |
| F7 | Origin doesn't predict quality | Results: diversity |

### Caveats and observations (discussion/appendix)

| # | Finding | Where |
|---|---------|-------|
| F5 | Sub-3B floor (n=1, observation) | Discussion: limitations |
| F8 | Closed marginally better than open (0.066) | Discussion: license |
| F11 | RAG QA biggest generational leap | Appendix |
| F15 | Verbosity ≠ primary bias driver | Discussion: methodology |

---

## 6. Detected Inconsistencies

**None that are true contradictions.** The F2 vs F9 tension (routing vs single
model) is resolved by framing as a spectrum. The F1 vs F8 confusion (Economy ≈
Premium but closed > open) is resolved by making clear these are different axes.

The only risk is a reader conflating price tier with license type. The paper
must explicitly state: "Economy includes both open (Qwen Turbo) and closed
(Seed 2.0 Lite) models. The Economy ≈ Premium finding compares price tiers,
not license types."
