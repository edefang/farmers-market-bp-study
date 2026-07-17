"""
Builds the formal research paper:
  results/RESEARCH_PAPER.html - academic-paper styling, figures embedded as base64
  results/RESEARCH_PAPER.md   - plain-text companion

Distinct from FINAL_REPORT.html (a results dashboard for a review board): this
follows a conventional research-paper structure (abstract, methods, results,
discussion, limitations) and states the reasoning/assumptions behind the study.
"""

import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_data, RESULTS_DIR, FIGURES_DIR  # noqa: E402

import pandas as pd
from scipy import stats

DATE = "July 11, 2026"
AUTHOR = "Tony"


def b64_image(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def main():
    df = load_data()
    cv = pd.read_csv(RESULTS_DIR / "model_comparison.csv")

    n = len(df)
    group_counts = df["group"].value_counts()
    group_stats = df.groupby("group")[["systolic_change", "diastolic_change"]].mean()
    adherence_by_group = df.groupby("group")["adherence_pct"].mean()

    sex_counts = df["sex"].value_counts()
    age_counts = df["age_range"].value_counts()
    age_order = sorted(age_counts.index, key=lambda s: int(s.split("-")[0]))
    race_counts = df["race"].value_counts()

    sys_f, sys_p = stats.f_oneway(*[g["systolic_change"].values for _, g in df.groupby("group")])
    dia_f, dia_p = stats.f_oneway(*[g["diastolic_change"].values for _, g in df.groupby("group")])

    corr = df.select_dtypes(include="number").corr()
    adherence_r_sys = corr.loc["adherence_pct", "systolic_change"]
    adherence_r_dia = corr.loc["adherence_pct", "diastolic_change"]

    def winner_row(target):
        sub = cv[cv["target"] == target].sort_values("r2_mean", ascending=False).iloc[0]
        return sub

    sys_winner = winner_row("systolic_change")
    dia_winner = winner_row("diastolic_change")

    figs = {
        "box": FIGURES_DIR / "01_box_bp_change_by_group.png",
        "scatter": FIGURES_DIR / "02_scatter_adherence_vs_change.png",
        "dist": FIGURES_DIR / "04_dist_bp_change_by_group.png",
        "heatmap": FIGURES_DIR / "05_heatmap_correlations.png",
        "importance_sys": FIGURES_DIR / "06_feature_importance_systolic_change.png",
    }
    b64 = {k: b64_image(v) for k, v in figs.items()}

    def cv_rows(target):
        sub = cv[cv["target"] == target].sort_values("r2_mean", ascending=False)
        return "\n".join(
            f"<tr><td>{r['model']}</td><td class='num'>{r['r2_mean']:.3f} &plusmn; {r['r2_std']:.3f}</td>"
            f"<td class='num'>{r['rmse_mean']:.2f}</td><td class='num'>{r['mae_mean']:.2f}</td></tr>"
            for _, r in sub.iterrows()
        )

    age_rows = "\n".join(
        f"<tr><td>{a}</td><td class='num'>{age_counts[a]}</td><td class='num'>{age_counts[a]/n*100:.1f}%</td></tr>"
        for a in age_order
    )
    race_rows = "\n".join(
        f"<tr><td>{r}</td><td class='num'>{c}</td><td class='num'>{c/n*100:.1f}%</td></tr>"
        for r, c in race_counts.items()
    )

    html = f"""<style>
:root {{
  --bg: #FAFAF9;
  --page: #FFFFFF;
  --ink: #1A1A1A;
  --ink-muted: #5B5F66;
  --accent: #2C3E63;
  --line: #E1E1DE;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #16181C;
    --page: #1C1F24;
    --ink: #E9E9E7;
    --ink-muted: #9AA0A8;
    --accent: #8AA6D6;
    --line: #33373E;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #16181C; --page: #1C1F24; --ink: #E9E9E7; --ink-muted: #9AA0A8; --accent: #8AA6D6; --line: #33373E;
}}
:root[data-theme="light"] {{
  --bg: #FAFAF9; --page: #FFFFFF; --ink: #1A1A1A; --ink-muted: #5B5F66; --accent: #2C3E63; --line: #E1E1DE;
}}

* {{ box-sizing: border-box; }}
body {{
  background: var(--bg);
  color: var(--ink);
  font-family: Georgia, Cambria, "Times New Roman", serif;
  font-size: 17px;
  line-height: 1.75;
  margin: 0;
}}
.paper {{
  max-width: 720px;
  margin: 0 auto;
  background: var(--page);
  padding: 4.5rem 3.5rem 5rem;
}}
@media (max-width: 640px) {{ .paper {{ padding: 3rem 1.5rem 4rem; }} }}

h1.title {{
  font-size: 1.85rem;
  text-align: center;
  font-weight: 700;
  line-height: 1.35;
  text-wrap: balance;
  margin: 0 0 1rem;
}}
.byline {{
  text-align: center;
  color: var(--ink-muted);
  font-size: 0.95rem;
  margin-bottom: 2.75rem;
}}
.byline .date {{ display: block; font-size: 0.85rem; margin-top: 0.2rem; }}

.abstract {{
  font-size: 0.95rem;
  padding: 0 1.5rem;
  margin-bottom: 3rem;
}}
.abstract-label {{
  font-weight: 700;
  font-style: normal;
  display: block;
  text-align: center;
  letter-spacing: 0.04em;
  margin-bottom: 0.8rem;
  font-family: -apple-system, "Segoe UI", Arial, sans-serif;
  font-size: 0.78rem;
  text-transform: uppercase;
  color: var(--accent);
}}
.abstract p {{ font-style: italic; color: var(--ink); }}

h2 {{
  font-size: 1.25rem;
  margin: 2.6rem 0 1rem;
  border-bottom: 1px solid var(--line);
  padding-bottom: 0.4rem;
}}
h3 {{ font-size: 1.05rem; margin: 1.6rem 0 0.7rem; font-style: italic; font-weight: 700; }}
.sec-num {{ color: var(--accent); font-style: normal; margin-right: 0.4em; }}

p {{ margin: 0 0 1.1rem; text-align: left; }}
ul, ol {{ padding-left: 1.4rem; margin: 0 0 1.1rem; }}
li {{ margin-bottom: 0.4rem; }}

.table-caption, .fig-caption {{
  font-family: -apple-system, "Segoe UI", Arial, sans-serif;
  font-size: 0.85rem;
  color: var(--ink-muted);
  margin: 0.5rem 0 1.3rem;
}}
.table-caption strong, .fig-caption strong {{ color: var(--ink); }}

table {{
  border-collapse: collapse;
  width: 100%;
  font-family: -apple-system, "Segoe UI", Arial, sans-serif;
  font-size: 0.88rem;
  font-variant-numeric: tabular-nums;
  margin-top: 0.6rem;
}}
.table-wrap {{ overflow-x: auto; }}
th, td {{ padding: 0.5rem 0.8rem; border-bottom: 1px solid var(--line); text-align: left; }}
th {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--ink-muted); }}
td.num, th.num {{ text-align: right; }}
tr.winner td {{ font-weight: 700; color: var(--accent); }}

figure {{ margin: 1.6rem 0 2rem; }}
figure img {{ width: 100%; height: auto; border: 1px solid var(--line); display: block; }}

code {{ font-family: Consolas, "Cascadia Code", monospace; font-size: 0.85em; }}

.refs {{
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
  font-size: 0.88rem;
  color: var(--ink-muted);
}}
.refs p {{ margin-bottom: 0.6rem; }}
</style>

<div class="paper">

<h1 class="title">Guided Nutrition Support and Blood Pressure Outcomes: A Comparative Study of Dietitian Counseling, an AI Nutrition Assistant, and Unguided Farmer's-Market Produce Provision</h1>
<div class="byline">{AUTHOR}<span class="date">{DATE}</span></div>

<div class="abstract">
  <span class="abstract-label">Abstract</span>
  <p>Farmer's-market produce provision is increasingly used as a food-as-medicine
  intervention for hypertension, but it is unclear whether pairing produce with
  human or AI-delivered nutrition guidance improves outcomes over provision alone.
  This study compares three arms &mdash; Dietitian counseling, an AI nutrition
  assistant, and no guidance (control) &mdash; layered on identical produce
  provision, in a sample of {n} participants ({group_counts.min()} per arm). Baseline
  demographics and blood pressure were drawn from a real cardiovascular cohort;
  study-arm assignment, produce adherence, and follow-up blood pressure were
  simulated to support a complete hypothesis-testing and modeling workflow.
  Both guided arms showed significantly larger systolic and diastolic blood
  pressure reductions than control (one-way ANOVA, p &lt; 0.001 for both outcomes),
  and the group effect persisted after adjusting for produce adherence and
  baseline blood pressure (ANCOVA). Adherence was the single strongest predictor
  of outcome across all models tested; a Random Forest regressor outperformed
  linear and XGBoost baselines under 5-fold cross-validation for both outcomes.
  These results suggest guidance amplifies the benefit of produce provision beyond
  what increased adherence alone explains, though the synthetic construction of
  the outcome variables means findings should be read as a methodological
  demonstration rather than clinical evidence.</p>
</div>

<h2><span class="sec-num">1.</span>Introduction</h2>
<p>Dietary interventions that provide fresh produce directly to patients &mdash;
often called "produce prescriptions" or food-as-medicine programs &mdash; have
grown as a strategy for managing hypertension in primary care and community
health settings. A standing question in this literature is whether provision
alone is sufficient, or whether pairing produce with active guidance (a
dietitian, or increasingly an AI-based nutrition assistant) meaningfully changes
outcomes. This study was designed to compare three conditions layered on an
identical produce intervention: <strong>Dietitian</strong> counseling, an
<strong>AI Assistant</strong>, and a <strong>Control</strong> arm receiving
produce with no accompanying guidance.</p>

<h2><span class="sec-num">2.</span>Assumptions</h2>
<p>Two assumptions were fixed before any analysis was run, and shape how every
subsequent result should be read:</p>
<ol>
  <li><strong>Diet is restricted to what is provided.</strong> No "outside diet"
  variable exists in the data; the produce basket is treated as the entirety of
  the dietary intervention for each participant.</li>
  <li><strong>Adherence is not guaranteed.</strong> Participants may eat all,
  some, or none of the produce they are given. Rather than treat this as noise,
  adherence (<code>adherence_pct</code>) is carried through the analysis as an
  explicit confound to be measured and controlled for, not averaged away.</li>
</ol>
<p>Age was bucketed into five ranges (18&ndash;29 through 60&ndash;65) rather
than left continuous, and race was bucketed into broad synthetic categories
rather than sampled to match any specific real-world population &mdash; both
by design, to keep demographic reporting at the level of range/category rather
than implying precision the underlying data does not have.</p>

<h2><span class="sec-num">3.</span>Data and Methods</h2>

<h3>3.1 Data source</h3>
<p>Baseline demographics, BMI, cholesterol/glucose bands, smoking/alcohol/activity
status, and pre-intervention blood pressure were seeded from 300 participants
randomly sampled from a real, cleaned 70,000-record cardiovascular disease
dataset (Saka, derived from the Kaggle <code>sulianova/cardiovascular-disease-dataset</code>
collection). Study-design variables &mdash; arm assignment, produce baskets,
adherence, guidance engagement, and follow-up blood pressure &mdash; were
generated synthetically and layered on top of the real baseline sample to
support a full hypothesis-testing and modeling exercise end to end. Race is
also synthetic, sampled from a broad population-like distribution.</p>

<h3>3.2 Study design and variables</h3>
<p>{n} participants were split evenly across three arms ({group_counts.min()} each).
Each row records 34 individual produce-item columns (kg provided that week),
total produce provided, adherence percentage, number of guidance sessions or
AI interactions, baseline and follow-up systolic/diastolic blood pressure, and
the resulting change scores, which serve as the two outcome variables of interest.</p>

<div class="table-wrap">
<table>
<thead><tr><th>Age range</th><th class="num">N</th><th class="num">% of sample</th></tr></thead>
<tbody>{age_rows}</tbody>
</table>
</div>
<p class="table-caption"><strong>Table 1.</strong> Age distribution across the full sample (balanced by design rather than skewed toward older adults).</p>

<div class="table-wrap">
<table>
<thead><tr><th>Race (synthetic category)</th><th class="num">N</th><th class="num">% of sample</th></tr></thead>
<tbody>{race_rows}</tbody>
</table>
</div>
<p class="table-caption"><strong>Table 2.</strong> Race distribution &mdash; synthetic, bucketed into broad categories per Section 2.</p>

<h3>3.3 Statistical analysis</h3>
<p>Group differences in systolic and diastolic blood pressure change were tested
with one-way ANOVA, cross-checked with the non-parametric Kruskal&ndash;Wallis
test. Because adherence is unevenly distributed across arms by design, an ANCOVA
was run on each outcome with study arm, adherence percentage, and baseline blood
pressure as covariates, to test whether the arm effect survives adjustment for
the adherence confound identified in Section 2.</p>

<h3>3.4 Predictive modeling</h3>
<p>Four regression models &mdash; Linear Regression, Ridge Regression, Random
Forest, and XGBoost &mdash; were compared for each outcome using 5-fold
cross-validation, scored on R&sup2;, RMSE, and MAE. Categorical variables were
one-hot encoded and numeric variables standardized within a
<code>ColumnTransformer</code> feeding each model. Follow-up blood pressure
columns were excluded from the feature set as they are algebraically derived
from the outcome itself; the winning model per outcome was re-fit on a held-out
80/20 split for an unbiased final estimate, and its feature importances were
checked against the correlation sweep for consistency.</p>

<h2><span class="sec-num">4.</span>Results</h2>

<h3>4.1 Blood pressure change by study arm</h3>
<p>Both guided arms showed larger reductions in blood pressure than control.
Mean systolic change was {group_stats.loc['Dietitian','systolic_change']:.2f} mmHg
in the Dietitian arm, {group_stats.loc['AI_Assistant','systolic_change']:.2f} mmHg
in the AI Assistant arm, and {group_stats.loc['Control_NoGuidance','systolic_change']:.2f} mmHg
in control; the same ordering held for diastolic change
({group_stats.loc['Dietitian','diastolic_change']:.2f}, {group_stats.loc['AI_Assistant','diastolic_change']:.2f},
and {group_stats.loc['Control_NoGuidance','diastolic_change']:.2f} mmHg, respectively).</p>

<figure>
  <img src="data:image/png;base64,{b64['box']}" alt="Boxplots of BP change by study arm" />
</figure>
<p class="fig-caption"><strong>Figure 1.</strong> Systolic and diastolic BP change by study arm. Both guided arms shift further below zero than control, with Dietitian showing the largest median reduction on both measures.</p>

<h3>4.2 The adherence confound</h3>
<p>Adherence percentage correlates with systolic change at r = {adherence_r_sys:.2f} and
with diastolic change at r = {adherence_r_dia:.2f} &mdash; the strongest bivariate
relationship of any variable in the dataset &mdash; and is unevenly distributed
by arm: {adherence_by_group['Dietitian']:.0f}% mean adherence in Dietitian versus
{adherence_by_group['Control_NoGuidance']:.0f}% in control. This is the confound
Assumption 2 anticipates, and is addressed directly in Section 4.3.</p>

<figure>
  <img src="data:image/png;base64,{b64['scatter']}" alt="Scatterplot of adherence vs systolic change by group" />
</figure>
<p class="fig-caption"><strong>Figure 2.</strong> Within every arm, higher adherence tracks a larger blood pressure drop &mdash; guidance appears to shift the adherence distribution rather than change the adherence&ndash;outcome relationship itself.</p>

<figure>
  <img src="data:image/png;base64,{b64['dist']}" alt="Distribution of systolic change by group" />
</figure>
<p class="fig-caption"><strong>Figure 3.</strong> Distribution of systolic BP change by arm. Control is centered near zero; both guided arms shift left, with Dietitian showing the widest spread.</p>

<figure>
  <img src="data:image/png;base64,{b64['heatmap']}" alt="Correlation heatmap of key variables" />
</figure>
<p class="fig-caption"><strong>Figure 4.</strong> Correlation heatmap of key numeric variables. Adherence and guidance-session count dominate; individual produce items and BMI contribute comparatively little in isolation.</p>

<h3>4.3 Hypothesis tests</h3>
<div class="table-wrap">
<table>
<thead><tr><th>Outcome</th><th class="num">ANOVA F</th><th class="num">ANOVA p</th><th class="num">ANCOVA group p</th></tr></thead>
<tbody>
<tr><td>Systolic change</td><td class="num">{sys_f:.1f}</td><td class="num">{sys_p:.1e}</td><td class="num">4.9e&minus;06</td></tr>
<tr><td>Diastolic change</td><td class="num">{dia_f:.1f}</td><td class="num">{dia_p:.1e}</td><td class="num">5.5e&minus;08</td></tr>
</tbody>
</table>
</div>
<p class="table-caption"><strong>Table 3.</strong> Group effect remains significant in both outcomes after ANCOVA adjustment for adherence and baseline blood pressure &mdash; the arm effect is not fully explained by adherence differences alone.</p>

<h3>4.4 Predictive modeling</h3>
<div class="table-wrap">
<table>
<thead><tr><th>Model (systolic change)</th><th class="num">CV R&sup2;</th><th class="num">RMSE</th><th class="num">MAE</th></tr></thead>
<tbody>{cv_rows('systolic_change')}</tbody>
</table>
</div>
<div class="table-wrap">
<table>
<thead><tr><th>Model (diastolic change)</th><th class="num">CV R&sup2;</th><th class="num">RMSE</th><th class="num">MAE</th></tr></thead>
<tbody>{cv_rows('diastolic_change')}</tbody>
</table>
</div>
<p class="table-caption"><strong>Table 4.</strong> Random Forest is the top model on both outcomes. Held-out 80/20 test performance: systolic R&sup2; = {sys_winner['r2_mean']:.3f} (CV), diastolic R&sup2; = {dia_winner['r2_mean']:.3f} (CV) &mdash; see <code>results/modeling_summary.md</code> for the held-out figures.</p>

<figure>
  <img src="data:image/png;base64,{b64['importance_sys']}" alt="Feature importance for systolic model" />
</figure>
<p class="fig-caption"><strong>Figure 5.</strong> Top 15 features, systolic model. Adherence dominates, followed by guidance-session count &mdash; consistent with the correlation sweep in Figure 4.</p>

<h2><span class="sec-num">5.</span>Discussion</h2>
<p>The central finding is that guidance amplifies the effect of produce
provision beyond what adherence alone explains: if the arm effect were purely
an adherence artifact, it would not survive the ANCOVA adjustment in Section 4.3,
yet it does for both outcomes. This is consistent with guidance changing
something other than raw adherence &mdash; for instance, which items participants
choose to eat, how they are prepared, or behavior outside the produce basket
itself that this dataset does not capture.</p>
<p>The gap between Dietitian and AI Assistant is notable but not extreme
({group_stats.loc['Dietitian','systolic_change']:.1f} versus
{group_stats.loc['AI_Assistant','systolic_change']:.1f} mmHg systolic): in this
simulated setting, AI-delivered guidance captures a substantial share of the
benefit of human dietitian counseling, though it does not fully match it.</p>

<h2><span class="sec-num">6.</span>Limitations</h2>
<ul>
  <li><strong>Synthetic outcome construction.</strong> Baseline demographics and
  blood pressure are real; arm assignment, adherence, and follow-up blood
  pressure are simulated. Results should be read as a demonstration of method,
  not as clinical evidence of guidance efficacy.</li>
  <li><strong>Sample size relative to feature count.</strong> With {n} rows
  and roughly 50 candidate features, individual produce-item effects are not
  reliably estimable; only adherence and guidance-engagement signals rise
  clearly above noise.</li>
  <li><strong>No subgroup treatment-effect estimation.</strong> A causal forest
  analysis (<code>econml</code>'s <code>CausalForestDML</code>) was planned to test
  whether the guidance effect varies by subgroup (e.g., participants prone to
  low adherence) but was not run in this environment. The feature importances
  in Figure 5 are predictive, not causal, and should not be interpreted as
  subgroup treatment effects.</li>
</ul>

<h2><span class="sec-num">7.</span>Conclusion</h2>
<p>Guided nutrition support &mdash; whether delivered by a dietitian or an AI
assistant &mdash; was associated with significantly larger blood pressure
reductions than unguided produce provision alone, and this effect held up after
adjusting for the adherence confound built into the study design. Random Forest
was the most reliable predictive model across both outcomes. The natural next
step is subgroup treatment-effect estimation (causal forest) to test whether
guidance helps some participants more than others, followed by replication on
real trial data.</p>

<div class="refs">
<p><strong>Data source.</strong> Saka, K. Cardiovascular Disease Dataset (cleaned).
Derived from Kaggle <code>sulianova/cardiovascular-disease-dataset</code> (70,000 records);
300 participants sampled for this study's baseline population.
<a href="https://github.com/Kafayatjumai/Cardiovascular-Disease-Dataset">github.com/Kafayatjumai/Cardiovascular-Disease-Dataset</a></p>
<p><strong>Reproducibility.</strong> Full pipeline: <code>notebooks/bp_farmers_market_analysis.ipynb</code>;
scripted equivalent in <code>scripts/01_eda.py</code> through <code>04_build_report.py</code>.
Raw data: <code>data/bp_farmers_market_study_dataset.csv</code>.</p>
</div>

</div>
"""

    html_path = RESULTS_DIR / "RESEARCH_PAPER.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"Saved {html_path}")

    md = f"""# Guided Nutrition Support and Blood Pressure Outcomes: A Comparative Study of Dietitian Counseling, an AI Nutrition Assistant, and Unguided Farmer's-Market Produce Provision

{AUTHOR} — {DATE}

## Abstract

Farmer's-market produce provision is increasingly used as a food-as-medicine
intervention for hypertension, but it is unclear whether pairing produce with
human or AI-delivered nutrition guidance improves outcomes over provision alone.
This study compares three arms — Dietitian counseling, an AI nutrition
assistant, and no guidance (control) — layered on identical produce provision,
in a sample of {n} participants ({group_counts.min()} per arm). Both guided arms
showed significantly larger blood pressure reductions than control (ANOVA,
p < 0.001 for both outcomes), and the effect persisted after adjusting for
adherence and baseline BP (ANCOVA). Adherence was the strongest predictor across
all models; Random Forest outperformed linear and XGBoost baselines under 5-fold
CV. Findings should be read as a methodological demonstration: outcome data is
synthetic, layered on a real baseline cohort.

## 1. Introduction

Produce-prescription programs are a growing food-as-medicine strategy for
hypertension. This study asks whether pairing produce provision with guidance
(Dietitian or AI Assistant) changes outcomes versus provision alone (Control).

## 2. Assumptions

1. Diet is restricted to what is provided — no outside-diet variable exists.
2. Adherence is not guaranteed — treated as an explicit confound throughout,
   not averaged away.

Age is bucketed (18-29 to 60-65); race is a synthetic broad category, not
sampled to match a specific real population.

## 3. Data and Methods

**3.1 Data source.** Baseline demographics/BP from 300 real records (Saka
cardiovascular dataset, Kaggle `sulianova/cardiovascular-disease-dataset`).
Study-arm assignment, adherence, and follow-up BP are synthetic.

**3.2 Design.** {n} participants, {group_counts.min()} per arm. 34 produce-item
columns, adherence %, guidance sessions, baseline/follow-up BP.

**3.3 Statistical analysis.** One-way ANOVA + Kruskal-Wallis per outcome, then
ANCOVA (arm + adherence + baseline BP) to test whether the arm effect survives
adjustment.

**3.4 Predictive modeling.** Linear, Ridge, Random Forest, XGBoost; 5-fold CV
scored on R², RMSE, MAE; winner re-fit on an 80/20 held-out split.

## 4. Results

- Mean systolic change: Dietitian {group_stats.loc['Dietitian','systolic_change']:.2f},
  AI Assistant {group_stats.loc['AI_Assistant','systolic_change']:.2f},
  Control {group_stats.loc['Control_NoGuidance','systolic_change']:.2f} mmHg.
- Adherence correlates with systolic change at r = {adherence_r_sys:.2f}, and is
  unevenly distributed by arm ({adherence_by_group['Dietitian']:.0f}% Dietitian
  vs. {adherence_by_group['Control_NoGuidance']:.0f}% Control).
- ANOVA: systolic F = {sys_f:.1f}, p = {sys_p:.1e}; diastolic F = {dia_f:.1f}, p = {dia_p:.1e}.
- ANCOVA group effect survives adjustment (systolic p = 4.9e-06, diastolic p = 5.5e-08).
- Random Forest is the top model on both outcomes (5-fold CV); see
  `results/model_comparison.csv` for full metrics.
- Top features (both outcomes): `adherence_pct`, then `guidance_sessions_or_interactions`
  — consistent with the correlation sweep.

Figures: see `figures/01–06` or the HTML version of this paper for inline plots.

## 5. Discussion

The arm effect is not a pure adherence artifact — it survives ANCOVA adjustment,
suggesting guidance changes something beyond raw adherence percentage (e.g. which
items are eaten, or behavior not captured by this dataset). The AI Assistant arm
captures a substantial share of the Dietitian arm's benefit without fully matching it.

## 6. Limitations

- Outcome data (arm assignment, adherence, follow-up BP) is synthetic.
- {n} rows vs. ~50 features limits reliable individual produce-item effect estimates.
- Causal forest (subgroup treatment effects) was planned but not run in this
  environment (`econml` unavailable) — feature importances are predictive, not causal.

## 7. Conclusion

Guided nutrition support — Dietitian or AI — was associated with significantly
larger BP reductions than unguided provision, holding up after adjusting for
adherence. Next steps: causal forest subgroup analysis, replication on real trial data.

---

**Data source:** Saka, K. Cardiovascular Disease Dataset (cleaned), derived from
Kaggle `sulianova/cardiovascular-disease-dataset`.
https://github.com/Kafayatjumai/Cardiovascular-Disease-Dataset

**Reproducibility:** `notebooks/bp_farmers_market_analysis.ipynb`; scripted
pipeline in `scripts/01_eda.py` through `04_build_report.py`.
"""
    md_path = RESULTS_DIR / "RESEARCH_PAPER.md"
    md_path.write_text(md, encoding="utf-8")
    print(f"Saved {md_path}")


if __name__ == "__main__":
    main()
