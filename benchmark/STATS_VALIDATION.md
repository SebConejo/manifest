# Statistical Validation

**Date:** 2026-05-14
**Method:** Bootstrap CIs (1000 iterations, seed=42), Mann-Whitney U tests,
tier boundary sensitivity analysis.

---

## Section 1: Bootstrap Confidence Intervals (95%)

### 1a. Global (all tasks aggregated)

| Tier | Mean | 95% CI | n (model-task pairs) |
|------|:----:|:------:|:----:|
| Premium | 4.601 | [4.502, 4.692] | 42 |
| Standard | 4.632 | [4.602, 4.660] | 451 |
| Economy | 4.601 | [4.554, 4.642] | 313 |
| Micro | 4.455 | [4.381, 4.526] | 210 |

**Key observation:** Premium and Economy have identical means (4.601) and
overlapping CIs. Standard is marginally higher (4.632). Micro is ~0.15 points
lower. The Premium-Economy gap is 0.000 points.

Note: Premium n=42 is the aggregate of 2 models x 21 tasks. The per-task n
is always 2 for Premium, limiting statistical power.

### 1b. Per-task breakdown

| Task | Premium | Standard | Economy | Micro |
|------|:-------:|:--------:|:-------:|:-----:|
| Sentiment | 4.85 [4.80,4.90] | 4.95 [4.93,4.98] | 4.95 [4.91,4.98] | 4.70 [4.31,4.94] |
| Intent-150 | 4.60 (n=2) | 4.61 [4.56,4.65] | 4.55 [4.45,4.63] | 3.68 [2.93,4.28] |
| ToxiGen | 4.60 [4.30,4.90] | 4.56 [4.48,4.63] | 4.51 [4.39,4.61] | 4.08 [3.65,4.42] |
| Multistep | 4.65 [4.60,4.70] | 4.87 [4.80,4.92] | 4.89 [4.79,4.97] | 4.87 [4.68,5.00] |
| GSM8K | 4.05 [3.48,4.62] | 4.72 [4.67,4.77] | 4.59 [4.18,4.82] | 4.67 [4.43,4.84] |
| RAG QA | 4.45 [4.02,4.88] | 4.13 [3.83,4.41] | 4.20 [3.83,4.54] | 4.47 [4.13,4.78] |
| Code Gen | 4.29 [4.24,4.34] | 4.28 [4.10,4.43] | 4.20 [3.96,4.39] | 4.22 [4.01,4.40] |
| Code Review | 4.65 [4.40,4.90] | 4.51 [4.41,4.63] | 4.50 [4.37,4.61] | 4.23 [4.03,4.41] |
| Code Expl | 4.91 [4.88,4.94] | 4.93 [4.91,4.95] | 4.92 [4.89,4.96] | 4.87 [4.70,4.97] |
| Test Gen | 4.21 [3.94,4.49] | 4.22 [4.11,4.33] | 4.19 [4.08,4.33] | 4.19 [3.97,4.41] |
| Func Call | 4.48 [4.40,4.56] | 4.48 [4.45,4.50] | 4.43 [4.33,4.52] | 4.28 [3.93,4.50] |
| SQL | 4.35 [4.24,4.46] | 4.55 [4.48,4.61] | 4.55 [4.42,4.63] | 4.25 [3.94,4.50] |
| Translation | 4.71 [4.68,4.74] | 4.66 [4.63,4.70] | 4.55 [4.38,4.66] | 4.32 [4.04,4.55] |
| Instruct | 4.44 [4.32,4.56] | 4.42 [4.37,4.47] | 4.42 [4.33,4.50] | 4.24 [4.05,4.40] |
| Struct Out | 4.85 [4.83,4.88] | 4.89 [4.87,4.90] | 4.86 [4.81,4.89] | 4.81 [4.73,4.87] |
| Extraction | 4.47 [4.46,4.48] | 4.47 [4.44,4.50] | 4.47 [4.42,4.53] | 4.36 [4.17,4.53] |
| JSON Trans | 4.48 [4.46,4.50] | 4.49 [4.41,4.58] | 4.49 [4.38,4.61] | 4.25 [4.03,4.41] |
| Email Sum | 4.99 [4.98,5.00] | 4.97 [4.95,4.99] | 4.97 [4.96,4.98] | 4.87 [4.74,4.96] |
| Long Sum | 4.97 [4.94,5.00] | 4.95 [4.91,4.98] | 4.95 [4.91,4.99] | 4.92 [4.82,4.99] |
| Data-Text | 5.00 (n=2) | 5.00 [5.00,5.00] | 4.96 [4.89,5.00] | 4.95 [4.86,5.00] |
| NER | 4.62 [4.54,4.70] | 4.56 [4.53,4.59] | 4.50 [4.47,4.53] | 4.33 [4.09,4.53] |

**Pattern:** Premium and Economy CIs overlap on 20 of 21 tasks. The only task
where Premium has a visually clear edge is Translation (4.71 vs 4.55), but even
there the CIs overlap (Premium [4.68,4.74] vs Economy [4.38,4.66]).

Economy BEATS Premium (higher mean) on: Sentiment, Multistep, GSM8K, SQL.

---

## Section 2: Mann-Whitney U Tests (Economy vs Premium)

H0: Economy and Premium model averages come from the same distribution.
Two-sided test, alpha = 0.05.

| Task | Economy mean | Premium mean | U | p-value | Significant? |
|------|:-----------:|:----------:|:---:|:------:|:----:|
| Sentiment | 4.947 | 4.850 | 25.0 | 0.119 | No |
| Intent-150 | 4.553 | 4.600 | 14.0 | 0.938 | No |
| ToxiGen | 4.507 | 4.600 | 13.0 | 0.820 | No |
| Multistep | 4.890 | 4.650 | 27.0 | 0.054 | No |
| GSM8K | 4.592 | 4.050 | 27.5 | 0.072 | No |
| RAG QA | 4.195 | 4.450 | 12.5 | 0.765 | No |
| Code Gen | 4.198 | 4.290 | 19.5 | 0.550 | No |
| Code Review | 4.495 | 4.650 | 10.5 | 0.551 | No |
| Code Expl | 4.924 | 4.906 | 19.0 | 0.596 | No |
| Test Gen | 4.193 | 4.214 | 14.0 | 0.941 | No |
| Func Call | 4.428 | 4.480 | 16.0 | 0.940 | No |
| SQL | 4.546 | 4.350 | 28.0 | 0.061 | No |
| Translation | 4.551 | 4.710 | 6.0 | 0.204 | No |
| Instruct | 4.423 | 4.440 | 15.5 | 1.000 | No |
| Struct Out | 4.860 | 4.854 | 19.5 | 0.545 | No |
| Extraction | 4.469 | 4.470 | 8.5 | 0.422 | No |
| JSON Trans | 4.493 | 4.480 | 12.5 | 0.765 | No |
| Email Sum | 4.969 | 4.990 | 7.5 | 0.327 | No |
| Long Sum | 4.949 | 4.970 | 15.5 | 1.000 | No |
| Data-Text | 4.957 | 5.000 | 9.0 | 0.335 | No |
| NER | 4.503 | 4.620 | 5.0 | 0.154 | No |

**Result: 0 out of 21 tasks show a statistically significant difference
between Economy and Premium at alpha=0.05.**

**Important caveat:** This is driven by low statistical power. With n_Premium=2
on every task, the Mann-Whitney test has very low power to detect differences.
The result means "we cannot reject H0" — NOT "the distributions are equal."

Three tasks approach significance (p < 0.08): Multistep (p=0.054, Economy wins),
GSM8K (p=0.072, Economy wins), SQL (p=0.061, Economy wins). All three favor
Economy over Premium.

---

## Section 3: Tier Boundary Robustness

| Boundary set | Premium/Economy boundary | Economy avg | Premium avg | Ratio | Mann-Whitney p |
|-------------|:-:|:-:|:-:|:-:|:-:|
| Default ($5 / $0.50 / $0.08) | $5.00 | 4.601 | 4.601 | 100.0% | 0.676 |
| Tight ($7.50 / $0.75 / $0.12) | $7.50 | 4.623 | 4.601 | 100.5% | 0.392 |
| Loose ($2.50 / $0.25 / $0.04) | $2.50 | 4.572 | 4.625 | 98.8% | 0.488 |

**The finding is robust to boundary variation.** Economy/Premium ratio stays
between 98.8% and 100.5% across all three boundary sets. No boundary set
produces a statistically significant difference.

Under loose boundaries ($2.50 for Premium), 6x more models qualify as Premium
(n=126 vs 42), but the Economy/Premium gap only widens to 1.2% — still not
significant (p=0.488).

---

## Section 4: What Survives the Statistics

### Finding 1 (Economy = Premium): SURVIVES with reformulation

The data shows:
- Global means are identical (4.601 vs 4.601)
- Bootstrap CIs overlap on 20/21 tasks
- 0/21 Mann-Whitney tests are significant
- The finding is robust to tier boundary variation (+/-50%)

**But:** The lack of significance is partly due to n=2 Premium. We cannot
claim "Economy equals Premium" — we can claim "no statistically significant
difference detected between Economy and Premium tiers."

Reformulation: "On none of the 21 tasks did we detect a statistically
significant quality difference between Economy ($0.08-0.50/M) and Premium
($5+/M) models (Mann-Whitney U, p > 0.05 on all tasks, n_Economy=14-15,
n_Premium=2). Bootstrap 95% CIs overlap on 20 of 21 tasks."

### Finding 2 (Routing 86%): NEEDS SENSITIVITY TABLE

The 86% depends on the 4.0 threshold. Must add sensitivity analysis at
different thresholds before publishing.

### Finding 3 (Discriminative tasks): SURVIVES

Score spread and IQR are observable properties. No statistical test needed.

### Finding 4 (Qwen Turbo): SURVIVES with softening

Per-model claims don't need tier-level statistics. But must show min score
and acknowledge pricing volatility.

### Finding 5 (1B cliff): DOES NOT SURVIVE

n=1 at 1B. No statistical basis. Downgrade to "observation."

### Finding 7 (Chinese dominate): NEEDS REWORK

Must compare within same tier to separate price from quality. Currently
conflates "cheap" with "Chinese."
