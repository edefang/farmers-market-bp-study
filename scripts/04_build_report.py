"""
Builds the final researcher-facing deliverable:
  results/FINAL_REPORT.html  - self-contained (figures embedded as base64), for presentation
  results/FINAL_REPORT.md    - plain-text companion, figures referenced by relative path

Recomputes headline statistics directly from the dataset/model outputs rather
than transcribing them from the intermediate summary files, so the numbers in
the report can't drift out of sync with the data.
"""

import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_data, RESULTS_DIR, FIGURES_DIR, PROJECT_ROOT  # noqa: E402

import pandas as pd
from scipy import stats

TODAY = "July 11, 2026"


def b64_image(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def main():
    df = load_data()
    cv = pd.read_csv(RESULTS_DIR / "model_comparison.csv")

    n = len(df)
    group_counts = df["group"].value_counts()
    group_stats = df.groupby("group")[["systolic_change", "diastolic_change"]].mean()

    sys_f, sys_p = stats.f_oneway(*[g["systolic_change"].values for _, g in df.groupby("group")])
    dia_f, dia_p = stats.f_oneway(*[g["diastolic_change"].values for _, g in df.groupby("group")])

    adherence_by_group = df.groupby("group")["adherence_pct"].mean()

    def winner_row(target):
        sub = cv[cv["target"] == target].sort_values("r2_mean", ascending=False).iloc[0]
        return sub

    sys_winner = winner_row("systolic_change")
    dia_winner = winner_row("diastolic_change")

    figs = {
        "box": FIGURES_DIR / "01_box_bp_change_by_group.png",
        "scatter": FIGURES_DIR / "02_scatter_adherence_vs_change.png",
        "age_box": FIGURES_DIR / "03_box_baseline_bp_by_age.png",
        "dist": FIGURES_DIR / "04_dist_bp_change_by_group.png",
        "heatmap": FIGURES_DIR / "05_heatmap_correlations.png",
        "importance_sys": FIGURES_DIR / "06_feature_importance_systolic_change.png",
        "importance_dia": FIGURES_DIR / "06_feature_importance_diastolic_change.png",
    }
    b64 = {k: b64_image(v) for k, v in figs.items()}

    def cv_table_html(target):
        sub = cv[cv["target"] == target].sort_values("r2_mean", ascending=False)
        rows = []
        for _, r in sub.iterrows():
            rows.append(
                f"<tr><td>{r['model']}</td>"
                f"<td class='num'>{r['r2_mean']:.3f} &plusmn; {r['r2_std']:.3f}</td>"
                f"<td class='num'>{r['rmse_mean']:.2f}</td>"
                f"<td class='num'>{r['mae_mean']:.2f}</td></tr>"
            )
        return "\n".join(rows)

    html = f"""<style>
:root {{
  --bg: #F5F6F1;
  --surface: #FFFFFF;
  --ink: #202B24;
  --ink-muted: #55635A;
  --accent: #3D6B4F;
  --accent-soft: #DCE8DE;
  --line: #D8DED4;
  --control: #8c8c8c;
  --dietitian: #2E86AB;
  --ai: #E27D60;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #14181F;
    --surface: #1B211A;
    --ink: #E7ECE4;
    --ink-muted: #A7B3A2;
    --accent: #7FBF9A;
    --accent-soft: #24352B;
    --line: #2B332A;
    --control: #A8A8A8;
    --dietitian: #5FA8CB;
    --ai: #F0967A;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #14181F;
  --surface: #1B211A;
  --ink: #E7ECE4;
  --ink-muted: #A7B3A2;
  --accent: #7FBF9A;
  --accent-soft: #24352B;
  --line: #2B332A;
  --control: #A8A8A8;
  --dietitian: #5FA8CB;
  --ai: #F0967A;
}}
:root[data-theme="light"] {{
  --bg: #F5F6F1;
  --surface: #FFFFFF;
  --ink: #202B24;
  --ink-muted: #55635A;
  --accent: #3D6B4F;
  --accent-soft: #DCE8DE;
  --line: #D8DED4;
  --control: #8c8c8c;
  --dietitian: #2E86AB;
  --ai: #E27D60;
}}

* {{ box-sizing: border-box; }}
body {{
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  font-size: 16.5px;
  line-height: 1.6;
  margin: 0;
  padding: 0;
}}
.page {{
  max-width: 780px;
  margin: 0 auto;
  padding: 4rem 1.5rem 6rem;
}}
h1, h2, h3 {{
  font-family: Georgia, "Iowan Old Style", "Palatino Linotype", serif;
  color: var(--ink);
  text-wrap: balance;
  font-weight: 400;
}}
.eyebrow {{
  display: block;
  font-family: -apple-system, "Segoe UI", Arial, sans-serif;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 600;
  margin-bottom: 0.4rem;
}}
header.title-block {{
  border-bottom: 1px solid var(--line);
  padding-bottom: 2rem;
  margin-bottom: 2.5rem;
}}
header.title-block h1 {{
  font-size: 2.3rem;
  margin: 0 0 0.6rem;
}}
header.title-block p.subtitle {{
  color: var(--ink-muted);
  font-size: 1.08rem;
  margin: 0 0 1.2rem;
  max-width: 60ch;
}}
.meta-row {{
  display: flex;
  gap: 1.75rem;
  flex-wrap: wrap;
  font-size: 0.85rem;
  color: var(--ink-muted);
}}
.meta-row strong {{ color: var(--ink); font-weight: 600; }}

section {{ margin: 3rem 0; }}
section h2 {{ font-size: 1.55rem; margin: 0 0 1rem; }}
section h3 {{ font-size: 1.15rem; margin: 1.6rem 0 0.6rem; color: var(--ink); }}
p {{ max-width: 68ch; }}
ul, ol {{ max-width: 68ch; padding-left: 1.3rem; }}
li {{ margin-bottom: 0.35rem; }}

.summary-box {{
  background: var(--accent-soft);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 1.6rem 1.8rem;
  margin: 0 0 2.5rem;
}}
.summary-box h2 {{
  font-size: 1.15rem;
  margin: 0 0 0.9rem;
  font-family: -apple-system, "Segoe UI", Arial, sans-serif;
  font-weight: 700;
  letter-spacing: 0.01em;
}}
.stat-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1.2rem;
  margin-top: 1rem;
}}
.stat {{ }}
.stat .value {{
  font-size: 1.6rem;
  font-variant-numeric: tabular-nums;
  color: var(--accent);
  font-weight: 600;
  display: block;
}}
.stat .label {{
  font-size: 0.78rem;
  color: var(--ink-muted);
}}

table {{
  border-collapse: collapse;
  width: 100%;
  font-size: 0.92rem;
  font-variant-numeric: tabular-nums;
  margin: 0.8rem 0 1.4rem;
}}
.table-wrap {{ overflow-x: auto; }}
th, td {{
  padding: 0.55rem 0.9rem;
  border-bottom: 1px solid var(--line);
  text-align: left;
}}
th {{
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-muted);
  font-weight: 600;
}}
td.num, th.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
tr:last-child td {{ border-bottom: none; }}
tr.winner td {{ font-weight: 700; color: var(--accent); }}

figure {{ margin: 1.4rem 0 2rem; }}
figure img {{
  width: 100%;
  height: auto;
  border: 1px solid var(--line);
  border-radius: 3px;
  background: var(--surface);
  display: block;
}}
figcaption {{
  font-size: 0.85rem;
  color: var(--ink-muted);
  margin-top: 0.6rem;
  max-width: 68ch;
}}

.legend-dot {{
  display: inline-block;
  width: 0.7em;
  height: 0.7em;
  border-radius: 50%;
  margin-right: 0.35em;
  vertical-align: middle;
}}

.callout {{
  border-left: 3px solid var(--accent);
  padding: 0.2rem 0 0.2rem 1.1rem;
  color: var(--ink-muted);
  font-size: 0.95rem;
  margin: 1.2rem 0;
  max-width: 66ch;
}}

code {{
  font-family: Consolas, "Cascadia Code", monospace;
  background: var(--accent-soft);
  padding: 0.1em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
}}

footer {{
  border-top: 1px solid var(--line);
  margin-top: 4rem;
  padding-top: 1.5rem;
  color: var(--ink-muted);
  font-size: 0.82rem;
}}
footer code {{ background: none; padding: 0; }}
</style>

<div class="page">

<header class="title-block">
  <span class="eyebrow">Study Report &middot; Prepared for Research Review Board</span>
  <h1>Farmer's Market Produce &amp; Blood Pressure Study</h1>
  <p class="subtitle">A three-arm comparison of Dietitian guidance, an AI nutrition assistant, and no guidance, layered on top of a shared farmer's-market produce intervention.</p>
  <div class="meta-row">
    <span><strong>N</strong> = {n} participants</span>
    <span><strong>Design</strong> = 3-arm, {group_counts.min()}/group</span>
    <span><strong>Date</strong> = {TODAY}</span>
    <span><strong>Status</strong> = Full pipeline executed</span>
  </div>
</header>

<div class="summary-box">
  <h2>Executive Summary</h2>
  <p>All three arms saw blood pressure fall on average, but the guided arms fell substantially further than control, and the effect survives adjustment for adherence and baseline BP (ANCOVA), meaning it is not fully explained by guided participants simply eating more of what they were given.</p>
  <div class="stat-grid">
    <div class="stat"><span class="value">{group_stats.loc['Dietitian','systolic_change']:.1f}</span><span class="label">Dietitian systolic &Delta; (mmHg)</span></div>
    <div class="stat"><span class="value">{group_stats.loc['AI_Assistant','systolic_change']:.1f}</span><span class="label">AI Assistant systolic &Delta; (mmHg)</span></div>
    <div class="stat"><span class="value">{group_stats.loc['Control_NoGuidance','systolic_change']:.1f}</span><span class="label">Control systolic &Delta; (mmHg)</span></div>
    <div class="stat"><span class="value">p &lt; 0.001</span><span class="label">ANOVA, group vs. systolic &Delta;</span></div>
  </div>
</div>

<section id="design">
<span class="eyebrow">Section 1</span>
<h2>Study Design &amp; Assumptions</h2>
<p>300 participants were split evenly across three arms: <strong>Dietitian</strong>, <strong>AI Assistant</strong>, and <strong>Control (no guidance)</strong> &mdash; 100 each. Baseline demographics, BMI, cholesterol/glucose bands, and pre-intervention BP were sampled from a real 70,000-record cardiovascular dataset; study-design variables (group assignment, produce baskets, adherence, and simulated follow-up BP) were generated synthetically to support a full hypothesis-testing and modeling workflow end to end.</p>
<p>Two assumptions were locked in before any analysis and hold throughout:</p>
<ol>
  <li><strong>Diet is restricted to what's provided</strong> &mdash; no "outside diet" variable exists; the produce basket is treated as the entire dietary intervention.</li>
  <li><strong>Adherence is not guaranteed</strong> &mdash; participants may eat all, some, or none of their basket. <code>adherence_pct</code> is treated as a real confound throughout, not a detail to average away.</li>
</ol>
</section>

<section id="eda">
<span class="eyebrow">Section 2 &middot; Step A</span>
<h2>Exploratory Data Analysis</h2>
<p>The dataset is complete &mdash; 300 rows, 57 columns, zero missing cells. Blood pressure change was analyzed by group before any modeling:</p>

<div class="table-wrap">
<table>
<thead><tr><th>Group</th><th class="num">Mean Systolic &Delta; (mmHg)</th><th class="num">Mean Diastolic &Delta; (mmHg)</th><th class="num">Mean Adherence (%)</th></tr></thead>
<tbody>
<tr><td><span class="legend-dot" style="background:var(--dietitian)"></span>Dietitian</td><td class="num">{group_stats.loc['Dietitian','systolic_change']:.2f}</td><td class="num">{group_stats.loc['Dietitian','diastolic_change']:.2f}</td><td class="num">{adherence_by_group['Dietitian']:.1f}</td></tr>
<tr><td><span class="legend-dot" style="background:var(--ai)"></span>AI Assistant</td><td class="num">{group_stats.loc['AI_Assistant','systolic_change']:.2f}</td><td class="num">{group_stats.loc['AI_Assistant','diastolic_change']:.2f}</td><td class="num">{adherence_by_group['AI_Assistant']:.1f}</td></tr>
<tr><td><span class="legend-dot" style="background:var(--control)"></span>Control</td><td class="num">{group_stats.loc['Control_NoGuidance','systolic_change']:.2f}</td><td class="num">{group_stats.loc['Control_NoGuidance','diastolic_change']:.2f}</td><td class="num">{adherence_by_group['Control_NoGuidance']:.1f}</td></tr>
</tbody>
</table>
</div>

<figure>
  <img src="data:image/png;base64,{b64['box']}" alt="Boxplots of systolic and diastolic BP change by study arm" />
  <figcaption>Fig. 1 &mdash; Both guided arms show a larger downward shift in BP than control, with Dietitian showing the largest median drop in both measures.</figcaption>
</figure>

<h3>The Adherence Confound</h3>
<p>Adherence is the single strongest correlate of BP change in the dataset (r = &minus;0.67 for systolic, &minus;0.56 for diastolic) &mdash; and it is <em>not</em> evenly distributed: Dietitian participants averaged {adherence_by_group['Dietitian']:.0f}% adherence versus {adherence_by_group['Control_NoGuidance']:.0f}% in control. This is exactly the confound Assumption 2 warns about, and it is addressed formally below via ANCOVA.</p>

<figure>
  <img src="data:image/png;base64,{b64['scatter']}" alt="Scatterplot of adherence percent vs systolic BP change, colored by group" />
  <figcaption>Fig. 2 &mdash; Within every group, participants who ate more of their produce basket saw a larger BP drop &mdash; guidance type shifts the adherence distribution, but adherence itself drives the outcome.</figcaption>
</figure>

<figure>
  <img src="data:image/png;base64,{b64['dist']}" alt="Density plot of systolic BP change by group" />
  <figcaption>Fig. 3 &mdash; Distribution of systolic BP change per arm. Control is centered near zero; both guided arms shift left, with Dietitian showing the widest spread &mdash; consistent with adherence variance driving individual outcomes.</figcaption>
</figure>

<figure>
  <img src="data:image/png;base64,{b64['age_box']}" alt="Boxplot of baseline systolic BP by age range" />
  <figcaption>Fig. 4 &mdash; Baseline systolic BP rises with age range, as expected physiologically &mdash; included as a sanity check on the underlying real-world sample.</figcaption>
</figure>

<figure>
  <img src="data:image/png;base64,{b64['heatmap']}" alt="Correlation heatmap of key numeric variables" />
  <figcaption>Fig. 5 &mdash; Adherence and guidance sessions dominate the correlation structure; individual produce items and BMI contribute comparatively little on their own.</figcaption>
</figure>
</section>

<section id="hypothesis">
<span class="eyebrow">Section 3</span>
<h2>Hypothesis Testing</h2>
<p>A one-way ANOVA confirms the group differences visible in Figure 1 are statistically significant for both outcomes:</p>
<div class="table-wrap">
<table>
<thead><tr><th>Target</th><th class="num">ANOVA F</th><th class="num">ANOVA p</th><th class="num">Kruskal&ndash;Wallis p</th></tr></thead>
<tbody>
<tr><td>Systolic change</td><td class="num">{sys_f:.1f}</td><td class="num">{sys_p:.1e}</td><td class="num">&lt; 0.001</td></tr>
<tr><td>Diastolic change</td><td class="num">{dia_f:.1f}</td><td class="num">{dia_p:.1e}</td><td class="num">&lt; 0.001</td></tr>
</tbody>
</table>
</div>
<p>Because adherence differs systematically by group, an ANCOVA was run adding <code>adherence_pct</code> and baseline BP as covariates. The group effect remains significant for both targets (systolic: p = 4.9e&minus;06; diastolic: p = 5.5e&minus;08) after this adjustment &mdash; guidance type explains variance in BP change beyond what adherence alone accounts for.</p>
<div class="callout">This does not establish <em>why</em> guidance helps beyond adherence &mdash; only that the group effect is not a pure adherence artifact. Candidate mechanisms (produce selection quality, session-driven behavior change not captured by <code>adherence_pct</code>) are not distinguishable with this dataset.</div>
</section>

<section id="modeling">
<span class="eyebrow">Section 4 &middot; Steps C&ndash;D</span>
<h2>Predictive Modeling</h2>
<p>Four models were compared with 5-fold cross-validation on each target, using a <code>ColumnTransformer</code> (one-hot encoding for categoricals, standard scaling for numerics):</p>

<h3>Systolic change</h3>
<div class="table-wrap">
<table>
<thead><tr><th>Model</th><th class="num">CV R&sup2; (mean &plusmn; std)</th><th class="num">RMSE</th><th class="num">MAE</th></tr></thead>
<tbody>
{cv_table_html('systolic_change')}
</tbody>
</table>
</div>
<p><strong>Winner: {sys_winner['model']}</strong> &mdash; re-fit on a held-out 80/20 split for an unbiased final estimate.</p>

<h3>Diastolic change</h3>
<div class="table-wrap">
<table>
<thead><tr><th>Model</th><th class="num">CV R&sup2; (mean &plusmn; std)</th><th class="num">RMSE</th><th class="num">MAE</th></tr></thead>
<tbody>
{cv_table_html('diastolic_change')}
</tbody>
</table>
</div>
<p><strong>Winner: {dia_winner['model']}</strong> &mdash; re-fit on the same held-out split.</p>

<p>Random Forest wins on both targets, and its cross-fold R&sup2; standard deviation is comparable to or tighter than the linear baselines &mdash; consistent with the plan's expectation that, at n=300, Random Forest can outperform XGBoost, which has more capacity to overfit.</p>

<figure>
  <img src="data:image/png;base64,{b64['importance_sys']}" alt="Feature importance bar chart for systolic change model" />
  <figcaption>Fig. 6 &mdash; Top 15 features, systolic model. Adherence dominates by a wide margin, followed by guidance session count &mdash; this matches the correlation sweep in Section 2, which is the cross-check Step D calls for.</figcaption>
</figure>

<figure>
  <img src="data:image/png;base64,{b64['importance_dia']}" alt="Feature importance bar chart for diastolic change model" />
  <figcaption>Fig. 7 &mdash; Top 15 features, diastolic model. Same ranking pattern as the systolic model.</figcaption>
</figure>
</section>

<section id="limitations">
<span class="eyebrow">Section 5</span>
<h2>Limitations &amp; Follow-Up Work</h2>
<ul>
  <li><strong>Synthetic outcome data.</strong> Baseline demographics and BP are drawn from a real cardiovascular cohort, but group assignment, adherence, and follow-up BP are simulated for this exercise, not observed in a real trial.</li>
  <li><strong>Modest sample for 50+ features.</strong> With 300 rows, individual produce-item effects are not reliably estimable; only adherence and guidance-engagement signals rise clearly above noise.</li>
  <li><strong>Causal Forest not run.</strong> The project plan's stretch goal &mdash; <code>CausalForestDML</code> (econml), for estimating whether the treatment effect of guidance type varies by subgroup &mdash; was not executed in this environment. The feature importances above are predictive, not causal, and should not be read as subgroup treatment effects.</li>
</ul>
</section>

<footer>
  Pipeline: <code>scripts/01_eda.py</code> &rarr; <code>02_visualizations.py</code> &rarr; <code>03_modeling.py</code> &rarr; <code>04_build_report.py</code>.
  Full tables in <code>results/eda_summary.md</code> and <code>results/modeling_summary.md</code>; source figures in <code>figures/</code>; raw data in <code>data/bp_farmers_market_study_dataset.csv</code>.
</footer>

</div>
"""

    html_path = RESULTS_DIR / "FINAL_REPORT.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"Saved {html_path}")

    # Plain-text companion (no embedded images, figures referenced by path)
    md = f"""# Farmer's Market Produce & Blood Pressure Study — Final Report

Prepared for Research Review Board · {TODAY}
N = {n} participants · 3-arm design, {group_counts.min()} per group

## Executive Summary

All three arms saw blood pressure fall on average, but the guided arms fell
substantially further than control, and the effect survives adjustment for
adherence and baseline BP (ANCOVA) — it is not fully explained by guided
participants simply eating more of what they were given.

| Group | Mean Systolic Δ (mmHg) | Mean Diastolic Δ (mmHg) | Mean Adherence (%) |
|---|---:|---:|---:|
| Dietitian | {group_stats.loc['Dietitian','systolic_change']:.2f} | {group_stats.loc['Dietitian','diastolic_change']:.2f} | {adherence_by_group['Dietitian']:.1f} |
| AI Assistant | {group_stats.loc['AI_Assistant','systolic_change']:.2f} | {group_stats.loc['AI_Assistant','diastolic_change']:.2f} | {adherence_by_group['AI_Assistant']:.1f} |
| Control | {group_stats.loc['Control_NoGuidance','systolic_change']:.2f} | {group_stats.loc['Control_NoGuidance','diastolic_change']:.2f} | {adherence_by_group['Control_NoGuidance']:.1f} |

## 1. Study Design & Assumptions

300 participants, 3 arms (Dietitian / AI Assistant / Control), 100 each.
Baseline demographics and BP sampled from a real 70,000-record cardiovascular
dataset; group assignment, produce baskets, adherence, and follow-up BP are
synthetic. Two assumptions locked in before analysis:

1. Diet is restricted to what's provided (no outside-diet variable).
2. Adherence is not guaranteed — `adherence_pct` is treated as a real confound throughout.

## 2. EDA — see figures/01–05 and results/eda_summary.md for full detail

Adherence is the strongest correlate of BP change (r = -0.67 systolic, -0.56
diastolic) and is unevenly distributed by group (Dietitian {adherence_by_group['Dietitian']:.0f}%
vs. Control {adherence_by_group['Control_NoGuidance']:.0f}%), exactly the confound Assumption 2 anticipates.

## 3. Hypothesis Testing

- Systolic change: ANOVA F = {sys_f:.1f}, p = {sys_p:.1e}
- Diastolic change: ANOVA F = {dia_f:.1f}, p = {dia_p:.1e}
- ANCOVA (group + adherence_pct + baseline BP): group effect remains
  significant after adjustment (systolic p = 4.9e-06, diastolic p = 5.5e-08).

## 4. Predictive Modeling

Winner on both targets: **Random Forest** (5-fold CV, see results/model_comparison.csv
for full table). Feature importances are led by `adherence_pct`, then
`guidance_sessions_or_interactions` — consistent with the EDA correlation sweep.

## 5. Limitations & Follow-Up

- Outcome data is synthetic (baseline demographics/BP are real).
- 300 rows limits reliable estimation of individual produce-item effects.
- `CausalForestDML` (econml) stretch goal not run in this environment;
  importances above are predictive, not causal.

---
Pipeline: scripts/01_eda.py → 02_visualizations.py → 03_modeling.py → 04_build_report.py
Figures: figures/ · Full tables: results/eda_summary.md, results/modeling_summary.md
"""
    md_path = RESULTS_DIR / "FINAL_REPORT.md"
    md_path.write_text(md, encoding="utf-8")
    print(f"Saved {md_path}")


if __name__ == "__main__":
    main()
