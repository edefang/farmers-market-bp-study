"""
Step B -- Visualizations
Farmer's Market Produce & Blood Pressure Study

Produces the six chart types called for in the project plan, each named to
match its purpose so a reader can match figure -> question at a glance:

  1. box_bp_change_by_group.png        - Compare BP change across the 3 groups
  2. scatter_adherence_vs_change.png   - Show the adherence confound
  3. box_baseline_bp_by_age.png        - Check age-related baseline differences
  4. dist_bp_change_by_group.png       - Shape/spread of outcome per group
  5. heatmap_correlations.png          - Fast multi-variable overview
  6. feature_importance.png            - Written by 03_modeling.py (not here);
                                          this script only reserves the name.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_data, FIGURES_DIR, GROUP_ORDER, GROUP_COLORS  # noqa: E402

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", context="talk", font_scale=0.75)
PALETTE = [GROUP_COLORS[g] for g in GROUP_ORDER]


def save(fig, name):
    path = FIGURES_DIR / name
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {path}")


def chart_box_bp_change_by_group(df):
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharey=False)
    for ax, target, label in zip(
        axes, ["systolic_change", "diastolic_change"], ["Systolic BP Change (mmHg)", "Diastolic BP Change (mmHg)"]
    ):
        sns.boxplot(
            data=df, x="group", y=target, order=GROUP_ORDER,
            hue="group", palette=PALETTE, legend=False, ax=ax,
        )
        ax.axhline(0, color="black", linestyle="--", linewidth=1, alpha=0.6)
        ax.set_xlabel("")
        ax.set_ylabel(label)
        ax.set_xticks(range(len(GROUP_ORDER)))
        ax.set_xticklabels(["Control", "Dietitian", "AI Assistant"], rotation=15)
    fig.suptitle("Blood Pressure Change by Study Arm", fontsize=16, y=1.03)
    save(fig, "01_box_bp_change_by_group.png")


def chart_scatter_adherence_vs_change(df):
    fig, ax = plt.subplots(figsize=(9, 7))
    for g in GROUP_ORDER:
        sub = df[df["group"] == g]
        ax.scatter(
            sub["adherence_pct"], sub["systolic_change"],
            label=g.replace("_", " "), color=GROUP_COLORS[g], alpha=0.7, edgecolor="white", linewidth=0.4,
        )
    ax.axhline(0, color="black", linestyle="--", linewidth=1, alpha=0.5)
    ax.set_xlabel("Adherence (% of provided produce eaten)")
    ax.set_ylabel("Systolic BP Change (mmHg)")
    ax.set_title("The Adherence Confound: BP Change vs. Adherence, by Group")
    ax.legend(title="Group", frameon=True)
    save(fig, "02_scatter_adherence_vs_change.png")


def chart_box_baseline_bp_by_age(df):
    age_order = sorted(df["age_range"].unique(), key=lambda s: int(s.split("-")[0]))
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=df, x="age_range", y="baseline_systolic_bp", order=age_order, color="#2E86AB", ax=ax)
    ax.set_xlabel("Age Range")
    ax.set_ylabel("Baseline Systolic BP (mmHg)")
    ax.set_title("Baseline Systolic BP by Age Range")
    save(fig, "03_box_baseline_bp_by_age.png")


def chart_dist_bp_change_by_group(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    for g in GROUP_ORDER:
        sub = df[df["group"] == g]
        sns.kdeplot(sub["systolic_change"], label=g.replace("_", " "), color=GROUP_COLORS[g], fill=True, alpha=0.25, ax=ax)
    ax.axvline(0, color="black", linestyle="--", linewidth=1, alpha=0.5)
    ax.set_xlabel("Systolic BP Change (mmHg)")
    ax.set_title("Distribution of Systolic BP Change by Group")
    ax.legend(title="Group")
    save(fig, "04_dist_bp_change_by_group.png")


def chart_heatmap_correlations(df):
    cols = [
        "adherence_pct", "total_produce_kg_provided", "guidance_sessions_or_interactions",
        "baseline_systolic_bp", "baseline_diastolic_bp", "bmi",
        "systolic_change", "diastolic_change",
    ]
    corr = df[cols].corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1,
        square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax,
    )
    ax.set_title("Correlation Heatmap: Key Variables")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    save(fig, "05_heatmap_correlations.png")


def main():
    df = load_data()
    chart_box_bp_change_by_group(df)
    chart_scatter_adherence_vs_change(df)
    chart_box_baseline_bp_by_age(df)
    chart_dist_bp_change_by_group(df)
    chart_heatmap_correlations(df)
    print("\nAll EDA-stage figures written to figures/.")
    print("Feature-importance chart (06) is produced by 03_modeling.py, once a model is fit.")


if __name__ == "__main__":
    main()
