# TaskBench Learnings

Persistent knowledge for future sessions. Read this file first.

Last updated: 2026-05-12

---

## 1. The Judge Crash Bug (critical, fixed)

**What happened:** The LLM judge (GPT-4o-mini) crashed silently when OpenAI
credits ran out mid-batch. `judge_response()` called `call_openai("gpt-4o-mini", ...)`
which returned `{"error": "You exceeded your current quota"}`. The error handler
returned score 0, indistinguishable from a real zero.

**Scope:** Affected ALL 9 models added in batch 2 on ALL 11 LLM-judged tasks.
The raw responses were correct but never scored.

**How we found it:** 9 models scored below 3.0/5. All failed on the same 11 tasks.
All passed the same 10 tasks (exact-match or judged before quota ran out).

**Fix applied:**
- Phase 1: Re-judge script (`re_judge_failed_scores.py`) re-scored 4,648 cases
  on 11 tasks for 9 models. Cost: ~$2.
- Phase 2: Extended rejudge to 620 additional cases on 5 more tasks
  (reasoning_gsm8k, sql_spider, extraction_hard_v2, function_calling, ner_extraction).
  Total rejudge log: 5,268 entries.

**Still outstanding (as of 2026-05-08):** 851 more zeros identified as judge crash.
Tasks: data_to_text (454), code_review_v2 (147), rag_qa (118), extraction_hard_v2 (68),
reasoning_gsm8k (31), reasoning (13), test_generation_v2 (12), instruction_following (5),
code_review (2), ner_extraction (1). These were missed by the first two rejudge passes.

**Lesson:** A score of 0 on a reputable model is a signal of infrastructure failure,
not model quality. Always check the raw response before trusting a zero.

**Prevention:** The judge should log errors prominently and skip the case instead
of writing score 0. Currently the error is silently converted to 0.

---

## 2. Empty Responses from OpenRouter (recurring)

**What happened:** DeepSeek V4 Pro and Nemotron via OpenRouter returned empty
responses intermittently (API timeouts, rate limits). The runner saved the empty
string and scored it 0.

**Scope:** ~450 empty-response zeros across all tasks, concentrated on
DeepSeek V4 Pro (~153), GPT-5.5 Pro (~101), and Nemotron (~97).

**Fix applied:** Multiple rounds of delete-and-rerun. Each round recovers some
cases but not all (OpenRouter remains intermittent for these models).

**Lesson:** OpenRouter is unreliable for expensive/slow models. After 2-3 retries,
accept partial data and document as a limitation rather than looping forever.

---

## 3. Reasoning Models and Format Compliance

**Problems encountered:**
- Reasoning models (o3, GPT-5.5 Pro, Kimi K2.6, Seed 2.0 Pro) wrap answers in
  `<think>` tags or verbose explanations. Exact-match scoring fails.
- Kimi K2.6 rejects `temperature=0` (only accepts `temperature=1`).
- GPT-5.5 Pro requires `/v1/responses` API, not `/v1/chat/completions`.
- Gemini 2.5 Pro: thinking tokens consumed `max_completion_tokens` budget,
  returning empty responses. Fix: set `max_completion_tokens=8192`.

**Fixes applied:**
- `strip_thinking()` function to remove `<think>` tags before scoring.
- `effective_max_tokens()` to handle thinking token budgets.
- `NO_TEMPERATURE_MODELS` list for models that reject temperature=0.
- `call_openai_responses()` for GPT-5.5 Pro.

---

## 4. Provider Reliability (empirical)

Ranked by reliability during this benchmark:

1. OpenAI (direct): never failed
2. Anthropic (direct): never failed
3. MiniMax (direct): never failed
4. Mistral (direct): works but rate-limits Mistral Large aggressively
5. Gemini (direct): works, free tier rate-limits 2.0-flash heavily
6. Moonshot (direct): works after endpoint fix (api.moonshot.ai, NOT api.moonshot.cn)
7. BytePlus (direct): works, $500 free credits, correct hostname is
   `ark.ap-southeast.bytepluses.com`
8. OpenRouter: works but slow on expensive models, intermittent empty responses

Azure was down for 2 days during the benchmark. 8 Azure-only models remain at
1-2 tasks. These are doublons of models available via other providers.

---

## 5. Operational Discipline

**Commit after every lot.** A power cut killed the first session. All data survived
because we had committed before. Never batch commits.

**Dedup after every run.** Parallel runs create duplicate CSV rows because resume
logic checks at startup, not per-write. Always dedup.

**Check OpenAI quota before judge batches.** The judge crash bug was caused by
exhausted credits. Run a test judge call before starting large batches.

**`--skip-azure` silently skips explicit models.** Azure models are skipped even
if listed in `--models` when `--skip-azure` is active. This caused confusion
when trying to complete gpt-5.1-chat and o4-mini.

**Delete partial rows before re-running.** If a model has 23/50 cases, the resume
logic re-runs all 50, creating 73 rows. Dedup removes exact duplicates but not
the partial+full overlap.

---

## 6. Task Difficulty Observations

- **data_to_text, code_explanation:** All models ace them. Low discriminative power.
- **RAG QA:** Biggest surprise. Models that look smart everywhere else hallucinate.
  Tests restraint (not making up answers).
- **ToxiGen moderation:** Adversarial gold. Subtle cases (coded language, cultural
  sarcasm) break premium models that overthink.
- **Instruction following:** Harder than it looks. Simple constraints like "exactly
  3 bullet points" trip up many models.
- **intent_clinc150:** 150 intents. Small models (llama-3.2-1b/3b, ministral-3b)
  fail legitimately. Expected behavior.

---

## 7. CSV and Raw File Sync

26 cases were found where the raw JSON had been re-judged (correct scores) but
the CSV still showed 0. This happens when the rejudge script updates JSON files
but the CSV rebuild step fails or is skipped.

**Lesson:** After any rejudge or rescore, always rebuild the CSV from raw JSON
files as the final step. Never trust that the CSV is in sync.

---

## 8. Race Condition: Never Run Rejudge + Run_batch Simultaneously

**What happened:** The rejudge script's `update_csv()` reads the entire CSV,
modifies one row, then writes the entire CSV back. When `run_batch.py` appends
rows concurrently, the rejudge overwrites the appends. This corrupted the CSV
from 51,685 rows down to ~9,000 visible tasks (entire tasks like code_generation,
data_to_text disappeared).

**Fix:** Created `scripts/rebuild_csv.py` that rebuilds the CSV from the raw
JSON source of truth (50,487 files). Always run sequentially: finish rejudge
first, then run_batch, then rebuild CSV.

**Lesson:** The raw JSON files in `results/raw/` are the **single source of
truth**. The CSV is a derived artifact. When in doubt, rebuild from raw.

---

## 9. Budget

Total spend as of 2026-05-12: **$143.81** (source: spend_tracker.json, 61,594 API calls).
Hard cap: $250. Remaining budget: **$106.19**.
Note: the spend tracker significantly underestimates real cost for reasoning models.
Real OpenAI billing was ~$180+ due to reasoning tokens and wrong hardcoded prices
(see section 16).
*(Previous: $123.01/60,905 calls, $122.37 pre-mistral-fix, $99.29 pre-rerun, ~$92.60 mid-session estimate.)*

---

## 10. Dataset Size Limitations

Two tasks have fewer than 50 cases in their datasets:
- **code_explanation:** 48 cases
- **structured_output:** 41 cases

This affects ALL models equally. Not an execution issue, not fixable.

---

## 11. Silent Error Swallowing in Provider Callers (critical, fixed)

**What happened:** `call_openai_responses()` (the caller for GPT-5.5 Pro, the only
model using `/v1/responses`) did not check for `"error"` in the API JSON response.
When the API returned `{"error": {"message": "rate limit exceeded"}}`, the function
found no `"output"` key, set `content = ""` and `usage = {0, 0}`, then returned a
valid-looking `{"choices": [...], "usage": {...}}` object. The runner's error check
(`if "error" in response`, line 795) never fired because the response contained
`"choices"`, not `"error"`.

**Smoking gun:** All 163 empty-response files for GPT-5.5 Pro have `input_tokens: 0,
output_tokens: 0`. A successful API call always has `input_tokens > 0`.

**Scope:** 163 false-empty results across 6 tasks (code_review_v2: 50/50, test_generation_v2:
39/49, sql_spider: 29/50, data_to_text: 26/50, extraction_hard_v2: 13/16, reasoning_gsm8k: 5/29).

**Fix:** Added `if "error" in data: return {"error": ...}` after `data = resp.json()`.
Now the error propagates to the runner, which prints it and skips the case (no raw file
written with false data). Same pattern as `call_anthropic` and all other callers.

**Lesson:** Every provider caller must check for `"error"` in the JSON response before
extracting content. The pattern of normalizing to `{"choices": [...]}` format MUST happen
only after confirming the response is not an error.

---

## 12. Reasoning Model Token Budget Must Be 8192+ (critical, fixed)

**What happened:** `effective_max_tokens()` boosted reasoning models from their task
default to `max(requested, 2000)`. But 2000 tokens is not enough for complex generative
tasks (test_generation_v2, code_review_v2, extraction_hard_v2). Reasoning models spend
invisible thinking tokens that count against `max_tokens`. On a 1000-token task boosted
to 2000, a model might spend 1900 tokens thinking and have 100 left for visible output.

**Smoking gun:** ALL empty responses from reasoning models on these tasks have
`output_tokens = 2000` exactly — the budget ceiling. After `strip_thinking()` removes
the `<think>` tags, the visible response is empty.

**Scope:** ~134 empty responses across kimi-k2.6 (45/50 on test_gen), o4-mini (30/50),
MiniMax-M2.7 (19/50), o3 (10/50), and others.

**Fix:** Changed `effective_max_tokens()` to return `max(requested, 8192)` for reasoning
models. This matches the Gemini 2.5 Pro fix already in place (which uses 8192 in
`call_gemini`). The cost impact is negligible — thinking tokens are consumed regardless
of the budget; the extra headroom only lets visible output through.

**Additional discovery: deepseek/deepseek-v4-pro was NOT in REASONING_MODELS.**
It hits the base 1000-token ceiling (no boost). Smoking gun: `output_tokens = 1000`
exactly on empty responses. Added to REASONING_MODELS.

**Additional discovery: `call_moonshot` had `max(max_tokens, 2000)` hardcoded** at
line 521, overriding the boost from `effective_max_tokens`. Pattern to avoid: never
duplicate budget logic in individual provider callers. The boost belongs in
`effective_max_tokens()` only; callers should use the value passed to them.

---

## 13. Cross-Session Reconciliation Method

**Problem:** After multiple sessions, .md files accumulated stale numbers (row counts,
spend, model counts) that contradicted each other. FINDINGS.md said 50,949 rows,
DATA_QUALITY_CHECK.md said 50,801, LEARNINGS.md said 50,346, CSV had 50,351.

**Method:** Cross-reference documentation against the 3 factual sources:
1. `results/rejudge_log.jsonl` — count lines, group by timestamp gaps to identify phases
2. `results/spend_tracker.json` — authoritative spend (updated programmatically)
3. `results/benchmark_results.csv` — rebuild from raw JSON, count rows

The factual sources are always right. The .md files are snapshots that go stale.
After reconciliation, update all .md files and note previous values.

**Lesson:** After any session that modifies data, always reconcile .md files against
the 3 factual sources before starting new work.

---

## 14. Crash-Proof Long Runs

**Problem:** VS Code crashed twice during long benchmark runs, killing the process.

**Solution:** tmux + nohup + caffeinate:
- `tmux new-session -d -s benchmark` — process survives VS Code crash
- `nohup python3 scripts/run_batch.py ... 2>&1 | tee -a results/rerun.log` — survives SIGHUP
- `caffeinate -dims &` — prevents Mac sleep (display, idle, system, disk)
- Commit after each model/task lot, not in batches

---

## 15. Current State (2026-05-12, final)

- **51,617 rows** in CSV, 51,705 raw files
- **47 models complete** (21/21 v2 tasks, ≥40 valid cases each)
- 9 partial models (deepseek-v4-flash 20/21, gemini-2.0-flash 4/21, 7 Azure legacy doublons at 1/21)
- 56 total models with data
- 728 zeros in CSV, all legitimate
- 0 judge-crash zeros remaining, 0 scores > 5, 0 empty-but-scored
- Total spend: **$143.81** (source: spend_tracker.json, 61,594 API calls)
- Real OpenAI spend: ~$180+ (reasoning tokens not tracked, see section 16)
- All re-runs complete (Cat A + Cat B + mistral-large + nemotron + o4-mini + gpt-5.5-pro)
- Next action: analysis and paper
*(Previous states: 51,403/43/$123.01, 50,978/42/$122.37, 50,351/35/$99.29, 50,346 initial.)*

---

## 16. Reasoning Token Cost Blind Spot (critical)

**What happened:** The spend_tracker uses hardcoded prices to compute cost_usd per
API call. For gpt-5.5-pro, the hardcoded output price was $20/M tokens. The real
OpenAI price is $75/M output tokens. Combined with invisible reasoning tokens
(charged by OpenAI but not counted in our completion_tokens), the real cost was
3-10x what we tracked.

**Scope:** gpt-5.5-pro alone cost ~$130+ real (OpenAI billing) vs $14.61 tracked.
The total for all OpenAI models: $28.76 tracked vs ~$180+ real. The discrepancy
comes from: (a) wrong hardcoded price ($20 vs $75/M output), (b) reasoning/thinking
tokens charged by OpenAI but invisible in our completion_tokens count, (c) o3 and
o4-mini also consume reasoning tokens not reflected in the tracker.

**Lesson:** Never trust hardcoded price trackers for reasoning models. Always verify
against provider billing dashboards. The spend_tracker is reliable for non-reasoning
models but fundamentally broken for models that consume invisible thinking tokens.

**Impact on the paper:** The cost_usd column in the CSV is 3-10x underestimated for
reasoning models (gpt-5.5-pro, o3, o4-mini, gpt-5.5). The paper should use provider
billing data for reasoning model costs, not the CSV cost_usd column.

---

## 17. Mistral 429 Silent Drop (critical, fixed)

**What happened:** `call_mistral` in `run_batch.py` did not check the HTTP status
code. Mistral returns 429 with `{"object": "error", "message": "Rate limit exceeded"}`
which has NO `"error"` key at the top level. The runner's `if "error" in response`
check (line 799) missed it entirely. The subsequent `response.get("choices", [])`
returned an empty list, and the case was silently lost with no error logged, no raw
file written.

**Scope:** Affected mistral-large-latest on 16 of 21 tasks. Cases were silently
dropped, making the model appear to have only 5/21 tasks complete when in reality
the API was returning 429 on every call beyond the 15 req/min rate limit.

**Fix:** Added explicit `resp.status_code == 429` check and `data.get("object") == "error"`
check in `call_mistral`. Added exponential backoff retry: 5s, 10s, 20s, 40s, 80s,
max 5 retries. After the fix, mistral-large-latest completed all 21/21 tasks in ~50
minutes at ~$0.60.

**Lesson:** Every provider caller must check HTTP status codes, not just the JSON body.
Different providers use different error response formats. The `if "error" in response`
pattern only works for OpenAI-style errors.

---

## 18. Manual Label Placement for Paper Figures (critical)

**What happened:** We iterated 7 times (v2-v8) on Pareto scatter plot labels.
Every automatic approach failed:
- `adjustText` library: labels ended up far from their points with long arrows
  crossing the entire graph, or stacked on top of each other, or placed over
  the legend.
- Manual offset with collision detection: still produced overlaps because the
  collision zones were estimated in data coordinates, not pixel coordinates.
- Increasing `force_text`, `force_points`, `expand` parameters: pushed labels
  to the edges of the plot or outside the axes.

**Root cause:** Scatter plots with 48 clustered points in a small area are a
worst case for auto-placement. The points are too dense and the label bounding
boxes too large. No amount of parameter tuning fixes this — the layout problem
is overconstrained.

**Fix:** Fully manual placement with `ax.annotate(xytext=(dx, dy), textcoords='offset points')`.
Each label position is hardcoded as a pixel offset from its point. Max 3 labels
per panel. Pick only the models that matter for the story (Pareto winner, worst
model, Premium outlier). Let the rest be anonymous dots — the reader can look up
individual models in the data tables.

**The validated style is documented in PARETO_STYLE_GUIDE.md.** Any future session
generating paper figures MUST read that file first and follow it exactly.

**Lesson:** For publication figures, never use auto-placement libraries. They
work for dashboards and exploratory charts, not for arXiv. Budget 5-10 minutes
per figure for manual label positioning. It's faster than 7 iterations of
auto-placement debugging.
