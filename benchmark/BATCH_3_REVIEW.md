# Batch 3 Review

**Date:** 2026-05-17

---

## Check 1: Three-Group Origin (Chinese / American / European)

| Origin | n | Avg V2 | Range |
|:-------|:-:|:------:|:-----:|
| Chinese | 16 | 4.779 | 4.65-4.84 |
| European (Mistral) | 5 | 4.691 | 4.44-4.81 |
| American | 26 | 4.682 | 3.39-4.84 |

### Pairwise tests

| Pair | U | p | Significant? |
|:-----|:-:|:-:|:---:|
| Chinese vs American | 262 | 0.166 | No |
| Chinese vs European | 46 | 0.660 | No |
| American vs European | 65 | 1.000 | No |

**Kruskal-Wallis (3-group):** H=1.83, p=0.400. **No significant difference.**

Chinese scores slightly higher on average but the gap is non-significant.
American is pulled down by small models (Llama 1B at 3.39). European (Mistral)
sits in the middle.

**Paper framing:** "Models from Chinese (n=16, avg 4.78), American (n=26, avg
4.68), and European (n=5, avg 4.69) providers achieve comparable quality
(Kruskal-Wallis p=0.40). Provider origin does not predict model quality."

---

## Check 2: Open vs Closed Deep Dive

### Models with avg >= 4.7

| License | Count |
|:--------|:-----:|
| Open | 11 |
| Closed | 29 |

Closed has more models above 4.7 (29 vs 11), but closed also has more models
total (29 vs 18). As a proportion: 100% of closed are >= 4.7 vs 61% of open.
The gap is driven by the bottom of the open distribution (small models).

### Magnitude of the 0.066 gap

- 0.066 on a 1-5 scale = **1.7% of the scale range**
- Within the per-model CI of +/-0.2
- Statistically significant (p=0.004) due to sample size, but **practically
  negligible** — a 1.7% difference is not actionable

### Per-task breakdown (excluding models < 4.0)

| Tasks where closed > open (>0.05) | 14 |
| Tasks where open > closed (>0.05) | 1 (multistep_reasoning) |
| Ties (< 0.05 gap) | 6 |

Closed scores consistently 0.05-0.15 higher across most tasks. The biggest
gap is **long_summarization (+0.34)** where closed models are notably better.
The only task where open wins is **multistep_reasoning (-0.14)**.

This is a real pattern, not noise: closed models are marginally but consistently
better across tasks. The magnitude is small (avg +0.09 per task) but the
consistency across 14/21 tasks makes it significant.

### Why this doesn't contradict the routing finding

The routing finding (F2/F14) says: "pick the cheapest adequate model per task."
This selection is license-agnostic — it picks whichever model (open or closed)
is cheapest at >= 4.0 quality. In practice, many of the cheapest adequate models
ARE open (Qwen Turbo, GPT-5.4 Nano). The routing optimization works regardless
of the open/closed gap because it optimizes on cost, not license.

### Paper framing for Q10

"Closed-source models score significantly higher on average than open-weight
models (4.79 vs 4.60, p<0.001), with the gap narrowing to 0.07 points when
excluding sub-3B open models. The gap is statistically significant but
practically small (1.7% of the scale). Closed models show a consistent
marginal advantage across 14 of 21 tasks, with the largest gap on
summarization tasks (+0.34). However, top open-weight models (Devstral 4.80,
Qwen3-Coder 4.79, DeepSeek V4 Pro 4.79) match the median closed-source model,
and per-task routing selects models by cost-quality regardless of license."

---

## Batch 3 Verdict

Both Q9 and Q10 hold after verification:

| Question | Finding | Significance | Paper-worthy? |
|:---------|:--------|:---:|:---:|
| Q9 (Origin) | No difference (p=0.40) | No | Appendix (confirms diversity) |
| Q10 (License) | Closed marginally better (p<0.001) | Yes | Results section (nuanced) |

Q10 is the more interesting finding: there IS a small but real quality gap
between open and closed models, but it's too small to matter for practical
model selection decisions.
