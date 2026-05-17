# Findings Critique v2 — Adversarial Review of All 17 Findings

**Date:** 2026-05-17

Findings F1-F7 were critiqued in FINDINGS_CRITIQUE.md. This document
covers the 10 new findings (F8-F17) and recaps the original 7.

---

## F1-F7 Recap (from FINDINGS_CRITIQUE.md)

| # | Finding | Strongest attack | Verdict |
|---|---------|:---:|:---:|
| F1 | Economy ≈ Premium | n=2 Premium (VERY STRONG) | MODERATE |
| F2 | Routing saves 99% | Baseline choice arbitrary (STRONG) | MODERATE |
| F3 | Tasks discriminative vs commodity | Observable property. Hard to attack | SOLID |
| F4 | Provider gradient flat | Well-tested with CIs and Wilcoxon | SOLID |
| F5 | Sub-3B floor | n=1 at 1B (VERY STRONG) | FRAGILE |
| F6 | RAG QA most discriminative | Observable. "Hardest" → "most discriminative" | SOLID |
| F7 | Origin doesn't predict quality | 3-group Kruskal-Wallis p=0.40 | SOLID |

---

## New Findings: Adversarial Analysis

### F8: Closed marginally better than open (0.066, p<0.001)

**Attack 8.1: Confounded by model size (VERY STRONG)**

"Your open set includes Llama 1B and 3B. Your closed set doesn't include
any sub-3B models. The gap is model size, not license. Compare same-size
open vs closed only."

**Defense:** We showed that even excluding sub-3B, the gap narrows to 0.066
but stays significant (p=0.004). Valid point about confounding. Add "the
gap persists after excluding sub-3B models" to the paper.

**Attack 8.2: Classification is debatable (STRONG)**

"Is DeepSeek open? Weights are available but training data is proprietary.
Is Mistral Small open? Apache 2.0 license but only API-accessed in your
benchmark. Your results change depending on classification."

**Defense:** Note debatable cases explicitly. Show sensitivity: if we move
DeepSeek and Qwen to closed, what happens? The finding is robust to
reasonable reclassifications because the top open models (Devstral, Gemma,
Phi) are unambiguously open.

**Attack 8.3: Practical significance (MEDIUM)**

"0.066 on a 1-5 scale is 1.7%. No practitioner would choose a model based
on a 1.7% quality difference. This finding is statistically significant but
practically irrelevant."

**Defense:** Agree. Frame as "statistically significant but practically
negligible." The paper should not overstate this.

**Verdict: MODERATE.** Defensible with caveats on confounding and classification.

---

### F9: 5 models cover all 21 tasks at ≥4.5

**Attack 9.1: Threshold sensitivity (STRONG)**

"At ≥4.7, zero models cover all tasks. Your finding is entirely dependent
on the 4.5 threshold. Why not 4.6 or 4.4?"

**Defense:** We show the full sensitivity (4.0: 37 models, 4.5: 5 models,
4.7: 0). The paper presents all three. The finding is: "a single cheap model
achieves 4.5/5 everywhere" which is descriptive, not prescriptive.

**Attack 9.2: Seed 2.0 Lite barely passes (MEDIUM)**

"RAG QA at exactly 4.50 — right on the threshold. One fewer case correct
and it drops below. Your 'covers all tasks' claim is fragile."

**Defense:** Acknowledged in Q12_ROBUSTNESS.md. 4 tasks within 0.2 margin.
Present as "marginal coverage" not "dominant coverage."

**Verdict: SOLID** with threshold sensitivity shown.

---

### F10: New gen cheaper AND better (GPT-4o → 5.4)

**Attack 10.1: Only 4 pairs (MEDIUM)**

"4 generational pairs is a small sample. GPT-4o→5.4 and Sonnet 4→4.6 might
be outliers. More pairs needed for a general claim."

**Defense:** We have the pairs available in our data. The pattern is consistent
across 3 of 4 providers (OpenAI, Anthropic = cheaper or equal; DeepSeek =
more expensive but better). One counterexample (DeepSeek) prevents a universal
claim. Frame as "trend" not "law."

**Attack 10.2: Quality delta is within noise (MEDIUM)**

"GPT-4o→5.4: +0.089 quality. Sonnet 4→4.6: +0.003. Both are within your
CI of +/-0.2. You can't claim 'better' when the improvement is not significant."

**Defense:** Fair. The quality claim is weak. The PRICE claim is strong
(-60% for GPT, -33% for Mini). Reframe: "new generations are cheaper at
equal quality" rather than "cheaper AND better."

**Verdict: SOLID on price**, MODERATE on quality.

---

### F11: RAG QA biggest generational leap

**Attack 11.1: Could be contamination (MEDIUM)**

"SQuAD v2 is from 2018. New models may have seen it in training. The
improvement could be memorization, not capability."

**Defense:** Valid concern, hard to disprove. Document as limitation.
The improvement is +0.38 to +1.48 across providers — hard to explain
by memorization alone since different providers would memorize differently.

**Verdict: MODERATE.** Real but contamination caveat.

---

### F12: Premium better on language, worse on classification

**Attack 12.1: Deltas are tiny (STRONG)**

"The 'pattern' is +0.11 for language, -0.09 for classification. Both are
within your task-level CI of +/-0.2. This is noise, not a pattern."

**Defense:** The pattern IS marginal. 17/21 tasks have delta < 0.2. Only
2 tasks have delta > 0.3 (Opus on SQL: -0.60, Opus on Instruct: +0.32).
Frame as "suggestive pattern" not "robust finding."

**Attack 12.2: n=2 Premium again (STRONG)**

"Your Premium group is Opus and GPT-5.5 Pro. Maybe Opus is bad at SQL
for model-specific reasons, not tier-level reasons."

**Defense:** Fair. Can't generalize from 2 models. Keep as observation.

**Verdict: FRAGILE.** Downgrade to "observation" in the paper.

---

### F13: Judge bias (r=0.35 → 0.90)

**Attack 13.1: Validated on 3 tasks, extrapolated to 17 (STRONG)**

"You proved V2 works on GSM8K, RAG QA, and code gen. You extrapolated to
14 other tasks without validation. The 14 might still be biased."

**Defense:** We can't validate on tasks without ground truth. But:
(a) the mechanism is identical (same rubric structure, same GPT-4o judge),
(b) the V1→V2 score changes are consistent in direction across all 17 tasks
(format-dependent tasks changed most, format-independent least),
(c) this is standard practice in evaluation papers.

**Attack 13.2: V2 might have its OWN bias (MEDIUM)**

"You showed V1 has format bias. How do you know V2 doesn't have a different
bias (e.g., favoring certain answer structures, or GPT-style outputs)?"

**Defense:** We can't prove absence of bias. We can only prove: V2 correlates
better with ground truth (r=0.90 vs 0.35). Any residual bias is smaller.
The paper should say "reduced format bias" not "eliminated bias."

**Verdict: SOLID** as a finding. The limitation (14 unvalidated tasks) must
be stated clearly.

---

### F14: 34.7% ranking flips

**Attack 14.1: Is this because V1 was random, or V2 changed rankings? (STRONG)**

"If V1 scores were essentially random on some tasks (r=-0.01 on RAG QA),
then any non-random V2 would produce flips. The 34.7% doesn't mean V2 is
right — it means V1 was broken. We already knew that from F13."

**Defense:** Correct. F14 is a consequence of F13, not independent evidence.
Its value is quantifying the IMPACT of the judge fix: "fixing the judge
changes 35% of rankings." This is useful for the field even if expected.

**Attack 14.2: Per-task rates vary wildly (MEDIUM)**

"RAG QA has 50% flips (random), Code Review has 20%. The aggregate 34.7%
is misleading — some tasks are stable, others are chaos."

**Defense:** Report both aggregate and per-task. The per-task variation is
informative: tasks where V1 was most wrong (RAG QA) show the most flips.

**Verdict: SOLID** as a quantification of F13's impact.

---

### F15: Verbosity ≠ primary bias driver

**Attack 15.1: Null result (MEDIUM)**

"You found that verbosity doesn't explain the bias (r=0.22, p=0.13). But
you don't explain what DOES. A null result is not a finding."

**Defense:** Agree that the mechanism remains partially unexplained. The value
is ruling out the obvious hypothesis. The true driver may be structural format
(markdown, code blocks, think tags) rather than length. Document as future work.

**Verdict: MODERATE.** Honest null result. Include in discussion, not results.

---

### F16: Qwen Turbo cheapest adequate on 17/21 tasks (≥4.0)

**Attack 16.1: Threshold dependent (MEDIUM)**

"At ≥4.5, GPT-5.4 Nano wins (F17). At ≥4.0, Qwen Turbo wins. The 'cheapest'
depends entirely on quality threshold."

**Defense:** Present both. The point is: "the cheapest adequate model changes
with your quality requirement." This IS the routing insight.

**Verdict: SOLID** when presented as threshold-dependent.

---

### F17: GPT-5.4 Nano cheapest on 16/21 tasks (≥4.5)

Same attack and defense as F16. Present together.

**Verdict: SOLID.**

---

## Summary: All 17 Findings Ranked

### SOLID (9 findings)

| # | Finding | Why solid |
|---|---------|-----------|
| F3 | Task discriminativeness | Observable, definition-based |
| F4 | Provider gradient flat | Wilcoxon + bootstrap validated |
| F6 | RAG QA most discriminative | Observable |
| F7 | Origin doesn't predict quality | Kruskal-Wallis p=0.40 |
| F9 | 5 models cover all at 4.5 | With sensitivity shown |
| F13 | Judge bias r=0.35→0.90 | Validated on 3 tasks |
| F14 | 34.7% ranking flips | Consequence of F13 |
| F16 | Qwen Turbo cheapest at 4.0 | Verifiable |
| F17 | GPT-5.4 Nano cheapest at 4.5 | Verifiable |

### MODERATE (5 findings)

| # | Finding | Key weakness |
|---|---------|-------------|
| F1 | Economy ≈ Premium | n=2 Premium |
| F2 | Routing saves 99% | Baseline and threshold dependent |
| F8 | Closed > open (0.066) | Confounded by model size |
| F10 | New gen cheaper | Quality delta within noise |
| F15 | Verbosity ≠ driver | Null result |

### FRAGILE (3 findings)

| # | Finding | Fatal flaw |
|---|---------|-----------|
| F5 | Sub-3B floor | n=1 |
| F11 | RAG QA gen leap | Contamination risk |
| F12 | Premium better on language | Deltas within noise, n=2 |
