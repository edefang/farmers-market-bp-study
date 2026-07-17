# Guided Nutrition Support and Blood Pressure Outcomes: A Comparative Study of Dietitian Counseling, an AI Nutrition Assistant, and Unguided Farmer's-Market Produce Provision

Tony, July 17, 2026

## Abstract

Farmer's-market produce provision is increasingly used as a food-as-medicine intervention for hypertension, but it's still unclear whether pairing that produce with human or AI-delivered nutrition guidance actually improves outcomes over giving out produce alone. I built a 300-participant, 3-arm dataset (Dietitian, AI Assistant, Control), layering synthetic study-design variables on top of a real 70,000-record cardiovascular baseline cohort. During cleaning, 4 rows turned up with physiologically implausible baseline blood pressure readings and were dropped, leaving 296 participants (99 Dietitian, 99 Control, 98 AI Assistant) for analysis. Both guided arms showed significantly larger blood pressure reductions than control (one-way ANOVA, p < 0.001 for both systolic and diastolic change), and that gap survived ANCOVA adjustment for adherence and baseline BP, meaning it isn't just an adherence artifact. Adherence percentage was the single strongest predictor across every model and every analysis lens tested. Random Forest outperformed Linear, Ridge, and XGBoost baselines under 5-fold cross-validation, and a follow-up check confirmed the adherence-to-outcome relationship itself is linear rather than curved, so a straight line is the right way to describe it, not a polynomial. These findings should be read as a methodological demonstration: the outcome data (arm assignment, adherence, follow-up BP) is synthetic, layered on a real baseline cohort, not a clinical trial result.

## List of Figures

- Figure 1. Baseline systolic BP by age range.
- Figure 2. Blood pressure change by study arm (boxplot).
- Figure 3. Distribution of systolic BP change by group.
- Figure 4. Correlation heatmap of key variables.
- Figure 5. Adherence vs. systolic BP change, by group.
- Figure 6. Feature importance, systolic change model.
- Figure 7. Feature importance, diastolic change model.
- Figure 8. Linear regression, all groups (general fit).
- Figure 9. Linear regression, Dietitian arm.
- Figure 10. Linear regression, AI Assistant arm.
- Figure 11. Linear regression, Control arm.

## 1. Introduction and Research Objective

Produce-prescription programs are becoming a common food-as-medicine strategy for treating hypertension, but most of them just hand out food and hope for the best. What's less clear is whether adding guidance on top of that produce, whether from a dietitian or an AI assistant, actually changes outcomes compared to just giving someone the produce and leaving them to it. That's the question this study sets out to answer.

The objective was threefold: first, test whether guided nutrition support (Dietitian or AI Assistant) produces significantly larger blood pressure reductions than unguided produce provision alone; second, determine whether any such effect is real or just a byproduct of guided participants eating more of what they're given; and third, build a predictive model of BP change to see which variables actually drive the outcome, and confirm that the model's functional form matches what the data actually shows rather than assuming it.

## 2. Background and Initial Assumptions and Hypotheses

**Background.** Produce-prescription and food-as-medicine programs are a growing strategy for managing hypertension, but the question this study is built around is simple: does pairing produce with guidance change outcomes, and does it matter whether that guidance is human or AI-delivered? Answering that requires isolating the guidance effect from the much more obvious confound sitting underneath it, adherence, since a box of produce does nothing if it isn't eaten.

**Assumptions, locked in before any outcome data was analyzed:**

1. Diet is restricted to what's provided. No outside-diet variable exists in this dataset; participants are treated as eating only the farmer's-market produce given to them.
2. Adherence is not guaranteed. Participants may eat all, some, or none of what's provided, and `adherence_pct` is carried through every step of the analysis as a real confound, not averaged away or ignored.
3. Age is bucketed into ranges (18-29 through 60-65), balanced across buckets rather than skewed toward older adults.
4. Race is a synthetic, broad category, included only to have a demographic field present, not sampled to match any specific real-world population.
5. Gender uses the two categories present in the source data.

**Hypotheses:**

- **H1:** Guided nutrition support (Dietitian or AI Assistant) produces significantly greater blood pressure reduction than unguided produce provision (Control).
- **H2:** The group effect will not be fully explained by adherence alone, meaning it should survive adjustment for adherence and baseline BP (ANCOVA).
- **H3:** Adherence percentage will be the strongest single predictor of BP change, regardless of study arm.
- **H4:** A tree-based model will outperform linear baselines, given the number of produce and demographic features in play, though the improvement may be limited by the small sample size.

## 3. Data Sources and Methodology

**3.1 Data source.** Baseline demographics and blood pressure come from 300 real records sampled from a 70,000-record cardiovascular dataset (Saka's cleaned "Cardiovascular Disease Dataset," Kaggle: `sulianova/cardiovascular-disease-dataset`, GitHub: `Kafayatjumai/Cardiovascular-Disease-Dataset`). That real sample seeded age, sex, BMI, cholesterol, glucose, smoking, alcohol intake, physical activity, and baseline systolic/diastolic BP. Everything about the study design itself, meaning group assignment, produce baskets, adherence, guidance sessions, and follow-up BP, was built synthetically on top of that real sample, since no real trial of this design exists to draw from.

**3.2 Data cleaning.** Checking `baseline_diastolic_bp` for plausibility turned up a max value of 1000, nowhere near a real diastolic reading. Three participants carried that value at baseline with a matching follow-up reading around 997 to 998, which points to a stray zero introduced somewhere upstream (100 becoming 1000) rather than three people independently producing the same impossible number. A fourth participant had a baseline systolic reading of 17, also not survivable. All four look like data entry artifacts in the source file rather than real extreme physiology, and dropping them is more honest than guessing at a corrected value. That leaves 296 participants: 99 Dietitian, 99 Control, 98 AI Assistant, close to but not exactly the even 100-per-arm the study was originally designed for.

**3.3 Dataset.** 296 rows, 57 columns after cleaning, no missing values (0 missing cells across all columns), with a dtype breakdown of 42 float64, 10 string, 3 int64, and 2 boolean columns. 34 `produce_<item>_kg` columns track how much of each item was provided that week, alongside `total_produce_kg_provided`, `adherence_pct` (percent of provided produce actually eaten), `guidance_sessions_or_interactions`, and baseline/follow-up BP for both systolic and diastolic readings. An explicit flag column, `assumption_diet_restricted_to_provided_produce`, documents Assumption 1 directly in the data rather than leaving it implicit.

**3.4 Statistical methodology.** For each outcome (`systolic_change`, `diastolic_change`) I ran a one-way ANOVA plus a Kruskal-Wallis test as a non-parametric check, then followed up with ANCOVA (arm, adherence, baseline BP) to test whether the arm effect held up once adherence and starting BP were controlled for. The logic: if the ANCOVA group effect stays significant after adding adherence as a covariate, the guidance-type effect is real and holds up beyond what adherence alone explains. If it loses significance, most of the apparent group effect is really an adherence effect in disguise.

**3.5 Predictive modeling methodology.** I tested four models, Linear Regression, Ridge Regression, Random Forest (300 estimators), and XGBoost (300 estimators), each behind a `ColumnTransformer` that standardized numeric columns and one-hot encoded categoricals. Columns that would leak the outcome (follow-up BP, since it's just baseline plus change) or carry no signal (participant ID, the constant assumption flag) were excluded from the feature set. Every model ran under 5-fold cross-validation (shuffled, fixed random seed) scored on R², RMSE, and MAE. The winner was chosen on highest mean CV R², checked against its standard deviation across folds, then re-fit on a genuine 80/20 held-out split to get an unbiased final performance number. Feature importances from the winning model were then cross-checked against the EDA correlation sweep as a sanity check.

**3.6 Functional-form check.** After the EDA scatter plot of adherence vs. systolic change raised the question of whether a straight line was really the right way to describe that relationship, I fit linear and polynomial (degree 2 and 3) regressions against the same data, pooled across all participants and separately within each arm, and compared training R² against 5-fold cross-validated R² to check whether the added curvature was capturing real structure or just fitting noise.

## 4. Data Preparation and Analysis

**4.1 Target distribution.** Across the 296 cleaned participants, mean systolic change was -3.85 mmHg (std 4.18, range -15.50 to 6.40) and mean diastolic change was -2.53 mmHg (std 2.60, range -11.20 to 5.50). Negative values mean BP dropped from baseline to follow-up, so on average BP fell across the whole sample, guided or not. Baseline systolic BP by age range was also checked (Figure 1): it rises gradually across the five age buckets with no bucket standing out as anomalous, which is what a real population sample should look like and a good sign the cleaning step above didn't leave anything else broken.

**Figure 1. Baseline systolic BP by age range.** Boxplot of `baseline_systolic_bp` across the five age buckets (18-29 through 60-65). Shows a gradual, expected rise in baseline BP with age and confirms no single age bucket is anomalously high or low before any group comparison is made.

![Figure 1: Baseline systolic BP by age range](../figures/03_box_baseline_bp_by_age.png)

**4.2 Group-level comparison.** Mean BP change differed sharply by study arm:

| Group | n | Systolic Δ mean (std) | Diastolic Δ mean (std) | Mean adherence (%) |
|---|---:|---:|---:|---:|
| Dietitian | 99 | -6.07 (4.23) | -4.08 (2.41) | 64.5 |
| AI Assistant | 98 | -4.36 (3.46) | -2.54 (2.36) | 55.3 |
| Control | 99 | -1.12 (3.17) | -0.96 (2.04) | 34.6 |

Figure 2 shows this same pattern visually for both outcomes side by side: the Control arm's box straddles zero, meaning many control participants saw little to no change, while Dietitian shows the largest leftward (more negative) shift and the widest spread, and AI Assistant sits between the two.

**Figure 2. Blood pressure change by study arm.** Side-by-side boxplots of systolic BP change (left) and diastolic BP change (right) for Control, Dietitian, and AI Assistant, with a dashed zero-reference line. Shows the ordering and spread of outcomes across arms at a glance, matching the group-means table above.

![Figure 2: Blood pressure change by study arm](../figures/01_box_bp_change_by_group.png)

The boxplot in Figure 2 shows medians and spread, but not the full shape of each group's distribution. Figure 3 fills that gap with an overlaid density plot of systolic change by group, which makes the degree of overlap between arms clearer than a boxplot alone: Control's distribution sits visibly to the right of Dietitian's, with AI Assistant's distribution overlapping both, consistent with it capturing a partial, not full, share of the Dietitian benefit.

**Figure 3. Distribution of systolic BP change by group.** Overlaid kernel density plots of `systolic_change` for each arm, with a dashed zero-reference line. Shows the shape and degree of overlap between arms, which a boxplot's summary statistics can understate.

![Figure 3: Distribution of systolic BP change by group](../figures/04_dist_bp_change_by_group.png)

**4.3 Correlation sweep.** Across every numeric column, `adherence_pct` was by far the strongest correlate of both outcomes (r = -0.67 for systolic change, r = -0.56 for diastolic change). `guidance_sessions_or_interactions` was a distant second (r = -0.26 systolic, -0.22 diastolic). Individual produce items showed only weak correlations, generally under |r| = 0.16 (for example `produce_lettuce_kg` at -0.16 systolic, `produce_cauliflower_kg` at 0.15 diastolic), which given roughly 50 features spread across fewer than 300 rows is consistent with noise rather than a real per-vegetable effect. No single produce item stood out as meaningfully protective.

Figure 4 gives a fast multi-variable view of these same relationships alongside the other key numeric columns, confirming adherence's correlation strength stands apart from the rest of the variable set at a glance.

**Figure 4. Correlation heatmap of key variables.** Pairwise correlation matrix across adherence, total produce provided, guidance sessions, baseline BP, BMI, and both outcome variables. Confirms `adherence_pct` as the standout correlate of both outcomes relative to every other variable in the matrix.

![Figure 4: Correlation heatmap of key variables](../figures/05_heatmap_correlations.png)

**4.4 Confound check.** Adherence was unevenly distributed by group exactly as the study design would produce it: 64.5% mean in Dietitian, 55.3% in AI Assistant, 34.6% in Control. It was not meaningfully confounded by age (ranging narrowly from 46.3% to 55.5% mean adherence across age buckets) or by sex (51.2% female vs. 52.0% male), which cleanly isolates group assignment and adherence as the two variables actually driving the outcome, rather than some hidden demographic split. Across the full sample, 11.1% of participants had near-zero adherence (10% or less), a built-in noise factor present in every arm by design.

Figure 5 shows this confound directly: adherence plotted against systolic change with each point colored by arm. Dietitian participants (highest adherence on average) cluster toward the high-adherence, large-negative-change side of the plot, while Control participants cluster toward the low-adherence side, visually illustrating why adherence has to be controlled for before attributing BP change to group assignment alone.

**Figure 5. Adherence vs. systolic BP change, by group.** Scatterplot of `adherence_pct` against `systolic_change`, colored by study arm, with a dashed zero-reference line. Illustrates the adherence confound described above and motivates the ANCOVA adjustment in Section 5.1.

![Figure 5: Adherence vs. systolic BP change, by group](../figures/02_scatter_adherence_vs_change.png)

## 5. Results and Findings

**5.1 Hypothesis testing.**

- Systolic change: one-way ANOVA F = 47.01, p = 1.96e-18; Kruskal-Wallis H = 72.93, p = 1.46e-16.
- Diastolic change: one-way ANOVA F = 46.46, p = 2.98e-18; Kruskal-Wallis H = 74.33, p = 7.22e-17.
- ANCOVA, systolic (group + adherence_pct + baseline_systolic_bp): group effect p = 8.44e-06, adherence effect p = 1.16e-27, model R² = 0.497.
- ANCOVA, diastolic (group + adherence_pct + baseline_diastolic_bp): group effect p = 7.98e-08, adherence effect p = 5.33e-15, model R² = 0.385.

The group effect survives ANCOVA adjustment in both outcomes, confirming H1 and H2: guidance type has a real effect on BP change beyond what adherence alone explains.

**5.2 Predictive modeling.**

*Target: systolic_change*

| Model | CV R² mean (std) | RMSE | MAE |
|---|---:|---:|---:|
| Random Forest | 0.418 (0.071) | 3.175 | 2.557 |
| XGBoost | 0.286 (0.106) | 3.507 | 2.765 |
| Ridge Regression | 0.234 (0.146) | 3.626 | 2.878 |
| Linear Regression | 0.223 (0.148) | 3.653 | 2.899 |

Winner: Random Forest. Held-out 80/20 test split: R² = 0.351, RMSE = 3.31, MAE = 2.59. Figure 6 shows the top 15 features behind that model's predictions, led by `adherence_pct` at an importance of 0.539, more than twenty times any other single feature.

**Figure 6. Feature importance, systolic change model.** Top 15 features from the winning Random Forest model for `systolic_change`, ranked by importance. `adherence_pct` dominates, consistent with the correlation sweep in Section 4.3.

![Figure 6: Feature importance, systolic change model](../figures/06_feature_importance_systolic_change.png)

*Target: diastolic_change*

| Model | CV R² mean (std) | RMSE | MAE |
|---|---:|---:|---:|
| Random Forest | 0.321 (0.109) | 2.094 | 1.670 |
| XGBoost | 0.164 (0.084) | 2.332 | 1.852 |
| Ridge Regression | 0.142 (0.264) | 2.323 | 1.861 |
| Linear Regression | 0.132 (0.271) | 2.335 | 1.870 |

Winner: Random Forest. Held-out 80/20 test split: R² = 0.386, RMSE = 2.10, MAE = 1.62. As with systolic change, Figure 7 confirms `adherence_pct` (importance 0.285) as the dominant feature, with `group_Dietitian` a distant second (0.060).

**Figure 7. Feature importance, diastolic change model.** Top 15 features from the winning Random Forest model for `diastolic_change`, ranked by importance. Same top-feature ordering as Figure 6, confirming the result isn't specific to one outcome.

![Figure 7: Feature importance, diastolic change model](../figures/06_feature_importance_diastolic_change.png)

Top features were consistent across both targets, confirming H3. One thing worth flagging directly: under 5-fold CV, systolic change is clearly the easier target to predict (R² = 0.418 vs. 0.321 for diastolic). But on the single 80/20 held-out split, that ordering flips, diastolic comes out higher (0.386) than systolic (0.351). With under 300 rows, a single train/test split is noisy enough to reorder two models that are genuinely close, which is exactly why the CV mean, not the one-off holdout number, is the number to trust for ranking the two targets against each other.

**5.3 Functional-form check (adherence vs. systolic change).** Pooled across all 296 participants, the linear fit was y = -0.104x + 1.50 (R² = 0.455, r = -0.674, p = 1.31e-40), shown in Figure 8. Moving to a quadratic fit only raised training R² to 0.465, and a cubic to 0.465, both negligible gains. Cross-validated R² told the real story: 0.449 for linear, 0.453 for quadratic, 0.442 for cubic, essentially flat, meaning the added curvature wasn't capturing real structure.

**Figure 8. Linear regression, all groups (general fit).** Adherence vs. systolic BP change across all 296 participants, with the fitted linear regression line and its equation, R², r, and p-value labeled. The pooled functional-form reference for Figures 9 through 11.

![Figure 8: Linear regression, all groups](../figures/07_regression_general.png)

The same pattern held within each arm individually, shown in Figures 9 through 11 and summarized in the table below:

| Group | n | r | Linear R² | Poly² R² | Linear CV R² | Poly² CV R² |
|---|---:|---:|---:|---:|---:|---:|
| Dietitian | 99 | -0.70 | 0.494 | 0.497 | 0.422 | 0.404 |
| AI Assistant | 98 | -0.50 | 0.253 | 0.253 | 0.173 | 0.159 |
| Control | 99 | -0.45 | 0.202 | 0.202 | 0.101 | 0.058 |

**Figure 9. Linear regression, Dietitian arm.** Adherence vs. systolic BP change for the Dietitian arm only, with fitted line and stats. Shows the steepest slope and tightest fit of the three arms.

![Figure 9: Linear regression, Dietitian arm](../figures/08_regression_dietitian.png)

**Figure 10. Linear regression, AI Assistant arm.** Adherence vs. systolic BP change for the AI Assistant arm only, with fitted line and stats. Flatter slope and weaker fit than Dietitian.

![Figure 10: Linear regression, AI Assistant arm](../figures/09_regression_ai_assistant.png)

**Figure 11. Linear regression, Control arm.** Adherence vs. systolic BP change for the Control arm only, with fitted line and stats. The flattest slope and weakest fit of the three, where the quadratic term actively hurt cross-validated performance (0.101 to 0.058), the clearest sign in the whole analysis that curvature was fitting noise rather than signal.

![Figure 11: Linear regression, Control arm](../figures/10_regression_control.png)

In every arm, the polynomial term added little to nothing to training R² and made cross-validated performance worse. A straight linear regression is the correct model for this relationship, both pooled and within each arm.

## 6. Explanation and Interpretation of Results

The headline finding is that guided nutrition support works, and it isn't just a story about who ate more of their produce box. The arm effect survives ANCOVA adjustment for adherence and baseline BP, which means guidance is changing something beyond the raw adherence percentage, possibly which specific items get eaten, possibly some behavior this dataset doesn't capture directly. That's a more interesting result than a simple "guided people ate more" explanation would be.

The AI Assistant arm captures a substantial share of the Dietitian arm's benefit (-4.36 mmHg vs. -6.07 mmHg systolic, visible in Figures 2 and 3) without fully matching it. That's meaningful on its own: it suggests guidance doesn't have to come from a human to move the needle, even if a trained dietitian still gets better results, likely by driving deeper or more consistent adherence (64.5% mean vs. 55.3%).

Adherence is the dominant variable in every analysis lens applied here: strongest correlation (Figure 4), strongest ANCOVA covariate, strongest feature importance in the winning model by a wide margin (Figures 6 and 7), and the clearest linear relationship to outcome (Figures 8 through 11). If there's one practical lever in this whole dataset, it's adherence, and that holds regardless of which arm a participant is in.

Random Forest beating the linear baselines by a real and, after cleaning, noticeably wider margin than before suggests there's meaningful nonlinear interaction structure in the data, for instance adherence combining with group membership in a way a straight additive model can't capture, rather than curvature in the adherence-outcome relationship itself, which the functional-form check in Section 5.3 confirmed is linear. That's a useful distinction: the tree model's edge comes from combining variables, not from bending the adherence line.

The weak, scattered correlations on individual produce items are best read as noise rather than signal, unsurprising with roughly 50 features spread across fewer than 300 rows. No specific vegetable should be read as more or less protective based on this dataset.

## 7. Limitations

- The outcome data, meaning arm assignment, adherence, and follow-up BP, is synthetic, layered on top of a real baseline cohort. Baseline demographics and starting BP are real; everything downstream of that is constructed. These findings are a methodological demonstration, not a clinical result.
- Four rows with physiologically implausible baseline BP readings (Section 3.2) were dropped during cleaning. That's a defensible call given how far outside any real range those values sat, but it's a judgment call, and it shifts the arm sizes slightly off the original 100-per-arm design (99, 99, 98).
- With under 300 rows against roughly 50 features, individual produce-item effects can't be reliably estimated; the weak correlations reported in Section 4.3 should not be read as causal or even reliably real.
- `CausalForestDML` (econml) was planned as a stretch goal for estimating whether the guidance-type treatment effect varies by subgroup (for example, whether AI helps low-adherence-prone participants more than high-adherence ones), but wasn't run because `econml` wasn't available in this environment. The feature importances reported here are predictive, not causal, and shouldn't be over-interpreted as treatment effects.
- The systolic-vs-diastolic model comparison is sensitive to which evaluation split is used: 5-fold CV ranks systolic as the easier target, but the single held-out split ranks diastolic higher. With this sample size, a single 80/20 split isn't a stable enough basis to declare one target definitively easier than the other; the CV numbers are the more trustworthy comparison, and even those carry a wide fold-to-fold standard deviation (0.071 to 0.148 across models).
- Race is a synthetic, broad demographic category, not sampled to match any specific real-world population, so results should not be generalized to any particular demographic distribution.

## 8. Conclusion and Recommendations

Guided nutrition support, whether from a dietitian or an AI assistant, was associated with significantly larger blood pressure reductions than unguided produce provision alone, and that held up even after adjusting for adherence. Adherence still matters, more than anything else in this dataset, but it isn't the whole story behind why guidance works.

**Recommendations:**

1. Run the causal forest subgroup analysis once `econml` is available in the environment, to test directly whether AI guidance helps some subgroups (for example, participants with a low baseline propensity to adhere) more than others, rather than relying on predictive feature importances as a substitute.
2. Replicate this design on real trial data. Every result here rests on a synthetic outcome layer over a real baseline cohort, and the next real test of these hypotheses needs real follow-up measurements.
3. Prioritize research on what actually drives adherence itself, since it is the single strongest lever in every model and every analysis angle tested here. Understanding adherence's own drivers may matter more than optimizing which produce items are provided.
4. Given that the adherence-to-outcome relationship is confirmed linear in both the pooled data and within every arm, future modeling work on this dataset can treat adherence as a linear term without needing polynomial expansion, which keeps the model simpler without giving up explanatory power.
5. Use repeated or nested cross-validation rather than a single 80/20 holdout split when comparing systolic and diastolic model performance going forward, given how easily the one-shot holdout split reordered the two targets relative to the more stable CV ranking.

---

**Data source:** Saka, K. Cardiovascular Disease Dataset (cleaned), derived from Kaggle `sulianova/cardiovascular-disease-dataset`. https://github.com/Kafayatjumai/Cardiovascular-Disease-Dataset

**Reproducibility:** `notebooks/bp_study_colab.ipynb` walks the full pipeline end to end for Google Colab, reading the dataset directly from this repo; the same pipeline also runs as standalone scripts: `scripts/01_eda.py`, `02_visualizations.py`, `03_modeling.py`, `06_regression_plots.py`, in that order. Full intermediate output in `results/eda_summary.md`, `results/modeling_summary.md`, and `results/model_comparison.csv`. All eleven figures referenced above are in `figures/`.
