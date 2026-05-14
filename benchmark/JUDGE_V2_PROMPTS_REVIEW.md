# Judge V2 Prompts Review

**Date:** 2026-05-14
**Scope:** 15 remaining LLM-judged tasks to re-judge with GPT-4o.

---

## 1. Task Classification

**All 15 tasks are generative with NO ground truth answer.** None have an
`expected` field in the raw files. The judge is the sole evaluator.

The 4 exact-match tasks (sentiment_sst2, intent_clinc150, moderation_toxigen,
multistep_reasoning) are NOT being re-judged — they use deterministic
label-matching, no LLM judge involved.

| # | Task | Type | What the model produces | Has expected? |
|---|------|------|------------------------|:---:|
| 1 | code_explanation | Generative | 1-2 sentence explanation of code | No |
| 2 | code_generation | Generative | Python function body | No |
| 3 | code_review_v2 | Generative | Bug/security analysis of code | No |
| 4 | data_to_text | Generative | Paragraph from structured data | No |
| 5 | email_summary_v2 | Generative | 2-sentence email summary | No |
| 6 | extraction_hard_v2 | Generative | JSON extraction from text | No |
| 7 | function_calling | Generative | JSON function call | No |
| 8 | instruction_following | Generative | Response following constraints | No |
| 9 | json_transform_v2 | Generative | Transformed JSON | No |
| 10 | long_summarization | Generative | 3-4 sentence summary | No |
| 11 | ner_extraction | Generative | JSON with persons/orgs/locations | No |
| 12 | sql_spider | Generative | SQL query | No |
| 13 | structured_output | Generative | JSON matching schema | No |
| 14 | test_generation_v2 | Generative | pytest unit tests | No |
| 15 | translation_enfr | Generative | French translation | No |

---

## 2. V2 Prompts (compact)

### Tasks with verifiable output (judge can check correctness)

**code_generation:** "Score 5 = correct implementation that would pass all
reasonable test cases. Score 1 = empty or completely wrong. Ignore code style,
variable naming, and comments. Only evaluate correctness."
*Correctness anchor: would the code run and produce correct output?*

**function_calling:** "Score 5 = correct function selected, all arguments
correct and properly typed. Score 2 = wrong function selected. Score 1 = not
valid JSON."
*Correctness anchor: right function + right arguments.*

**sql_spider:** "Score 5 = query would return exactly the correct results on
the given schema. Score 1 = not valid SQL. Ignore SQL style."
*Correctness anchor: would the query return the right rows?*

**extraction_hard_v2 / structured_output:** "Score 5 = valid JSON, all fields
present, all values correctly extracted from the text. Score 1 = not JSON.
Respond with ONLY a number 1-5."
*Correctness anchor: do the extracted values match the source text?*

**json_transform_v2:** "Score 5 = valid JSON matching target format, all data
values correctly mapped. Score 1 = not JSON or completely wrong."
*Correctness anchor: are the values in the right fields?*

**ner_extraction:** "Score 5 = all persons, organizations, and locations correctly
identified and categorized. Score 1 = no entities correctly identified."
*Correctness anchor: did it find the right entities?*

### Tasks where correctness = completeness

**email_summary_v2:** "Score 5 = captures main point AND all action items.
Score 3 = misses the main point or key action items. Score 1 = unrelated.
Ignore length and writing style."
*Correctness anchor: are the key facts from the email present?*

**long_summarization:** "Score 5 = all key facts, main argument, and important
numbers captured. Score 1 = unrelated. Ignore writing quality."
*Correctness anchor: are the important facts present?*

**data_to_text:** "Score 5 = all key data points from the input mentioned in
the text. Score 1 = unrelated. A plain list that includes all data scores
higher than elegant prose that omits data points."
*Correctness anchor: are all data points included?*

### Tasks where correctness = accuracy of analysis

**code_review_v2:** "Score 5 = identifies all critical bugs and security issues.
Score 2 = mostly generic advice, does not identify specific bugs. A terse review
that names the bug scores higher than a verbose review that misses it."
*Correctness anchor: did it find the real bugs in THIS code?*

**code_explanation:** "Score 5 = correctly identifies the algorithm/pattern and
explains what the code does. Score 2 = mostly wrong understanding. A brief
correct explanation scores higher than a long incorrect one."
*Correctness anchor: is the technical identification accurate?*

**test_generation_v2:** "Score 5 = tests cover happy path, edge cases, and error
cases. Would catch most bugs. Score 2 = tests exist but are trivial or test the
wrong things. Ignore test style and naming conventions."
*Correctness anchor: would these tests actually catch bugs?*

### Tasks where correctness = constraint satisfaction

**instruction_following:** "Score 5 = all constraints met exactly. Score 3 = 1
constraint clearly violated. Score 1 = constraints completely ignored. Count the
constraints literally. Do not give credit for 'close enough.'"
*Correctness anchor: literal constraint counting.*

**translation_enfr:** "Score 5 = all meaning accurately preserved. No omissions,
no additions. Score 1 = meaning completely changed. Ignore whether the French
sounds literary or natural."
*Correctness anchor: is the meaning of the source preserved?*

---

## 3. Do exact-match tasks need a judge?

**No. The 4 exact-match tasks (sentiment, intent, moderation, multistep) use
deterministic scoring and are NOT part of this re-judge.** They score 5 if the
model's response contains the expected label, 0 otherwise. No LLM involved.

For completeness, here's the comparison:

| Approach | Reliability | Cost | When to use |
|----------|:---:|:---:|---|
| Label parser (current) | Deterministic, r=1.0 | $0 | Tasks with a single expected label |
| LLM judge | Variable, r=0.35-0.90 | ~$0.0015/call | Tasks with free-form output |

A parser would NOT work for the 15 generative tasks because there's no single
correct output to match against. The judge is necessary.

---

## 4. How V2 forces correctness over presentation

Every V2 prompt includes one of these anti-bias mechanisms:

| Mechanism | Tasks | How it works |
|-----------|-------|-------------|
| "Ignore formatting, style, length" | All 15 | Explicit instruction at end of every prompt |
| Verifiable output anchor | code_gen, func_call, sql, extraction, json, NER (6) | The judge can check if the output IS correct (valid JSON, right function, right SQL) |
| Completeness checklist | email_sum, long_sum, data_to_text (3) | "Are ALL key facts present?" — binary check per fact |
| Bug identification | code_review, code_expl (2) | "Did it find the SPECIFIC bugs?" — not "did it write well?" |
| Coverage count | test_gen, instruction (2) | "How many cases covered?" / "How many constraints met?" — countable |
| Meaning preservation | translation (1) | "Is the MEANING preserved?" — not "is it elegant?" |

**Concrete example — code_review_v2:**

V1 prompt: "Rate this code review on a 1-5 scale. 5=identifies all major bugs
and security issues with specific fixes."

V2 prompt adds: "A terse review that correctly names the bug scores higher than
a verbose review that misses it. Ignore formatting and writing quality."

The key addition is the **inversion example** — telling the judge that a short
correct answer beats a long wrong one. V1 never said this, letting the judge
default to "longer = better."

---

## 5. Limitations of V2 on tasks without ground truth

Even with V2 prompts, we cannot VALIDATE the judge on these 15 tasks the way
we validated on GSM8K and RAG QA. We proved the mechanism works (r jumped from
0.35 to 0.90 on tasks with ground truth), but we're extrapolating to tasks
without ground truth.

The honest framing for the paper:
- "Judge reliability validated on 2 tasks with ground truth (r=0.90)"
- "Same correctness-focused rubric methodology applied to 15 generative tasks"
- "We cannot independently verify judge accuracy on tasks without ground truth"

This is standard practice in LLM evaluation papers — nobody has ground truth
for open-ended generation.

---

## 6. Cost and runtime estimate

| Metric | Value |
|--------|------:|
| Cases to re-judge | 35,562 |
| GPT-4o cost per call | ~$0.0015 |
| Estimated cost | ~$54 |
| Runtime at 75 calls/min | ~8 hours |
