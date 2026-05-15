"""Re-judge 15 generative tasks with GPT-4o and V2 correctness-focused prompts."""
import json, glob, os, sys, time, requests, subprocess
from pathlib import Path

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
JUDGE_MODEL = "gpt-4o"
MAX_RETRIES = 5
LOG_FILE = "results/rejudge_v2_full_log.jsonl"
PROGRESS_FILE = "results/rejudge_v2_progress.log"

TASKS = [
    "code_explanation", "code_generation", "code_review_v2", "data_to_text",
    "email_summary_v2", "extraction_hard_v2", "function_calling",
    "instruction_following", "json_transform_v2", "long_summarization",
    "ner_extraction", "sql_spider", "structured_output", "test_generation_v2",
    "translation_enfr",
]

PROMPTS = {
    "code_explanation": """You are evaluating a code explanation.

The code: {input}
The model's explanation: {response}

Score on a 1-5 scale based on TECHNICAL ACCURACY:
5 = Correctly identifies the algorithm/pattern and explains what the code does
4 = Correct overall understanding with 1 minor inaccuracy
3 = Partially correct but misses the core algorithm or misidentifies the pattern
2 = Mostly wrong understanding of what the code does
1 = Empty or completely wrong explanation

A brief correct explanation scores higher than a long incorrect one.
Respond with ONLY a number 1-5.""",

    "code_generation": """You are evaluating a Python function completion.

The function signature and docstring were: {input}
The model's implementation: {response}

Score on a 1-5 scale based on FUNCTIONAL CORRECTNESS:
5 = Implementation is correct and would pass all reasonable test cases
4 = Mostly correct, handles main cases but misses 1 edge case
3 = Core logic is right but has a bug that would fail on common inputs
2 = Partially relevant code but fundamentally flawed logic
1 = Empty, wrong language, or completely unrelated to the function

Ignore code style, variable naming, and comments. Only evaluate correctness.
Respond with ONLY a number 1-5.""",

    "code_review_v2": """You are evaluating a code review response.

The code being reviewed: {input}
The model's review: {response}

Score on a 1-5 scale based on BUG IDENTIFICATION:
5 = Identifies all critical bugs and security issues present in the code
4 = Identifies the main bugs, misses 1 minor issue
3 = Identifies some real issues but misses critical bugs
2 = Mostly generic advice, does not identify the specific bugs in this code
1 = Empty, irrelevant, or identifies no real issues

A terse review that correctly names the bug scores higher than a verbose review that misses it. Ignore formatting and writing quality.
Respond with ONLY a number 1-5.""",

    "data_to_text": """You are evaluating a data-to-text conversion.

Structured data: {input}
Model's text: {response}

Score on a 1-5 scale based on DATA INCLUSION:
5 = All key data points from the input are mentioned in the text
4 = Most data points included, 1 minor omission
3 = Some data points included, significant omissions
2 = Major data points missing
1 = Empty, wrong, or unrelated to the data

Ignore prose quality. A plain list that includes all data scores higher than elegant prose that omits data points.
Respond with ONLY a number 1-5.""",

    "email_summary_v2": """You are evaluating an email summary.

Original email: {input}
Model's summary: {response}

Score on a 1-5 scale based on INFORMATION COMPLETENESS:
5 = Summary captures the main point AND all action items from the email
4 = Summary captures the main point, misses 1 minor action item
3 = Summary captures the topic but misses the main point or key action items
2 = Summary is vaguely related but misses most content
1 = Empty, wrong, or unrelated to the email

Ignore length and writing style. A terse complete summary scores higher than a verbose incomplete one.
Respond with ONLY a number 1-5.""",

    "extraction_hard_v2": """You are evaluating structured data extraction.

Schema requested: {schema}
Source text: {input}
Model's extraction: {response}

Score on a 1-5 scale based on EXTRACTION ACCURACY:
5 = Valid JSON, all fields present, all values correctly extracted from the text
4 = Valid JSON, 1 minor field error (typo, slight value difference)
3 = Valid JSON but 2+ field errors or missing fields
2 = Invalid JSON but contains some correctly extracted values
1 = Empty, not JSON, or no correctly extracted values

Respond with ONLY a number 1-5.""",

    "function_calling": """You are evaluating a function call generation.

Available functions: {functions}
User request: {input}
Model's function call: {response}

Score on a 1-5 scale based on CORRECTNESS:
5 = Correct function selected, all arguments correct and properly typed
4 = Correct function, 1 minor argument error (typo, wrong format)
3 = Correct function but missing or wrong required arguments
2 = Wrong function selected
1 = Not valid JSON, empty, or completely unrelated

Respond with ONLY a number 1-5.""",

    "instruction_following": """You are evaluating instruction following. The user gave a specific instruction with explicit constraints.

User instruction: {input}
Model's response: {response}

Score on a 1-5 scale based on CONSTRAINT SATISFACTION:
5 = All constraints met exactly
4 = All constraints met with 1 minor deviation
3 = 1 constraint clearly violated
2 = Multiple constraints violated
1 = Constraints completely ignored or empty response

Count the constraints literally. Do not give credit for "close enough."
Respond with ONLY a number 1-5.""",

    "json_transform_v2": """You are evaluating a JSON transformation.

Input JSON: {input}
Target format: {target}
Model's output: {response}

Score on a 1-5 scale based on TRANSFORMATION CORRECTNESS:
5 = Valid JSON matching target format, all data values correctly mapped
4 = Valid JSON, 1 minor mapping error
3 = Valid JSON but significant mapping errors or missing fields
2 = Invalid JSON or mostly wrong mappings
1 = Empty, not JSON, or completely wrong

Respond with ONLY a number 1-5.""",

    "long_summarization": """You are evaluating a text summary.

Original text: {input}
Model's summary: {response}

Score on a 1-5 scale based on FACTUAL COMPLETENESS:
5 = All key facts, main argument, and important numbers captured
4 = Main argument captured, 1 key fact missing
3 = Gets the topic right but misses important facts or numbers
2 = Vaguely related but misses the main argument
1 = Empty, wrong, or unrelated

Ignore writing quality. Only evaluate whether the important information from the original text is present in the summary.
Respond with ONLY a number 1-5.""",

    "ner_extraction": """You are evaluating named entity extraction.

Source text: {input}
Model's extraction: {response}

Score on a 1-5 scale based on ENTITY CORRECTNESS:
5 = All persons, organizations, and locations correctly identified and categorized
4 = Most entities correct, 1 minor miss or miscategorization
3 = Major entities found but several missed or miscategorized
2 = Many errors, most entities wrong or missing
1 = Empty, wrong format, or no entities correctly identified

Respond with ONLY a number 1-5.""",

    "sql_spider": """You are evaluating a SQL query.

Database schema: {schema}
Question: {input}
Model's SQL: {response}

Score on a 1-5 scale based on QUERY CORRECTNESS:
5 = Query would return exactly the correct results on the given schema
4 = Correct logic, minor syntax issue that wouldn't affect results
3 = Right tables and joins but wrong filtering or aggregation
2 = Queries the wrong tables or uses wrong join logic
1 = Not valid SQL, empty, or completely unrelated

Ignore SQL style. Only evaluate correctness.
Respond with ONLY a number 1-5.""",

    "structured_output": """You are evaluating structured data extraction.

Target schema: {target_schema}
Source text: {input}
Model's extraction: {response}

Score on a 1-5 scale based on EXTRACTION ACCURACY:
5 = Valid JSON, all fields present, all values correctly extracted from the text
4 = Valid JSON, 1 minor field error
3 = Valid JSON but 2+ field errors or missing fields
2 = Invalid JSON but contains some correctly extracted values
1 = Empty, not JSON, or no correctly extracted values

Respond with ONLY a number 1-5.""",

    "test_generation_v2": """You are evaluating unit tests for a Python function.

The function: {input}
The generated tests: {response}

Score on a 1-5 scale based on BUG-CATCHING EFFECTIVENESS:
5 = Tests cover happy path, edge cases, and error cases. Would catch most bugs.
4 = Good coverage of happy path and some edge cases. Misses 1 category.
3 = Only happy path tests. No edge cases or error cases.
2 = Tests exist but are trivial or test the wrong things
1 = No valid tests, syntax errors, or empty

Ignore test style and naming conventions. Only evaluate coverage and correctness.
Respond with ONLY a number 1-5.""",

    "translation_enfr": """You are evaluating an English-to-French translation.

English source: {input}
Model's French translation: {response}

Score on a 1-5 scale based on MEANING ACCURACY:
5 = All meaning accurately preserved. No omissions, no additions, no errors.
4 = Meaning preserved with 1 minor inaccuracy (wrong word choice, slight nuance shift)
3 = Most meaning preserved but 1 significant error or omission
2 = Several meaning errors, important content lost or changed
1 = Wrong language, empty, or meaning completely changed

Ignore whether the French sounds literary or natural. Only evaluate whether the meaning of the English source is preserved.
Respond with ONLY a number 1-5.""",
}

# Fields that different tasks use for their prompt template placeholders
TASK_FIELDS = {
    "extraction_hard_v2": ["schema", "input"],
    "function_calling": ["functions", "input"],
    "json_transform_v2": ["input", "target"],
    "sql_spider": ["schema", "input"],
    "structured_output": ["target_schema", "input"],
}

def call_judge(prompt):
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
    body = {
        "model": JUDGE_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 5,
        "temperature": 0,
    }
    backoff = [2, 5, 10, 20, 40]
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post("https://api.openai.com/v1/chat/completions",
                                json=body, headers=headers, timeout=30)
            if resp.status_code == 429:
                wait = backoff[min(attempt, len(backoff)-1)]
                time.sleep(wait)
                continue
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            for c in content.strip():
                if c.isdigit() and 1 <= int(c) <= 5:
                    return int(c), content.strip()
            return None, content.strip()
        except Exception as e:
            time.sleep(2)
    return None, "max_retries"

def load_dataset(task):
    sys.path.insert(0, "scripts")
    from run_batch import TASK_DEFS
    td = TASK_DEFS[task]
    with open(td["dataset"]) as f:
        return [json.loads(l) for l in f]

def log_progress(msg):
    with open(PROGRESS_FILE, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    print(msg, flush=True)

def main():
    total = 0
    errors = 0
    
    for task_idx, task in enumerate(TASKS):
        log_progress(f">>> Task {task_idx+1}/15: {task}")
        
        dataset = load_dataset(task)
        files = sorted(glob.glob(f"results/raw/{task}_*.json"))
        task_count = 0
        task_errors = 0
        
        for filepath in files:
            d = json.load(open(filepath))
            response = d.get("response", "")
            if not response:
                continue
            
            # Build judge prompt
            template = PROMPTS[task]
            
            # Get the original case data for extra fields
            case_idx = d.get("case_idx")
            if case_idx is None:
                parts = os.path.basename(filepath).rsplit("_", 1)
                try:
                    case_idx = int(parts[-1].replace(".json", ""))
                except:
                    continue
            
            case_data = dataset[case_idx] if case_idx < len(dataset) else {}
            
            # Build format kwargs
            fmt = {"response": response[:3000], "input": case_data.get("input", "")[:3000]}
            extra_fields = TASK_FIELDS.get(task, [])
            for field in extra_fields:
                if field != "input":
                    fmt[field] = str(case_data.get(field, ""))[:2000]
            
            try:
                prompt = template.format(**fmt)
            except KeyError as e:
                task_errors += 1
                continue
            
            new_score, raw = call_judge(prompt)
            total += 1
            task_count += 1
            
            if new_score is None:
                errors += 1
                task_errors += 1
                continue
            
            # Save
            d["judge_v2_score"] = new_score
            d["judge_v2_raw"] = raw
            d["judge_v2_model"] = JUDGE_MODEL
            with open(filepath, "w") as f:
                json.dump(d, f, indent=2)
            
            entry = {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "task": task,
                "model": d.get("model", ""),
                "old_score": d.get("score", 0),
                "new_score": new_score,
            }
            with open(LOG_FILE, "a") as f:
                f.write(json.dumps(entry) + "\n")
            
            if task_count % 100 == 0:
                error_rate = task_errors / task_count * 100 if task_count > 0 else 0
                log_progress(f"  {task}: {task_count} done ({task_errors} errors, {error_rate:.1f}%)")
                # Safety: abort if error rate > 1%
                if task_count > 50 and error_rate > 1.0:
                    log_progress(f"  ABORT: error rate {error_rate:.1f}% > 1% threshold")
                    return
        
        log_progress(f">>> Done: {task} ({task_count} cases, {task_errors} errors)")
        
        # Commit after each task
        subprocess.run(["git", "add", "results/raw/", LOG_FILE, PROGRESS_FILE], 
                       capture_output=True)
        subprocess.run(["git", "commit", "-m", f"data(benchmark): V2 re-judge {task} with GPT-4o"],
                       capture_output=True)
    
    log_progress(f"\n=== COMPLETE: {total} cases, {errors} errors ===")

if __name__ == "__main__":
    main()
