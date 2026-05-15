# Paper Strategy

**Date:** 2026-05-15
**Status:** Pre-writing strategy. All data final (51,580 rows, 46 models,
21 tasks, V2 judge validated at r=0.90).

---

## Q1: Angle Principal

### Candidats

| Angle | Strength | Weakness |
|-------|----------|----------|
| "Economy ≈ Premium" | Commercially relevant, practitioners care | n=2 Premium, stat power too low to claim equality |
| "LLM-judge bias revealed" | Methodologically novel, r=0.35→0.90 | Niche audience, less commercially exciting |
| "Routing saves 70%" | Directly validates Manifest, actionable | Reads as marketing, reviewers will be skeptical |
| "Per-task cost-quality Pareto" | The actual dataset contribution | Descriptive, not a strong claim |

### Recommendation: Lead with the methodology story, use cost-quality as the payload.

The strongest, most defensible angle is **"How to measure LLM cost-quality,
and what we found when we did it right."** This combines:

1. **Methodological contribution** (novel, defensible):
   - We show that a generic LLM judge (r=0.35) is unreliable
   - We show that correctness-focused rubrics fix it (r=0.90)
   - We show the format bias systematically inflates Economy and deflates Premium
   - This is a contribution to evaluation methodology, not just a leaderboard

2. **Empirical contribution** (the dataset, the findings):
   - 46 models × 21 tasks × 50 cases = largest per-task cost-quality benchmark
   - Cost as a first-class axis (unique vs HELM, Arena, MMLU)
   - 7 findings on the cost-quality landscape

3. **Practical contribution** (routing, Pareto frontiers):
   - Per-task Pareto frontiers as a decision tool
   - Routing savings quantified

The paper title would be something like:

> **TaskBench: Measuring LLM Cost-Quality Tradeoffs Across 21 Production Tasks**

Not "Economy models match Premium" (too strong a claim). Not "Routing saves money"
(too commercial). The benchmark IS the contribution; the findings are what we
found inside it.

---

## Q2: Audience Cible

### Recommendation: Practitioners first, academics as validators.

| Audience | What they want | How to serve them |
|----------|---------------|-------------------|
| **ML practitioners** (primary) | "Which model for my use case, at what cost?" | Pareto frontiers, top-5 tables, routing guide |
| **Evaluation researchers** (secondary) | "How to evaluate LLMs reliably?" | Judge bias analysis, dual-metric validation |
| **CTOs/founders** (tertiary) | "Should we use expensive models?" | Executive summary, tier comparison |

The paper should be readable by a senior ML engineer. No heavy math. Tables and
figures carry the argument. The methodology section should be rigorous enough for
academic review but not drown in formalism.

**Structure implication:** Short paper (8 pages + appendix) with:
- 2 pages methodology (judge validation is the key novel bit)
- 3 pages results (5-6 figures, key findings)
- 1 page discussion (routing, practical implications)
- 2 pages intro + related work + conclusion
- Appendix: full Pareto frontiers (21 tasks), complete model table, judge prompts

---

## Q3: Scope

### Recommendation: One paper + one companion blog post.

**The paper** (arXiv): Full methodology, judge validation, 7 findings with
statistical backing. Written for the ML community. Citable.

**The blog post** (manifest.build/blog): "Which LLM should you use? We tested
46 models." Pareto frontiers, top-5 per task, routing savings. Written for
practitioners. Links to the paper for methodology.

**Why not multiple papers:** We don't have enough depth in any sub-area for a
second paper. The judge bias finding alone is not enough (fix is simple, not
a research contribution). The cost analysis alone is descriptive (no new
method).

---

## Q4: Venue

### Recommendation: arXiv direct, consider COLM 2027 as follow-up.

| Venue | Pros | Cons | Timeline |
|-------|------|------|----------|
| **arXiv** (cs.CL + cs.LG) | Immediate, no review gatekeeping, citable | No prestige, no feedback | 2 weeks |
| NeurIPS Datasets & Benchmarks | Prestigious, right track | 6 month cycle, may reject for "too applied" | Dec 2026 |
| ACL | Top NLP venue | Benchmark papers often rejected as "not novel enough" | 6 months |
| **COLM** (Conference on LMs) | New venue, benchmark-friendly, right audience | Less established | ~6 months |
| EMNLP | Good for empirical work | Competitive | 6 months |

**arXiv first** because:
1. The data becomes stale fast (new models monthly). A 6-month review cycle
   means the models are outdated by publication.
2. The benchmark is the contribution, not a novel algorithm. Peer review adds
   rigor but doesn't change the dataset.
3. We can submit to COLM 2027 later with an updated version (more models,
   deeper analysis) if the arXiv version gets traction.

**Risk of arXiv-only:** No peer review means any methodological weakness is
discovered in public, not in private review. Our FINDINGS_CRITIQUE.md
self-review mitigates this.

---

## Q5: Positionnement vs Benchmarks Existants

### What exists and what we add

| Benchmark | What it does | What we add |
|-----------|-------------|-------------|
| **HELM** (Stanford) | Comprehensive multi-metric evaluation | We add **cost as a primary axis**. HELM measures quality only. |
| **Chatbot Arena** (LMSYS) | Human preference ranking | We provide **per-task granularity**. Arena gives one Elo score. |
| **MMLU / MMLU-Pro** | Academic knowledge testing | We measure **production tasks**, not exam questions. |
| **Berkeley Function Calling** | Function calling leaderboard | We cover function calling + 20 other tasks. |
| **MT-Bench** | Multi-turn conversation quality | We're single-turn. Different scope. |
| **Artificial Analysis** | Speed + price comparison | We add **per-task quality**. They show aggregate. |
| **RouterBench / RouterArena** | Router evaluation | We benchmark **models**, they benchmark **routers**. Our data is what routers use to make decisions. |

**Our unique position:**
1. **Cost-quality Pareto per task** — nobody else does this
2. **46 models × 21 tasks** — broader than any per-task benchmark
3. **Judge bias validation** — we show the evaluation matters, not just the scores
4. **Open data** — all 51,580 rows + 51,705 raw responses publicly available

**One-line pitch for Related Work:**
"TaskBench is the first benchmark to systematically measure per-task cost-quality
tradeoffs across 46 LLM models from 9 providers, with a validated correctness-
focused evaluation methodology."

---

## Q6: Risques Principaux

### Risk 1: "n=2 Premium is too small" (CRITICAL)

A reviewer will say: "You claim Economy matches Premium based on 2 Premium
models. That's anecdotal, not statistical."

**Mitigation:** We don't claim equality. We say "no significant difference
detected" and explicitly state n=2 as a limitation. We frame it as: "even
with only 2 Premium models, the data suggests the gap is < 0.3 points." The
finding is suggestive, not conclusive.

### Risk 2: "Your judge isn't validated on 15 of 17 tasks" (HIGH)

We validated on GSM8K and RAG QA (r=0.90) but extrapolated to 15 other tasks
without ground truth.

**Mitigation:** We report the validation honestly. We note that the rubric
mechanism is identical across all tasks. We offer the V1→V2 comparison as
evidence that the fix generalizes (consistent direction of change across
all 15 tasks).

### Risk 3: "Prices change, your benchmark is instantly outdated" (MEDIUM)

LLM prices drop monthly. Our cost comparisons have a shelf life of weeks.

**Mitigation:** We frame results at the tier level (Premium/Standard/Economy/Micro),
not at the model level. Tier-level findings are more durable because relative
pricing between tiers rarely inverts. We publish the raw data so anyone can
recompute with current prices.

### Risk 4: "50 cases per task is too few" (MEDIUM)

Our CI is +/-0.2 on a 1-5 scale. Differences < 0.3 are not significant.

**Mitigation:** We report CIs on every comparison. We avoid claiming significance
where we don't have it. 50 cases is standard for benchmark papers (HELM uses
similar per-task sample sizes).

### Risk 5: "This is an ad for Manifest" (HIGH)

The routing savings finding directly validates the authors' commercial product.

**Mitigation:**
1. The routing calculation is reproducible (code + data public)
2. We compare against multiple baselines, not just "Manifest vs nothing"
3. The finding is: "routing helps" — true for any router, not just Manifest
4. We disclose the conflict of interest in the paper

### Risk 6: "No multi-turn, no vision, no audio" (LOW)

Valid limitation but doesn't invalidate what we DID test.

**Mitigation:** Listed in Limitations section. Frame as future work.

---

## Recommended Paper Structure

```
Title: TaskBench: Measuring LLM Cost-Quality Tradeoffs
       Across 21 Production Tasks

Abstract (200 words)

1. Introduction (1.5 pages)
   - The problem: practitioners choose models by gut, not data
   - What's missing: per-task cost-quality benchmarks
   - Our contribution: 46 models, 21 tasks, validated judge

2. Related Work (0.5 pages)
   - HELM, Arena, MMLU, RouterBench positioning

3. Methodology (2 pages)
   - 3.1 Task selection and datasets
   - 3.2 Model selection and provider diversity
   - 3.3 Evaluation: the judge bias problem and our fix
         (r=0.35 → 0.90, this is the novel bit)
   - 3.4 Cost measurement
   - 3.5 Statistical methods (bootstrap, Mann-Whitney)

4. Results (3 pages)
   - 4.1 The cost-quality landscape (heatmap)
   - 4.2 Per-task Pareto frontiers (3-4 representative figures)
   - 4.3 Tier comparison with CIs (Economy ≈ Premium)
   - 4.4 Task discriminativeness
   - 4.5 Routing savings

5. Discussion (1 page)
   - 5.1 Practical implications (routing, model selection)
   - 5.2 The judge bias finding (evaluation methodology)
   - 5.3 Limitations

6. Conclusion (0.5 pages)

Appendix:
   A. Full Pareto frontiers (21 tasks)
   B. Complete model table with prices
   C. Judge prompts V1 and V2
   D. Statistical tables
```

---

## Timeline

| Week | Deliverable |
|------|------------|
| 1 | Draft sections 3-4 (methodology + results). Generate final figures. |
| 2 | Draft sections 1-2, 5-6 (intro, related work, discussion). |
| 3 | Internal review. Fix issues. Polish figures. |
| 4 | Submit to arXiv. Write companion blog post. |
