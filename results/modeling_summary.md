# Modeling Summary — Farmer's Market Produce & Blood Pressure Study

## Target: `systolic_change`

| model             |   r2_mean |   r2_std |   rmse_mean |   mae_mean |
|:------------------|----------:|---------:|------------:|-----------:|
| Random Forest     |     0.379 |    0.157 |       3.202 |      2.620 |
| Ridge Regression  |     0.294 |    0.159 |       3.426 |      2.738 |
| Linear Regression |     0.286 |    0.158 |       3.446 |      2.758 |
| XGBoost           |     0.269 |    0.165 |       3.466 |      2.804 |

**Winner (highest 5-fold CV mean R^2): Random Forest**

Held-out 80/20 test split (unbiased final estimate): R^2 = 0.450, RMSE = 3.60, MAE = 2.99

**Top 5 features (Feature Importance):**

- `adherence_pct`: 0.457
- `guidance_sessions_or_interactions`: 0.044
- `group_Control_NoGuidance`: 0.027
- `produce_cabbage_kg`: 0.025
- `bmi`: 0.020

## Target: `diastolic_change`

| model             |   r2_mean |   r2_std |   rmse_mean |   mae_mean |
|:------------------|----------:|---------:|------------:|-----------:|
| Random Forest     |     0.321 |    0.064 |       2.109 |      1.682 |
| Ridge Regression  |     0.195 |    0.097 |       2.294 |      1.842 |
| Linear Regression |     0.183 |    0.098 |       2.311 |      1.856 |
| XGBoost           |     0.181 |    0.064 |       2.318 |      1.853 |

**Winner (highest 5-fold CV mean R^2): Random Forest**

Held-out 80/20 test split (unbiased final estimate): R^2 = 0.237, RMSE = 2.16, MAE = 1.75

**Top 5 features (Feature Importance):**

- `adherence_pct`: 0.340
- `guidance_sessions_or_interactions`: 0.069
- `produce_cauliflower_kg`: 0.040
- `total_produce_kg_provided`: 0.033
- `group_Dietitian`: 0.025

## Stretch Goal Not Run

`CausalForestDML` (econml) was listed as a stretch goal for estimating whether the guidance-type treatment effect varies by subgroup (e.g., low- vs. high-adherence-prone participants). It was not run in this pass because `econml` was not available in the environment; the Random Forest / XGBoost feature importances above are a predictive, not causal, substitute and should not be over-interpreted as treatment effects.
