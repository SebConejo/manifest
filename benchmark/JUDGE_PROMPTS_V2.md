# Judge Prompts V2

**Date:** 2026-05-14
**Goal:** Fix the format bias. V1 judge rewarded presentation over correctness
(r=0.348 vs ground truth). V2 forces evaluation on factual correctness with
explicit anchors and anti-bias instructions.

**Judge model:** GPT-4o (upgraded from GPT-4o-mini for better rubric adherence)
**Cost estimate:** ~2,400 LLM-judged rows * ~$0.005/call = ~$12

---

## Design Principles

1. **Correctness first.** Score 5 requires factual correctness, not just good writing.
2. **Format-neutral.** Verbose and concise answers get the same score if equally correct.
3. **Explicit anchors.** Each score level has a concrete, verifiable criterion.
4. **Anti-bias instruction.** Every prompt includes "Ignore formatting, length, and style."
5. **Expected answer when available.** For tasks with ground truth, the judge receives it.

---

## 17 LLM-Judged Tasks

### 1. reasoning_gsm8k

**What changed:** V1 said "correct answer with sound reasoning." V2 gives the
expected answer and makes numerical match the primary criterion.

```
You are evaluating a math problem response.

Expected correct answer: {expected}

The model was asked: {input}
The model responded: {response}

Score on a 1-5 scale based on CORRECTNESS OF THE FINAL ANSWER:
5 = Final numerical answer matches expected exactly
4 = Final answer is within 1% of expected (rounding difference)
3 = Reasoning approach is correct but final answer is wrong
2 = Partially correct reasoning but wrong answer
1 = Completely wrong answer, no valid reasoning, or empty

Ignore formatting, verbosity, and style. A correct answer in any format scores 5.
Respond with ONLY a number 1-5.
```

### 2. rag_qa

**What changed:** V1 rewarded eloquence. V2 checks if the expected answer appears
in the response and penalizes hallucination explicitly.

```
You are evaluating a question-answering response. The model was given a context
passage and asked to answer ONLY from that context.

Expected correct answer: {expected}
Context provided: {context}

The model responded: {response}

Score on a 1-5 scale based on FACTUAL CORRECTNESS:
5 = Response contains the expected answer and adds no information beyond the context
4 = Response contains the expected answer but includes minor extra details
3 = Response is partially correct (contains part of the expected answer)
2 = Response does not contain the expected answer but is related to the topic
1 = Response is wrong, hallucinated (not from context), or empty

A one-word correct answer scores 5. A long correct answer also scores 5.
Ignore formatting, length, and style.
Respond with ONLY a number 1-5.
```

### 3. code_generation

**What changed:** V1 said "correct implementation that would pass all tests."
V2 is more specific about what "correct" means and ignores style.

```
You are evaluating a Python function completion.

The function signature and docstring were: {input}
The model's implementation: {response}

Score on a 1-5 scale based on FUNCTIONAL CORRECTNESS:
5 = Implementation is correct and would pass all reasonable test cases
4 = Mostly correct, handles main cases but misses 1 edge case
3 = Core logic is right but has a bug that would fail on common inputs
2 = Partially relevant code but fundamentally flawed logic
1 = Empty, wrong language, or completely unrelated to the function

Ignore code style, variable naming, and comments. Only evaluate correctness.
Respond with ONLY a number 1-5.
```

### 4. code_review_v2

**What changed:** V1 rewarded detailed prose. V2 focuses on whether real bugs
were identified.

```
You are evaluating a code review response.

The code being reviewed: {input}
The model's review: {response}

Score on a 1-5 scale based on BUG IDENTIFICATION:
5 = Identifies all critical bugs and security issues present in the code
4 = Identifies the main bugs, misses 1 minor issue
3 = Identifies some real issues but misses critical bugs
2 = Mostly generic advice, does not identify the specific bugs in this code
1 = Empty, irrelevant, or identifies no real issues

A terse review that correctly names the bug scores higher than a verbose
review that misses it. Ignore formatting and writing quality.
Respond with ONLY a number 1-5.
```

### 5. code_explanation

**What changed:** V1 evaluated clarity. V2 evaluates technical accuracy.

```
You are evaluating a code explanation.

The code: {input}
The model's explanation: {response}

Score on a 1-5 scale based on TECHNICAL ACCURACY:
5 = Correctly identifies the algorithm/pattern and explains what the code does
4 = Correct overall understanding with 1 minor inaccuracy
3 = Partially correct but misses the core algorithm or misidentifies the pattern
2 = Mostly wrong understanding of what the code does
1 = Empty or completely wrong explanation

A brief correct explanation scores higher than a long incorrect one.
Respond with ONLY a number 1-5.
```

### 6. test_generation_v2

**What changed:** V1 rewarded "comprehensive tests with good assertions."
V2 checks if the tests would actually catch bugs.

```
You are evaluating unit tests for a Python function.

The function: {input}
The generated tests: {response}

Score on a 1-5 scale based on BUG-CATCHING EFFECTIVENESS:
5 = Tests cover happy path, edge cases, and error cases. Would catch most bugs.
4 = Good coverage of happy path and some edge cases. Misses 1 category.
3 = Only happy path tests. No edge cases or error cases.
2 = Tests exist but are trivial or test the wrong things
1 = No valid tests, syntax errors, or empty

Ignore test style and naming conventions. Only evaluate coverage and correctness.
Respond with ONLY a number 1-5.
```

### 7. function_calling

**What changed:** V1 was already correctness-focused. V2 adds structural
validation.

```
You are evaluating a function call generation.

Available functions: {functions}
User request: {input}
Model's function call: {response}

Score on a 1-5 scale based on CORRECTNESS:
5 = Correct function selected, all arguments correct and properly typed
4 = Correct function, 1 minor argument error (typo, wrong format)
3 = Correct function but missing or wrong required arguments
2 = Wrong function selected
1 = Not valid JSON, empty, or completely unrelated

Respond with ONLY a number 1-5.
```

### 8. sql_spider

**What changed:** V1 said "correct logic." V2 is specific about SQL correctness.

```
You are evaluating a SQL query.

Database schema: {schema}
Question: {input}
Expected behavior: return the correct results for the question.
Model's SQL: {response}

Score on a 1-5 scale based on QUERY CORRECTNESS:
5 = Query would return exactly the correct results on the given schema
4 = Correct logic, minor syntax issue (e.g., missing alias) that wouldn't affect results
3 = Right tables and joins but wrong filtering or aggregation
2 = Queries the wrong tables or uses wrong join logic
1 = Not valid SQL, empty, or completely unrelated

Ignore SQL style (uppercase keywords, formatting). Only evaluate correctness.
Respond with ONLY a number 1-5.
```

### 9. translation_enfr

**What changed:** V1 rewarded "natural French." V2 focuses on meaning preservation.

```
You are evaluating an English-to-French translation.

English source: {input}
Model's French translation: {response}

Score on a 1-5 scale based on MEANING ACCURACY:
5 = All meaning accurately preserved. No omissions, no additions, no errors.
4 = Meaning preserved with 1 minor inaccuracy (wrong word choice, slight nuance shift)
3 = Most meaning preserved but 1 significant error or omission
2 = Several meaning errors, important content lost or changed
1 = Wrong language, empty, or meaning completely changed

Ignore whether the French sounds "literary" or "natural." Only evaluate
whether the meaning of the English source is preserved.
Respond with ONLY a number 1-5.
```

### 10. extraction_hard_v2

**What changed:** V1 rewarded "valid JSON with all fields." V2 checks field
values against the source text.

```
You are evaluating structured data extraction.

Schema requested: {schema}
Source text: {input}
Model's extraction: {response}

Score on a 1-5 scale based on EXTRACTION ACCURACY:
5 = Valid JSON, all fields present, all values correctly extracted from the text
4 = Valid JSON, 1 minor field error (typo, slight value difference)
3 = Valid JSON but 2+ field errors or missing fields
2 = Invalid JSON but contains some correctly extracted values
1 = Empty, not JSON, or no correctly extracted values

Respond with ONLY a number 1-5.
```

### 11. structured_output

Same prompt as extraction_hard_v2 (both are JSON extraction tasks).

### 12. json_transform_v2

```
You are evaluating a JSON transformation.

Input JSON: {input}
Target format: {target}
Model's output: {response}

Score on a 1-5 scale based on TRANSFORMATION CORRECTNESS:
5 = Valid JSON matching target format, all data values correctly mapped
4 = Valid JSON, 1 minor mapping error
3 = Valid JSON but significant mapping errors or missing fields
2 = Invalid JSON or mostly wrong mappings
1 = Empty, not JSON, or completely wrong

Respond with ONLY a number 1-5.
```

### 13. email_summary_v2

```
You are evaluating an email summary.

Original email: {input}
Model's summary: {response}

Score on a 1-5 scale based on INFORMATION COMPLETENESS:
5 = Summary captures the main point AND all action items from the email
4 = Summary captures the main point, misses 1 minor action item
3 = Summary captures the topic but misses the main point or key action items
2 = Summary is vaguely related but misses most content
1 = Empty, wrong, or unrelated to the email

Ignore length and writing style. A terse complete summary scores higher
than a verbose incomplete one.
Respond with ONLY a number 1-5.
```

### 14. long_summarization

```
You are evaluating a text summary.

Original text: {input}
Model's summary: {response}

Score on a 1-5 scale based on FACTUAL COMPLETENESS:
5 = All key facts, main argument, and important numbers captured
4 = Main argument captured, 1 key fact missing
3 = Gets the topic right but misses important facts or numbers
2 = Vaguely related but misses the main argument
1 = Empty, wrong, or unrelated

Ignore writing quality. Only evaluate whether the important information
from the original text is present in the summary.
Respond with ONLY a number 1-5.
```

### 15. data_to_text

```
You are evaluating a data-to-text conversion.

Structured data: {input}
Model's text: {response}

Score on a 1-5 scale based on DATA INCLUSION:
5 = All key data points from the input are mentioned in the text
4 = Most data points included, 1 minor omission
3 = Some data points included, significant omissions
2 = Major data points missing
1 = Empty, wrong, or unrelated to the data

Ignore prose quality. A plain list that includes all data scores higher
than elegant prose that omits data points.
Respond with ONLY a number 1-5.
```

### 16. ner_extraction

```
You are evaluating named entity extraction.

Source text: {input}
Model's extraction: {response}

Score on a 1-5 scale based on ENTITY CORRECTNESS:
5 = All persons, organizations, and locations correctly identified and categorized
4 = Most entities correct, 1 minor miss or miscategorization
3 = Major entities found but several missed or miscategorized
2 = Many errors, most entities wrong or missing
1 = Empty, wrong format, or no entities correctly identified

Respond with ONLY a number 1-5.
```

### 17. instruction_following

```
You are evaluating instruction following. The user gave a specific instruction
with explicit constraints (e.g., "exactly 3 bullet points", "no more than 50 words").

User instruction: {input}
Model's response: {response}

Score on a 1-5 scale based on CONSTRAINT SATISFACTION:
5 = All constraints met exactly
4 = All constraints met with 1 minor deviation
3 = 1 constraint clearly violated
2 = Multiple constraints violated
1 = Constraints completely ignored or empty response

Count the constraints literally. Do not give credit for "close enough."
Respond with ONLY a number 1-5.
```

---

## Tasks NOT re-judged (exact-match, 4 tasks)

These keep their current scoring (score 5 if exact label match, 0 otherwise):
- sentiment_sst2
- intent_clinc150
- moderation_toxigen
- multistep_reasoning

No judge involved. No change needed.

---

## Implementation Notes

- **Judge model:** GPT-4o ($2.50/M input, $10/M output) instead of GPT-4o-mini
- **Max judge tokens:** 5 (force single-digit response)
- **Temperature:** 0
- **Expected answer injection:** reasoning_gsm8k and rag_qa prompts include `{expected}`.
  Other tasks do not have a ground-truth answer — the judge evaluates on its own.
- **Input truncation:** First 3000 chars of input (up from 2000 in V1) to give
  the judge more context on long tasks (extraction, summarization).
- **Response truncation:** First 3000 chars of response (up from 2000).

### Cost estimate

17 LLM-judged tasks × ~48 models × ~50 cases = ~40,800 judge calls.
Each call: ~600 input tokens + ~2 output tokens.
Cost: 40,800 × (600 × $2.50 + 2 × $10) / 1M = ~$62.

**This is significantly more than V1 ($4 with gpt-4o-mini).** The alternative
is to re-judge only the 2 tasks where we have ground truth (reasoning_gsm8k +
rag_qa = ~4,800 calls = ~$7.50) and keep V1 scores for the other 15 tasks.

### Recommended approach

**Re-judge only reasoning_gsm8k and rag_qa first (~$7.50).** Verify the new
r is > 0.8 on these two tasks. If yes, decide whether to re-judge the other
15 tasks. If no, the problem is deeper than prompts.
