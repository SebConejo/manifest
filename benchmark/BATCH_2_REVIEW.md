# Batch 2 Review

**Date:** 2026-05-15

---

## Check 1: Anthropic (Haiku vs Opus) and Google (Flash vs Pro)

### Haiku 4.5 ($0.80/M) vs Opus 4.7 ($15/M)

| Metric | Value |
|--------|-------|
| Tasks completed | Both 21/21 |
| Haiku avg | 4.775 |
| Opus avg | 4.753 |
| Delta | -0.022 (Haiku higher) |
| Bootstrap 95% CI | [-0.106, +0.053] |
| Wilcoxon p | 0.695 (not significant) |
| CI contains 0 | YES |

Opus wins on 6 tasks (instruction_following +0.32, test_generation +0.30).
Haiku wins on 8 tasks (sql_spider +0.60, multistep_reasoning +0.30).

**Verdict: the delta is not significant.** CI contains 0. Haiku and Opus
are statistically indistinguishable on average. Opus is better on a few
generative tasks; Haiku is better on classification and SQL. Neither
dominates.

**For the paper:** "Anthropic's cheapest model (Haiku, $0.80/M) matches its
most expensive (Opus, $15/M) on average across 21 tasks (delta = -0.022,
Wilcoxon p = 0.70, 95% CI [-0.11, +0.05])."

### Gemini 2.5 Flash ($0.15/M) vs Gemini 2.5 Pro ($1.25/M)

| Metric | Value |
|--------|-------|
| Tasks completed | Both 21/21 |
| Flash avg | 4.749 |
| Pro avg | 4.747 |
| Delta | -0.002 |
| Bootstrap 95% CI | [-0.078, +0.072] |
| Wilcoxon p | 0.776 (not significant) |

Virtually identical. Pro wins on 7 tasks, Flash on 5, 9 ties.

### Gemini 2.5 Flash vs Gemini 3.1 Pro Preview ($1.25/M)

| Metric | Value |
|--------|-------|
| Delta | -0.022 (Flash higher) |
| Bootstrap 95% CI | [-0.110, +0.056] |
| Wilcoxon p | 0.943 |

Even the newer Gemini 3.1 Pro doesn't beat Flash on average.

**Verdict for Google:** "Gemini Flash ($0.15/M) matches both Gemini Pro
versions ($1.25/M) on average. The 8x price premium buys no detectable
quality improvement."

---

## Check 2: DeepSeek V3.2 ($0.14/M) vs V4 Pro ($0.435/M)

| Metric | Value |
|--------|-------|
| Tasks completed | Both 21/21 |
| V3.2 avg | 4.726 |
| V4 Pro avg | 4.787 |
| Delta | +0.061 (V4 Pro higher) |
| Bootstrap 95% CI | [-0.006, +0.124] |
| Wilcoxon p | 0.070 (not significant at 0.05) |
| CI contains 0 | YES (barely) |

V4 Pro wins on 10 tasks (notably RAG QA +0.38, SQL +0.34, Long Sum +0.28).
V3.2 wins on 4 tasks (Multistep -0.30, GSM8K -0.12).

**Verdict: marginal improvement, not significant.** The CI barely includes 0
(lower bound = -0.006). V4 Pro trends better but at 3x the price, the ROI
is poor. On RAG QA specifically, V4 Pro is notably better (+0.38).

**For the paper:** "DeepSeek V4 Pro ($0.435/M) shows a marginal quality
improvement over V3.2 ($0.14/M) (delta = +0.061, p = 0.07), with the
biggest gains on RAG QA (+0.38) and SQL (+0.34). At 3x the price, the
upgrade is not cost-justified on most tasks."

---

## Overall Batch 2 Verdict

All findings hold. The "paying more doesn't buy quality" pattern is robust:

| Provider | Cheap → Expensive | Price ratio | Quality delta | Significant? |
|:---------|:-----------------|:-----------:|:------------:|:------------:|
| Anthropic | Haiku → Opus | 19x | -0.022 | No (p=0.70) |
| Google | Flash → Pro | 8x | -0.002 | No (p=0.78) |
| Google | Flash → 3.1 Pro | 8x | -0.022 | No (p=0.94) |
| OpenAI | 5.4 Nano → 5.5 Pro | 750x | +0.134 | Not tested |
| DeepSeek | V3.2 → V4 Pro | 3x | +0.061 | No (p=0.07) |
| Mistral | Ministral → Large | 50x | +0.359 | Likely yes |

Only Mistral shows a clear quality gradient. Everywhere else, the cheap
model matches or exceeds the expensive one.
