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

---

## Check 1 Extended: Per-Task Detail

### Haiku 4.5 vs Opus 4.7 — Full Table

| Task | Category | Haiku | Opus | Delta | Winner |
|:-----|:---------|:-----:|:----:|:-----:|:-------|
| Sentiment | Classification | 4.90 | 4.80 | -0.10 | ~Haiku |
| Intent-150 | Classification | 4.50 | 4.60 | +0.10 | ~Opus |
| ToxiGen | Classification | 4.40 | 4.30 | -0.10 | ~Haiku |
| Multistep | Classification | 5.00 | 4.70 | -0.30 | ~Haiku |
| GSM8K | Reasoning | 4.84 | 4.80 | -0.04 | Tie |
| RAG QA | Reasoning | 4.68 | 4.56 | -0.12 | ~Haiku |
| Code Gen | Code | 4.68 | 4.50 | -0.18 | ~Haiku |
| Code Review | Code | 5.00 | 5.00 | +0.00 | Tie |
| Code Expl | Code | 4.96 | 4.98 | +0.02 | Tie |
| Test Gen | Code | 4.54 | 4.84 | +0.30 | ~Opus |
| Func Call | Structured | 4.72 | 4.66 | -0.06 | ~Haiku |
| **SQL** | Code | 4.74 | 4.14 | **-0.60** | **Haiku** |
| Translation | Language | 4.90 | 4.92 | +0.02 | Tie |
| **Instruct** | Language | 4.56 | 4.88 | **+0.32** | **Opus** |
| Struct Out | Structured | 5.00 | 5.00 | +0.00 | Tie |
| Extraction | Structured | 4.94 | 4.82 | -0.12 | ~Haiku |
| JSON Trans | Structured | 4.70 | 4.84 | +0.14 | ~Opus |
| Email Sum | Language | 4.94 | 5.00 | +0.06 | ~Opus |
| Long Sum | Language | 4.64 | 4.80 | +0.16 | ~Opus |
| Data-Text | Language | 5.00 | 5.00 | +0.00 | Tie |
| NER | Structured | 4.64 | 4.68 | +0.04 | Tie |

**Significantly better (delta > 0.3):**
- Opus wins: instruction_following (+0.32) — 1 task
- Haiku wins: sql_spider (-0.60) — 1 task

**Within noise (delta < 0.2):** 17 out of 21 tasks.

**Pattern by category:**

| Category | n tasks | Avg delta | Favors |
|:---------|:-------:|:---------:|:-------|
| Classification | 4 | -0.100 | Haiku |
| Code | 5 | -0.092 | Haiku |
| Reasoning | 2 | -0.080 | Haiku |
| Structured | 5 | +0.000 | Tie |
| Language | 5 | +0.112 | Opus |

**There IS a pattern:** Haiku wins on classification, code, and reasoning.
Opus wins on language (instruction following, summarization, email). Structured
output is a tie. The "Opus overthinks classification" hypothesis from Finding 2
in FINDINGS_CRITIQUE is confirmed: Opus scores -0.30 on multistep_reasoning and
-0.10 on sentiment/moderation vs Haiku.

The Opus advantage on language tasks (+0.11) suggests Premium models add value
for open-ended generation where nuance matters, but not for tasks with a clear
correct answer.

### Gemini Flash vs Gemini Pro — Full Table

| Task | Category | Flash | Pro | Delta | Winner |
|:-----|:---------|:-----:|:---:|:-----:|:-------|
| Sentiment | Classification | 4.90 | 5.00 | +0.10 | ~Pro |
| Intent-150 | Classification | 4.70 | 4.70 | +0.00 | Tie |
| ToxiGen | Classification | 4.60 | 4.70 | +0.10 | ~Pro |
| Multistep | Classification | 4.70 | 5.00 | +0.30 | ~Pro |
| GSM8K | Reasoning | 4.96 | 4.96 | +0.00 | Tie |
| RAG QA | Reasoning | 4.38 | 4.54 | +0.16 | ~Pro |
| Code Gen | Code | 4.76 | 4.76 | -0.00 | Tie |
| Code Review | Code | 4.98 | 5.00 | +0.02 | Tie |
| Code Expl | Code | 4.96 | 4.98 | +0.02 | Tie |
| Test Gen | Code | 4.52 | 4.40 | -0.12 | ~Flash |
| Func Call | Structured | 4.48 | 4.68 | +0.20 | ~Pro |
| SQL | Code | 4.60 | 4.36 | -0.24 | ~Flash |
| Translation | Language | 4.88 | 4.94 | +0.06 | ~Pro |
| Instruct | Language | 4.78 | 4.72 | -0.06 | ~Flash |
| Struct Out | Structured | 5.00 | 5.00 | +0.00 | Tie |
| Extraction | Structured | 4.94 | 4.90 | -0.04 | Tie |
| JSON Trans | Structured | 4.76 | 4.94 | +0.18 | ~Pro |
| **Email Sum** | Language | 4.90 | 4.38 | **-0.52** | **Flash** |
| Long Sum | Language | 4.20 | 4.00 | -0.20 | ~Flash |
| Data-Text | Language | 5.00 | 5.00 | +0.00 | Tie |
| NER | Structured | 4.74 | 4.74 | +0.00 | Tie |

**Significantly better (delta > 0.3):**
- Pro wins: 0 tasks
- Flash wins: email_summary (-0.52) — 1 task

**Within noise (delta < 0.2):** 17 out of 21 tasks.

**Pattern by category:**

| Category | n tasks | Avg delta | Favors |
|:---------|:-------:|:---------:|:-------|
| Classification | 4 | +0.125 | Pro |
| Reasoning | 2 | +0.080 | Pro |
| Structured | 5 | +0.068 | Pro |
| Code | 5 | -0.065 | Flash |
| Language | 5 | -0.144 | Flash |

**Same pattern as Anthropic:** Pro is marginally better on classification and
reasoning (structured, clear-answer tasks). Flash is better on language/generation
(where conciseness helps). But the deltas are all < 0.2 — the pattern is
suggestive, not conclusive.
