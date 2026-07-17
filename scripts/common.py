"""Shared paths and constants for the BP / Farmer's Market Study pipeline."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "bp_farmers_market_study_dataset.csv"
FIGURES_DIR = PROJECT_ROOT / "figures"
RESULTS_DIR = PROJECT_ROOT / "results"

FIGURES_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

GROUP_ORDER = ["Control_NoGuidance", "Dietitian", "AI_Assistant"]
GROUP_COLORS = {
    "Control_NoGuidance": "#8c8c8c",
    "Dietitian": "#2E86AB",
    "AI_Assistant": "#E27D60",
}

TARGETS = ["systolic_change", "diastolic_change"]

PRODUCE_COLS = None  # filled in lazily by load_data()


def load_data():
    import pandas as pd

    df = pd.read_csv(DATA_PATH)
    global PRODUCE_COLS
    PRODUCE_COLS = [c for c in df.columns if c.startswith("produce_")]
    return df
