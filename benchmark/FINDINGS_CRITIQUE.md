# Findings Critique — Adversarial Self-Review

**Date:** 2026-05-14
**Purpose:** Anticipate every reviewer attack before submission.
**Tone:** Hostile reviewer. No charity.

---

## Finding 1: Economy = Premium (already critiqued)

See previous analysis. 10 attacks identified. 3 VERY STRONG (#3 CI too wide,
#6 n=2 Premium, #9 no statistical tests).

**Verdict: FRAGILE.** The structural intuition is correct but the claim as
stated is not defensible with n=2 Premium models and no significance tests.

---

## Finding 2: Per-task routing saves 86%

**Claim:** Cheapest adequate model (score >= 4.0) per task costs $0.000009/query.
Best single model (Devstral) costs $0.000063/query. Saving: 86%.

### Attack 2.1: The "adequate" threshold is arbitrary (VERY STRONG)

"Why 4.0? If I set the threshold at 4.5, the cheapest adequate model per task
is more expensive and the savings drop. If I set it at 3.5, savings increase.
The 86% number is a function of your arbitrary threshold, not a property of the
market. Show sensitivity: savings at 3.5, 4.0, 4.5, 4.8."

### Attack 2.2: Devstral is a weird baseline (STRONG)

"Your 'best single model' is Devstral, a Mistral coding specialist at $0.20/M.
Nobody uses a coding model for sentiment analysis. A real user's single model
would be GPT-4o or Claude Sonnet. Compare against GPT-4o ($2.50/M) or the actual
most popular model, not the statistical best-average. The savings would be higher
but the comparison would be honest."

### Attack 2.3: Cost data is unreliable for reasoning models (STRONG)

"You admitted gpt-5.5-pro costs are 3.75x underestimated. The routing calculation
uses these wrong costs. If Premium models are really 4x more expensive than your
CSV says, the savings from routing are HIGHER but for the wrong reasons — you're
comparing wrong numbers."

### Attack 2.4: The routed set changes per task — operational complexity (MEDIUM)

"Routing across 21 tasks requires maintaining 21 API integrations, 21 API keys,
21 failure modes. The 86% saving doesn't account for engineering cost. A single
model is operationally simpler. This is an engineering paper, not just math."

### Attack 2.5: Quality loss is not measured (STRONG)

"You say 'negligible quality loss' but the threshold is 4.0. On a 1-5 scale,
4.0 means 'good with minor issues.' The best single model scores 4.75 average.
That's a 0.75-point quality drop — 15% of the scale. Is that 'negligible'?
A user who needs 4.5+ quality gets no savings because the cheap models don't
qualify."

### What's needed to defend:
- Sensitivity analysis: savings at thresholds 3.5, 4.0, 4.5, 4.8
- Compare against realistic baselines (GPT-4o, Claude Sonnet, not Devstral)
- Acknowledge quality-cost tradeoff explicitly (savings come with quality loss)
- Correct the costs (Option A-lite) before computing savings

**Verdict: MODERATE.** The structural finding (routing is cheaper) is trivially
true. The 86% number is fragile because it depends on threshold, baseline, and
cost accuracy.

---

## Finding 3: 7 discriminative vs 5 commodity tasks

**Claim:** Tasks split into tiers by score spread. High-discrimination (spread > 1.5)
vs commodity (spread < 0.5).

### Attack 3.1: Spread is not discrimination (STRONG)

"A spread of 3.20 on intent_clinc150 could mean one terrible model (Llama 1B)
dragging the minimum down while 45 other models are clustered at 4.5-4.7. That's
not 'discrimination' — it's one outlier. True discrimination would be measured
by standard deviation or interquartile range, not max-min."

### Attack 3.2: The threshold (1.5 / 0.5) is arbitrary (MEDIUM)

"Why is 1.5 the cutoff for 'high discrimination'? You have a continuous variable
(spread) and you're discretizing it into 3 bins. The bins are chosen to make a
clean narrative. Show the actual distribution."

### Attack 3.3: Task difficulty != task usefulness (MEDIUM)

"You conflate discrimination with importance. data_to_text is 'commodity' because
all models score 4.5+. But data-to-text generation is a real production task.
Calling it commodity dismisses it. A more useful framing: 'on data_to_text, you can
safely use the cheapest model' — which is a routing recommendation, not a dismissal."

### Attack 3.4: Ceiling effect again (STRONG)

"The 5 'commodity' tasks may simply have easy test cases. If you added harder
cases (adversarial data-to-text, complex summarization), the spread would increase.
Your task difficulty is an artifact of your dataset curation, not a property of
the task category."

### What's needed to defend:
- Use IQR or std instead of max-min for discrimination
- Show that commodity tasks remain commodity even with harder cases (or acknowledge
  the dataset dependency)
- Frame as "low spread" rather than "commodity" — more neutral

**Verdict: SOLID with rewording.** The observation (some tasks separate models,
others don't) is factual. The interpretation needs nuance.

---

## Finding 4: Qwen Turbo = best default model

**Claim:** Qwen Turbo ($0.05/M) achieves 4.62/5 avg across 21 tasks at
$0.00001/query. Best value overall.

### Attack 4.1: 4.62/5 is not "good" on every task (VERY STRONG)

"Average 4.62 across 21 tasks hides the per-task distribution. What's Qwen Turbo's
WORST task? If it scores 2.5 on intent_clinc150, it's not a 'safe default' — it
fails on 1 in 21 tasks. Show the min, not just the mean."

### Attack 4.2: Other models beat it on the metric that matters (STRONG)

"Qwen3-8B scores 4.70 avg for $0.00006/query. DeepSeek V3.2 scores 4.68. Devstral
scores 4.75. They cost marginally more but are better. Why crown Qwen Turbo when
3 models within 2x the cost are objectively better? The 'best default' depends on
your cost sensitivity."

### Attack 4.3: Pricing changes (MEDIUM)

"Qwen Turbo is $0.05/M today. In 3 months it could be $0.15/M or discontinued.
Model-specific recommendations have a shelf life of weeks. The finding is perishable."

### Attack 4.4: Chinese model availability (MEDIUM)

"Qwen Turbo is accessed via OpenRouter from a Chinese provider. Some enterprises
cannot use Chinese-origin models (compliance, data residency). Recommending it as
'universal default' ignores deployment constraints."

### What's needed to defend:
- Show the per-task min for Qwen Turbo (and top alternatives)
- Present as "one of the best defaults" not "THE best"
- Show a table of top-5 defaults with tradeoffs
- Acknowledge pricing volatility

**Verdict: MODERATE.** Factually correct but the "best" claim is overfit to
current pricing and ignores practical constraints.

---

## Finding 5: 1B parameter cliff

**Claim:** Below ~3B params, quality drops sharply. Llama-3.2-1B (1.2B) averages
3.60/5, only model below 4.0.

### Attack 5.1: n=1 at 1B (VERY STRONG)

"You have exactly ONE model at 1B parameters (Llama-3.2-1B). One data point is
not a 'cliff.' Maybe Llama-3.2-1B is just a bad model. Maybe another 1B model
(Qwen-0.5B, Phi-1.5) would score 4.0+. You cannot claim a parameter cliff from
a single model."

### Attack 5.2: The 3B models are not controlled (STRONG)

"Llama 1B vs Llama 3B vs Ministral 3B: these are different architectures,
different training data, different fine-tuning. The quality difference could be
architecture, not parameter count. To claim a parameter cliff, you need same
architecture at different sizes (Llama 1B/3B/8B/70B) — which you have for Llama
but not for Mistral or Qwen."

### Attack 5.3: Task-specific, not general (MEDIUM)

"Llama 1B fails on classification (1.50 on intent_clinc150) but scores 5.0 on
multistep_reasoning. The 'cliff' is task-dependent, not general. Say 'below 3B,
models fail on fine-grained classification' — not 'below 3B, models are unreliable.'"

### What's needed to defend:
- Add more <3B models if possible (not feasible now)
- Narrow the claim: "the only sub-3B model tested" instead of "the 1B cliff"
- Show the per-task breakdown for 1B/3B/8B to demonstrate the gradient
- Acknowledge n=1

**Verdict: FRAGILE.** The observation is real but "cliff" from one data point
is not defensible. Downgrade to "observation" or "preliminary."

---

## Finding 6: RAG QA is the hardest generative task

**Claim:** RAG QA has spread 2.48 (2.50-4.98) and many strong models fail.
Most discriminative generative task.

### Attack 6.1: "Hardest" by what metric? (STRONG)

"Highest spread doesn't mean hardest. intent_clinc150 has spread 3.20 — higher
than RAG QA. You say RAG QA is the hardest 'generative' task but that qualifier
is doing heavy lifting. If you include exact-match tasks, RAG QA isn't even the
most discriminative."

### Attack 6.2: 50 cases from SQuAD v2 (MEDIUM)

"SQuAD v2 is a well-known dataset from 2018. Modern models have likely seen it
in training. Your 50 cases may be in the training set. Performance differences
could reflect memorization, not capability. Did you check for contamination?"

### Attack 6.3: The judge evaluates differently on RAG (STRONG)

"RAG QA has a specific rubric: '1 = hallucinated.' This is a binary property
(did the model stay in context or not), not a quality gradient. The 1-5 scale
is misleading here — it's effectively pass/fail. Models scoring 2.5 are failing
completely, not 'doing moderately.'"

### Attack 6.4: Strong models "fail" at 2.5-3.5 — or do they? (MEDIUM)

"You claim 'many strong models score below 4.0.' Show me which ones. If it's
Mistral Large at 3.0 and Qwen Flash at 3.0, those are mid-tier models, not
'strong.' If Claude Opus or GPT-5.5 score below 4.0 on RAG QA, THAT would be
a finding. But I suspect the low scorers are the usual suspects."

### What's needed to defend:
- Say "most discriminative generative task" consistently (not "hardest")
- Check for dataset contamination (hard to verify, document as limitation)
- Show which specific strong models fail on RAG QA
- Consider if the 1-5 scale is appropriate or if pass/fail would be more honest

**Verdict: SOLID with precise wording.** The discrimination is factual and
observable. "Hardest" is editorializing — "most discriminative" is defensible.

---

## Finding 7: Chinese models dominate Pareto

**Claim:** Qwen, DeepSeek, ByteDance Seed consistently on or near the Pareto
frontier across multiple tasks.

### Attack 7.1: Price advantage, not quality advantage (VERY STRONG)

"Chinese models are cheap because Chinese labor and compute costs are lower, and
some providers (DeepSeek, Qwen) are subsidized or loss-leading. Being on the Pareto
frontier means 'good quality for the price' — not 'better quality.' If prices
normalize, the finding evaporates. You're measuring pricing strategy, not model
capability."

### Attack 7.2: "Dominate" is loaded language (STRONG)

"'Chinese models dominate Pareto' implies superiority. What you actually found is
'some Chinese models appear on the Pareto frontier.' How many? On how many tasks?
Is it 1 model on 20 tasks (Qwen Turbo), or 10 models on 2 tasks each? The word
'dominate' oversells the finding."

### Attack 7.3: Provider routing introduces confounds (MEDIUM)

"Your Chinese models go through OpenRouter. OpenRouter adds latency and potentially
modifies responses (content filtering, token limits). American models go direct.
You're comparing models through different infrastructure. The cost comparison is
apples-to-oranges because OpenRouter takes a margin."

### Attack 7.4: Selection bias in model choice (STRONG)

"You included 13 Chinese-origin models vs 15 American-origin. But the Chinese
models are disproportionately in the Economy/Micro tier. You have no Chinese
Premium model (no Chinese model at $5+/M). Of course cheaper models appear on the
Pareto frontier — they're cheaper by definition. Compare at the same price tier."

### Attack 7.5: Geopolitical framing is unnecessary (MEDIUM)

"Why frame this by country of origin at all? The user doesn't care if a model is
Chinese or American — they care about cost and quality. 'Qwen Turbo is the best
value' is a useful finding. 'Chinese models dominate' is a geopolitical statement
that adds controversy without adding value."

### What's needed to defend:
- Count precisely: how many Chinese models on Pareto, on how many tasks
- Compare at same price tier (Chinese Economy vs American Economy)
- Reframe: "models from Chinese providers offer competitive quality at lower
  price points" instead of "dominate"
- Acknowledge subsidized pricing
- Drop the geopolitical angle in the main paper, move to discussion section

**Verdict: FRAGILE as stated.** The observation (cheap Chinese models are good)
is valid. The "dominate Pareto" framing is inflammatory and imprecise. Needs
heavy rewording.

---

## Synthesis: Findings Ranked by Defensibility

### SOLID (publishable with minor rewording)

| Finding | Why solid | What to fix |
|---------|----------|-------------|
| F3: Tasks split by discrimination | Observable property of the data, not dependent on methodology | Use IQR not max-min, say "low spread" not "commodity" |
| F6: RAG QA most discriminative generative | Factual, large spread, reproducible | Say "most discriminative" not "hardest", check contamination |

### MODERATE (publishable with significant caveats)

| Finding | Core issue | What to fix |
|---------|-----------|-------------|
| F1: Economy = Premium | n=2 Premium, no stat tests, CI overlap | Reformulate as "within 0.3 points", add bootstrap CIs, caveat n=2 |
| F2: Routing saves 86% | Threshold-dependent, wrong baseline | Sensitivity analysis at 3.5/4.0/4.5, use GPT-4o as baseline, fix costs |
| F4: Qwen Turbo best default | Overfit to current pricing, ignores constraints | Present top-5 table, show per-task min, say "one of the best" |

### FRAGILE (needs major rework or downgrade to "observation")

| Finding | Fatal flaw | Options |
|---------|-----------|---------|
| F5: 1B parameter cliff | n=1 at 1B params | Downgrade to "preliminary observation", remove "cliff" language |
| F7: Chinese dominate Pareto | Inflammatory framing, price advantage not quality | Reframe entirely: "competitive quality at lower price points" |

### Findings NOT in the list that SHOULD be

A reviewer will also ask: "where is your analysis of judge reliability?" and
"where is your comparison to existing benchmarks (MMLU scores)?" These are
conspicuous absences.

**Missing analysis 1:** Judge reliability — inter-rater agreement between
GPT-4o-mini judge and the native accuracy metric on the 4 exact-match tasks.
We HAVE this data. We should compute and report the correlation.

**Missing analysis 2:** Comparison to MMLU/Arena rankings — do our quality
rankings correlate with public leaderboard rankings? If yes, our benchmark
adds the cost dimension. If no, we need to explain why.
