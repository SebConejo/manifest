# Exact-Match Zeros Investigation

Date: 2026-05-07
**RESOLVED (2026-05-12)** — All empty-response cases identified here have been re-run.
DeepSeek V4 Pro and Nemotron are now complete at 21/21 tasks. Final CSV has 728 zeros,
all legitimate classification failures.

## Summary

276 zeros on exact-match tasks across 4 tasks and 9 models. Investigation of
40 sampled cases reveals three categories:

| Category | Count | % | Description |
|----------|-------|---|-------------|
| Empty response | 27/40 | 68% | Model returned empty string. API error or thinking tokens consumed all output. |
| Legitimate failure | 11/40 | 68% | Model gave wrong answer (e.g., answered B instead of C). Real error. |
| Wrapped in explanation | 2/40 | 5% | Model explained instead of giving bare label. Label is in the text but exact-match missed it. |

## By Task

### intent_clinc150 (116 zeros)

Sampled 10 cases:
- 9 empty responses (90%): Almost all from DeepSeek V4 Pro and Nemotron.
  These models returned empty strings, likely because the API call failed
  silently (thinking tokens consumed max_tokens, or OpenRouter timeout).
- 1 wrapped in explanation: Nemotron explains its reasoning instead of
  giving just the label.

**Verdict:** Mostly API errors (empty responses). The models never got a
chance to answer. These cases should be RE-RUN (not rescored).

### moderation_toxigen (69 zeros)

Sampled 10 cases:
- 7 empty responses (70%): All DeepSeek V4 Pro. Same pattern.
- 3 legitimate failures (30%): Models answered "safe" when expected "toxic"
  or vice versa. These are real classification errors.

**Verdict:** Mix of API errors (70%) and real failures (30%). Re-run the
empty responses. Keep the legitimate failures as score 0.

### multistep_reasoning (10 zeros)

Sampled 10 cases:
- 2 empty responses (20%): DeepSeek V4 Pro.
- 8 legitimate failures (80%): Models answered B when expected C, etc.
  These are genuine wrong answers on ARC-Challenge multiple choice.

**Verdict:** Mostly real failures. These models genuinely got the questions
wrong. Keep as score 0 (correct behavior of exact-match scoring).

### sentiment_sst2 (81 zeros)

Sampled 10 cases:
- 9 empty responses (90%): Almost all DeepSeek V4 Pro.
- 1 wrapped in explanation: Nemotron explains sentiment instead of saying
  "positive" or "negative".

**Verdict:** Mostly API errors. Re-run the empty responses.

## Root Cause Analysis

**DeepSeek V4 Pro** accounts for the vast majority of empty responses (est.
~200 of the 276 zeros). This model, accessed via OpenRouter, had intermittent
API failures that returned empty responses. The runner saved the empty response
and scored it 0.

**Nemotron Super 120B** has a mix: some empty responses and some "explanation
instead of label" responses. The explanation responses are a genuine format
compliance issue (the model does not follow "respond with ONLY the label").

## Recommended Actions

| Action | Cases affected | Method |
|--------|---------------|--------|
| Re-run DeepSeek V4 Pro on cases with empty responses | ~200 | Delete empty rows, re-run via run_batch.py |
| Re-run Nemotron on cases with empty responses | ~20 | Same |
| Keep legitimate failures as score 0 | ~40 | No action needed |
| Keep Nemotron "explanation" responses as score 0 | ~10 | Legitimate format failure, score 0 is correct |

**Estimated cost of re-run:** ~$0.05 (just the model calls, judge not needed
for exact-match tasks).

## Decision

Pending user approval.
