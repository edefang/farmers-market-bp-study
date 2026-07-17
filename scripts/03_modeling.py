"""
Step C/D -- ML Modeling
Farmer's Market Produce & Blood Pressure Study

For each target (systolic_change, diastolic_change):
  1. Build a ColumnTransformer (one-hot encode categoricals, scale numerics).
  2. Run 5-fold CV for Linear Regression, Ridge, Random Forest, XGBoost.
     Score on R^2, RMSE, MAE.
  3. Pick a winner per Step D's rules (mean R^2, tie-break on std across folds).
  4. Re-fit the winner on a genuine 80/20 train/test split for an unbiased
     final number, and pull feature importances / coefficients (top 15).

Outputs:
  results/model_comparison.csv   - CV metrics for every model x target
  results/modeling_summary.md    - narrative results + winner + held-out score
  figures/06_feature_importance_<target>.png

Note: the project plan's Step C lists a stretch goal (CausalForestDML from
`econml`) for subgroup treatment-effect estimation. That library has heavy,
finicky native dependencies and is not installed in this environment; it's
called out as follow-up work in the final report rather than run here.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_data, RESULTS_DIR, FIGURES_DIR  # noqa: E402

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_validate, train_test_split, KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor

RANDOM_STATE = 42
TARGETS = ["systolic_change", "diastolic_change"]

# Columns that would leak the outcome (follow-up BP is baseline + change) or
# carry no information (constant flag / free-text id) are excluded from X.
LEAK_OR_ID_COLS = [
    "participant_id", "followup_systolic_bp", "followup_diastolic_bp",
    "systolic_change", "diastolic_change", "assumption_diet_restricted_to_provided_produce",
]

CATEGORICAL_COLS = [
    "group", "age_range", "sex", "race", "cholesterol", "glucose",
    "smoke", "alcohol_intake", "physical_activity", "ate_provided_food",
]

MODELS = {
    "Linear Regression": LinearRegression(),
    "Ridge Regression": Ridge(alpha=1.0, random_state=RANDOM_STATE),
    "Random Forest": RandomForestRegressor(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1),
    "XGBoost": XGBRegressor(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1, verbosity=0),
}


def build_preprocessor(numeric_cols, categorical_cols):
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
        ]
    )


def get_feature_names(preprocessor):
    num_cols = preprocessor.transformers_[0][2]
    cat_encoder = preprocessor.transformers_[1][1]
    cat_names = cat_encoder.get_feature_names_out(preprocessor.transformers_[1][2])
    return list(num_cols) + list(cat_names)


def run_target(df, target, all_out):
    drop_cols = [c for c in LEAK_OR_ID_COLS if c != target] + [target]
    X = df.drop(columns=drop_cols)
    y = df[target]

    categorical_cols = [c for c in CATEGORICAL_COLS if c in X.columns]
    numeric_cols = [c for c in X.columns if c not in categorical_cols]

    preprocessor = build_preprocessor(numeric_cols, categorical_cols)
    cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    rows = []
    for name, model in MODELS.items():
        pipe = Pipeline([("prep", preprocessor), ("model", model)])
        scores = cross_validate(
            pipe, X, y, cv=cv,
            scoring={"r2": "r2", "neg_rmse": "neg_root_mean_squared_error", "neg_mae": "neg_mean_absolute_error"},
            n_jobs=-1,
        )
        rows.append({
            "target": target,
            "model": name,
            "r2_mean": scores["test_r2"].mean(),
            "r2_std": scores["test_r2"].std(),
            "rmse_mean": -scores["test_neg_rmse"].mean(),
            "mae_mean": -scores["test_neg_mae"].mean(),
        })

    cv_table = pd.DataFrame(rows).sort_values("r2_mean", ascending=False).reset_index(drop=True)
    all_out["cv_tables"][target] = cv_table

    # Step D.2: don't pick on mean R^2 alone -- report std alongside it
    # (already in the table); winner = highest mean R^2 among the four models.
    winner_name = cv_table.iloc[0]["model"]
    all_out["winners"][target] = winner_name

    # Step D.4: refit winner on a genuine held-out split for an unbiased final number.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)
    winner_pipe = Pipeline([("prep", build_preprocessor(numeric_cols, categorical_cols)), ("model", MODELS[winner_name])])
    winner_pipe.fit(X_train, y_train)
    y_pred = winner_pipe.predict(X_test)
    holdout = {
        "r2": r2_score(y_test, y_pred),
        "rmse": mean_squared_error(y_test, y_pred) ** 0.5,
        "mae": mean_absolute_error(y_test, y_pred),
    }
    all_out["holdout"][target] = holdout

    # Step D.3: feature importances / coefficients (top 15), to cross-check
    # against the Section 4 correlation sweep from the EDA stage.
    feature_names = get_feature_names(winner_pipe.named_steps["prep"])
    model = winner_pipe.named_steps["model"]
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        importance_label = "Feature Importance"
    else:
        importances = np.abs(model.coef_)
        importance_label = "|Standardized Coefficient|"

    imp_series = pd.Series(importances, index=feature_names).sort_values(ascending=False).head(15)
    all_out["importances"][target] = (imp_series, importance_label, winner_name)

    fig, ax = plt.subplots(figsize=(9, 7))
    imp_series.sort_values().plot.barh(ax=ax, color="#2E86AB")
    ax.set_xlabel(importance_label)
    ax.set_title(f"Top 15 Features, {winner_name} ({target})")
    fig.tight_layout()
    fig_path = FIGURES_DIR / f"06_feature_importance_{target}.png"
    fig.savefig(fig_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {fig_path}")

    return cv_table


def main():
    df = load_data()
    all_out = {"cv_tables": {}, "winners": {}, "holdout": {}, "importances": {}}

    for target in TARGETS:
        run_target(df, target, all_out)

    combined_cv = pd.concat(all_out["cv_tables"].values(), ignore_index=True)
    combined_cv.to_csv(RESULTS_DIR / "model_comparison.csv", index=False)
    print(f"Saved {RESULTS_DIR / 'model_comparison.csv'}")

    # Narrative summary
    lines = ["# Modeling Summary, Farmer's Market Produce & Blood Pressure Study\n"]
    for target in TARGETS:
        lines.append(f"\n## Target: `{target}`\n\n")
        cv_table = all_out["cv_tables"][target].copy()
        cv_table_display = cv_table.drop(columns="target").round(3)
        lines.append(cv_table_display.to_markdown(index=False, floatfmt=".3f") + "\n")

        winner = all_out["winners"][target]
        holdout = all_out["holdout"][target]
        lines.append(
            f"\n**Winner (highest 5-fold CV mean R^2): {winner}**\n\n"
            f"Held-out 80/20 test split (unbiased final estimate): "
            f"R^2 = {holdout['r2']:.3f}, RMSE = {holdout['rmse']:.2f}, MAE = {holdout['mae']:.2f}\n\n"
        )

        imp_series, importance_label, _ = all_out["importances"][target]
        lines.append(f"**Top 5 features ({importance_label}):**\n\n")
        for feat, val in imp_series.head(5).items():
            lines.append(f"- `{feat}`: {val:.3f}\n")

    lines.append(
        "\n## Stretch Goal Not Run\n\n"
        "`CausalForestDML` (econml) was listed as a stretch goal for estimating "
        "whether the guidance-type treatment effect varies by subgroup (e.g., "
        "low- vs. high-adherence-prone participants). It was not run in this "
        "pass because `econml` was not available in the environment; the "
        "Random Forest / XGBoost feature importances above are a predictive, "
        "not causal, substitute and should not be over-interpreted as treatment effects.\n"
    )

    summary_path = RESULTS_DIR / "modeling_summary.md"
    summary_path.write_text("".join(lines), encoding="utf-8")
    print(f"Saved {summary_path}")


if __name__ == "__main__":
    main()
