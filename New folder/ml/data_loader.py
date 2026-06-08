"""
Load HIV risk datasets from CSV (Kaggle/UCI) or fall back to synthetic data.
Place your dataset at ml/data/hiv_dataset.csv with columns documented below.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from train import generate_synthetic_dataset

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_CSV = DATA_DIR / "hiv_dataset.csv"

# Expected columns (map your CSV headers via COLUMN_MAP)
COLUMN_MAP = {
    "Age": "age",
    "age": "age",
    "Gender": "gender",
    "gender": "gender",
    "BMI": "bmi",
    "bmi": "bmi",
    "STI": "sti_history",
    "sti_history": "sti_history",
    "CD4": "cd4_count",
    "cd4_count": "cd4_count",
    "CD4_Count": "cd4_count",
    "Behavioral": "behavioral_score",
    "behavioral_score": "behavioral_score",
    "Risk": "risk_class",
    "risk_class": "risk_class",
    "HIV_Risk": "risk_class",
}


def _engineer_from_raw(df: pd.DataFrame) -> pd.DataFrame:
    bmi = df["bmi"].astype(float)
    df["bmi_category"] = pd.cut(
        bmi, bins=[0, 18.5, 25, 30, 100], labels=["underweight", "normal", "overweight", "obese"]
    ).astype(str)
    age = df["age"].astype(int)
    df["age_group"] = pd.cut(
        age, bins=[0, 25, 40, 55, 100], labels=["young", "adult", "middle", "senior"]
    ).astype(str)
    df["medical_risk_index"] = (
        df["sti_history"] * 2
        + df["behavioral_score"] * 0.8
        + (df["cd4_count"] < 350).astype(int) * 2
        + (df["age"] > 50).astype(int) * 0.5
    ).round(2)
    df["risk_score_feat"] = (df["medical_risk_index"] + (bmi > 30).astype(int) * 0.5).round(2)
    return df


def load_dataset(csv_path: str | Path | None = None) -> pd.DataFrame:
    path = Path(csv_path) if csv_path else DEFAULT_CSV
    if path.exists():
        raw = pd.read_csv(path)
        renamed = {}
        for col in raw.columns:
            key = col.strip()
            if key in COLUMN_MAP:
                renamed[col] = COLUMN_MAP[key]
            elif key.lower() in COLUMN_MAP:
                renamed[col] = COLUMN_MAP[key.lower()]
        df = raw.rename(columns=renamed)
        required = ["age", "gender", "bmi", "sti_history", "cd4_count", "behavioral_score", "risk_class"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"CSV missing columns after mapping: {missing}")
        df["gender"] = df["gender"].astype(str).str.lower()
        if df["risk_class"].dtype == object:
            label_map = {
                "low": 0, "low risk": 0, "medium": 1, "medium risk": 1,
                "high": 2, "high risk": 2,
            }
            df["risk_class"] = df["risk_class"].astype(str).str.lower().map(label_map).fillna(df["risk_class"])
        df["risk_class"] = df["risk_class"].astype(int)
        df = df.drop_duplicates()
        return _engineer_from_raw(df)
    return generate_synthetic_dataset()
