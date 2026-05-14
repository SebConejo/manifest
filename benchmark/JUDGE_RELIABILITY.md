# Judge Reliability Analysis

**Date:** 2026-05-14
**Judge:** GPT-4o-mini, temperature=0, task-specific rubrics, scale 1-5.

---

## Summary

| Comparison | Pearson r | p-value | n models | Verdict |
|:-----------|:---------:|:-------:|:--------:|:-------:|
| GSM8K: judge score vs exact-answer accuracy | **0.388** | 0.006 | 48 | WEAK |
| RAG QA: judge score vs fuzzy accuracy | **-0.013** | 0.932 | 48 | NONE |
| Cross-task: exact-match avg vs judge avg | **0.668** | <0.001 | 48 | MODERATE |
| **Weighted mean** | **0.348** | | | **FAIL (< 0.6)** |

**Verdict: The LLM judge does NOT reliably track ground-truth accuracy.**
The weighted mean correlation (r=0.348) is well below the 0.6 threshold
for partial validation. This is a serious methodological issue.

---

## Analysis 1: GSM8K (r = 0.388)

The judge scores math reasoning on a 1-5 rubric. We independently extracted
the numerical answer from each response and compared to the expected answer.

**r = 0.388 — statistically significant (p=0.006) but weak.**

The correlation is low because the judge evaluates PRESENTATION, not correctness.
A model that gives the right answer in a verbose, unconventional format gets a
low judge score. A model that gives a clean, well-formatted wrong answer can
get a medium judge score.

### Key divergences

| Model | Judge (1-5) | Accuracy | Pattern |
|:------|:---:|:---:|:---|
| Claude Opus 4.7 | 3.48 | 96% | Correct answers penalized for verbose format |
| Nemotron 120B | 1.84 | 84% | Correct answers but format completely non-standard |
| Llama 1B | 3.66 | 38% | Bad accuracy but format looks reasonable to judge |
| Grok 4.20 | 4.56 | 70% | Clean format inflates judge score despite errors |

**Direction of bias:** The judge systematically UNDER-scores verbose reasoning
models (Opus, Nemotron) and OVER-scores concise models that format cleanly
but get the answer wrong. This is a format bias, not a random error.

---

## Analysis 2: RAG QA (r = -0.013)

The judge scores RAG answers on a 1-5 rubric ("1=hallucinated, 5=correct from
context"). We independently checked if the expected answer string appears in
the response (fuzzy accuracy).

**r = -0.013 — zero correlation. The judge score is uncorrelated with
whether the response contains the correct answer.**

### Why the correlation is zero

The judge evaluates "quality of response" broadly — fluency, completeness,
format. A model that gives a detailed, well-written response that happens to
include the correct answer plus some hallucinated context scores 5. A model
that gives just the correct answer in one word scores 4. A model that gives
a beautifully written wrong answer scores 3-4.

The fuzzy accuracy metric (expected substring in response) is binary and
tests only extraction correctness. These two metrics measure different things.

### Extreme divergences

| Model | Judge (1-5) | Contains expected? | What happened |
|:------|:---:|:---:|:---|
| Qwen3.6 Plus | 2.50 | 88% | Correct answers scored low (format issue?) |
| Seed 2.0 Mini | 2.72 | 88% | Same pattern |
| Mistral Small | 4.38 | 34% | Eloquent hallucinations scored high |
| GPT-5.4 Nano | 4.68 | 56% | Well-formatted wrong answers score well |
| Llama 1B | 3.54 | 18% | Low on both (consistent, at least) |

**The judge rewards eloquence over correctness on RAG QA.** Models that
hallucinate confidently score higher than models that give terse correct
answers. This is the opposite of what RAG QA should test.

---

## Analysis 3: Cross-task rank consistency (r = 0.668)

For each model, we computed two averages: mean score across 4 exact-match
tasks, and mean score across 17 LLM-judged tasks. We correlated these
across 48 models.

**Pearson r = 0.668 (moderate). Spearman rho = 0.013 (none).**

The Pearson/Spearman divergence means the correlation is driven by a few
extreme points (Llama 1B low on both, top models high on both), not by a
consistent rank ordering. The judge produces a similar top/bottom ranking
but scrambles the middle.

---

## Implications for the Paper

### What this means

1. **LLM-judge scores on generative tasks are NOT accuracy metrics.** They
   measure perceived quality (format, fluency, apparent correctness), not
   actual correctness. The paper must never claim "model X is more accurate
   than model Y" based on judge scores.

2. **The format bias is systematic and directional.** Verbose reasoning
   models are penalized. Concise models are rewarded. This specifically
   disadvantages Premium reasoning models (Opus, GPT-5.5 Pro) and could
   partially explain why "Economy = Premium" on judge scores — Economy
   models happen to produce the format the judge prefers.

3. **RAG QA judge scores are unreliable.** r = -0.013 means the 1-5 score
   on RAG QA has zero predictive value for whether the answer is correct.
   Finding 6 ("RAG QA is the hardest task") is based on these unreliable
   scores.

### What to do

**Option 1: Report both metrics (RECOMMENDED)**

For tasks with ground truth (GSM8K, RAG QA), report:
- Native accuracy (exact match / fuzzy match) as the PRIMARY quality metric
- LLM-judge score as a SECONDARY "usability" metric (format, fluency)

This is honest and turns the divergence into a finding: "accuracy and
perceived quality measure different things."

**Option 2: Re-judge with a better rubric**

The current RAG QA rubric rewards fluency. A rubric explicitly focused on
"does the response contain the correct answer?" would correlate better.
Cost: ~$2 for 2,400 calls. But this re-scores all models, changing results.

**Option 3: Drop judge scores on tasks with ground truth**

Use only native accuracy for GSM8K, RAG QA, and the 4 exact-match tasks.
Use judge scores only for tasks without ground truth (code review,
summarization, etc.). This is the cleanest separation but reduces the
judge's role to 11 of 21 tasks.

### Impact on findings

| Finding | Impact |
|:--------|:-------|
| F1 (Economy = Premium) | WEAKENED — format bias favors Economy style |
| F2 (Routing 86%) | WEAKENED — quality threshold based on unreliable judge |
| F3 (Discriminative tasks) | UNCHANGED — spread is spread regardless of metric |
| F4 (Qwen Turbo best default) | WEAKENED — "best" based on judge that rewards conciseness |
| F6 (RAG QA hardest) | INVALID as stated — judge score unreliable on RAG QA |
| F7 (Chinese dominate Pareto) | WEAKENED — if Chinese models are more concise |
