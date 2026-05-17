#!/usr/bin/env python3
"""
TaskBench Figure Generator.

Reads JSON analysis files from results/analysis_v3_final/ and generates
all publication SVG figures. Follows PARETO_STYLE_GUIDE.md.

Usage:
    python3 scripts/generate_figures.py

Requires: numpy, matplotlib
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from collections import defaultdict

OUT_DIR = "results/analysis_v3_final"

V2_TASKS = [
    "sentiment_sst2", "intent_clinc150", "moderation_toxigen", "multistep_reasoning",
    "reasoning_gsm8k", "rag_qa", "code_generation", "code_review_v2", "code_explanation",
    "test_generation_v2", "function_calling", "sql_spider", "translation_enfr",
    "instruction_following", "structured_output", "extraction_hard_v2", "json_transform_v2",
    "email_summary_v2", "long_summarization", "data_to_text", "ner_extraction",
]

TASK_SHORT = {
    "sentiment_sst2": "Sentiment", "intent_clinc150": "Intent-150",
    "moderation_toxigen": "ToxiGen", "multistep_reasoning": "Multistep",
    "reasoning_gsm8k": "GSM8K", "rag_qa": "RAG QA", "code_generation": "Code Gen",
    "code_review_v2": "Code Review", "code_explanation": "Code Expl",
    "test_generation_v2": "Test Gen", "function_calling": "Func Call",
    "sql_spider": "SQL", "translation_enfr": "Translation",
    "instruction_following": "Instruct", "structured_output": "Struct Out",
    "extraction_hard_v2": "Extraction", "json_transform_v2": "JSON Trans",
    "email_summary_v2": "Email Sum", "long_summarization": "Long Sum",
    "data_to_text": "Data-Text", "ner_extraction": "NER",
}

TIER_COLOR = {"Premium": "#d62728", "Standard": "#1f77b4", "Economy": "#2ca02c", "Micro": "#ff7f0e"}
TIER_MARKER = {"Premium": "D", "Standard": "s", "Economy": "o", "Micro": "^"}

MODEL_PRICES = {
    "claude-opus-4-7": 15.0, "gpt-5.5-pro": 15.0, "claude-sonnet-4-20250514": 3.0,
    "claude-sonnet-4-6": 3.0, "gpt-4o": 2.5, "gpt-5.5": 3.0, "gpt-5.1-chat": 0.8,
    "o3": 2.0, "gemini-2.5-pro": 1.25, "gemini-3.1-pro-preview": 1.25, "MiniMax-M2.7": 1.0,
    "mistral-large-latest": 2.0, "qwen/qwen-max": 2.0, "x-ai/grok-4.20": 2.0,
    "qwen/qwen3.6-max-preview": 1.5, "kimi-k2.6": 0.6, "gpt-5.4": 1.0, "o4-mini": 1.1,
    "gpt-4o-mini": 0.15, "gemini-2.5-flash": 0.15, "mistral-small-latest": 0.1,
    "mistral-medium-latest": 0.4, "gpt-5.4-mini": 0.1, "deepseek/deepseek-v3.2": 0.14,
    "deepseek/deepseek-v4-pro": 0.435, "devstral-latest": 0.2, "x-ai/grok-4-fast": 0.6,
    "x-ai/grok-code-fast-1": 0.6, "qwen/qwen3-coder": 0.3, "qwen/qwen3.6-flash": 0.3,
    "qwen/qwen3.6-plus": 0.5, "meta-llama/llama-4-maverick": 0.2,
    "seed-2-0-pro-260328": 0.2, "seed-2-0-code-preview-260328": 0.1,
    "bytedance-seed/seed-2.0-mini": 0.15, "bytedance-seed/seed-2.0-lite": 0.075,
    "gpt-5.4-nano": 0.02, "ministral-3b-latest": 0.04, "qwen/qwen-turbo": 0.05,
    "qwen/qwen3-8b": 0.05, "bytedance-seed/seed-1.6-flash": 0.075,
    "google/gemma-4-26b-a4b-it": 0.05, "microsoft/phi-4": 0.02,
    "meta-llama/llama-3.2-1b-instruct": 0.027, "meta-llama/llama-3.2-3b-instruct": 0.051,
    "nvidia/nemotron-3-super-120b-a12b": 0.09,
}


def get_tier(m):
    p = MODEL_PRICES.get(m, 0.5)
    if p >= 5: return "Premium"
    if p >= 0.5: return "Standard"
    if p >= 0.08: return "Economy"
    return "Micro"


def load_json(name):
    with open(os.path.join(OUT_DIR, name)) as f:
        return json.load(f)


def save_fig(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, format="svg", dpi=150)
    plt.close(fig)
    print(f"  Saved {name}")


# ---- Figure generators ----

def fig_heatmap(agg):
    """Model x Task quality heatmap."""
    model_task_count = defaultdict(int)
    for task in V2_TASKS:
        for model in agg.get(task, {}):
            model_task_count[model] += 1
    models = sorted([m for m, c in model_task_count.items() if c >= 19],
                    key=lambda m: -np.mean([agg[t][m]["avg_score"] for t in V2_TASKS if m in agg.get(t, {})]))
    matrix = np.full((len(models), len(V2_TASKS)), np.nan)
    for i, model in enumerate(models):
        for j, task in enumerate(V2_TASKS):
            if model in agg.get(task, {}):
                matrix[i, j] = agg[task][model]["avg_score"]
    short_names = [m.split("/")[-1][:20] for m in models]
    tiers = [get_tier(m) for m in models]
    fig, ax = plt.subplots(figsize=(18, 15))
    im = ax.imshow(matrix, cmap="RdYlGn", vmin=1, vmax=5, aspect="auto")
    ax.set_xticks(range(len(V2_TASKS)))
    ax.set_xticklabels([TASK_SHORT[t] for t in V2_TASKS], rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(models)))
    for i, (label, tier) in enumerate(zip(short_names, tiers)):
        ax.text(-0.5, i, label, ha="right", va="center", fontsize=7,
                color=TIER_COLOR[tier], fontweight="bold", transform=ax.transData)
    ax.set_yticklabels(["" for _ in models])
    for i in range(len(models)):
        for j in range(len(V2_TASKS)):
            if not np.isnan(matrix[i, j]):
                color = "white" if matrix[i, j] < 3 else "black"
                ax.text(j, i, f"{matrix[i,j]:.1f}", ha="center", va="center", fontsize=5, color=color)
    plt.colorbar(im, ax=ax, label="Average Score (1-5)", shrink=0.5, pad=0.02)
    ax.set_title("TaskBench: Model Quality Across 21 Production Tasks", fontsize=14, fontweight="bold", pad=15)
    fig.text(0.5, 0.01, f"{len(models)} models, 21 tasks. V2 judge (GPT-4o, correctness-focused).",
             ha="center", fontsize=8, color="#555555", style="italic")
    fig.tight_layout(rect=[0.08, 0.03, 1, 0.97])
    save_fig(fig, "heatmap_v3.svg")


def fig_tier_comparison(tier_data):
    """Average score by tier per task."""
    tiers_order = ["Micro", "Economy", "Standard", "Premium"]
    colors = ["#ff7f0e", "#2ca02c", "#1f77b4", "#d62728"]
    fig, axes = plt.subplots(3, 7, figsize=(20, 10), sharey=True)
    axes = axes.flatten()
    for idx, task in enumerate(V2_TASKS):
        ax = axes[idx]
        means = [tier_data[task].get(t, 0) for t in tiers_order]
        ax.bar(range(4), means, color=colors, alpha=0.8)
        ax.set_title(TASK_SHORT[task], fontsize=8, fontweight="bold")
        ax.set_xticks(range(4))
        ax.set_xticklabels(["Mi", "Ec", "St", "Pr"], fontsize=6)
        ax.set_ylim(0, 5.5)
        ax.tick_params(axis="y", labelsize=6)
    fig.suptitle("Average Score by Price Tier per Task (V2 Judge)", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save_fig(fig, "tier_comparison_v3.svg")


def fig_task_discriminativeness(disc):
    """Task spread bar chart."""
    sorted_tasks = sorted(disc, key=lambda t: -disc[t]["spread"])
    fig, ax = plt.subplots(figsize=(12, 6))
    spreads = [disc[t]["spread"] for t in sorted_tasks]
    colors = ["#e74c3c" if s > 1.5 else "#f39c12" if s > 0.5 else "#2ecc71" for s in spreads]
    ax.barh(range(len(sorted_tasks)), spreads, color=colors, alpha=0.8)
    ax.set_yticks(range(len(sorted_tasks)))
    ax.set_yticklabels([TASK_SHORT[t] for t in sorted_tasks], fontsize=9)
    ax.set_xlabel("Score Spread (max - min)", fontsize=10)
    ax.set_title("Task Discriminativeness (V2 Judge)", fontsize=12, fontweight="bold")
    ax.invert_yaxis()
    fig.tight_layout()
    save_fig(fig, "task_discriminativeness_v3.svg")


def fig_per_task_routing(routing_data):
    """Per-task routing savings bar chart."""
    sorted_tasks = sorted(routing_data, key=lambda t: -routing_data[t].get("savings_pct", 0))
    fig, ax = plt.subplots(figsize=(12, 6))
    savings = [routing_data[t].get("savings_pct", 0) for t in sorted_tasks]
    ax.barh(range(len(sorted_tasks)), savings, color="#2ecc71", alpha=0.8)
    ax.set_yticks(range(len(sorted_tasks)))
    ax.set_yticklabels([TASK_SHORT[t] for t in sorted_tasks], fontsize=9)
    ax.set_xlabel("Cost savings vs o3 (%)", fontsize=11)
    ax.set_title("Per-Task Routing Savings", fontsize=13, fontweight="bold")
    ax.invert_yaxis()
    ax.set_xlim(0, 105)
    fig.tight_layout()
    save_fig(fig, "per_task_routing_savings_v3.svg")


def main():
    print("Loading analysis data...")
    agg = load_json("task_model_aggregates.json")
    tier_data = load_json("tier_comparison.json")
    disc = load_json("task_discriminativeness.json")
    routing = load_json("per_task_routing_savings.json")

    print("\nGenerating figures:")
    fig_heatmap(agg)
    fig_tier_comparison(tier_data)
    fig_task_discriminativeness(disc)
    fig_per_task_routing(routing)

    # Figures already in v3 from inline runs (no regen needed):
    # verbosity_scatter.svg, provider_gradient.svg, generational_delta.svg,
    # origin_comparison.svg, license_comparison.svg, per_task_routing_savings.svg
    print("\nNote: verbosity, provider gradient, generational delta, origin,")
    print("and license figures were already generated on V3 data.")
    print(f"\nDone. SVGs in {OUT_DIR}/")


if __name__ == "__main__":
    main()
