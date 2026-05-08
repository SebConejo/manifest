# Next Phase Plan

**Date:** 2026-05-08
**Status:** All .md files updated, reconciliation complete, investigations done.

---

## 1. Documentation Updates (DONE)

All stale .md files have been updated to reflect factual truth:

| File | What changed |
|------|-------------|
| FINDINGS.md | Data snapshot: 50,351 rows, 35 complete models, $99.29 spent |
| METHODOLOGY.md §11b.9 | Same corrections |
| SESSION_NOTES.md §3 | Same corrections |
| LEARNINGS.md §9, §11 | Budget $99.29, row count 50,351, 35 complete models |
| DATA_QUALITY_CHECK.md | Marked as PARTIALLY SUPERSEDED with correct numbers |
| ZEROS_INVESTIGATION.md | Marked as RESOLVED (851 judge-crash zeros fixed in phase 3) |

---

## 2. Investigation Results

### 2a. GPT-5.5 Pro — BUG IN CODE (fixable)

**Root cause:** `call_openai_responses()` in `run_batch.py` (lines 435-463) does NOT check for `"error"` in the API response JSON. When the Responses API returns an error (rate limit, content policy, etc.), the function silently returns an empty response with zero tokens. The main runner sees this as a valid API call and writes `response: "", tokens: {input: 0, output: 0}` to the raw file.

**Evidence:** All 163 empty-response files for gpt-5.5-pro have `input_tokens: 0, output_tokens: 0` — the smoking gun. A successful call always has `input_tokens > 0`.

**Scope:** 163 empty responses across 6 tasks. Worst: code_review_v2 (50/50), test_generation_v2 (39/49), sql_spider (29/50), data_to_text (26/50).

**Fix:** Add 2 lines to `call_openai_responses()`:
```python
data = resp.json()
if "error" in data:
    return {"error": data["error"].get("message", str(data["error"]))}
```
Then delete the 163 empty raw files and re-run. Expected cost: ~$3-5 (GPT-5.5 Pro is expensive but only ~163 calls).

**Verdict: FIXABLE. Fix the bug, re-run.**

### 2b. test_generation_v2 — TOKEN BUDGET TOO LOW (fixable)

**Root cause:** Reasoning models (kimi-k2.6, o3, o4-mini, MiniMax-M2.7) use invisible thinking tokens that count against `max_tokens`. The `effective_max_tokens()` function boosts to 2000, but complex generative tasks (test generation, code review) need more. All empty responses have `output_tokens = 2000` exactly — the budget is exhausted by thinking.

**Evidence:**
- kimi-k2.6: 45/50 empty, all at `output_tokens = 2000`
- o3: 10/50 empty, all at `output_tokens = 2000`
- o4-mini: 30/50 empty, all at `output_tokens = 2000`
- MiniMax-M2.7: 19/50 empty, all at `output_tokens = 2000`
- Gemini 2.5 Pro: 0 empty — already fixed with `max_completion_tokens: 8192`

**Additional finding:** `deepseek/deepseek-v4-pro` is NOT in `REASONING_MODELS` but IS a reasoning model. It hits the base 1000-token ceiling (no boost). All its empties have `output_tokens = 1000`.

**Fix:**
1. Increase `effective_max_tokens()` from `max(x, 2000)` to `max(x, 8192)` for tasks with `max_output_tokens >= 500` (matches the Gemini fix already in place)
2. Add `deepseek/deepseek-v4-pro` to `REASONING_MODELS`
3. Delete affected empty raw files, re-run

**Scope of fix:** ~134 cases across kimi-k2.6 (45), o4-mini (30), MiniMax-M2.7 (19), o3 (10), deepseek-v4-pro (~30 from token budget issue). Estimated cost: ~$2-4.

**Verdict: FIXABLE. Increase token budget, re-run.**

### 2c. Kimi K2.6 — SAME AS 2b (token budget)

**Root cause:** Identical to 2b. All 120 empty responses have `output_tokens = 2000`. The model is in `REASONING_MODELS` and gets the 2000-token boost, but 2000 isn't enough for complex generative tasks.

**Temperature handling:** Correct — kimi-k2.6 is in `NO_TEMPERATURE_MODELS`, working properly.

**Provider:** Moonshot direct API (api.moonshot.ai), not OpenRouter. No provider reliability issue.

**Verdict: FIXABLE via 2b fix. Same token budget increase.**

---

## 3. Classification of 14 Incomplete Models

### Category A: FIXABLE (code bugs, re-run will work)

| Model | Current | Issue | Fix | Est. cost |
|-------|---------|-------|-----|-----------|
| **gpt-5.5-pro** | 14/21 | `call_openai_responses()` silently swallows API errors | Fix error handling, re-run 163 cases | ~$4 |
| **kimi-k2.6** | 18/21 | Token budget 2000 too low for generative tasks | Increase to 8192, re-run ~120 cases | ~$1.50 |
| **deepseek/deepseek-v4-pro** | 18/21 | Not in REASONING_MODELS, hits 1000-token ceiling + OpenRouter intermittent empties | Add to REASONING_MODELS + increase budget + re-run ~150 cases | ~$2 |
| **o4-mini** | 20/21 | Token budget 2000 too low on test_gen/code_review | Increase to 8192, re-run ~30 cases | ~$0.50 |
| **nvidia/nemotron** | 17/21 | Mix: OpenRouter empties + token budget on some tasks | Increase budget, re-run ~55 cases | ~$0.50 |
| **MiniMax-M2.7** | 20/21 (close) | Token budget on test_generation_v2 (19 empties) | Increase to 8192, re-run ~29 cases | ~$0.30 |
| **o3** | 20/21 (close) | Token budget on test_generation_v2 (10 empties) + 1 missing code_generation case | Increase budget, re-run ~19 cases | ~$1 |

**Subtotal: ~$10, ~566 cases to re-run across 7 models.**

### Category B: FIXABLE but low priority (random API gaps, small)

| Model | Current | Issue | Fix | Est. cost |
|-------|---------|-------|-----|-----------|
| **gpt-5.4** | 19/21 | Missing multistep_reasoning + extraction_hard_v2 | Run 2 missing tasks (100 cases) | ~$0.30 |
| **gpt-5.4-mini** | 19/21 | Same | Same | ~$0.15 |
| **gpt-5.4-nano** | 19/21 | Same | Same | ~$0.10 |
| **deepseek/deepseek-v4-flash** | 20/21 | test_generation_v2 partial + scattered empties | Re-run ~11 cases | ~$0.10 |
| **qwen/qwen3.6-plus** | 20/21 | multistep_reasoning partial | Re-run ~10 cases | ~$0.05 |
| **mistral-medium-latest** | 20/21 | test_generation_v2 partial | Re-run ~10 cases | ~$0.05 |
| **gemini-2.5-pro** | 20/21 | Rate limiting on several tasks | Re-run ~4 cases | ~$0.20 |

**Subtotal: ~$1, ~245 cases to re-run across 7 models.**

### Category C: ACCEPT AS-IS (systemic or impractical to fix)

| Model | Current | Issue | Decision |
|-------|---------|-------|----------|
| **gpt-5.5** | 20/21 (close) | 13 empties on code_review_v2 only | Uses standard chat API, intermittent failures. Could re-run but marginal. Accept 37/50 valid cases. |
| **mistral-large-latest** | 5/21 | Severe rate limiting even on paid tier | 3 attempts made, always rate-limited. Document as limitation. |
| **gemini-2.0-flash** | 4/21 | Google free tier rate limit | Would need paid API key. Document as limitation. |
| 8 Azure doublons | 1-2/21 | Azure down, models available elsewhere | Intentionally not completing. |

---

## 4. Recommendation: One Strategy

### Fix the 2 bugs, re-run targeted cases, ship the paper with 42+ complete models.

**The 2 code fixes:**
1. **`call_openai_responses()` error handling** — 2 lines of code. Unblocks gpt-5.5-pro entirely.
2. **`effective_max_tokens()` boost to 8192** for tasks with high output + add deepseek-v4-pro to REASONING_MODELS. Unblocks kimi-k2.6, o3, o4-mini, MiniMax, Nemotron, deepseek-v4-pro.

**The re-run:**
- Category A (7 models, ~566 cases): **~$10**
- Category B (7 models, ~245 cases): **~$1**
- Total: **~$11**, well within the $150.71 remaining budget

**Expected outcome after re-run:**
- Category A models jump from 14-20/21 to 21/21 → adds 7 complete models → **42 complete models**
- Category B models jump from 19-20/21 to 21/21 → adds up to 7 more → potentially **42-49 complete models**
- Total: **42-49 models at 21/21**, up from current 35

**Why not 3 options:**
- Doing nothing (ship with 35) wastes the diagnostic work and leaves fixable bugs in the data.
- Doing everything (including mistral-large and gemini-2.0-flash) would burn time on rate limits with no guarantee of completion.
- The middle path (fix bugs + targeted re-run of categories A+B) gives maximum ROI: 2 code fixes, ~$11, and the paper goes from "35 models with gaps" to "42+ models, gaps documented."

**Execution order:**
1. Fix `call_openai_responses()` (2 lines)
2. Fix `effective_max_tokens()` + add deepseek-v4-pro to REASONING_MODELS
3. Delete empty-response raw files for Category A+B models
4. Run Category A (the expensive one: gpt-5.5-pro, kimi-k2.6, deepseek-v4-pro, o3, o4-mini, nemotron, MiniMax)
5. Run Category B (cheap: gpt-5.4 family, v4-flash, qwen3.6-plus, mistral-medium, gemini-2.5-pro)
6. Rebuild CSV
7. Verify: count complete models, check zeros, update docs
8. Move to analysis and paper

**Budget:** $11 estimated / $150.71 available = 7% of remaining budget.

**What the paper says about gaps:** mistral-large-latest (5/21) and gemini-2.0-flash (4/21) are documented in LIMITATIONS.md as "provider rate limiting prevented full evaluation." This is honest and common in benchmark papers. gpt-5.5 (13 empties on 1 task) stays at 37/50 — acceptable. The 8 Azure doublons are excluded from analysis (same model weights, different provider).
