# Final State Review V3 (post V2 judge)

**Date:** 2026-05-15
**Scope:** All checks on CSV rebuilt with GPT-4o V2 judge scores.

---

## Check 1: Row Coherence — OK

| Metric | Value |
|--------|------:|
| CSV rows | 51,580 |
| LLM-judged task rows | 40,350 |
| Exact-match task rows | 9,966 |
| Non-v2 task rows | 1,264 |
| Sum | 51,580 |
| Raw files with judge_v2_score | 40,350 |
| V1-only LLM cases in CSV | 0 |

All 40,350 LLM-judged cases have V2 scores. No cases missed.
The stated "40,350 re-judged" matches exactly.

---

## Check 2: Score Distributions — OK

No suspicious distributions. No model has >98% at score 5 or >20% at score 0-1.

Notable patterns (all expected):
- Exact-match tasks (intent, moderation, sentiment, multistep) have bimodal
  distributions (0 or 5) — correct, these are binary.
- long_summarization has 43% at 4 and 57% at 5 — V2 is stricter on factual
  completeness (V1 was 94% at 5). This is the intended effect.
- rag_qa has 10% at 1 — models that hallucinate get correctly penalized.

---

## Check 3: Anti-Regression — OK

10 random V1→V2 comparisons:

| Task | Model | V1 | V2 | Delta | Assessment |
|------|-------|:--:|:--:|:-----:|:-----------|
| json_transform | qwen3.6-plus | 4 | 5 | +1 | Correct output, V1 format penalty removed |
| extraction_hard | qwen3-coder | 5 | 5 | 0 | Consistent |
| instruction_following | deepseek-v4-flash | 5 | 5 | 0 | Consistent |
| rag_qa | qwen3-8b | 5 | 1 | -4 | Model said "Not found" when answer WAS in context. V2 correct. |
| long_summarization | deepseek-v4-flash | 4 | 5 | +1 | V1 format penalty removed |
| function_calling | llama-3.2-3b | 5 | 5 | 0 | Consistent |
| function_calling | gpt-4o | 5 | 5 | 0 | Consistent |
| code_generation | devstral | 5 | 5 | 0 | Consistent |
| reasoning_gsm8k | gpt-5.4-nano | 5 | 5 | 0 | Consistent |
| reasoning_gsm8k | gpt-4o-mini | 5 | 5 | 0 | Consistent |

7/10 unchanged (consistent). 2/10 rose by 1 (format penalty removed).
1/10 dropped by 4 (V1 was wrong, V2 correct — model gave wrong answer).
Pattern is as expected.

---

## Check 4: Scores Out of Range — OK

| Check | Count |
|-------|------:|
| Scores outside [0-5] | 0 |
| Score=0 on exact-match | 682 |
| Score=0 on LLM-judged | 0 |

No out-of-range scores. Zeros appear only on exact-match tasks (legitimate
classification errors). Zero LLM-judged zeros confirms V2 judge always
returns 1-5.

---

## Check 5: Complete Models — OK

46 models at 21/21 tasks with >= 40 cases each. Unchanged from pre-V2-rebuild.

---

## Check 6: Duplicates — OK

0 duplicate (task, model, case_idx) triples.

---

## Check 7: Findings Coherence — OK

| Claim in FINAL_FINDINGS_v3.md | Source file | Value | Match? |
|-------------------------------|-----------|-------|:------:|
| Premium avg = 4.791 | stats_validation.json | 4.791 | YES |
| Economy avg = 4.749 | stats_validation.json | 4.749 | YES |
| Gap = 0.042 | computed | 0.042 | YES |
| Best single model = o3 | routing_savings.json | o3 | YES |
| Savings = 99.7% | routing_savings.json | 99.7 | YES |
| intent_clinc150 spread = 3.20 | task_discriminativeness.json | 3.2 | YES |

All numbers verified.

---

## Check 8: Git State — OK

Working tree clean. All changes committed and pushed to SebConejo/manifest.

---

## Overall Verdict

| Check | Verdict |
|-------|:-------:|
| 1. Row coherence | **OK** |
| 2. Score distributions | **OK** |
| 3. Anti-regression | **OK** |
| 4. Scores out of range | **OK** |
| 5. Complete models | **OK** |
| 6. Duplicates | **OK** |
| 7. Findings coherence | **OK** |
| 8. Git state | **OK** |

**All 8 checks pass. No errors found. Data is clean and ready for paper.**
