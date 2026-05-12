# Zero-Score Investigation Report

**Date:** 2026-05-08
**RESOLVED (2026-05-12)** — The 851 judge-crash zeros identified here were fixed in rejudge
phase 3 (902 entries). Final CSV has 728 zeros, all legitimate. 47 models complete at 21/21 tasks.

**Scope:** 1,675 zero-scored rows with non-empty `response_preview` in `benchmark_results.csv` (pre-phase-3)

---

## Executive Summary

| Category | Count | Action needed |
|----------|------:|---------------|
| Judge crash bug (needs re-judging) | 851 | Re-run LLM judge |
| CSV stale (JSON already fixed) | 26 | Re-sync CSV from raw JSON |
| Legitimate failures (LLM-judged) | 12 | No action |
| Legitimate failures (exact-match) | 786 | No action |
| **Total** | **1,675** | |

**Bottom line:** 851 zeros are the same silent judge crash bug from the previous round. The first re-judge batch (4,648 cases) missed these. They need a second re-judge pass. Another 26 cases were already re-judged in the raw JSON files but the CSV was never updated.

---

## Methodology

For each category, raw JSON files at `results/raw/{task}_{model}_{case_idx}.json` were read and compared against the CSV. Key fields checked:
- `score` in JSON vs CSV (to detect stale CSV)
- `judge_rerun` flag (present on 4,540 previously re-judged files)
- `expected` field (empty for all LLM-judged tasks, present for exact-match)
- `response` quality (manual review of sampled cases)

---

## Category 1: data_to_text (454 LLM-judged zeros)

**Verdict: ALL 454 are judge crash bug.**

### Evidence
- `expected` field is empty for all cases (LLM judge evaluates quality, no reference answer).
- 400 data_to_text cases were re-judged in the first batch; 383 scored 5, 10 scored 4, 6 scored 3. Zero of the re-judged cases stayed at 0.
- These 454 were NOT included in the re-judge batch (no `judge_rerun` flag).
- Responses are high-quality data-to-text transformations across ALL models.

### Samples (all valid, all scored 0)
| Model | Case | Response excerpt |
|-------|------|-----------------|
| claude-sonnet-4-6 | 39 | "Apple Inc. (AAPL) is currently trading at $185.50, reflecting a positive day change of 2.3%..." |
| gemini-3.1-pro-preview | 3 | "Priced at $999, the iPhone 15 Pro features a vibrant 6.1-inch OLED display..." |
| qwen/qwen3-8b | 23 | "Apple's stock (AAPL) currently trades at $185.50, up 2.3%..." |
| devstral-latest | 5 | "'Oppenheimer,' directed by Christopher Nolan, is a 2023 drama/history film..." |
| meta-llama/llama-3.2-1b-instruct | 0 | "Acme Corp, a leading provider of innovative solutions, reported a significant revenue increase..." |

### Model distribution
6 models have ALL 50 cases at zero (llama-3.2-1b, llama-3.2-3b, qwen-turbo, qwen3-8b, gemma-4-26b, phi-4). Claude-sonnet has 45/50 at zero (5 were judged correctly by the non-crashing judge runs).

---

## Category 2: code_review_v2 (147 LLM-judged zeros)

**Verdict: ALL 147 are judge crash bug.**

### Evidence
- `expected` empty. Responses are detailed, structured code reviews with bug identification, security analysis, and fix suggestions.
- 393 code_review_v2 cases were re-judged in the first batch. These 147 were missed.
- claude-sonnet-4-6 (50) and gemini-3.1-pro-preview (50) account for 68% of the zeros.

### Samples
| Model | Case | Response excerpt |
|-------|------|-----------------|
| claude-sonnet-4-6 | 32 | "## Code Review: `get_env(key)` ### Bugs **1. Missing Import** ```python os is not imported..." |
| gpt-5.4-mini | 16 | "This code has a few major problems. ## What's wrong ### 1) MD5 is not suitable for password storage..." |
| ministral-3b-latest | 8 | "Here's a detailed review... ### 1. Missing Input Validation..." |

---

## Category 3: rag_qa (123 LLM-judged zeros)

**Verdict: 118 are judge crash bug. 5 are legitimate wrong answers.**

### Evidence
- Despite being LLM-judged (`eval_type=llm_judge`), the `expected` field is populated.
- 82/123 responses match expected EXACTLY (case-insensitive).
- 36/123 responses contain the expected answer with minor additions (trailing period, article "The", full sentence wrapping).
- 5/123 are genuinely wrong answers (paraphrased or different entity).

### Format mismatch examples (judge crash, not wrong)
| Model | Case | Expected | Response |
|-------|------|----------|----------|
| gemini-2.5-pro | 7 | "mass of the system" | "The mass of the system." |
| gpt-4o | 0 | "Lake Uberlingen" | "Lake Uberlingen." |
| gemini-2.5-pro | 38 | "Charles River" | "The Charles River" |
| mistral-small-latest | 1 | "1665" | "The Great Plague of London occurred in **1665**." |

### Legitimate wrong answers (5 cases)
| Model | Case | Expected | Response |
|-------|------|----------|----------|
| gpt-5.1-chat | 3 | "Hassan al-Turabi" | "Hassan al-Turabi" (unicode hyphen difference) |
| o4-mini | 36 | "gaseous oxygen." | "Oxygen (gaseous oxygen)" |
| deepseek/deepseek-v4-flash | 10 | "The Saxon Garden" | "Saxon Garden" |

---

## Category 4: extraction_hard_v2 (68 LLM-judged zeros)

**Verdict: ALL 68 are judge crash bug.**

### Evidence
- `expected` empty. Only 16 extraction_hard_v2 cases were re-judged in the first batch.
- Responses are well-structured JSON extractions (invoices, job postings, meeting minutes, etc.).
- Dominated by qwen/qwen3.6-flash (40) and qwen/qwen3.6-max-preview (25).

### Samples
| Model | Case | Response excerpt |
|-------|------|-----------------|
| qwen/qwen3.6-flash | 16 | `{"product": "TaskFlow Pro", "price_per_user": 29, "competitors": [...]...}` |
| qwen/qwen3.6-flash | 4 | `{"title": "Senior Backend Engineer", "company": "CloudMatrix", ...}` |
| qwen/qwen3.6-flash | 39 | `{"date": "March 15, 2024", "time": "2:00-4:30 PM EST", ...}` |

---

## Category 5: reasoning_gsm8k (59 LLM-judged zeros)

**Verdict: 31 judge crash, 25 CSV stale, 3 legitimate failures.**

### Breakdown
- **25 CSV stale:** JSON files already have correct scores (4-5) but CSV still shows 0. 23 are qwen/qwen3.6-plus, 1 mistral-medium, 1 llama-4-maverick.
- **28 correct answer:** Response contains `ANSWER: X` matching expected value. Judge crash.
- **3 format match:** Expected "7", got "7.00" (numeric equivalence). Judge crash.
- **3 legitimate:** Wrong numerical answer (gpt-4o-mini case 44, gemini-2.5-flash case 44, grok-4.20 case 28).

---

## Category 6: intent_clinc150 (323 exact-match zeros)

**Verdict: ALL 323 are legitimate failures.**

### Breakdown
- **274 wrong label:** Model predicted a different intent label entirely. Examples: expected `accept_reservations`, got `book_hotel`; expected `report_fraud`, got `fraud`.
- **49 echo/format failures:** Model echoed the prompt instead of producing a label (primarily nvidia/nemotron-3-super-120b-a12b with 53 zeros total).

### Top affected models
| Model | Count | Failure type |
|-------|------:|--------------|
| nvidia/nemotron-3-super-120b-a12b | 53 | Mostly prompt echo |
| meta-llama/llama-3.2-3b-instruct | 35 | Wrong label |
| meta-llama/llama-3.2-1b-instruct | 32 | Wrong label |
| ministral-3b-latest | 14 | Wrong label |

These are small/weak models failing at fine-grained intent classification (150 intents). This is expected.

---

## Category 7: moderation_toxigen (288 exact-match zeros)

**Verdict: ALL 288 are legitimate failures.**

### Breakdown
- **268 wrong label:** Model said "safe" when expected "toxic" or vice versa. Binary classification error.
- **20 echo/format:** Model echoed the prompt (nemotron pattern) or added explanation text.

### Sample
| Model | Case | Expected | Response |
|-------|------|----------|----------|
| claude-haiku-4-5-20251001 | 6 | toxic | safe |
| gpt-5.4-nano | 26 | safe | toxic |
| microsoft/phi-4 | 14 | toxic | "Safe\n\nThe text suggests excluding trans people..." |

Toxicity detection is genuinely hard. Models disagree on borderline cases. Legitimate.

---

## Category 8: sentiment_sst2 (71 exact-match zeros)

**Verdict: 70 legitimate, 1 CSV stale.**

### Breakdown
- **57 wrong label:** Model said "negative" when expected "positive" or vice versa.
- **14 echo/verbose:** Nemotron prompt-echo pattern (21 nemotron cases) or verbose response.
- **1 CSV stale:** JSON has non-zero score but CSV shows 0.

---

## Category 9: multistep_reasoning (75 exact-match zeros)

**Verdict: 74 legitimate, 1 CSV stale.**

All are wrong answers to multiple-choice questions (expected "B", got "C", etc.). Spread across many models including strong ones (o3, gpt-5.4, gemini-2.5-pro).

---

## Remaining small categories

| Task | Count | Eval | Verdict |
|------|------:|------|---------|
| intent_hard | 14 | exact | Legitimate (wrong labels) |
| reasoning | 13 | llm_judge | Judge crash (valid step-by-step reasoning) |
| intent_easy | 12 | exact | Legitimate (wrong labels) |
| test_generation_v2 | 12 | llm_judge | Judge crash (valid test suites) |
| instruction_following | 5 | llm_judge | Judge crash (valid responses) |
| sentiment | 4 | exact | Legitimate (wrong labels) |
| code_generation | 3 | llm_judge | Legitimate (nemotron/minimax echo prompt instead of generating code) |
| code_review | 2 | llm_judge | Judge crash (valid code reviews) |
| sql_spider | 1 | llm_judge | Legitimate (minimax echo) |
| ner_extraction | 1 | llm_judge | Judge crash (valid JSON NER output) |

---

## Judge crash pattern

The raw JSON files contain NO `judge_response` or `judge_score` fields for un-re-judged cases. The only judge metadata is `judge_rerun` (boolean) and `judge_raw` (string), both added only during the re-judge pass. This confirms the original judge crashed silently, defaulting to score 0 without recording any judge output.

The first re-judge batch processed 4,540 cases. These 851 were missed, likely because the re-judge script selected cases based on criteria that didn't cover all affected rows (possibly filtered by specific models or tasks).

---

## Model concentration analysis

### Judge crash zeros (851 cases) - top models affected
| Model | Count | Notes |
|-------|------:|-------|
| claude-sonnet-4-6 | 96 | Mostly data_to_text (45) + code_review_v2 (50) |
| gemini-3.1-pro-preview | 91 | Same pattern |
| qwen/qwen3-8b | 52 | data_to_text (50) + extraction (1) + code_review (1) |
| devstral-latest | 51 | data_to_text (45) + code_review (6) |
| qwen/qwen-turbo | 51 | data_to_text (50) + code_review (1) |
| qwen/qwen3.6-flash | 50 | extraction_hard_v2 (40) + others |
| meta-llama/llama-3.2-1b-instruct | 50 | data_to_text (50) |
| meta-llama/llama-3.2-3b-instruct | 50 | data_to_text (50) |
| google/gemma-4-26b-a4b-it | 50 | data_to_text (50) |
| microsoft/phi-4 | 50 | data_to_text (50) |

The judge crash is NOT model-specific. It affects strong and weak models equally. The concentration on data_to_text is because that task had 454 affected cases (the largest single batch).

### Legitimate exact-match zeros - top models
| Model | Count | Pattern |
|-------|------:|---------|
| nvidia/nemotron-3-super-120b-a12b | 106 | Echoes prompts instead of answering |
| meta-llama/llama-3.2-1b-instruct | 76 | Small model, poor classification |
| meta-llama/llama-3.2-3b-instruct | 45 | Small model |
| ministral-3b-latest | 36 | Small model |

---

## Recommended actions

1. **Re-judge 851 cases** across: data_to_text (454), code_review_v2 (147), rag_qa (118), extraction_hard_v2 (68), reasoning_gsm8k (31), reasoning (13), test_generation_v2 (12), instruction_following (5), code_review (2), ner_extraction (1).

2. **Sync CSV from raw JSON** for 26 cases where the JSON was already re-judged but the CSV wasn't updated (25 reasoning_gsm8k + 1 multistep_reasoning).

3. **No action** on 798 legitimate zeros (786 exact-match + 12 LLM-judged genuine failures).
