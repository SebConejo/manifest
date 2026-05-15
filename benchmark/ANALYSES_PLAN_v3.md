# Analyses Plan v3 — Extended Judge Validation + NQ1 Clarification

**Date:** 2026-05-15

---

## Part 1: Three Additional Judge Validations

### Validation 3: translation_enfr (BLEU vs V2 score)

**Ground truth available:** YES. Dataset has `expected_translation` (reference
French) from OPUS-100 for all 50 cases.

**Method:**
- For each raw file: compute BLEU score between model response and expected_translation
  using `sacrebleu` or a simple 4-gram BLEU implementation.
- Per model: average BLEU across 50 cases = "native accuracy."
- Per model: average V2 judge score across 50 cases.
- Pearson r between the two series across ~48 models.

**Output:** r value, scatter plot.

**Feasibility:** HIGH. Reference translations exist. BLEU computation is
deterministic, no API calls needed. Need to `pip install sacrebleu` or
implement basic BLEU.

**Time:** 25 min.

**Risk:** BLEU is a coarse metric — it penalizes valid paraphrases. A model
that translates correctly but differently from the reference scores low on
BLEU but high on V2. This could produce a LOW correlation even if V2 is
correct. If r < 0.6, it might be BLEU's fault, not V2's. We should note this.

### Validation 4: code_generation (pass@1 vs V2 score)

**Ground truth available:** YES. Dataset has `expected_tests` (Python test
code from HumanEval) and `entry_point` for all 50 cases.

**Method:**
- For each raw file: extract the model's code, prepend the function signature
  from the prompt, append the test code from `expected_tests`, run with Python
  subprocess. Record pass (0 errors) or fail.
- Per model: pass@1 = fraction of 50 cases that pass all tests.
- Pearson r between pass@1 and avg V2 score across ~48 models.

**Output:** r value, scatter plot.

**Feasibility:** MEDIUM. Running arbitrary model-generated code is risky
(infinite loops, import errors, syntax errors). Need a sandboxed executor
with timeout. Each execution takes ~1-5 seconds. 48 models × 50 cases =
2,400 executions, ~30-60 min runtime.

**Time:** 45-60 min (script + execution + debugging failed cases).

**Risk:** MEDIUM. Some models generate code with subtle imports or dependencies
that break the test harness. The pass rate will be noisy. But this is the gold
standard for code generation evaluation — if V2 correlates with it, that's
strong evidence.

### Validation 5: function_calling (structural match vs V2 score)

**Ground truth available:** PARTIAL. Dataset has the list of available functions
and the user request, but NO expected function call.

**Method:** We can derive a structural check:
- Parse model response as JSON: `{"name": "...", "arguments": {...}}`
- Check (a) JSON valid, (b) function name exists in the available functions list
- This gives a "structural correctness" rate per model (not full correctness —
  we can't check argument values without ground truth)

**Alternative:** We CAN construct expected calls ourselves for the 50 cases
(they're hand-curated, the correct function is usually obvious from the input).
But that's manual work (~1 hour) and introduces subjectivity.

**Output:** r between structural_correctness and V2 score.

**Feasibility:** LOW-MEDIUM. Structural correctness (valid JSON + correct
function name) is a weak metric. Many models will have 100% structural
correctness but vary in argument correctness. The correlation will be noisy.

**Time:** 30 min for structural check. 1+ hour if we manually annotate expected calls.

**Risk:** HIGH that r is low — structural correctness is too coarse. A model
that calls the right function with wrong arguments passes structural but fails
in practice. V2 judge evaluates full correctness; this metric doesn't.

---

### Honest Assessment of the 3 Validations

| Validation | Ground truth quality | Expected r | Confidence in result |
|-----------|:---:|:---:|:---:|
| translation (BLEU) | Good (OPUS-100 refs) | 0.5-0.8 | MEDIUM — BLEU penalizes valid paraphrases |
| code_gen (pass@1) | Excellent (HumanEval tests) | 0.7-0.9 | HIGH — gold standard metric |
| func_call (structural) | Weak (no expected args) | 0.3-0.6 | LOW — metric too coarse |

**Recommendation:**

- **Do translation_enfr (BLEU)** — cheap, fast, informative even if r is moderate
  (BLEU is known to underperform on translation quality).
- **Do code_generation (pass@1)** — this is the strongest validation we can add.
  HumanEval pass@1 is the industry-standard metric. If V2 correlates with it,
  that's a powerful result.
- **Skip function_calling** — the ground truth is too weak. Structural match
  doesn't measure what V2 measures. A low r would be uninformative (the metric
  is bad, not the judge).

This gives us 4 validated tasks (GSM8K, RAG QA, Translation, Code Generation)
covering 3 task types (reasoning, extraction, generation). That's solid for a
paper.

---

## Part 2: NQ1 Ranking Flip Calculation — Precise Specification

### Definition

A **ranking flip** for a pair (M1, M2) on task T occurs when:
- V1: avg_score_V1(M1, T) > avg_score_V1(M2, T)
- V2: avg_score_V2(M1, T) < avg_score_V2(M2, T)
(or vice versa)

Tied scores (V1: M1 == M2) are excluded from the flip count. They are
counted separately as "tied pairs."

### Scope

- **Per task:** For each of the 17 LLM-judged tasks, compute flips among
  all model pairs. Report flip rate per task.
- **Global:** Aggregate across tasks. Report overall flip rate.
- Only models with >= 40 cases on the task are included.

### Computation

For a task with N models, there are N*(N-1)/2 ordered pairs.

```python
flips = 0
total = 0
tied = 0
for i in range(N):
    for j in range(i+1, N):
        v1_diff = v1_avg[i] - v1_avg[j]
        v2_diff = v2_avg[i] - v2_avg[j]
        if abs(v1_diff) < 0.001 or abs(v2_diff) < 0.001:
            tied += 1
            continue
        total += 1
        if (v1_diff > 0 and v2_diff < 0) or (v1_diff < 0 and v2_diff > 0):
            flips += 1

flip_rate = flips / total
```

### What constitutes a "meaningful" flip rate

No established benchmark in the literature for this exact metric. However:

- **Kendall tau** distance between V1 and V2 rankings is a related metric.
  Tau = 1 means identical, tau = -1 means perfectly reversed.
  `tau = 1 - 2 * flip_rate`

- In evaluation methodology papers (Zheng et al. 2023, "Judging LLM-as-a-Judge"),
  inter-judge agreement is typically measured by agreement rate (% of pairwise
  comparisons where two judges agree). High agreement = >80%. Moderate = 60-80%.
  Low = <60%.

- Our flip rate maps to agreement rate as: `agreement = 1 - flip_rate`.
  A flip rate of 15% means 85% agreement between V1 and V2 (moderate-high).
  A flip rate of 30% means 70% agreement (moderate).
  A flip rate of 50% means 50% (random).

### Interpretation guide

| Flip rate | Agreement | Interpretation |
|:---:|:---:|---|
| < 10% | > 90% | V1 and V2 largely agree. Judge fix had minimal ranking impact. |
| 10-20% | 80-90% | Some rankings changed. The fix corrected real biases. |
| 20-30% | 70-80% | Significant ranking instability. Judge choice matters. |
| > 30% | < 70% | Major instability. V1 rankings are unreliable. |

### Output

- `ranking_flips.json`: per-task flip rate, global flip rate, Kendall tau,
  top 10 model pairs that flipped.
- 1-2 sentence punchline for the paper.

---

## Execution Plan

### Phase 0: Extended judge validations (before the 7 analyses)

| Step | What | Time |
|------|------|:----:|
| 0a | translation_enfr BLEU vs V2 | 25 min |
| 0b | code_generation pass@1 vs V2 | 45-60 min |
| Review checkpoint | If both r > 0.7: proceed. If not: discuss. | — |

### Phase 1: Must-have analyses

| Step | What | Time |
|------|------|:----:|
| 1a | NQ1: Ranking flips | 30 min |
| 1b | NQ2: Verbosity correlation | 25 min |
| 1c | Q12: Coverage matrix | 30 min |
| Review checkpoint | Validate results before Phase 2 | — |

### Phase 2: High + Medium analyses

| Step | What | Time |
|------|------|:----:|
| 2a | Q15: Per-task routing savings | 20 min |
| 2b | Q11: Generational delta | 25 min |
| 2c | Q4: Provider gradient | 30 min |
| Review checkpoint | — | — |

### Phase 3: Low priority (if time permits)

| Step | What | Time |
|------|------|:----:|
| 3a | Q9/Q10: Origin + license comparison | 30 min |

**Total realistic: 4-5 hours.**
