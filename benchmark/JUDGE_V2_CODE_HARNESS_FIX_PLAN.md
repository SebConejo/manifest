# Code Generation Harness Fix Plan

**Date:** 2026-05-15
**Problem:** 46% of HumanEval cases fail with IndentationError due to harness
inability to properly inject model code into function signatures.

---

## Root Cause

The prompt says "Return ONLY the function body." Models comply and return
unindented code. The harness needs to:
1. Insert that code into the function signature (which ends with `:\n`)
2. Indent it as a function body (4 spaces)

Current harness does naive indentation that breaks on:
- Multi-line code with mixed indentation
- Code that includes its own `def` (model returns full function)
- Code with imports at the top (before the body)
- Code with helper functions nested inside
- Code wrapped in markdown with extra whitespace

## Fix Strategy

Instead of trying to indent arbitrary code into a function body (fragile),
**use Python's `exec` to define the function dynamically.** This is how
OpenAI's original HumanEval evaluator works.

### Approach

```python
def build_program(prompt, response, entry_point, tests):
    code = strip_markdown(response)
    
    # Strategy 1: response has the full function → use it directly
    if contains_function_def(code, entry_point):
        program = extract_imports(code) + "\n" + extract_function(code, entry_point)
    
    # Strategy 2: response is a function body → inject into prompt
    else:
        # Use textwrap.indent to properly indent ALL lines
        body = textwrap.indent(textwrap.dedent(code), '    ')
        program = prompt + body
    
    # Add any imports the response needs but didn't include
    program = add_missing_imports(program) + "\n\n" + tests + f"\ncheck({entry_point})\n"
    return program
```

Key improvements over current:
1. **`textwrap.dedent` then `textwrap.indent`**: handles ANY starting
   indentation level correctly. Dedent normalizes to 0, then indent adds 4.
2. **Function detection**: regex for `def {entry_point}(` handles models
   that return the full function.
3. **Import extraction**: if the body starts with `import` or `from`,
   move those lines BEFORE the function definition.
4. **Missing import injection**: scan for `List`, `Optional`, `Dict`, `Tuple`
   etc. and add `from typing import ...` if needed.

## Validation Plan

### Step 1: Build and unit-test the harness (30 min)

Test on 10 known cases covering each edge case:
- Case with just `return x` (1 line body)
- Case with imports + body
- Case with full function def
- Case with markdown-wrapped code
- Case with nested helper function
- Case with 0-indent body
- Case with 4-indent body
- Case with 8-indent body (model over-indented)

### Step 2: Run on all 2,394 cases (10 min)

Compare error breakdown to current:
- Target: < 5% indentation errors (down from 46%)
- Target: pass rate > 80% (up from 47%)

### Step 3: Compute r with V2 judge (5 min)

If pass@1 is now reliable, r should be > 0.6 (many models cluster at high
pass@1, so variance is compressed — expect moderate-high r, not necessarily 0.9).

### Step 4: Manual verification (30 min)

- 20 cases where OLD harness = fail, NEW harness = pass: confirm code is correct
- 10 cases where BOTH harness = fail: confirm code is actually wrong
- 5 cases where OLD harness = pass, NEW harness = fail: investigate (should be 0)

## Time Estimate

| Step | Time |
|------|:----:|
| Build harness with edge case handling | 30 min |
| Run all cases | 10 min |
| Compute correlation | 5 min |
| Manual verification (30 cases) | 30 min |
| Write results + commit | 15 min |
| **Total** | **~1.5 hours** |

Realistic adjustment: add 30 min for debugging edge cases that I haven't
anticipated. **Total: ~2 hours.**

## What if r is still < 0.6 after fix?

If pass@1 is now reliable (< 5% harness errors) and r is still < 0.6,
then the V2 judge genuinely disagrees with pass@1 on code generation.
Possible reasons:
- V2 judge evaluates "would this code work?" while pass@1 tests specific
  test cases — code can be logically correct but fail on edge cases
- V2 judge evaluates code quality beyond correctness (handling edge cases,
  readability) which pass@1 doesn't capture
- V2 judge is actually wrong on code generation specifically

In that case, we'd need to investigate which metric is right by reading
20 disagreement cases.
