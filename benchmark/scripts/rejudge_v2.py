"""Re-judge reasoning_gsm8k and rag_qa with GPT-4o and V2 correctness-focused prompts."""
import json, glob, os, sys, time, requests
from pathlib import Path

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
JUDGE_MODEL = "gpt-4o"
MAX_RETRIES = 3

PROMPTS = {
    "reasoning_gsm8k": """You are evaluating a math problem response.

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
Respond with ONLY a number 1-5.""",

    "rag_qa": """You are evaluating a question-answering response. The model was given a context passage and asked to answer ONLY from that context.

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
Respond with ONLY a number 1-5.""",
}

def call_judge(prompt):
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
    body = {
        "model": JUDGE_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 5,
        "temperature": 0,
    }
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post("https://api.openai.com/v1/chat/completions",
                                json=body, headers=headers, timeout=30)
            if resp.status_code == 429:
                wait = 5 * (attempt + 1)
                print(f"  RATE_LIMIT, retry {attempt+1}/{MAX_RETRIES} in {wait}s", flush=True)
                time.sleep(wait)
                continue
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            # Extract number
            for c in content.strip():
                if c.isdigit() and 1 <= int(c) <= 5:
                    return int(c), content.strip()
            return None, content.strip()
        except Exception as e:
            print(f"  ERROR: {e}", flush=True)
            time.sleep(2)
    return None, "max_retries"

def load_dataset_case(task, case_idx):
    """Load the original dataset case to get context/input for the judge prompt."""
    sys.path.insert(0, "scripts")
    from run_batch import TASK_DEFS
    td = TASK_DEFS[task]
    with open(td["dataset"]) as f:
        cases = [json.loads(l) for l in f]
    if case_idx < len(cases):
        return cases[case_idx]
    return {}

def main():
    tasks = ["reasoning_gsm8k", "rag_qa"]
    log_path = "results/rejudge_v2_log.jsonl"
    
    total = 0
    errors = 0
    
    for task in tasks:
        print(f"\n=== Re-judging {task} with GPT-4o ===", flush=True)
        files = sorted(glob.glob(f"results/raw/{task}_*.json"))
        
        for filepath in files:
            d = json.load(open(filepath))
            response = d.get("response", "")
            if not response:
                continue
            
            expected = str(d.get("expected", ""))
            case_idx = d.get("case_idx")
            
            # Build judge prompt
            template = PROMPTS[task]
            
            if task == "rag_qa":
                # Need the context from the dataset
                if case_idx is not None:
                    case_data = load_dataset_case(task, case_idx)
                else:
                    # Try to extract case_idx from filename
                    parts = os.path.basename(filepath).rsplit("_", 1)
                    idx = int(parts[-1].replace(".json", ""))
                    case_data = load_dataset_case(task, idx)
                context = case_data.get("context", "")[:3000]
                judge_input = case_data.get("input", "")[:500]
                prompt = template.format(
                    expected=expected[:200],
                    context=context,
                    response=response[:3000],
                )
            else:
                # reasoning_gsm8k
                if case_idx is not None:
                    case_data = load_dataset_case(task, case_idx)
                else:
                    parts = os.path.basename(filepath).rsplit("_", 1)
                    idx = int(parts[-1].replace(".json", ""))
                    case_data = load_dataset_case(task, idx)
                prompt = template.format(
                    expected=expected,
                    input=case_data.get("input", "")[:2000],
                    response=response[:3000],
                )
            
            new_score, raw = call_judge(prompt)
            total += 1
            
            if new_score is None:
                errors += 1
                print(f"  PARSE_ERROR on {os.path.basename(filepath)}: raw='{raw}'", flush=True)
                continue
            
            old_score = d.get("score", 0)
            
            # Save to raw file
            d["judge_v2_score"] = new_score
            d["judge_v2_raw"] = raw
            d["judge_v2_model"] = JUDGE_MODEL
            with open(filepath, "w") as f:
                json.dump(d, f, indent=2)
            
            # Log
            entry = {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "task": task,
                "model": d.get("model", ""),
                "case": os.path.basename(filepath),
                "old_score": old_score,
                "new_score": new_score,
                "judge_raw": raw,
            }
            with open(log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
            
            if total % 100 == 0:
                print(f"  Processed {total} cases ({errors} errors)", flush=True)
        
        print(f"  Done: {task}", flush=True)
    
    print(f"\n=== COMPLETE: {total} cases, {errors} errors ===", flush=True)

if __name__ == "__main__":
    main()
