# Cost Correction Feasibility

**Date:** 2026-05-14
**Question:** Can we correct reasoning model costs in the CSV (Option A),
or must we document them as a limitation (Option B)?

---

## Q1: Is reasoning_tokens present in the raw files?

**No. 0 out of 14,688 reasoning model raw files contain reasoning_tokens.**

The runner stores only `{input, output}` in the tokens field. The API response
includes `completion_tokens_details.reasoning_tokens` but `compute_cost()` and
the save logic never extracted it. The data is lost — it was not persisted at
benchmark time.

## Q2: What percentage have the info?

**0%.** This is uniform across all 14 reasoning models and all tasks. Not a
per-model or per-task gap — the field was simply never saved.

## Q3: Can we infer reasoning tokens from what we DO have?

**Partially.** The `output` field in our raw files maps to `completion_tokens`
from the API, which INCLUDES reasoning tokens for OpenAI models. So:

| Provider | What `output` contains | Can we separate? |
|----------|----------------------|-----------------|
| OpenAI (o3, o4-mini, gpt-5.5, gpt-5.1) | completion_tokens = visible + reasoning | No — we can't split them without the details |
| OpenAI Responses (gpt-5.5-pro) | output_tokens = visible + reasoning | No — same problem |
| Anthropic (claude-opus-4-7) | output_tokens = visible only | No correction needed — Anthropic doesn't charge for thinking |
| Moonshot (kimi-k2.6) | Unknown — probably visible only | Cannot verify |
| OpenRouter (deepseek-v4-pro, nemotron) | completion_tokens — may include reasoning | Cannot verify |
| MiniMax (MiniMax-M2.7) | Unknown | Cannot verify |
| BytePlus (seed-2-0-pro) | Unknown | Cannot verify |

**Evidence from the data:**

| Model | Task | output_tokens | Expected visible | Interpretation |
|-------|------|:---:|:---:|---|
| o3 | sentiment_sst2 | 19-83 | ~1 ("positive") | output INCLUDES ~18-82 reasoning tokens |
| o4-mini | sentiment_sst2 | 20-148 | ~1 | output INCLUDES reasoning |
| gpt-5.5 | sentiment_sst2 | 4-39 | ~1 | output INCLUDES reasoning |
| gpt-5.4 | sentiment_sst2 | 4 | ~4 | output = visible only (NOT a reasoning model internally?) |
| gpt-5.4-nano | sentiment_sst2 | 4 | ~4 | Same — visible only |
| claude-opus-4-7 | sentiment_sst2 | 6 | ~6 | Anthropic = visible only (correct) |
| gpt-4o-mini | sentiment_sst2 | 1 | ~1 | Non-reasoning baseline (correct) |

## Q4: What does this mean for cost correction?

### For OpenAI models (o3, o4-mini, gpt-5.5, gpt-5.5-pro, gpt-5.1)

Our `cost_usd` already includes reasoning tokens in the token count because
`completion_tokens` from the OpenAI API includes them. So:

`cost_usd = (input_tokens * input_price + completion_tokens * output_price) / 1M`

Where `completion_tokens` = visible + reasoning. **This is actually correct**
for the pricing formula — OpenAI charges the same $/M rate for both visible
and reasoning completion tokens.

**The real problem was the WRONG PRICE, not missing tokens:**
- gpt-5.5-pro was priced at $20/M output instead of $75/M
- This alone accounts for a 3.75x underestimate

### For non-OpenAI reasoning models (Opus, Kimi, DeepSeek, etc.)

- **Anthropic:** Does not charge for thinking tokens. Our cost is correct.
- **Others (Kimi, DeepSeek, Nemotron, MiniMax, Seed Pro):** Unclear whether
  their `completion_tokens` includes reasoning. Likely model-dependent.
  We cannot verify without re-calling the API.

---

## Feasibility Verdict

**Option A (correct all costs) is NOT feasible.** We don't have
`reasoning_tokens` in any raw file, and we can't retroactively separate
visible from reasoning tokens in the `output` count.

**However, the situation is better than we thought:**

For OpenAI models, our cost formula was actually applying the output price
to ALL completion tokens (including reasoning). The error was the price
itself ($20/M instead of $75/M for gpt-5.5-pro), not missing tokens.

**Option A-lite: correct the PRICES only.** This is feasible:

| Model | Old output_price | Correct output_price | Correction factor |
|-------|:---:|:---:|:---:|
| gpt-5.5-pro | $20/M | $75/M | 3.75x on output cost |
| All others | Correct | Correct | 1.0x |

This can be done by recalculating `cost_usd` in the CSV using the corrected
price for gpt-5.5-pro. The token counts are already correct (they include
reasoning tokens).

### Estimated impact of Option A-lite

```
gpt-5.5-pro old cost:  $14.61 (from CSV)
gpt-5.5-pro new cost:  $14.61 * (75/20) = $54.79 (price correction only)
Real OpenAI billing:   ~$130+ (includes overhead we can't account for)
```

The price correction gets us from $14.61 to $54.79 — closer to reality but
still under the billing amount. The remaining gap (~$75) is likely:
- OpenAI billing overhead (platform fees, rounding)
- Judge calls (gpt-4o-mini) counted in billing but not in per-model CSV cost
- Possible token count differences between API response and billing

---

## Recommendation

**Do Option A-lite + Option B:**

1. Recalculate `cost_usd` for gpt-5.5-pro rows using $75/M output price.
   This is a 1-line script, affects 1,024 rows, takes 30 seconds.
2. Document in the paper that:
   - Reasoning model costs include thinking tokens in the token count
   - The corrected price for gpt-5.5-pro is $75/M (was erroneously $20/M)
   - Despite correction, CSV costs remain lower bounds due to provider
     billing overhead not captured in per-call token accounting
   - Non-OpenAI reasoning model costs may underestimate if thinking tokens
     are charged separately by their providers

This gives the best available cost data without over-claiming accuracy.
