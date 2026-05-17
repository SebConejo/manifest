#!/usr/bin/env python3
"""
Rebuild benchmark_results.csv from raw JSON files.

The CSV can get corrupted by race conditions (concurrent writes from rejudge
and run_batch). This script rebuilds it entirely from the raw JSON source of
truth in results/raw/.

Usage:
    python scripts/rebuild_csv.py              # rebuild
    python scripts/rebuild_csv.py --dry-run    # show stats only
"""

import csv
import json
import os
import re
import sys
from pathlib import Path


# Model registry — must match run_batch.py MODELS
MODELS = {
    "claude-opus-4-7": {"provider": "anthropic", "input_price": 15.00, "output_price": 75.00},
    "claude-sonnet-4-20250514": {"provider": "anthropic", "input_price": 3.00, "output_price": 15.00},
    "claude-sonnet-4-6": {"provider": "anthropic", "input_price": 3.00, "output_price": 15.00},
    "claude-haiku-4-5-20251001": {"provider": "anthropic", "input_price": 0.80, "output_price": 4.00},
    "gpt-5.5": {"provider": "openai", "input_price": 3.00, "output_price": 12.00},
    "gpt-5.5-pro": {"provider": "openai_responses", "input_price": 15.00, "output_price": 75.00},
    "o3": {"provider": "openai", "input_price": 2.00, "output_price": 8.00},
    "gpt-5.4": {"provider": "openai", "input_price": 1.00, "output_price": 4.00},
    "gpt-5.4-mini": {"provider": "openai", "input_price": 0.30, "output_price": 1.20},
    "gpt-5.4-nano": {"provider": "openai", "input_price": 0.10, "output_price": 0.40},
    "gpt-4o": {"provider": "openai", "input_price": 2.50, "output_price": 10.00},
    "gpt-4o-mini": {"provider": "openai", "input_price": 0.15, "output_price": 0.60},
    "gemini-3.1-pro-preview": {"provider": "gemini", "input_price": 2.50, "output_price": 15.00},
    "gemini-2.5-pro": {"provider": "gemini", "input_price": 1.25, "output_price": 10.00},
    "gemini-2.5-flash": {"provider": "gemini", "input_price": 0.15, "output_price": 0.60},
    "gemini-2.0-flash": {"provider": "gemini", "input_price": 0.10, "output_price": 0.40},
    "MiniMax-M2.7": {"provider": "minimax", "input_price": 1.10, "output_price": 4.40},
    "mistral-large-latest": {"provider": "mistral", "input_price": 2.00, "output_price": 6.00},
    "mistral-medium-latest": {"provider": "mistral", "input_price": 0.40, "output_price": 2.00},
    "mistral-small-latest": {"provider": "mistral", "input_price": 0.10, "output_price": 0.30},
    "ministral-3b-latest": {"provider": "mistral", "input_price": 0.04, "output_price": 0.04},
    "devstral-latest": {"provider": "mistral", "input_price": 0.10, "output_price": 0.30},
    "seed-2-0-pro-260328": {"provider": "byteplus", "input_price": 0.60, "output_price": 2.40},
    "seed-2-0-code-preview-260328": {"provider": "byteplus", "input_price": 0.30, "output_price": 1.20},
    "kimi-k2.6": {"provider": "moonshot", "input_price": 0.60, "output_price": 2.40},
    "bytedance-seed/seed-2.0-lite": {"provider": "openrouter", "input_price": 0.25, "output_price": 1.00},
    "bytedance-seed/seed-1.6-flash": {"provider": "openrouter", "input_price": 0.075, "output_price": 0.30},
    "bytedance-seed/seed-2.0-mini": {"provider": "openrouter", "input_price": 0.10, "output_price": 0.40},
    "qwen/qwen-max": {"provider": "openrouter", "input_price": 1.04, "output_price": 4.16},
    "qwen/qwen3.6-plus": {"provider": "openrouter", "input_price": 0.325, "output_price": 1.30},
    "qwen/qwen3-coder": {"provider": "openrouter", "input_price": 0.22, "output_price": 0.88},
    "qwen/qwen3.6-flash": {"provider": "openrouter", "input_price": 0.25, "output_price": 1.00},
    "qwen/qwen3.6-max-preview": {"provider": "openrouter", "input_price": 1.30, "output_price": 5.20},
    "deepseek/deepseek-v3.2": {"provider": "openrouter", "input_price": 0.25, "output_price": 1.10},
    "deepseek/deepseek-v4-flash": {"provider": "openrouter", "input_price": 0.14, "output_price": 0.56},
    "deepseek/deepseek-v4-pro": {"provider": "openrouter", "input_price": 0.435, "output_price": 1.74},
    "meta-llama/llama-4-maverick": {"provider": "openrouter", "input_price": 0.15, "output_price": 0.60},
    "x-ai/grok-4.20": {"provider": "openrouter", "input_price": 1.25, "output_price": 5.00},
    "x-ai/grok-4-fast": {"provider": "openrouter", "input_price": 0.20, "output_price": 0.80},
    "x-ai/grok-code-fast-1": {"provider": "openrouter", "input_price": 0.20, "output_price": 0.80},
    "meta-llama/llama-3.2-1b-instruct": {"provider": "openrouter", "input_price": 0.027, "output_price": 0.027},
    "meta-llama/llama-3.2-3b-instruct": {"provider": "openrouter", "input_price": 0.051, "output_price": 0.051},
    "qwen/qwen-turbo": {"provider": "openrouter", "input_price": 0.033, "output_price": 0.033},
    "qwen/qwen3-8b": {"provider": "openrouter", "input_price": 0.050, "output_price": 0.050},
    "google/gemma-4-26b-a4b-it": {"provider": "openrouter", "input_price": 0.060, "output_price": 0.060},
    "microsoft/phi-4": {"provider": "openrouter", "input_price": 0.065, "output_price": 0.065},
    "nvidia/nemotron-3-super-120b-a12b": {"provider": "openrouter", "input_price": 0.09, "output_price": 0.09},
    "DeepSeek-V3.2": {"provider": "azure", "input_price": 0.30, "output_price": 1.10},
    "DeepSeek-R1": {"provider": "azure", "input_price": 0.55, "output_price": 2.19},
    "gpt-5.1-chat": {"provider": "azure", "input_price": 0.80, "output_price": 3.20},
    "o4-mini": {"provider": "azure", "input_price": 1.10, "output_price": 4.40},
    "grok-4-20-non-reasoning": {"provider": "azure", "input_price": 2.00, "output_price": 8.00},
    "grok-4-20-reasoning": {"provider": "azure", "input_price": 2.00, "output_price": 8.00},
    "Kimi-K2.6": {"provider": "azure", "input_price": 0.60, "output_price": 2.40},
    "Llama-4-Scout-17B-16E-Instruct": {"provider": "azure", "input_price": 0.17, "output_price": 0.17},
    "mistral-medium-2505": {"provider": "azure", "input_price": 0.40, "output_price": 2.00},
    "Codestral-2501": {"provider": "azure", "input_price": 0.30, "output_price": 0.90},
}

# Task eval types — must match run_batch.py TASK_DEFS
TASK_EVAL_TYPES = {
    "sentiment_sst2": "exact",
    "reasoning_gsm8k": "llm_judge",
    "code_explanation": "llm_judge",
    "code_generation": "llm_judge",
    "intent_clinc150": "exact",
    "rag_qa": "llm_judge",
    "moderation_toxigen": "exact",
    "email_summary_v2": "llm_judge",
    "data_to_text": "llm_judge",
    "long_summarization": "llm_judge",
    "code_review_v2": "llm_judge",
    "structured_output": "llm_judge",
    "extraction_hard_v2": "llm_judge",
    "instruction_following": "llm_judge",
    "json_transform_v2": "llm_judge",
    "test_generation_v2": "llm_judge",
    "multistep_reasoning": "exact",
    "function_calling": "llm_judge",
    "ner_extraction": "llm_judge",
    "sql_spider": "llm_judge",
    "translation_enfr": "llm_judge",
    # Legacy v1 tasks
    "sentiment": "exact",
    "reasoning": "llm_judge",
    "intent_easy": "exact",
    "intent_hard": "exact",
    "code_review": "llm_judge",
    "email_summary": "llm_judge",
    "entity_extraction": "llm_judge",
    "extraction_hard": "llm_judge",
    "json_transform": "llm_judge",
    "content_moderation": "exact",
    "sql_generation": "llm_judge",
    "test_generation": "llm_judge",
    "translation": "llm_judge",
}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    os.chdir(Path(__file__).parent.parent)
    raw_dir = "results/raw"
    csv_path = "results/benchmark_results.csv"

    rows = []
    errors = 0
    skipped_empty = 0

    for filename in sorted(os.listdir(raw_dir)):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(raw_dir, filename)
        try:
            with open(filepath) as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            errors += 1
            continue

        model = data.get("model", "")
        task = data.get("task", "")
        case_idx = data.get("case", "")
        response = data.get("response", "") or ""
        # Prefer V2 judge score if available, fall back to V1
        score = data.get("judge_v2_score") or data.get("score", 0) or 0
        cost = data.get("cost", 0) or 0
        tokens = data.get("tokens", {})

        # Skip empty responses (no point keeping them)
        if not response.strip() and score == 0:
            skipped_empty += 1
            continue

        # Get model info
        model_info = MODELS.get(model, {})
        provider = model_info.get("provider", "unknown")
        input_price = model_info.get("input_price", 0)
        output_price = model_info.get("output_price", 0)

        # Get eval type
        eval_type = TASK_EVAL_TYPES.get(task, "llm_judge")

        # Get tokens
        input_tokens = tokens.get("input", 0) if isinstance(tokens, dict) else 0
        output_tokens = tokens.get("output", 0) if isinstance(tokens, dict) else 0

        # Response preview
        preview = response[:100].replace("\n", " ") if response else ""

        # Timestamp from file mtime
        mtime = os.path.getmtime(filepath)
        from datetime import datetime
        timestamp = datetime.fromtimestamp(mtime).strftime("%Y%m%d_%H%M%S")

        rows.append([
            timestamp, task, case_idx, model, provider,
            input_price, output_price, input_tokens, output_tokens,
            cost, score, eval_type, preview
        ])

    print(f"Raw files scanned: {len(rows) + errors + skipped_empty}")
    print(f"Valid rows: {len(rows)}")
    print(f"Skipped (empty response, score 0): {skipped_empty}")
    print(f"Errors: {errors}")

    # Dedup by (task, model, case_idx) — keep the one with highest score
    from collections import defaultdict
    dedup = {}
    for row in rows:
        key = (row[1], row[3], row[2])  # task, model, case_idx
        if key in dedup:
            existing_score = float(dedup[key][10])
            new_score = float(row[10])
            if new_score > existing_score:
                dedup[key] = row
        else:
            dedup[key] = row

    final_rows = sorted(dedup.values(), key=lambda r: (r[1], r[3], int(r[2]) if str(r[2]).isdigit() else 0))
    print(f"After dedup: {len(final_rows)} (removed {len(rows) - len(final_rows)} duplicates)")

    if args.dry_run:
        # Show stats
        from collections import Counter
        tasks = Counter(r[1] for r in final_rows)
        models = Counter(r[3] for r in final_rows)
        zeros = sum(1 for r in final_rows if float(r[10]) == 0)
        print(f"\nTasks: {len(tasks)}")
        print(f"Models: {len(models)}")
        print(f"Zeros: {zeros}")
        print(f"\nTop tasks:")
        for t, n in tasks.most_common(25):
            print(f"  {t}: {n}")
        return

    # Backup old CSV
    if os.path.exists(csv_path):
        backup = csv_path + ".bak"
        import shutil
        shutil.copy2(csv_path, backup)
        print(f"\nBacked up old CSV to {backup}")

    # Write new CSV
    header = [
        "timestamp", "task", "case_idx", "model", "provider",
        "input_price_per_m", "output_price_per_m", "input_tokens", "output_tokens",
        "cost_usd", "score", "eval_type", "response_preview"
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(final_rows)

    print(f"Wrote {len(final_rows)} rows to {csv_path}")


if __name__ == "__main__":
    main()
