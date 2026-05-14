# Pareto Figure Style Guide

**Validated on:** RAG QA (v8), 2026-05-14
**Reference file:** `results/analysis_v2_final/pareto_rag_qa_v8.svg`

This document defines the exact visual style for all TaskBench Pareto scatter
plots. A new session MUST follow this guide to produce consistent figures.
Do NOT use auto-placement libraries (adjustText, etc.) — they failed after
7 iterations. See LEARNINGS.md section 18.

---

## Layout: Dual Panel

Two panels side by side, same y-axis range, different x-axis ranges.

```python
fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(14, 6.5),
    gridspec_kw={'width_ratios': [1, 1], 'wspace': 0.25})
```

- **Left panel ("Low-cost models"):** x-axis 0 to P75 * 1.5 millicents (typically 0-1 mc).
  Shows the dense cluster where most models live. This is where the action is.
- **Right panel ("Full price range"):** x-axis 0 to max_cost * 1.1 millicents.
  Shows Premium outliers. Contains a dashed grey rectangle marking the left panel's
  range with label "see left panel".

```python
# Compute x ranges
sorted_costs = sorted(costs_millicents)
p75 = sorted_costs[int(len(sorted_costs) * 0.75)]
x_left_max = max(1.0, round(p75 * 1.5, 1))
x_right_max = max(costs_millicents) * 1.1
```

Y-axis: `min(scores) - 0.3` to `5.4` (same for both panels).

---

## Points

| Tier | Color | Marker | Hex |
|------|-------|--------|-----|
| Premium | Red | Diamond `D` | `#d62728` |
| Standard | Blue | Square `s` | `#1f77b4` |
| Economy | Green | Circle `o` | `#2ca02c` |
| Micro | Orange | Triangle `^` | `#ff7f0e` |

```python
TIER_COLOR = {'Premium': '#d62728', 'Standard': '#1f77b4', 'Economy': '#2ca02c', 'Micro': '#ff7f0e'}
TIER_MARKER = {'Premium': 'D', 'Standard': 's', 'Economy': 'o', 'Micro': '^'}
```

Point size: `s=35`. Edge: `edgecolors='#444444', linewidths=0.5`. Alpha: `0.75`.

```python
ax.scatter(x, y, c=TIER_COLOR[tier], marker=TIER_MARKER[tier],
           s=35, alpha=0.75, zorder=3, edgecolors='#444444', linewidths=0.5,
           label=f'{tier} (n={count})' if is_left_panel else tier)
```

---

## Pareto Frontier Line

**Color: black** (`#222222`). **Solid line**, not dashed. **Width: 2.5**.

```python
ax.plot(pareto_costs, pareto_scores,
        color='#222222', linewidth=2.5, alpha=0.8, zorder=2,
        solid_capstyle='round',
        label='Pareto frontier' if is_left_panel else None)
```

The frontier is computed as: sort by cost ascending, keep only points where
score strictly increases.

```python
def compute_pareto(costs, scores):
    pareto = []
    best = -1
    for i in sorted(range(len(costs)), key=lambda i: costs[i]):
        if scores[i] > best:
            pareto.append(i)
            best = scores[i]
    return pareto
```

---

## Labels

### Rules (non-negotiable)

1. **Maximum 3 labels per panel.** More creates clutter.
2. **Fully manual placement.** Use `ax.annotate` with `xytext` in offset points.
3. **No label touches another label, a point, the legend, or the axes.**
4. **Short arrows only** (10-30 pixel offset). No cross-chart arrows.
5. If a label cannot be placed cleanly, remove it.

### Which models to label

**Left panel (3 labels):**
- Pareto winner: highest quality on the frontier (usually top-right of frontier)
- Worst model: lowest score in the panel (usually bottom-left)
- Sweet spot: cheapest model scoring >= 4.5 (or an interesting intermediate)

**Right panel (2 labels):**
- Most expensive Premium model (usually Claude Opus or GPT-5.5 Pro)
- Second Premium or the most expensive Standard that tells a story

Do NOT repeat a model that's already labeled on the left panel.

### Label style

```python
label_style = dict(
    fontsize=7.5,
    color='#222222',
    bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='#bbbbbb', lw=0.4, alpha=0.9),
    arrowprops=dict(arrowstyle='-', color='#777777', lw=0.7, shrinkA=0, shrinkB=2),
    zorder=11,
)

# Example: label below-right of point
ax.annotate('Qwen Turbo', xy=(x, y), xytext=(15, -20),
            textcoords='offset points', fontweight='bold', **label_style)
```

Bold for Pareto-frontier models. Normal weight for non-frontier.

### Offset directions cheat sheet

| Position needed | xytext |
|----------------|--------|
| Below-right | `(15, -20)` |
| Below-left | `(-25, -18)` |
| Above-right | `(15, 12)` |
| Above-left | `(-25, 15)` |
| Right | `(18, 0)` |
| Left | `(-25, 0)` |

Adjust by +/-5 pixels to avoid specific collisions.

---

## Legend

Position: `loc='lower right'` on the left panel only. `framealpha=0.9`, `fontsize=8`.
The right panel has no legend (same colors, would be redundant).

```python
ax_left.legend(fontsize=8, loc='lower right', framealpha=0.9)
```

If labels collide with lower-right, move legend to `'upper left'` — but check
that the upper-left area is empty first.

---

## Titles and Caption

**Suptitle** (above both panels):
```python
fig.suptitle(f'{task_title}: Cost vs Quality', fontsize=14, fontweight='bold', y=0.99)
```

**Panel titles:**
```python
ax_left.set_title(f'Low-cost models (0–{x_left_max:.0f} mc)', fontsize=11, fontweight='bold')
ax_right.set_title(f'Full price range (0–{x_right_max:.0f} mc)', fontsize=11, fontweight='bold')
```

**Caption** (below both panels):
```python
fig.text(0.5, 0.005,
    f'n = {n} models, {n_cases} cases each. Dataset: {dataset}. Evaluation: {eval_method}.',
    ha='center', fontsize=8, color='#555555', style='italic')
```

**Axes:**
```python
ax.set_xlabel('Cost per query (millicents)', fontsize=10)
ax_left.set_ylabel('Average quality score (1–5)', fontsize=10)
```

---

## Zoom Rectangle (right panel)

Grey dashed rectangle marking the left panel's x-range:

```python
from matplotlib.patches import Rectangle
rect = Rectangle((0, y_min), x_left_max, y_max - y_min,
                  lw=1.5, edgecolor='#aaaaaa', facecolor='#f5f5f5',
                  alpha=0.2, linestyle='--', zorder=1)
ax_right.add_patch(rect)
ax_right.annotate('← see left panel',
    xy=(x_left_max + x_right_max*0.01, y_min + 0.12),
    fontsize=7, color='#999999', style='italic')
```

---

## Grid and Ticks

```python
ax.grid(True, alpha=0.15)
ax.tick_params(labelsize=9)
```

---

## Tight Layout

```python
fig.tight_layout(rect=[0, 0.03, 1, 0.96])
```

The `rect` leaves room for the suptitle (top) and caption (bottom).

---

## Per-Task Label Positions

Each task needs its own hardcoded label positions because point distributions
differ. When generating a new task's Pareto:

1. Generate the figure WITHOUT labels first
2. Open the SVG and identify the 3-5 key models visually
3. Look up their (cost, score) coordinates
4. Add `ax.annotate` calls with offset-point positions
5. Verify no overlaps by opening the SVG

This takes ~3 minutes per task. It's faster than debugging auto-placement.

---

## Display Names

Use human-readable model names, not API IDs:

```python
DISPLAY_NAMES = {
    'claude-opus-4-7': 'Claude Opus 4.7',
    'gpt-5.5-pro': 'GPT-5.5 Pro',
    'gpt-4o-mini': 'GPT-4o Mini',
    'qwen/qwen-turbo': 'Qwen Turbo',
    'qwen/qwen3-8b': 'Qwen3-8B',
    'meta-llama/llama-3.2-1b-instruct': 'Llama 1B',
    'meta-llama/llama-3.2-3b-instruct': 'Llama 3B',
    'bytedance-seed/seed-2.0-lite': 'Seed 2.0 Lite',
    'nvidia/nemotron-3-super-120b-a12b': 'Nemotron 120B',
    'ministral-3b-latest': 'Ministral 3B',
    'devstral-latest': 'Devstral',
    # ... add more as needed
}
```

---

## Tier Boundaries

| Tier | Input price/M tokens |
|------|---------------------|
| Premium | >= $5.00 |
| Standard | $0.50 - $4.99 |
| Economy | $0.08 - $0.49 |
| Micro | < $0.08 |
