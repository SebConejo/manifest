# Paper Outline

**Date:** 2026-05-15
**Status:** Pre-writing. Outline for validation before drafting.

---

## 1. Title Candidates

| # | Title | Angle | Strength | Weakness |
|---|-------|-------|----------|----------|
| A | **TaskBench: Measuring LLM Cost-Quality Tradeoffs Across 21 Production Tasks** | Benchmark-first | Clear, descriptive, what-it-is | Generic, doesn't highlight the novel bit |
| B | **When LLM Judges Lie: Format Bias in Production LLM Benchmarks** | Methodology-first | Provocative, highlights the novel contribution | Undersells the dataset (46 models, 21 tasks) |
| C | **The $0.15 Model is Good Enough: Cost-Quality Pareto Frontiers for 46 LLMs** | Finding-first | Immediately actionable, memorable | Oversimplifies, n=2 Premium caveat |
| D | **TaskBench: 46 Models, 21 Tasks, and Why Your LLM Judge is Wrong** | Hybrid (benchmark + methodology) | Covers both contributions, intriguing | "Your judge is wrong" is confrontational |
| E | **How Much Should You Pay for LLM Quality? A 46-Model Benchmark with Judge Validation** | Question framing | Practitioner-friendly, frames the problem | Long, "with Judge Validation" feels tacked on |

**My pick: D** — it names the scale (46/21), promises useful data, and flags
the methodological contribution without overpromising. The "why your judge is
wrong" hook drives reads.

Backup: A if we want conservative/academic, C if we want maximum practitioner reach.

---

## 2. Detailed Outline

### Abstract (200 words)

We benchmark 46 LLM models across 21 production tasks, measuring both quality
and per-query cost. We discover that a standard LLM-as-judge (GPT-4o-mini)
has a severe format bias (r=0.35 vs ground truth) that systematically
under-scores verbose reasoning models and over-scores concise wrong answers.
After correcting with task-specific correctness rubrics (r=0.90), we find
no statistically significant quality gap between Economy ($0.08-0.50/M) and
Premium ($5+/M) models on any of the 21 tasks. Per-task model routing
reduces cost by 70% vs using a single model. We release the full dataset
(51,580 scored cases) and evaluation prompts.

---

### 1. Introduction (1.5 pages)

**1.1 The problem (0.5 page)**

Every developer using LLM APIs faces the same question: which model for this
task, at what cost? Current benchmarks (MMLU, Arena, HELM) measure general
capability but not per-task cost-efficiency. A model that ranks #1 on Arena
might cost 100x more than the #5 model for the same quality on sentiment
classification.

**1.2 Our contribution (0.5 page)**

Three contributions:
1. **TaskBench**, the first benchmark measuring per-task cost-quality Pareto
   frontiers across 46 models, 21 production tasks, and 9 API providers.
2. **A judge reliability analysis** showing that standard LLM-as-judge
   evaluation has a systematic format bias (r=0.35) that inflates Economy
   model scores and deflates Premium reasoning models.
3. **Corrected evaluation methodology** using task-specific correctness rubrics
   validated against ground truth (r=0.90), enabling more accurate cost-quality
   comparisons.

**1.3 Key findings preview (0.5 page)**

- No significant quality gap between Economy and Premium tiers (Mann-Whitney
  p>0.05 on 21/21 tasks)
- Per-task routing saves 70% vs single-model deployment
- 10 of 21 tasks are highly discriminative (score spread > 1.5); the other 11
  are commodity (any model works)
- Sub-3B parameter models are unreliable for production use

---

### 2. Related Work (0.75 pages)

**2.1 General LLM benchmarks** — MMLU, Arena, HELM. What they measure, what
they miss (cost, per-task granularity). We complement them, not replace.

**2.2 Cost-aware LLM evaluation** — FrugalGPT (cascading, 1 task, 3 models),
Cost-Aware Model Selection (classification, ~10 models). We extend to 21 tasks
and 46 models.

**2.3 LLM-as-judge** — MT-Bench introduced LLM judges. Known biases: position
bias, verbosity bias, self-enhancement bias. Our contribution: we quantify
format bias specifically and show it distorts cost-quality comparisons.

**2.4 Model routing** — RouterBench, RouterArena benchmark routers. We produce
the underlying data that routers use. Complementary, not competing.

---

### 3. Methodology (2.5 pages)

**3.1 Task selection (0.5 page)**

21 production tasks in 4 categories:
- Classification (4 tasks, exact-match): sentiment, intent-150, moderation, multistep
- Structured output (5 tasks, LLM-judge): extraction, JSON transform, NER, function calling, structured output
- Generation (8 tasks, LLM-judge): code gen, code review, test gen, summarization (x2), email, data-to-text, code explanation
- Reasoning & language (4 tasks, LLM-judge): GSM8K, RAG QA, translation, instruction following

50 cases per task from standard datasets (SST-2, CLINC-150, GSM8K, ToxiGen,
Spider, OPUS-100, SQuAD v2, HumanEval, ARC-Challenge) and hand-curated sets.

**3.2 Model selection (0.25 page)**

46 complete models across 4 price tiers and 9 API providers. Table in appendix.
Selection criteria: API availability, price tier coverage, provider diversity.

**3.3 Cost measurement (0.25 page)**

Per-query cost from token counts × provider-published prices. Prices snapshot
at benchmark time (April-May 2026). Reasoning model costs include thinking
tokens (verified via API: completion_tokens includes reasoning_tokens).

**3.4 The judge problem: format bias in LLM evaluation (1 page)**

This is the key methodological section.

**3.4.1 Setup.** We initially used GPT-4o-mini with generic quality rubrics
("rate 1-5 for quality"). Standard practice in the field.

**3.4.2 Discovery.** On tasks with ground truth (GSM8K, RAG QA), the judge
score correlated poorly with actual correctness (r=0.388, r=-0.013). The judge
rewarded concise formatting over correct content. Claude Opus (96% accuracy)
scored 3.5/5 on GSM8K. Mistral Small (34% RAG accuracy) scored 4.4/5.

**3.4.3 Diagnosis.** The bias is systematic and directional: verbose reasoning
models are penalized, concise models are rewarded regardless of correctness.
This specifically distorts cost-quality comparisons because Economy models
produce shorter, "cleaner" output that the judge prefers.

**3.4.4 Fix.** Task-specific correctness rubrics with explicit anchors
("5 = numerical answer matches expected"). Upgraded to GPT-4o. Anti-format
instruction: "Ignore formatting, verbosity, and style."

**3.4.5 Validation.** r jumped to 0.905 (GSM8K) and 0.887 (RAG QA). The fix
was extended to all 17 LLM-judged tasks (40,350 cases re-scored).

**3.5 Statistical methods (0.25 page)**

Bootstrap CIs (1000 iterations). Mann-Whitney U for tier comparisons. Tier
boundary sensitivity (+/-50%).

---

### 4. Results (2.5 pages)

**4.1 The cost-quality landscape (0.5 page)**

Heatmap figure: 46 models × 21 tasks. Key observation: the right side
(generative tasks) shows more variance than the left (classification).
Most of the map is green (4.5+). Red spots concentrated on Micro tier
and high-discrimination tasks.

**4.2 Economy vs Premium: no significant gap (0.75 page)**

Tier comparison with bootstrap CIs. Premium 4.791 [4.729, 4.853] vs
Economy 4.749 [4.715, 4.777]. Gap: 0.042 points. Mann-Whitney p>0.05 on
all 21 tasks. Robust to tier boundary variation.

Caveat paragraph: n=2 Premium limits power. The finding is "no difference
detected," not "no difference exists."

**4.3 Task discriminativeness (0.5 page)**

Bar chart: spread per task. 10 high-discrimination (1.5-3.2), 9 medium
(0.8-1.5), 2 low (<0.8). On low-discrimination tasks, any model works.
On high-discrimination tasks, model choice means 1.5/5 vs 4.7/5.

**4.4 Per-task Pareto frontiers (0.5 page)**

3-4 representative dual-panel figures (RAG QA, ToxiGen, Data-to-Text,
Code Review). Each shows the dense cheap cluster + expensive outliers.
Key observation: Premium models are rarely on the frontier.

**4.5 Routing savings (0.25 page)**

Table: single model vs per-task routing at different quality thresholds.
70% savings at threshold 4.0. The savings come from commodity tasks where
a $0.00001/query model suffices.

---

### 5. Discussion (1 page)

**5.1 Implications for practitioners (0.5 page)**

Three practical recommendations:
1. Default to Economy tier for most production tasks
2. Use per-task routing for maximum savings
3. Reserve Premium/reasoning models for high-discrimination tasks only

**5.2 Implications for evaluation methodology (0.5 page)**

The judge bias finding generalizes beyond this benchmark. Any LLM-as-judge
evaluation using generic quality rubrics likely has format bias. We recommend:
- Always validate against ground truth on 2+ tasks
- Use task-specific correctness rubrics with explicit anchors
- Report both judge score and native accuracy where available

---

### 6. Limitations (0.5 page)

- n=2 Premium models
- Judge validated on 2/17 LLM-judged tasks (extrapolated to 15)
- 50 cases per task (CI +/-0.2)
- Single-turn only
- Prices snapshot (April-May 2026)
- Potential contamination (models may have seen standard datasets)
- English-only (except EN-FR translation)

---

### 7. Conclusion (0.25 page)

TaskBench shows that for most production LLM tasks, Economy models deliver
quality indistinguishable from Premium at 10-100x lower cost. We also show
that standard LLM-as-judge evaluation has a format bias that distorts
cost-quality comparisons. We release the full dataset and evaluation prompts.

---

## 3. Length

**Target: 8 pages main + 4-6 pages appendix = 12-14 total.**

8 pages is tight for the content above. The judge bias section (3.4) alone
needs 1 full page. But 8 pages forces concision, which makes for a better
paper on arXiv/Twitter. Everything that doesn't fit goes to appendix.

For HN/Twitter reach: 8 pages is ideal. People read the abstract + figures.
The blog post covers the accessible version.

---

## 4. Figures

### Main paper (6 figures)

| # | Figure | What it shows | Finding supported |
|---|--------|--------------|-------------------|
| 1 | **Heatmap** (46×21) | Full landscape overview | F3 (discriminative vs commodity) |
| 2 | **Judge bias before/after** | r=0.35 → r=0.90 scatter plot, V1 vs V2 on GSM8K | Methodology contribution |
| 3 | **Tier comparison** with CIs | Premium/Standard/Economy/Micro bar chart per task | F1 (Economy ≈ Premium) |
| 4 | **Pareto dual-panel: RAG QA** | High-discrimination task, cheap cluster + Premium outliers | F6, shows model diversity |
| 5 | **Pareto dual-panel: Data-to-Text** | Commodity task, everything clustered at 4.5+ | F3, shows "any model works" |
| 6 | **Task discriminativeness** | Horizontal bar chart, spread per task | F3, overview |

### Appendix figures

- 19 remaining Pareto dual-panels (one per task)
- Score distribution shift V1→V2 per task (table or small multiples)
- Routing savings sensitivity table (thresholds 3.5/4.0/4.5/4.8)
- Full model table with prices, providers, case counts
- Bootstrap CI table per (task, tier)
- Judge prompts V1 and V2 (full text)

---

## 5. Judge Bias: Structural Position

### Recommendation: Part of Methodology (section 3.4), not a separate section.

**Why in Methodology, not Results:**

The judge bias is not a "result" of the benchmark — it's a methodological
problem we discovered and fixed BEFORE reporting results. Putting it in
Methodology says: "here is how we ensured our evaluation is reliable."
Putting it in Results says: "here is something we found" — which undersells
it and confuses the narrative flow.

However, section 3.4 is the longest methodology sub-section (1 page). This
is unusual but justified: the fix is the most original contribution.

**In Results:** Reference it briefly in 4.2 (tier comparison): "Using V1
(uncorrected) judge, the gap appears to be 0.000. With V2 (corrected),
the gap is 0.042. Both are non-significant." This shows the judge fix matters
but doesn't change the structural finding.

---

## 6. Manifest Disclosure

### Recommendation: Conflict of interest statement after Acknowledgments.

**Placement:** Standard academic practice is a "Conflict of Interest" or
"Author Disclosure" section after the main text, before References.

**Wording:**

> **Disclosure.** The first author is the founder of Manifest, an open-source
> LLM model router. Manifest was not used in this benchmark. The routing
> savings analysis (Section 4.5) is based on the benchmark data and applies
> to any routing system, not specifically to Manifest. All code, data, and
> evaluation prompts are publicly available at [GitHub URL].

**Why this wording:**
- States the affiliation clearly
- States Manifest was not used (the benchmark ran direct API calls)
- States the routing finding is generic (not a Manifest ad)
- Points to open data (reproducibility = trust)

**Do NOT:** Put the disclosure in a footnote (looks like hiding). Do NOT
omit it (will be discovered and damage credibility).
