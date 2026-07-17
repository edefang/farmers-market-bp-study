# Farmer's Market Produce and Blood Pressure Study

A comparative study testing whether pairing farmer's-market produce provision with guidance, either from a **dietitian** or an **AI nutrition assistant**, changes blood pressure outcomes more than giving out produce alone (**control**). 300 participants, 100 per arm, baseline demographics and BP sampled from a real 70,000-record cardiovascular dataset, with the study design itself (group assignment, produce baskets, adherence, follow-up BP) built synthetically on top.

**Headline finding:** guided nutrition support (dietitian or AI) produced significantly larger BP reductions than unguided produce provision (p < 0.001), and that effect survived adjustment for adherence and baseline BP. Adherence percentage was the strongest predictor across every model tested, and the relationship between adherence and outcome is confirmed linear, not curved.

## Start here

**[COMPREHENSIVE_RESEARCH_PAPER.md](COMPREHENSIVE_RESEARCH_PAPER.md)** (or the [PDF](COMPREHENSIVE_RESEARCH_PAPER.pdf)) is the full write-up: introduction, background and hypotheses, methodology, EDA, results, interpretation, limitations, and recommendations, with all 11 figures embedded inline.

## Repository layout

| Path | Contents |
|---|---|
| `COMPREHENSIVE_RESEARCH_PAPER.md` / `.pdf` | The full research paper (read this first) |
| `data/bp_farmers_market_study_dataset.csv` | 300 rows x 57 columns; the study dataset |
| `scripts/` | Reproducible pipeline, run in order: `01_eda.py` → `02_visualizations.py` → `03_modeling.py` → `04_build_report.py` → `05_build_paper.py` → `06_regression_plots.py` |
| `figures/` | All 11 charts referenced in the paper (EDA, feature importance, regression fits) |
| `results/eda_summary.md` | Full exploratory data analysis output |
| `results/modeling_summary.md` | Full model comparison, cross-validation scores, feature importances |
| `results/model_comparison.csv` | Raw CV metrics for every model x target |

## Reproducing the pipeline

```
pip install pandas numpy scipy scikit-learn xgboost matplotlib seaborn
cd scripts
python 01_eda.py
python 02_visualizations.py
python 03_modeling.py
python 04_build_report.py
python 05_build_paper.py
python 06_regression_plots.py
```

## Data source

Baseline demographics and blood pressure: Saka, K. *Cardiovascular Disease Dataset* (cleaned), derived from Kaggle `sulianova/cardiovascular-disease-dataset`. https://github.com/Kafayatjumai/Cardiovascular-Disease-Dataset

All study-design variables (group assignment, produce baskets, adherence, guidance sessions, follow-up BP) are synthetic, layered on top of that real baseline sample. See the paper's Limitations section before drawing any conclusions beyond a methodology demonstration.
