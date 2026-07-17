"""
Step A -- Exploratory Data Analysis
Farmer's Market Produce & Blood Pressure Study

Runs, in order:
  1. Shape & integrity check
  2. Target distribution (systolic_change, diastolic_change)
  3. Group-level comparison (mean/std/count of BP change per group)
  4. Full correlation sweep against each target
  5. Confound check (adherence vs. group, age_range, sex)

All output is written to results/eda_summary.md so it can be handed to
a non-technical reader without re-running the script.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_data, RESULTS_DIR, TARGETS  # noqa: E402

import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols

pd.set_option("display.width", 120)


def section(title: str) -> str:
    return f"\n## {title}\n\n"


def df_to_md(df: pd.DataFrame, floatfmt: str = ".2f") -> str:
    return df.to_markdown(floatfmt=floatfmt)


def main():
    df = load_data()
    out = ["# EDA Summary — Farmer's Market Produce & Blood Pressure Study\n"]

    # 1. Shape & integrity check
    out.append(section("1. Shape & Integrity Check"))
    out.append(f"- Rows: **{df.shape[0]}**, Columns: **{df.shape[1]}**\n")
    missing = df.isna().sum()
    missing = missing[missing > 0]
    if missing.empty:
        out.append("- Missing values: **none** (0 missing cells across all columns)\n")
    else:
        out.append("- Missing values found:\n\n")
        out.append(df_to_md(missing.to_frame("missing_count")) + "\n")
    dtype_counts = df.dtypes.astype(str).value_counts()
    out.append("- Dtype breakdown: " + ", ".join(f"{v} `{k}`" for k, v in dtype_counts.items()) + "\n")
    group_counts = df["group"].value_counts()
    out.append("- Group sizes: " + ", ".join(f"{k}={v}" for k, v in group_counts.items()) + "\n")

    # 2. Target distribution
    out.append(section("2. Target Distribution"))
    target_stats = df[TARGETS].describe().T[["mean", "std", "min", "max"]]
    out.append(df_to_md(target_stats) + "\n")
    out.append(
        "\nNegative values mean BP dropped from baseline to follow-up. "
        f"Overall mean systolic change: **{df['systolic_change'].mean():.2f} mmHg**, "
        f"mean diastolic change: **{df['diastolic_change'].mean():.2f} mmHg**.\n"
    )

    # 3. Group-level comparison
    out.append(section("3. Group-Level Comparison (BP Change by Study Arm)"))
    group_stats = df.groupby("group")[TARGETS].agg(["mean", "std", "count"])
    group_stats.columns = ["_".join(c) for c in group_stats.columns]
    group_stats = group_stats.reindex(["Dietitian", "AI_Assistant", "Control_NoGuidance"])
    out.append(df_to_md(group_stats) + "\n")

    # 4. Full correlation sweep
    out.append(section("4. Correlation Sweep (numeric columns vs. targets)"))
    numeric_df = df.select_dtypes(include="number")
    corr = numeric_df.corr()[TARGETS].drop(index=TARGETS, errors="ignore")
    corr_sorted_sys = corr["systolic_change"].abs().sort_values(ascending=False).head(15)
    corr_sorted_dia = corr["diastolic_change"].abs().sort_values(ascending=False).head(15)

    out.append("**Top 15 correlates of `systolic_change` (by absolute value):**\n\n")
    top_sys = corr.loc[corr_sorted_sys.index, ["systolic_change"]]
    out.append(df_to_md(top_sys) + "\n")

    out.append("\n**Top 15 correlates of `diastolic_change` (by absolute value):**\n\n")
    top_dia = corr.loc[corr_sorted_dia.index, ["diastolic_change"]]
    out.append(df_to_md(top_dia) + "\n")

    # 5. Confound check
    out.append(section("5. Confound Check — Adherence vs. Group / Demographics"))
    adherence_by_group = df.groupby("group")["adherence_pct"].agg(["mean", "std", "median"])
    adherence_by_group = adherence_by_group.reindex(["Dietitian", "AI_Assistant", "Control_NoGuidance"])
    out.append("**Adherence (%) by group:**\n\n")
    out.append(df_to_md(adherence_by_group) + "\n")

    adherence_by_age = df.groupby("age_range")["adherence_pct"].agg(["mean", "std", "count"])
    out.append("\n**Adherence (%) by age range:**\n\n")
    out.append(df_to_md(adherence_by_age) + "\n")

    adherence_by_sex = df.groupby("sex")["adherence_pct"].agg(["mean", "std", "count"])
    out.append("\n**Adherence (%) by sex:**\n\n")
    out.append(df_to_md(adherence_by_sex) + "\n")

    low_adherence_pct = (df["adherence_pct"] <= 10).mean() * 100
    out.append(
        f"\n- Participants with near-zero adherence (<=10%): **{low_adherence_pct:.1f}%** of the full sample.\n"
        "- This confirms adherence is unevenly distributed by design (Dietitian group skews higher) "
        "and must be controlled for (ANCOVA / regression covariate) before attributing BP change to group assignment alone.\n"
    )

    # 6. Hypothesis tests (ANOVA / Kruskal-Wallis / ANCOVA) -- suggested next step
    # from README_dataset.md, formalizing what section 3 shows descriptively.
    out.append(section("6. Hypothesis Tests — Is the Group Difference Real?"))
    for target in TARGETS:
        groups = [g[target].values for _, g in df.groupby("group")]
        f_stat, p_anova = stats.f_oneway(*groups)
        h_stat, p_kw = stats.kruskal(*groups)
        out.append(f"**{target}**\n\n")
        out.append(
            f"- One-way ANOVA: F = {f_stat:.2f}, p = {p_anova:.2e}\n"
            f"- Kruskal-Wallis (non-parametric check): H = {h_stat:.2f}, p = {p_kw:.2e}\n"
        )

        # ANCOVA: does the group effect survive after controlling for adherence
        # and baseline BP (the two confounds identified in sections 4-5)?
        baseline_col = "baseline_systolic_bp" if "systolic" in target else "baseline_diastolic_bp"
        model = ols(f"{target} ~ C(group) + adherence_pct + {baseline_col}", data=df).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        group_p = anova_table.loc["C(group)", "PR(>F)"]
        adherence_p = anova_table.loc["adherence_pct", "PR(>F)"]
        out.append(
            f"- ANCOVA (group + adherence_pct + {baseline_col}): "
            f"group effect p = {group_p:.2e}, adherence effect p = {adherence_p:.2e}, "
            f"model R² = {model.rsquared:.3f}\n\n"
        )

    out.append(
        "**Interpretation:** if the ANCOVA group p-value stays significant after adding "
        "`adherence_pct` as a covariate, the guidance-type effect holds up beyond what adherence "
        "alone explains. If it loses significance, most of the apparent group effect is actually "
        "an adherence effect (Dietitian participants simply ate more of what they were given).\n"
    )

    report = "".join(out)
    out_path = RESULTS_DIR / "eda_summary.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"Wrote {out_path}")
    print("\n--- Preview ---\n")
    print(report[:2000])


if __name__ == "__main__":
    main()
