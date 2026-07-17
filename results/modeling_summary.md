# Modeling Summary, Farmer's Market Produce & Blood Pressure Study

## Target: `systolic_change`

| model             |   r2_mean |   r2_std |   rmse_mean |   mae_mean |
|:------------------|----------:|---------:|------------:|-----------:|
| Random Forest     |     0.418 |    0.071 |       3.175 |      2.557 |
| XGBoost           |     0.286 |    0.106 |       3.507 |      2.765 |
| Ridge Regression  |     0.234 |    0.146 |       3.626 |      2.878 |
| Linear Regression |     0.223 |    0.148 |       3.653 |      2.899 |

**Winner (highest 5-fold CV mean R^2): Random Forest**

Held-out 80/20 test split (unbiased final estimate): R^2 = 0.351, RMSE = 3.31, MAE = 2.59

**Top 5 features (Feature Importance):**

- `adherence_pct`: 0.539
- `produce_radishes_kg`: 0.025
- `produce_lettuce_kg`: 0.021
- `bmi`: 0.021
- `produce_onions_kg`: 0.017

## Target: `diastolic_change`

| model             |   r2_mean |   r2_std |   rmse_mean |   mae_mean |
|:------------------|----------:|---------:|------------:|-----------:|
| Random Forest     |     0.321 |    0.109 |       2.094 |      1.670 |
| XGBoost           |     0.164 |    0.084 |       2.332 |      1.852 |
| Ridge Regression  |     0.142 |    0.264 |       2.323 |      1.861 |
| Linear Regression |     0.132 |    0.271 |       2.335 |      1.870 |

**Winner (highest 5-fold CV mean R^2): Random Forest**

Held-out 80/20 test split (unbiased final estimate): R^2 = 0.386, RMSE = 2.10, MAE = 1.62

**Top 5 features (Feature Importance):**

- `adherence_pct`: 0.285
- `group_Dietitian`: 0.060
- `produce_cauliflower_kg`: 0.046
- `guidance_sessions_or_interactions`: 0.045
- `total_produce_kg_provided`: 0.035

## Stretch Goal Not Run

`CausalForestDML` (econml) was listed as a stretch goal for estimating whether the guidance-type treatment effect varies by subgroup (e.g., low- vs. high-adherence-prone participants). It was not run in this pass because `econml` was not available in the environment; the Random Forest / XGBoost feature importances above are a predictive, not causal, substitute and should not be over-interpreted as treatment effects.
