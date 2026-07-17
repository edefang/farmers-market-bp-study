# EDA Summary Farmer's Market Produce & Blood Pressure Study

## 1. Shape & Integrity Check

- Rows: **300**, Columns: **57**
- Missing values: **none** (0 missing cells across all columns)
- Dtype breakdown: 42 `float64`, 10 `str`, 3 `int64`, 2 `bool`
- Group sizes: AI_Assistant=100, Dietitian=100, Control_NoGuidance=100

## 2. Target Distribution

|                  |   mean |   std |    min |   max |
|:-----------------|-------:|------:|-------:|------:|
| systolic_change  |  -3.83 |  4.18 | -15.50 |  6.40 |
| diastolic_change |  -2.53 |  2.59 | -11.20 |  5.50 |

Negative values mean BP dropped from baseline to follow-up. Overall mean systolic change: **-3.83 mmHg**, mean diastolic change: **-2.53 mmHg**.

## 3. Group-Level Comparison (BP Change by Study Arm)

| group              |   systolic_change_mean |   systolic_change_std |   systolic_change_count |   diastolic_change_mean |   diastolic_change_std |   diastolic_change_count |
|:-------------------|-----------------------:|----------------------:|------------------------:|------------------------:|-----------------------:|-------------------------:|
| Dietitian          |                  -6.07 |                  4.21 |                  100.00 |                   -4.08 |                   2.40 |                   100.00 |
| AI_Assistant       |                  -4.32 |                  3.48 |                  100.00 |                   -2.54 |                   2.34 |                   100.00 |
| Control_NoGuidance |                  -1.09 |                  3.17 |                  100.00 |                   -0.96 |                   2.03 |                   100.00 |

## 4. Correlation Sweep (numeric columns vs. targets)

**Top 15 correlates of `systolic_change` (by absolute value):**

|                                   |   systolic_change |
|:----------------------------------|------------------:|
| adherence_pct                     |             -0.67 |
| followup_systolic_bp              |              0.27 |
| guidance_sessions_or_interactions |             -0.26 |
| produce_lettuce_kg                |             -0.15 |
| produce_radishes_kg               |              0.12 |
| produce_kale_kg                   |              0.10 |
| produce_beets_kg                  |              0.09 |
| produce_squash_kg                 |              0.09 |
| followup_diastolic_bp             |              0.09 |
| produce_carrots_kg                |             -0.08 |
| produce_fennel_kg                 |              0.08 |
| baseline_diastolic_bp             |              0.07 |
| produce_swiss_chard_kg            |              0.07 |
| produce_zucchini_kg               |              0.06 |
| produce_tomatoes_kg               |              0.06 |

**Top 15 correlates of `diastolic_change` (by absolute value):**

|                                   |   diastolic_change |
|:----------------------------------|-------------------:|
| adherence_pct                     |              -0.56 |
| guidance_sessions_or_interactions |              -0.22 |
| followup_systolic_bp              |               0.15 |
| produce_cauliflower_kg            |               0.14 |
| produce_fennel_kg                 |               0.11 |
| produce_squash_kg                 |               0.10 |
| produce_arugula_kg                |               0.09 |
| produce_bell_peppers_kg           |               0.09 |
| produce_tomatoes_kg               |               0.09 |
| produce_lettuce_kg                |              -0.08 |
| produce_potatoes_kg               |              -0.08 |
| produce_broccoli_kg               |              -0.07 |
| total_produce_kg_provided         |               0.07 |
| produce_scallions_kg              |              -0.06 |
| produce_asparagus_kg              |              -0.06 |

## 5. Confound Check Adherence vs. Group / Demographics

**Adherence (%) by group:**

| group              |   mean |   std |   median |
|:-------------------|-------:|------:|---------:|
| Dietitian          |  64.56 | 27.83 |    73.05 |
| AI_Assistant       |  55.16 | 22.67 |    59.95 |
| Control_NoGuidance |  34.83 | 21.08 |    33.75 |

**Adherence (%) by age range:**

| age_range   |   mean |   std |   count |
|:------------|-------:|------:|--------:|
| 18-29       |  54.46 | 26.64 |   60.00 |
| 30-39       |  46.34 | 28.92 |   60.00 |
| 40-49       |  51.37 | 31.03 |   60.00 |
| 50-59       |  55.38 | 23.70 |   60.00 |
| 60-65       |  50.01 | 23.77 |   60.00 |

**Adherence (%) by sex:**

| sex    |   mean |   std |   count |
|:-------|-------:|------:|--------:|
| Female |  51.23 | 26.06 |  201.00 |
| Male   |  52.10 | 28.90 |   99.00 |

- Participants with near-zero adherence (<=10%): **11.0%** of the full sample.
- This confirms adherence is unevenly distributed by design (Dietitian group skews higher) and must be controlled for (ANCOVA / regression covariate) before attributing BP change to group assignment alone.

## 6. Hypothesis Tests Is the Group Difference Real?

**systolic_change**

- One-way ANOVA: F = 48.08, p = 8.14e-19
- Kruskal-Wallis (non-parametric check): H = 74.59, p = 6.37e-17
- ANCOVA (group + adherence_pct + baseline_systolic_bp): group effect p = 4.93e-06, adherence effect p = 1.77e-27, model R² = 0.494

**diastolic_change**

- One-way ANOVA: F = 47.41, p = 1.35e-18
- Kruskal-Wallis (non-parametric check): H = 75.97, p = 3.19e-17
- ANCOVA (group + adherence_pct + baseline_diastolic_bp): group effect p = 5.48e-08, adherence effect p = 3.52e-15, model R² = 0.386

**Interpretation:** if the ANCOVA group p-value stays significant after adding `adherence_pct` as a covariate, the guidance-type effect holds up beyond what adherence alone explains. If it loses significance, most of the apparent group effect is actually an adherence effect (Dietitian participants simply ate more of what they were given).
