"""
HIVCare AI - Model training pipeline per SRS Section 5.
Trains ensemble classifier; exports model.pkl and metrics for dashboard.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTENC
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

RANDOM_STATE = 42
OUTPUT_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = OUTPUT_DIR / "model.pkl"
METRICS_PATH = OUTPUT_DIR / "metrics.json"


def generate_synthetic_dataset(n_samples: int = 5000) -> pd.DataFrame:
    """Synthetic HIV risk dataset aligned with SRS features (for demo / Colab substitute)."""
    rng = np.random.default_rng(RANDOM_STATE)
    age = rng.integers(18, 75, n_samples)
    gender = rng.choice(["male", "female", "other"], n_samples, p=[0.48, 0.48, 0.04])
    bmi = rng.normal(24, 5, n_samples).clip(15, 45)
    sti_history = rng.choice([0, 1], n_samples, p=[0.7, 0.3])
    cd4_count = rng.integers(150, 1200, n_samples)
    behavioral_score = rng.integers(0, 6, n_samples)  # 0-5 risk behaviors

    # Engineered features (SRS Section 5)
    bmi_category = pd.cut(
        bmi, bins=[0, 18.5, 25, 30, 100], labels=["underweight", "normal", "overweight", "obese"]
    ).astype(str)
    age_group = pd.cut(
        age, bins=[0, 25, 40, 55, 100], labels=["young", "adult", "middle", "senior"]
    ).astype(str)
    medical_risk_index = (
        (sti_history * 2)
        + (behavioral_score * 0.8)
        + ((cd4_count < 350).astype(int) * 2)
        + ((age > 50).astype(int) * 0.5)
    )
    risk_score_feat = medical_risk_index + (bmi > 30).astype(int) * 0.5

    # Target: 0=Low, 1=Medium, 2=High
    logit = (
        -2.0
        + sti_history * 1.5
        + behavioral_score * 0.6
        + (cd4_count < 350) * 1.8
        + (cd4_count < 200) * 1.2
        + (age > 55) * 0.4
        + (bmi > 30) * 0.3
    )
    probs = 1 / (1 + np.exp(-logit))
    risk_class = np.where(probs < 0.35, 0, np.where(probs < 0.65, 1, 2))

    return pd.DataFrame(
        {
            "age": age,
            "gender": gender,
            "bmi": bmi.round(1),
            "sti_history": sti_history,
            "cd4_count": cd4_count,
            "behavioral_score": behavioral_score,
            "bmi_category": bmi_category,
            "age_group": age_group,
            "medical_risk_index": medical_risk_index.round(2),
            "risk_score_feat": risk_score_feat.round(2),
            "risk_class": risk_class,
        }
    )


def build_pipeline(X: pd.DataFrame) -> tuple[Pipeline, list[str], list[str]]:
    numeric_features = [
        "age",
        "bmi",
        "sti_history",
        "cd4_count",
        "behavioral_score",
        "medical_risk_index",
        "risk_score_feat",
    ]
    categorical_features = ["gender", "bmi_category", "age_group"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    ensemble = VotingClassifier(
        estimators=[
            ("lr", LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)),
            ("dt", DecisionTreeClassifier(max_depth=8, random_state=RANDOM_STATE)),
            ("rf", RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE)),
            (
                "svm",
                SVC(kernel="rbf", probability=True, random_state=RANDOM_STATE),
            ),
        ],
        voting="soft",
    )

    pipeline = Pipeline([("preprocess", preprocessor), ("classifier", ensemble)])
    return pipeline, numeric_features, categorical_features


def _evaluate_tensorflow_baseline(X_train, y_train, X_test, y_test, feature_cols) -> float | None:
    """Optional TensorFlow MLP baseline (SRS technology stack)."""
    try:
        import tensorflow as tf
        from sklearn.preprocessing import LabelEncoder

        tf.random.set_seed(RANDOM_STATE)
        le = LabelEncoder()
        X = pd.get_dummies(X_train[feature_cols], columns=["gender", "bmi_category", "age_group"])
        X_t = pd.get_dummies(X_test[feature_cols], columns=["gender", "bmi_category", "age_group"])
        X_t = X_t.reindex(columns=X.columns, fill_value=0)
        model = tf.keras.Sequential(
            [
                tf.keras.layers.Input(shape=(X.shape[1],)),
                tf.keras.layers.Dense(64, activation="relu"),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(32, activation="relu"),
                tf.keras.layers.Dense(3, activation="softmax"),
            ]
        )
        model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
        y_enc = le.fit_transform(y_train)
        model.fit(X.values, y_enc, epochs=15, batch_size=64, verbose=0)
        y_pred = np.argmax(model.predict(X_t.values, verbose=0), axis=1)
        return float(accuracy_score(y_test, y_pred))
    except ImportError:
        return None


def main(csv_path: str | None = None) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plots_dir = OUTPUT_DIR / "plots"
    plots_dir.mkdir(exist_ok=True)

    try:
        from data_loader import load_dataset

        df = load_dataset(csv_path)
    except Exception:
        df = generate_synthetic_dataset()
    df = df.drop_duplicates()

    feature_cols = [
        "age",
        "gender",
        "bmi",
        "sti_history",
        "cd4_count",
        "behavioral_score",
        "bmi_category",
        "age_group",
        "medical_risk_index",
        "risk_score_feat",
    ]
    X = df[feature_cols]
    y = df["risk_class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    # SMOTE balancing (SRS Phase 5) — categorical-aware
    cat_cols = ["gender", "bmi_category", "age_group"]
    X_train_enc = X_train.copy()
    cat_maps = {}
    for col in cat_cols:
        cat = pd.Categorical(X_train[col])
        cat_maps[col] = list(cat.categories)
        X_train_enc[col] = cat.codes
    cat_idx = [feature_cols.index(c) for c in cat_cols]
    smote = SMOTENC(categorical_features=cat_idx, random_state=RANDOM_STATE)
    X_res, y_train_bal = smote.fit_resample(X_train_enc, y_train)
    X_train_bal = pd.DataFrame(X_res, columns=feature_cols)
    for col in cat_cols:
        codes = np.round(X_train_bal[col]).astype(int).clip(0, len(cat_maps[col]) - 1)
        X_train_bal[col] = [cat_maps[col][i] for i in codes]

    pipeline, _, _ = build_pipeline(X_train_bal)
    pipeline.fit(X_train_bal, y_train_bal)

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)

    # Multiclass ROC-AUC (ovr)
    try:
        roc_auc = float(roc_auc_score(y_test, y_proba, multi_class="ovr", average="weighted"))
    except ValueError:
        roc_auc = 0.0

    fpr_list, tpr_list = [], []
    for cls in sorted(np.unique(y_test)):
        y_bin = (y_test == cls).astype(int)
        if y_bin.sum() == 0 or y_bin.sum() == len(y_bin):
            continue
        fpr, tpr, _ = roc_curve(y_bin, y_proba[:, cls])
        fpr_list.append(fpr.tolist())
        tpr_list.append(tpr.tolist())

    nn_accuracy = _evaluate_tensorflow_baseline(X_train_bal, y_train_bal, X_test, y_test, feature_cols)

    # Training plots for dashboard / reports
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns

        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Purples")
        plt.title("Confusion Matrix")
        plt.ylabel("Actual")
        plt.xlabel("Predicted")
        plt.tight_layout()
        plt.savefig(plots_dir / "confusion_matrix.png", dpi=120)
        plt.close()

        plt.figure(figsize=(6, 5))
        for i, label in enumerate(["Low", "Medium", "High"]):
            if i < len(fpr_list):
                plt.plot(fpr_list[i], tpr_list[i], label=label)
        plt.plot([0, 1], [0, 1], "k--", alpha=0.4)
        plt.xlabel("FPR")
        plt.ylabel("TPR")
        plt.title("ROC Curves (One-vs-Rest)")
        plt.legend()
        plt.tight_layout()
        plt.savefig(plots_dir / "roc_curves.png", dpi=120)
        plt.close()
    except Exception:
        pass

    background = X_train_bal.sample(min(100, len(X_train_bal)), random_state=RANDOM_STATE)

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, average="weighted", zero_division=0)),
        "f1_score": float(f1_score(y_test, y_pred, average="weighted", zero_division=0)),
        "roc_auc": roc_auc,
        "neural_network_accuracy": nn_accuracy,
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
        "roc_curves": {
            "fpr": fpr_list,
            "tpr": tpr_list,
            "class_names": ["Low Risk", "Medium Risk", "High Risk"],
        },
        "feature_columns": feature_cols,
        "class_labels": {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"},
    }

    joblib.dump(
        {
            "pipeline": pipeline,
            "feature_columns": feature_cols,
            "class_labels": metrics["class_labels"],
            "background": background.to_dict(orient="records"),
        },
        MODEL_PATH,
    )
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Model saved to {MODEL_PATH}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Target 89%+: {'PASS' if metrics['accuracy'] >= 0.89 else 'REVIEW'}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, default=None, help="Path to Kaggle/UCI CSV")
    args = parser.parse_args()
    main(csv_path=args.csv)
