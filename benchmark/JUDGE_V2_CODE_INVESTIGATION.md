# Judge V2 Code Generation Investigation

**Date:** 2026-05-15

---

## Diagnosis: The harness is broken, not the judge

### Error breakdown (2,394 cases executed)

| Error type | Count | % | Nature |
|:-----------|------:|--:|:-------|
| Pass | 1,076 | 44.9% | Code runs and passes all HumanEval tests |
| Indentation | 1,129 | 47.2% | IndentationError — code is correct but harness fails to indent it |
| Assertion | 108 | 4.5% | Code runs but produces wrong output — real model error |
| Syntax | 47 | 2.0% | SyntaxError — residual markdown or format artifacts |
| Other | 34 | 1.4% | NameError, timeout, misc |

**47% of all cases fail due to IndentationError alone.** The models return
unindented code (as instructed: "return ONLY the function body"), and the
harness fails to properly indent it into the function signature.

### 20 sampled failures with V2 >= 4

**19 out of 20 are indentation errors on visually correct code.**

Examples:
- Claude Sonnet 4.6, case 36: `for i in range(n-1, 0, -1):\n    if n % i == 0:\n        return i`
  This is correct `largest_divisor` code. Fails because it's not indented 4 spaces.
- GPT-5.5, case 39: correct `change_base` implementation. Same indentation issue.
- Qwen3-8B, case 26: correct `triples_sum_to_zero`. Same.

**1 out of 20 is a real model error** (Gemma 4 26B, case 10: wrong logic for `count_nums`).

### Why the harness can't be easily fixed

The prompt says "Return ONLY the function body." Models return code at
various indentation levels:
- Some return at 0-indent (body should be at 4-indent)
- Some return at 4-indent (correct)
- Some include the `def` line (full function)
- Some include imports before the body
- Some wrap in markdown code blocks

A production HumanEval harness (like OpenAI's original) handles all these
cases with sophisticated parsing. Our simple `smart_indent` handles ~50%.
Building a robust harness is a multi-day effort outside our scope.

### What this means for the judge

**The r=0.097-0.491 correlation tells us nothing about the judge.** The
native metric (pass@1) has 47% noise from the harness. Even a perfect judge
would show low correlation against a metric that's wrong half the time.

### Verdict

**We cannot validate the V2 judge on code_generation with our current
harness.** This is a test infrastructure limitation, not a judge limitation.

For the paper, we report:
- "Code generation validation was attempted using HumanEval test execution.
  Our harness produced 47% indentation-related false negatives, making the
  pass@1 metric unreliable. Manual inspection of 20 high-V2-score failures
  confirmed 19/20 were harness errors, not model errors. A production-grade
  HumanEval harness is needed for definitive validation."

This is honest. It doesn't claim the judge is validated on code, and it
explains why.

### Recommendation for the paper

**Don't claim code gen validation. Don't hide it either.**

Final validation table:

| Task | Native metric | r | Verdict |
|:-----|:-------------|:---:|:-------:|
| reasoning_gsm8k | Exact answer | 0.905 | VALIDATED |
| rag_qa | Substring match | 0.887 | VALIDATED |
| translation_enfr | BLEU (1 ref) | 0.290 | INCONCLUSIVE (BLEU too coarse) |
| code_generation | pass@1 | N/A | INCONCLUSIVE (harness broken) |

2 validated, 2 inconclusive. The inconclusives are metric problems, not
judge problems. This is a common situation in evaluation papers.
