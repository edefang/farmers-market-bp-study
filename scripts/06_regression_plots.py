"""
Step: Regression plots for adherence vs. systolic BP change.

Produces one general (pooled) linear regression plot and one linear
regression plot per study arm, each fit and drawn separately.

  07_regression_general.png      - all 300 participants, one fit
  08_regression_dietitian.png    - Dietitian arm only
  09_regression_ai_assistant.png - AI Assistant arm only
  10_regression_control.png      - Control arm only
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_data, FIGURES_DIR, GROUP_COLORS  # noqa: E402

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

X_COL = "adherence_pct"
Y_COL = "systolic_change"

PANELS = [
    ("07_regression_general.png", "All Groups (General)", None, "#444444"),
    ("08_regression_dietitian.png", "Dietitian", "Dietitian", GROUP_COLORS["Dietitian"]),
    ("09_regression_ai_assistant.png", "AI Assistant", "AI_Assistant", GROUP_COLORS["AI_Assistant"]),
    ("10_regression_control.png", "Control (No Guidance)", "Control_NoGuidance", GROUP_COLORS["Control_NoGuidance"]),
]


def fit_and_plot(df, filename, title, group_filter, color):
    sub = df if group_filter is None else df[df["group"] == group_filter]
    x = sub[X_COL].values
    y = sub[Y_COL].values

    slope, intercept, r, p, se = stats.linregress(x, y)
    r2 = r ** 2

    fig, ax = plt.subplots(figsize=(8, 6.5))
    ax.scatter(x, y, color=color, alpha=0.65, edgecolor="white", linewidth=0.4, label="Participants")

    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, color="black", linewidth=2, label="Linear fit")

    ax.axhline(0, color="black", linestyle="--", linewidth=1, alpha=0.4)
    ax.set_xlabel("Adherence (% of provided produce eaten)")
    ax.set_ylabel("Systolic BP Change (mmHg)")
    ax.set_title(f"{title}: Adherence vs. Systolic BP Change")

    eq = f"y = {slope:.3f}x + {intercept:.2f}"
    stats_text = f"{eq}\nR² = {r2:.3f}\nr = {r:.3f}, p = {p:.2e}\nn = {len(sub)}"
    ax.text(
        0.03, 0.05, stats_text, transform=ax.transAxes,
        fontsize=10.5, verticalalignment="bottom",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.85, edgecolor="#ccc"),
    )
    ax.legend(loc="upper right", frameon=True)

    path = FIGURES_DIR / filename
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {path}  (slope={slope:.4f}, R2={r2:.4f}, r={r:.4f}, p={p:.2e}, n={len(sub)})")


def main():
    df = load_data()
    for filename, title, group_filter, color in PANELS:
        fit_and_plot(df, filename, title, group_filter, color)


if __name__ == "__main__":
    main()
