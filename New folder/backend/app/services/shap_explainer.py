"""SHAP-based model explainability (SRS §5 / Future SHAP)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import shap

from app.schemas.prediction import PredictRequest
from app.services.features import engineer_features
from app.services.ml_engine import load_model


def compute_shap_explanation(data: PredictRequest) -> dict | None:
    bundle = load_model()
    background = bundle.get("background")
    if background is None or len(background) == 0:
        return None

    pipeline = bundle["pipeline"]
    X = engineer_features(data)
    preprocess = pipeline.named_steps["preprocess"]
    classifier = pipeline.named_steps["classifier"]

    bg_df = pd.DataFrame(background)
    bg_trans = preprocess.transform(bg_df)
    X_trans = preprocess.transform(X)

    try:
        feature_names = list(preprocess.get_feature_names_out())
    except Exception:
        feature_names = [f"feature_{i}" for i in range(X_trans.shape[1])]

    explainer = shap.Explainer(
        classifier.predict_proba,
        bg_trans,
        feature_names=feature_names,
    )
    shap_values = explainer(X_trans)
    proba = classifier.predict_proba(X_trans)[0]
    pred_idx = int(np.argmax(proba))

    values = shap_values.values
    if values.ndim == 3:
        row_shap = values[0, :, pred_idx]
    else:
        row_shap = values[0]

    pairs = sorted(zip(feature_names, row_shap), key=lambda x: abs(float(x[1])), reverse=True)[:12]
    return {
        "predicted_class_index": pred_idx,
        "feature_importance": [
            {"feature": str(name), "shap_value": round(float(val), 5)}
            for name, val in pairs
        ],
    }
