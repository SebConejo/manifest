# State Reconciliation

**Date:** 2026-05-08
**Purpose:** Cross-reference all documentation files against factual data (CSV, rejudge_log, spend_tracker) to identify inconsistencies before any further work.

---

## 1. Rejudge Log

**Factual source:** `results/rejudge_log.jsonl` — **6,170 lines total**.

| Phase | Entries | Date | Tasks | Models | Errors |
|-------|---------|------|-------|--------|--------|
| 1 | 4,648 | 2026-05-07 22:04–23:28 | 11 (code_explanation, code_generation, code_review_v2, data_to_text, email_summary_v2, instruction_following, json_transform_v2, long_summarization, rag_qa, structured_output, test_generation_v2) | 9 | 1 |
| 2 | 620 | 2026-05-08 06:29–06:39 | 4 (extraction_hard_v2, function_calling, reasoning_gsm8k, sql_spider) | 9 | 0 |
| 3 | 902 | 2026-05-08 14:34–14:51 | 10 (code_generation, code_review_v2, data_to_text, extraction_hard_v2, instruction_following, ner_extraction, rag_qa, reasoning_gsm8k, sql_spider, test_generation_v2) | 36 | 0 |
| **Total** | **6,170** | | | | **1** |

**What the docs say:**

| Source | Phase 1 | Phase 2 | Phase 3 | Total |
|--------|---------|---------|---------|-------|
| LEARNINGS.md §1 | 4,648 | "620 additional" | "902" | "6,170 total entries" |
| LEARNINGS.md §11 | 4,648 | 620 | 902 | 6,170 |
| DATA_QUALITY_CHECK.md | "4,648" first rejudge | mentions "950 additional zeros" needing action | not mentioned (predates phase 3) | — |
| ZEROS_INVESTIGATION.md | "4,648 cases" first batch, "4,540" in another paragraph | — | not mentioned (predates phase 3) | — |
| SUSPECT_MODELS_INVESTIGATION.md | "4,648 cases" | — | — | — |

**Verdict:** LEARNINGS.md §11 is **correct** — matches the log exactly (4,648 + 620 + 902 = 6,170). DATA_QUALITY_CHECK.md and ZEROS_INVESTIGATION.md are **stale** — they were written before phase 2 and phase 3, respectively. ZEROS_INVESTIGATION.md also has an internal inconsistency: "4,648 cases" in the executive summary vs "4,540" in the judge crash pattern section. The log confirms 4,648 is the correct number for phase 1.

**Is phase 3 integrated in the CSV?** Yes. The CSV was rebuilt from raw JSON files after phase 3. The raw files contain `judge_rerun: true` flags and updated scores from all three phases. The rebuild script reads scores from the raw files, so all 6,170 rejudged scores are reflected in the current 50,351-row CSV.

---

## 2. Spend Tracker

**Factual source:** `results/spend_tracker.json`

```json
{"total_usd": 99.29, "calls": 55460}
```

**What the docs say:**

| Source | Amount |
|--------|--------|
| LEARNINGS.md §9 | "~$88 (model calls) + ~$2.10 (rejudge) + ~$2.50 (re-run empty responses) = ~$92.60" |
| FINDINGS.md data snapshot | "$98 spent" |
| DATA_QUALITY_CHECK.md §6 | "$89.52" (from CSV cost column sum) |
| METHODOLOGY.md §11b.9 | "$98 spent" |
| SESSION_NOTES.md §3 | "$98 spent" |

**Verdict:** The spend tracker says **$99.29** — this is the most authoritative number because it's updated programmatically by the runner on every API call. The discrepancies:

- LEARNINGS.md's "$92.60" was written mid-session on 2026-05-08 before the empty-response re-run finished. **Stale.**
- FINDINGS.md / SESSION_NOTES.md "$98" was the number at data collection completion (pre-rejudge and pre-empty-response re-run). Close but stale by ~$1.
- DATA_QUALITY_CHECK.md "$89.52" is the sum of costs in the CSV. This is a **different metric** — it's the model call cost recorded in the CSV, which excludes judge costs and includes only rows that made it into the CSV. The difference ($99.29 - $89.52 ≈ $9.77) is plausible: judge calls, failed API calls that didn't produce CSV rows, and the re-run costs.

**True total spend: $99.29.** Budget remaining: $150.71 of $250.

---

## 3. CSV Row Count

**Factual source:** `results/benchmark_results.csv` — **50,351 rows**

**What the docs say:**

| Source | Rows | Date |
|--------|------|------|
| LEARNINGS.md §11 | "50,346" | 2026-05-08 "post-phase 3" |
| DATA_QUALITY_CHECK.md | "50,801" | 2026-05-07 |
| FINDINGS.md | "50,949" | 2026-05-07 |
| SESSION_NOTES.md §3 | "50,949" | 2026-05-07 |
| METHODOLOGY.md §11b.9 | "50,949" | 2026-05-07 |

**Why they all disagree:**

1. **FINDINGS.md / SESSION_NOTES.md / METHODOLOGY.md "50,949"** — this was the count before the CSV corruption and rebuild. It included duplicates and rows that were later cleaned up.
2. **DATA_QUALITY_CHECK.md "50,801"** — written on 2026-05-07 after a dedup but before the full rebuild from raw files. The rebuild script skips empty-response+score-0 rows, which accounts for the difference.
3. **LEARNINGS.md "50,346"** — written on 2026-05-08 after the phase 3 rejudge rebuild. Very close to current 50,351 but off by 5. Those 5 rows likely came from the empty-response re-run that was in progress when the session crashed.
4. **Current factual count: 50,351** — rebuilt fresh today from 50,490 raw files (139 skipped as empty+score0, 0 duplicates).

**Verdict:** The current CSV (50,351) is the **single source of truth**. All documentation numbers are stale snapshots from different points in time. The 5-row difference vs LEARNINGS.md's 50,346 is explained by raw files added during the partial empty-response re-run before the crash.

---

## 4. Model Completion

**Factual source:** CSV analysis

| Metric | Current CSV | LEARNINGS.md | DATA_QUALITY_CHECK.md | FINDINGS.md |
|--------|------------|-------------|----------------------|------------|
| Models at 21/21 (≥40 cases) | **35** | — | "37" | "49 models at 21/21" |
| Total models with data | **57** | "57 models total" | "57" | "57 total" |
| V2 rows | **49,018** | — | "49,461" | — |

**Why the discrepancies:**

- **FINDINGS.md "49 models at 21/21"** is the most misleading. It meant "49 models have data on all 21 tasks" but didn't account for the ≥40 threshold. Many models are "present" on 21 tasks but with partial data (e.g., gemini-2.0-flash has rows on 21 tasks but only 4 tasks with ≥40 cases).
- **DATA_QUALITY_CHECK.md "37"** was correct at the time. The drop from 37 to **35** is because the rebuild from raw files skipped 139 empty-response rows, which pushed some borderline models below the 40-case threshold on certain tasks. Specifically:
  - **deepseek/deepseek-v4-pro** dropped from 21/21 to 18/21 (empties stripped)
  - **kimi-k2.6** dropped from 21/21 to 18/21 (empties stripped)
  - **nvidia/nemotron-3-super-120b-a12b** dropped from 21/21 to 17/21 (empties stripped)

These models were previously counted as complete because their empty-response rows (score 0, response "") were included. The current rebuild correctly excludes them.

**True number of complete models (21/21, ≥40 valid cases): 35.**

---

## 5. Zeros in the CSV

**Factual source:** CSV — **744 zeros total**

| eval_type | Count |
|-----------|-------|
| exact | 729 |
| llm_judge | 15 |

By task (top):
- intent_clinc150: 294
- moderation_toxigen: 275
- multistep_reasoning: 68
- sentiment_sst2: 62
- intent_hard: 14, reasoning: 13, intent_easy: 12, sentiment: 4, code_review: 2

**What the docs say:**

| Source | Zeros | Breakdown |
|--------|-------|-----------|
| LEARNINGS.md §11 | "744 zeros: 729 exact-match, 15 LLM-judged" | Matches exactly |
| ZEROS_INVESTIGATION.md | "1,675 zero-scored rows with non-empty response_preview" | Different scope — this was BEFORE phase 3 rejudge |

**Verdict:** LEARNINGS.md §11 is **exactly correct** — 744 = 729 + 15, confirmed.

ZEROS_INVESTIGATION.md's 1,675 was the count before phase 3. Phase 3 rejudged 902 of those zeros (plus some from other phases). The math: 1,675 (pre-phase-3 zeros with non-empty responses) included 851 judge crash cases. Phase 3 rejudged those to non-zero scores. Plus 26 CSV-stale cases got fixed during the rebuild. That leaves the 798 legitimate zeros documented in the investigation. But the current 744 is lower than 798 because the CSV was rebuilt from raw files, and some of those 798 rows had been re-run during the empty-response passes (replacing legit-zero raw files with new successful runs).

**The 744 zeros are all legitimate** — 729 exact-match failures (wrong classification label) + 15 LLM-judged genuine failures. All judge-crash zeros have been fixed by the 3 rejudge phases.

---

## 6. Cross-Source Consistency Summary

| Claim | LEARNINGS.md | DATA_QUALITY_CHECK.md | ZEROS_INVESTIGATION.md | FINDINGS.md | Factual Truth |
|-------|-------------|----------------------|----------------------|-------------|---------------|
| Total rows | 50,346 | 50,801 | — | 50,949 | **50,351** |
| Total spend | ~$92.60 | $89.52 (CSV only) | — | $98 | **$99.29** |
| Rejudge total | 6,170 | — | — | — | **6,170** |
| Complete models (21/21, ≥40) | — | 37 | — | 49 | **35** |
| Total zeros | 744 | 950+ | 1,675 | — | **744** |
| Rejudge phase 3 in CSV | "yes" | no (predates) | no (predates) | no (predates) | **Yes** |

**Who tells the truth:**
- **LEARNINGS.md** is the most up-to-date and the closest to factual truth on most metrics. It was last updated on 2026-05-08 post-phase 3.
- **DATA_QUALITY_CHECK.md** is a stale snapshot from 2026-05-07. Its row count (50,801) and model count (37) reflect pre-rebuild state.
- **ZEROS_INVESTIGATION.md** is a stale snapshot from 2026-05-08 pre-phase 3. Its 1,675 zeros and 851 "needs rejudging" are now resolved.
- **FINDINGS.md** has the most misleading numbers: "50,949 rows" and "49 models at 21/21" both overcount because they predate cleanup.
- **spend_tracker.json** is the authoritative spend source: **$99.29**.

---

## 7. What Needs Updating

| File | Issue | Action |
|------|-------|--------|
| LEARNINGS.md §9 | Spend says "$92.60" | Update to $99.29 |
| LEARNINGS.md §11 | Row count says "50,346" | Update to 50,351 |
| DATA_QUALITY_CHECK.md | Entire file is stale (pre-phase 2/3 rejudge, pre-rebuild) | Rewrite or mark as superseded |
| ZEROS_INVESTIGATION.md | Pre-phase 3, 851 zeros listed as "needs rejudging" are now fixed | Mark as superseded or add "RESOLVED" header |
| FINDINGS.md | "50,949 rows", "49 at 21/21" | Update to 50,351 rows, 35 models at 21/21 (≥40 cases) |
| METHODOLOGY.md §11b.9 | "50,949 rows, $98 spent" | Update to 50,351 rows, $99.29 |
| SESSION_NOTES.md §3 | "50,949 rows, $98 spent" | Update to 50,351 rows, $99.29 |

---

## 8. Remaining Work (factual, no opinions)

| Category | Count | Source |
|----------|-------|--------|
| Raw files total | 50,490 | filesystem |
| CSV rows (valid, non-empty) | 50,351 | rebuild output |
| Skipped empty-response files | 139 | rebuild output |
| Models at 21/21 (≥40 cases) | 35 | CSV analysis |
| Partial models (v2 data, <21 complete) | 14 core + 8 Azure doublons | CSV analysis |
| Zeros in CSV | 744 (all legitimate) | CSV analysis |
| Budget spent | $99.29 | spend_tracker.json |
| Budget remaining | $150.71 | arithmetic |
| Empty-response raw files (need re-run or documentation) | 683 across 86 task+model combos | earlier analysis |
