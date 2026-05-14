# Cost Correction Feasibility

**Date:** 2026-05-14
**Question:** Can we correct reasoning model costs in the CSV (Option A),
or must we document them as a limitation (Option B)?

---

## Evidence from live API tests

### Test 1: o3 (chat completions API)

```
Prompt: train problem requiring math reasoning
completion_tokens: 649
completion_tokens_details.reasoning_tokens: 256
visible output: 393 tokens (910 chars, correct answer)

CHECK: 649 = 256 + 393 ✓
CONCLUSION: completion_tokens INCLUDES reasoning_tokens
```

### Test 2: gpt-5.5-pro (Responses API)

```
Same prompt
output_tokens: 293
output_tokens_details.reasoning_tokens: 146
visible output: 147 tokens

CHECK: 293 = 146 + 147 ✓
CONCLUSION: output_tokens INCLUDES reasoning_tokens
```

**Both APIs confirm: the token count we stored in raw files already
includes reasoning tokens.** The cost formula `(input * price_input +
output * price_output) / 1M` is structurally correct. The problem is
only the prices, not the token counts.

---

## What's wrong with the prices

| Model | CSV price (input/output) | Correct price | Error |
|-------|:---:|:---:|---|
| gpt-5.5-pro | $5 / $20 | $15 / $75 | 3x input, 3.75x output |
| gpt-5.4 | $2 / $6 | $1 / $4 | Overpriced in CSV |
| gpt-5.1-chat | $2 / $6 | $0.80 / $3.20 | Overpriced in CSV |
| All other OpenAI models | Correct | Correct | No error |

Note: gpt-5.4 and gpt-5.1-chat are overpriced in our CSV (we charged MORE
than reality). Only gpt-5.5-pro is underpriced.

---

## Reconciliation: CSV vs OpenAI dashboard

| Component | Amount | % of dashboard |
|-----------|-------:|:-:|
| CSV model costs (corrected prices) | $72.64 | 47% |
| Judge calls (~47K gpt-4o-mini) | $3.82 | 2% |
| Aborted nightly run (May 10, killed) | ~$32 | 21% |
| Failed API calls not in CSV | ~$10-15 | 8% |
| Other re-run attempts (Cat A/B/final) | ~$20-30 | 16% |
| **Total estimated** | **$138-153** | **89-98%** |
| **Dashboard actual** | **$156** | **100%** |
| Remaining unexplained | $3-18 | 2-11% |

The $156 is explained within estimation error by the sum of: corrected CSV
costs + non-CSV API calls (judge, failures, aborted runs, re-runs).

---

## Option A-lite: correct prices in CSV

**Feasible.** Fix 3 models' prices and recalculate cost_usd:

```python
PRICE_CORRECTIONS = {
    'gpt-5.5-pro':  (15.0, 75.0),   # was (5, 20)
    'gpt-5.4':      (1.0, 4.0),     # was (2, 6)
    'gpt-5.1-chat': (0.80, 3.20),   # was (2, 6)
}
```

Affects 3,175 rows (1,024 + 1,039 + 1,112). Token counts unchanged.

**Impact on total CSV cost:**
- Before: $45.31 all OpenAI models
- After: $72.64 all OpenAI models
- Net change: +$27.33 (mostly from gpt-5.5-pro +$29.02, offset by
  gpt-5.4 -$0.75 and gpt-5.1-chat -$0.75)

---

## Recommendation

**Do Option A-lite + Option B.**

1. **A-lite:** Recalculate cost_usd for 3 models with correct prices.
   One script, 30 seconds, rebuild CSV.
2. **B:** Document in the paper:
   - Token counts include reasoning tokens (verified by API test)
   - Prices corrected for gpt-5.5-pro, gpt-5.4, gpt-5.1-chat
   - CSV costs are the best available per-call estimates
   - Total project spend was ~$156 on OpenAI (dashboard) due to
     failed calls, retries, and aborted runs not reflected in CSV
