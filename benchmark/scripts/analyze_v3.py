#!/usr/bin/env python3
"""
TaskBench V3 Analysis Pipeline.

Reads benchmark_results.csv (with V2 judge scores) and generates all analysis
JSON files in results/analysis_v3_final/.

Usage:
    python3 scripts/analyze_v3.py

Requires: numpy, scipy
"""
import csv, json, os, sys
import numpy as np
from scipy import stats as sp_stats
from collections import defaultdict

np.random.seed(42)
N_BOOT = 1000

OUT_DIR = "results/analysis_v3_final"
CSV_PATH = "results/benchmark_results.csv"

V2_TASKS = [
    "sentiment_sst2", "intent_clinc150", "moderation_toxigen", "multistep_reasoning",
    "reasoning_gsm8k", "rag_qa", "code_generation", "code_review_v2", "code_explanation",
    "test_generation_v2", "function_calling", "sql_spider", "translation_enfr",
    "instruction_following", "structured_output", "extraction_hard_v2", "json_transform_v2",
    "email_summary_v2", "long_summarization", "data_to_text", "ner_extraction",
]

EXACT_TASKS = {"sentiment_sst2", "intent_clinc150", "moderation_toxigen", "multistep_reasoning"}
LLM_TASKS = [t for t in V2_TASKS if t not in EXACT_TASKS]

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

ORIGIN = {
    "qwen/qwen-turbo": "Chinese", "qwen/qwen3-8b": "Chinese", "qwen/qwen-max": "Chinese",
    "qwen/qwen3-coder": "Chinese", "qwen/qwen3.6-flash": "Chinese",
    "qwen/qwen3.6-plus": "Chinese", "qwen/qwen3.6-max-preview": "Chinese",
    "deepseek/deepseek-v3.2": "Chinese", "deepseek/deepseek-v4-pro": "Chinese",
    "bytedance-seed/seed-1.6-flash": "Chinese", "bytedance-seed/seed-2.0-lite": "Chinese",
    "bytedance-seed/seed-2.0-mini": "Chinese", "seed-2-0-pro-260328": "Chinese",
    "seed-2-0-code-preview-260328": "Chinese", "kimi-k2.6": "Chinese", "MiniMax-M2.7": "Chinese",
    "gpt-4o": "American", "gpt-4o-mini": "American", "gpt-5.1-chat": "American",
    "gpt-5.4": "American", "gpt-5.4-mini": "American", "gpt-5.4-nano": "American",
    "gpt-5.5": "American", "gpt-5.5-pro": "American", "o3": "American", "o4-mini": "American",
    "claude-opus-4-7": "American", "claude-sonnet-4-20250514": "American",
    "claude-sonnet-4-6": "American", "claude-haiku-4-5-20251001": "American",
    "gemini-2.5-flash": "American", "gemini-2.5-pro": "American",
    "gemini-3.1-pro-preview": "American", "x-ai/grok-4-fast": "American",
    "x-ai/grok-4.20": "American", "x-ai/grok-code-fast-1": "American",
    "meta-llama/llama-3.2-1b-instruct": "American", "meta-llama/llama-3.2-3b-instruct": "American",
    "meta-llama/llama-4-maverick": "American", "google/gemma-4-26b-a4b-it": "American",
    "microsoft/phi-4": "American", "nvidia/nemotron-3-super-120b-a12b": "American",
    "mistral-small-latest": "European", "mistral-medium-latest": "European",
    "mistral-large-latest": "European", "ministral-3b-latest": "European",
    "devstral-latest": "European",
}

LICENSE = {
    "meta-llama/llama-3.2-1b-instruct": "Open", "meta-llama/llama-3.2-3b-instruct": "Open",
    "meta-llama/llama-4-maverick": "Open", "deepseek/deepseek-v3.2": "Open",
    "deepseek/deepseek-v4-pro": "Open", "qwen/qwen-turbo": "Open", "qwen/qwen3-8b": "Open",
    "qwen/qwen-max": "Open", "qwen/qwen3-coder": "Open", "qwen/qwen3.6-flash": "Open",
    "qwen/qwen3.6-plus": "Open", "qwen/qwen3.6-max-preview": "Open",
    "google/gemma-4-26b-a4b-it": "Open", "microsoft/phi-4": "Open",
    "nvidia/nemotron-3-super-120b-a12b": "Open", "ministral-3b-latest": "Open",
    "mistral-small-latest": "Open", "devstral-latest": "Open",
}
# Everything not in LICENSE is Closed


def get_tier(model):
    p = MODEL_PRICES.get(model, 0.5)
    if p >= 5: return "Premium"
    if p >= 0.5: return "Standard"
    if p >= 0.08: return "Economy"
    return "Micro"


def bootstrap_ci(vals, n_boot=N_BOOT):
    arr = np.array(vals)
    means = [float(np.mean(np.random.choice(arr, len(arr), replace=True))) for _ in range(n_boot)]
    return round(float(np.mean(arr)), 3), round(float(np.percentile(means, 2.5)), 3), round(float(np.percentile(means, 97.5)), 3)


def load_data():
    """Load CSV and return per-(task, model) aggregates (>= 40 cases)."""
    raw = defaultdict(lambda: defaultdict(lambda: {"scores": [], "costs": []}))
    with open(CSV_PATH) as f:
        for r in csv.DictReader(f):
            if r["task"] in V2_TASKS:
                raw[r["task"]][r["model"]]["scores"].append(float(r["score"]))
                raw[r["task"]][r["model"]]["costs"].append(float(r["cost_usd"]))
    agg = {}
    for task in V2_TASKS:
        agg[task] = {}
        for model in raw[task]:
            d = raw[task][model]
            if len(d["scores"]) >= 40:
                agg[task][model] = {
                    "avg_score": float(np.mean(d["scores"])),
                    "avg_cost": float(np.mean(d["costs"])),
                    "n": len(d["scores"]),
                }
    return agg


def save(name, data):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Saved {name}")


# ---- Individual analyses ----

def task_model_aggregates(agg):
    """Save raw aggregates."""
    save("task_model_aggregates.json", agg)


def tier_comparison(agg):
    """Average V2 score by tier, per task and global."""
    tier_task = defaultdict(lambda: defaultdict(list))
    tier_global = defaultdict(list)
    for task in V2_TASKS:
        for model, d in agg[task].items():
            tier = get_tier(model)
            tier_task[task][tier].append(d["avg_score"])
            tier_global[tier].append(d["avg_score"])
    result = {}
    for task in V2_TASKS:
        result[task] = {t: round(float(np.mean(tier_task[task][t])), 3) for t in tier_task[task]}
    save("tier_comparison.json", result)
    return tier_global


def stats_validation(tier_global):
    """Bootstrap CIs and Mann-Whitney for tier comparisons."""
    boot = {}
    for tier in ["Premium", "Standard", "Economy", "Micro"]:
        vals = tier_global[tier]
        if len(vals) >= 2:
            mean, lo, hi = bootstrap_ci(vals)
            boot[tier] = {"mean": mean, "ci_lo": lo, "ci_hi": hi, "n": len(vals)}
    save("stats_validation.json", {"bootstrap": boot})


def task_discriminativeness(agg):
    """Score spread per task."""
    result = {}
    for task in V2_TASKS:
        scores = [d["avg_score"] for d in agg[task].values()]
        result[task] = {
            "spread": round(max(scores) - min(scores), 3),
            "std": round(float(np.std(scores)), 3),
            "min": round(min(scores), 3),
            "max": round(max(scores), 3),
        }
    save("task_discriminativeness.json", result)


def top5_per_task(agg):
    """Top 5 models per task by quality then cost."""
    result = {}
    for task in V2_TASKS:
        ranked = sorted(agg[task].items(), key=lambda x: (-x[1]["avg_score"], x[1]["avg_cost"]))
        result[task] = [{"rank": i + 1, "model": m, "avg_score": round(d["avg_score"], 3),
                         "avg_cost": round(d["avg_cost"], 6)} for i, (m, d) in enumerate(ranked[:5])]
    save("top5_per_task.json", result)


def routing_savings(agg):
    """Single best model vs cheapest adequate per task."""
    model_task_count = defaultdict(int)
    for task in V2_TASKS:
        for model in agg[task]:
            model_task_count[model] += 1
    complete = [m for m, c in model_task_count.items() if c == 21]
    best = max(complete, key=lambda m: np.mean([agg[t][m]["avg_score"] for t in V2_TASKS]))
    best_cost = float(np.mean([agg[t][best]["avg_cost"] for t in V2_TASKS]))
    best_score = float(np.mean([agg[t][best]["avg_score"] for t in V2_TASKS]))
    routed = 0
    for task in V2_TASKS:
        adequate = [(m, d) for m, d in agg[task].items() if d["avg_score"] >= 4.0]
        if adequate:
            routed += min(adequate, key=lambda x: x[1]["avg_cost"])[1]["avg_cost"]
    routed_avg = routed / len(V2_TASKS)
    savings = round((1 - routed_avg / best_cost) * 100, 1) if best_cost > 0 else 0
    save("routing_savings.json", {
        "single_best": {"model": best, "avg_score": round(best_score, 3), "avg_cost": round(best_cost, 6)},
        "routed_avg_cost": round(routed_avg, 6), "savings_pct": savings,
    })


def per_task_routing_savings(agg):
    """Savings per task vs o3."""
    result = {}
    for task in V2_TASKS:
        o3_cost = agg[task].get("o3", {}).get("avg_cost", 0)
        adequate = [(m, d) for m, d in agg[task].items() if d["avg_score"] >= 4.0]
        if adequate and o3_cost > 0:
            cheapest_m, cheapest_d = min(adequate, key=lambda x: x[1]["avg_cost"])
            result[task] = {"o3_cost": round(o3_cost, 6), "cheapest_model": cheapest_m,
                            "cheapest_cost": round(cheapest_d["avg_cost"], 6),
                            "savings_pct": round((1 - cheapest_d["avg_cost"] / o3_cost) * 100, 1)}
    save("per_task_routing_savings.json", result)


def coverage_matrix(agg):
    """Models covering all 21 tasks at different thresholds."""
    result = {"thresholds": {}}
    for threshold in [4.0, 4.5, 4.7]:
        count = sum(1 for m in set(model for t in agg for model in agg[t])
                    if sum(1 for t in V2_TASKS if m in agg.get(t, {}) and agg[t][m]["avg_score"] >= threshold) == 21)
        result["thresholds"][str(threshold)] = count
    # Cheapest per task at 4.5
    cheapest = {}
    for task in V2_TASKS:
        adequate = [(m, agg[task][m]) for m in agg[task] if agg[task][m]["avg_score"] >= 4.5]
        if adequate:
            best = min(adequate, key=lambda x: MODEL_PRICES.get(x[0], 999))
            cheapest[task] = {"model": best[0], "score": round(best[1]["avg_score"], 3),
                              "cost": round(best[1]["avg_cost"], 6)}
    result["cheapest_per_task"] = cheapest
    result["unique_cheapest"] = sorted(set(v["model"] for v in cheapest.values()))
    # All covering at 4.5
    covering = []
    for m in set(model for t in agg for model in agg[t]):
        if sum(1 for t in V2_TASKS if m in agg.get(t, {}) and agg[t][m]["avg_score"] >= 4.5) == 21:
            cost = float(np.mean([agg[t][m]["avg_cost"] for t in V2_TASKS if m in agg.get(t, {})]))
            score = float(np.mean([agg[t][m]["avg_score"] for t in V2_TASKS if m in agg.get(t, {})]))
            covering.append((m, round(cost, 6), round(score, 3)))
    result["all_covering_4_5"] = sorted(covering, key=lambda x: x[1])
    save("coverage_matrix.json", result)
    save("q12_robustness.json", result)  # alias


def generational_delta(agg):
    """Quality delta for 4 generational pairs."""
    pairs = [
        ("gpt-4o", "gpt-5.4", "GPT-4o to GPT-5.4"),
        ("gpt-4o-mini", "gpt-5.4-mini", "GPT-4o Mini to GPT-5.4 Mini"),
        ("claude-sonnet-4-20250514", "claude-sonnet-4-6", "Sonnet 4 to Sonnet 4.6"),
        ("deepseek/deepseek-v3.2", "deepseek/deepseek-v4-pro", "DeepSeek V3.2 to V4 Pro"),
    ]
    result = {}
    for old, new, label in pairs:
        per_task = {}
        for task in V2_TASKS:
            if old in agg.get(task, {}) and new in agg.get(task, {}):
                per_task[task] = {"old": round(agg[task][old]["avg_score"], 3),
                                  "new": round(agg[task][new]["avg_score"], 3),
                                  "delta": round(agg[task][new]["avg_score"] - agg[task][old]["avg_score"], 3)}
        deltas = [v["delta"] for v in per_task.values()]
        old_p, new_p = MODEL_PRICES.get(old, 0), MODEL_PRICES.get(new, 0)
        result[label] = {
            "old_model": old, "new_model": new,
            "old_price": old_p, "new_price": new_p,
            "price_change_pct": round((new_p - old_p) / old_p * 100) if old_p else 0,
            "avg_quality_delta": round(float(np.mean(deltas)), 3) if deltas else 0,
            "improved": sum(1 for d in deltas if d > 0.1),
            "same": sum(1 for d in deltas if abs(d) <= 0.1),
            "worse": sum(1 for d in deltas if d < -0.1),
            "n_tasks": len(deltas), "per_task": per_task,
        }
    save("generational_delta.json", result)


def provider_gradient(agg):
    """Per-provider quality gradient (price vs score)."""
    providers = {
        "OpenAI": [("gpt-4o-mini", 0.15), ("gpt-5.4-nano", 0.02), ("gpt-5.4-mini", 0.1),
                   ("gpt-5.1-chat", 0.8), ("gpt-5.4", 1.0), ("gpt-4o", 2.5),
                   ("gpt-5.5", 3.0), ("gpt-5.5-pro", 15.0), ("o3", 2.0), ("o4-mini", 1.1)],
        "Anthropic": [("claude-haiku-4-5-20251001", 0.80), ("claude-sonnet-4-6", 3.0),
                      ("claude-sonnet-4-20250514", 3.0), ("claude-opus-4-7", 15.0)],
        "Mistral": [("ministral-3b-latest", 0.04), ("mistral-small-latest", 0.1),
                    ("mistral-medium-latest", 0.4), ("devstral-latest", 0.2), ("mistral-large-latest", 2.0)],
        "Qwen": [("qwen/qwen-turbo", 0.05), ("qwen/qwen3-8b", 0.05), ("qwen/qwen3-coder", 0.3),
                 ("qwen/qwen3.6-flash", 0.3), ("qwen/qwen3.6-plus", 0.5), ("qwen/qwen-max", 2.0),
                 ("qwen/qwen3.6-max-preview", 1.5)],
        "Google": [("gemini-2.5-flash", 0.15), ("gemini-2.5-pro", 1.25), ("gemini-3.1-pro-preview", 1.25)],
    }
    result = {}
    for prov, models in providers.items():
        points = []
        for model, price in sorted(models, key=lambda x: x[1]):
            scores = [agg[t][model]["avg_score"] for t in V2_TASKS if model in agg.get(t, {})]
            if len(scores) >= 15:
                points.append({"model": model, "price": price, "avg_score": round(float(np.mean(scores)), 3)})
        result[prov] = points
    save("provider_gradient.json", result)


def origin_comparison(agg):
    """Quality by provider origin (Chinese / American / European)."""
    model_avgs = {}
    for model in set(m for t in agg for m in agg[t]):
        scores = [agg[t][model]["avg_score"] for t in V2_TASKS if model in agg.get(t, {})]
        if len(scores) >= 15:
            model_avgs[model] = float(np.mean(scores))
    groups = defaultdict(list)
    for m, s in model_avgs.items():
        origin = ORIGIN.get(m)
        if origin:
            groups[origin].append(s)
    result = {}
    for origin in ["Chinese", "American", "European"]:
        vals = groups.get(origin, [])
        result[origin] = {"n": len(vals), "avg": round(float(np.mean(vals)), 3) if vals else 0,
                          "min": round(min(vals), 3) if vals else 0, "max": round(max(vals), 3) if vals else 0}
    # Pairwise MW
    pairs = {}
    for a, b in [("Chinese", "American"), ("Chinese", "European"), ("American", "European")]:
        if len(groups[a]) >= 2 and len(groups[b]) >= 2:
            u, p = sp_stats.mannwhitneyu(groups[a], groups[b], alternative="two-sided")
            pairs[f"{a}_vs_{b}"] = {"U": round(float(u)), "p": round(float(p), 4)}
    result["pairwise_tests"] = pairs
    # Kruskal-Wallis
    all_groups = [groups[o] for o in ["Chinese", "American", "European"] if len(groups[o]) >= 2]
    if len(all_groups) >= 2:
        h, p = sp_stats.kruskal(*all_groups)
        result["kruskal_wallis"] = {"H": round(float(h), 2), "p": round(float(p), 4)}
    save("origin_comparison.json", result)


def license_comparison(agg):
    """Quality by weight availability (open vs closed)."""
    model_avgs = {}
    for model in set(m for t in agg for m in agg[t]):
        scores = [agg[t][model]["avg_score"] for t in V2_TASKS if model in agg.get(t, {})]
        if len(scores) >= 15:
            model_avgs[model] = float(np.mean(scores))
    open_scores = [s for m, s in model_avgs.items() if LICENSE.get(m) == "Open"]
    closed_scores = [s for m, s in model_avgs.items() if LICENSE.get(m) != "Open"]
    u, p = sp_stats.mannwhitneyu(open_scores, closed_scores, alternative="two-sided")
    save("license_comparison.json", {
        "open": {"n": len(open_scores), "avg": round(float(np.mean(open_scores)), 3),
                 "models": sorted(m for m in model_avgs if LICENSE.get(m) == "Open")},
        "closed": {"n": len(closed_scores), "avg": round(float(np.mean(closed_scores)), 3),
                   "models": sorted(m for m in model_avgs if LICENSE.get(m) != "Open")},
        "mann_whitney_p": round(float(p), 4),
        "significant": bool(p < 0.05),
    })


def ranking_flips(agg):
    """Count model-pair ranking flips between V1 and V2 scores (requires raw files)."""
    import glob
    task_model_v1 = defaultdict(lambda: defaultdict(list))
    task_model_v2 = defaultdict(lambda: defaultdict(list))
    for filepath in glob.glob("results/raw/*.json"):
        try:
            d = json.load(open(filepath))
        except:
            continue
        task, model = d.get("task", ""), d.get("model", "")
        v1, v2, resp = d.get("score"), d.get("judge_v2_score"), d.get("response", "")
        if task not in LLM_TASKS or not resp or v1 is None or v2 is None:
            continue
        task_model_v1[task][model].append(v1)
        task_model_v2[task][model].append(v2)
    # Filter >= 40
    for task in list(task_model_v1.keys()):
        for model in list(task_model_v1[task].keys()):
            if len(task_model_v1[task][model]) < 40:
                del task_model_v1[task][model]
                task_model_v2[task].pop(model, None)
    all_flips, all_total = 0, 0
    per_task = {}
    for task in LLM_TASKS:
        common = sorted(set(task_model_v1[task]) & set(task_model_v2[task]))
        v1a = {m: np.mean(task_model_v1[task][m]) for m in common}
        v2a = {m: np.mean(task_model_v2[task][m]) for m in common}
        flips, total, tied = 0, 0, 0
        for i in range(len(common)):
            for j in range(i + 1, len(common)):
                d1 = v1a[common[i]] - v1a[common[j]]
                d2 = v2a[common[i]] - v2a[common[j]]
                if abs(d1) < 0.01 or abs(d2) < 0.01:
                    tied += 1
                    continue
                total += 1
                if (d1 > 0) != (d2 > 0):
                    flips += 1
        per_task[task] = {"flips": flips, "total_pairs": total, "tied": tied,
                          "flip_rate": round(flips / total * 100, 1) if total else 0,
                          "kendall_tau": round(1 - 2 * flips / total, 3) if total else 1}
        all_flips += flips
        all_total += total
    save("ranking_flips.json", {
        "global": {"flips": all_flips, "total_pairs": all_total,
                   "flip_rate_pct": round(all_flips / all_total * 100, 1) if all_total else 0,
                   "kendall_tau": round(1 - 2 * all_flips / all_total, 3) if all_total else 1},
        "per_task": per_task,
    })


def verbosity_correlation():
    """Correlation between response length and V1→V2 delta (requires raw files)."""
    import glob
    model_len = defaultdict(list)
    model_v1 = defaultdict(list)
    model_v2 = defaultdict(list)
    for filepath in glob.glob("results/raw/*.json"):
        try:
            d = json.load(open(filepath))
        except:
            continue
        task, model = d.get("task", ""), d.get("model", "")
        v1, v2, resp = d.get("score"), d.get("judge_v2_score"), d.get("response", "")
        if task not in LLM_TASKS or not resp or v1 is None or v2 is None:
            continue
        model_len[model].append(len(resp))
        model_v1[model].append(v1)
        model_v2[model].append(v2)
    models = [m for m in model_len if len(model_len[m]) >= 200]
    avg_len = [float(np.mean(model_len[m])) for m in models]
    delta = [float(np.mean(model_v2[m]) - np.mean(model_v1[m])) for m in models]
    r, p = sp_stats.pearsonr(avg_len, delta)
    save("verbosity_correlation.json", {
        "r_verbosity_vs_delta": round(r, 4), "p_verbosity_vs_delta": round(p, 6),
        "n_models": len(models),
    })


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Loading data...")
    agg = load_data()
    print(f"Loaded {sum(len(v) for v in agg.values())} task-model pairs across {len(agg)} tasks\n")

    print("Running analyses:")
    task_model_aggregates(agg)
    tg = tier_comparison(agg)
    stats_validation(tg)
    task_discriminativeness(agg)
    top5_per_task(agg)
    routing_savings(agg)
    per_task_routing_savings(agg)
    coverage_matrix(agg)
    generational_delta(agg)
    provider_gradient(agg)
    origin_comparison(agg)
    license_comparison(agg)
    print("\n  Reading raw files for ranking flips...")
    ranking_flips(agg)
    print("  Reading raw files for verbosity...")
    verbosity_correlation()

    print(f"\nDone. {len(os.listdir(OUT_DIR))} files in {OUT_DIR}/")


if __name__ == "__main__":
    main()
