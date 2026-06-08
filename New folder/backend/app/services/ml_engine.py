from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.config import settings
from app.schemas.prediction import PredictRequest

_model_bundle: dict | None = None
_metrics: dict | None = None

RECOMMENDATIONS = {
    "Low Risk": (
        "Continue preventive awareness: practice safe behaviors, "
        "regular wellness checkups, and stay informed about HIV prevention."
    ),
    "Medium Risk": (
        "Suggested screening: schedule HIV testing and consult a healthcare "
        "provider for personalized screening based on your profile."
    ),
    "High Risk": (
        "Immediate healthcare consultation recommended. Contact a clinic or "
        "healthcare professional promptly for evaluation and support."
    ),
}


def _resolve_path(relative: str) -> Path:
    base = Path(__file__).resolve().parents[2]
    return (base / relative).resolve()


def load_model() -> dict:
    global _model_bundle
    if _model_bundle is None:
        path = _resolve_path(settings.model_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Model not found at {path}. Run: python ml/train.py"
            )
        _model_bundle = joblib.load(path)
    return _model_bundle


def load_metrics() -> dict:
    global _metrics
    if _metrics is None:
        path = _resolve_path(settings.metrics_path)
        if path.exists():
            _metrics = json.loads(path.read_text(encoding="utf-8"))
        else:
            _metrics = {}
    return _metrics


from app.services.features import engineer_features


def predict_risk(data: PredictRequest) -> dict:
    bundle = load_model()
    pipeline = bundle["pipeline"]
    class_labels = bundle["class_labels"]

    X = engineer_features(data)
    proba = pipeline.predict_proba(X)[0]
    pred_idx = int(np.argmax(proba))
    confidence = float(proba[pred_idx])
    risk_level = class_labels.get(pred_idx, class_labels.get(str(pred_idx), "Unknown"))

    explanation = {
        "top_factors": [
            {"feature": "cd4_count", "impact": "lower CD4 increases risk" if data.cd4_count < 350 else "within typical range"},
            {"feature": "sti_history", "impact": "elevated" if data.sti_history else "none reported"},
            {"feature": "behavioral_score", "impact": f"score {data.behavioral_score}/5"},
        ],
        "class_probabilities": {
            class_labels.get(i, str(i)): round(float(p), 4) for i, p in enumerate(proba)
        },
    }
    try:
        from app.services.shap_explainer import compute_shap_explanation

        shap_data = compute_shap_explanation(data)
        if shap_data:
            explanation["shap"] = shap_data
    except Exception:
        pass  # SHAP optional if model/background unavailable

    return {
        "risk_level": risk_level,
        "confidence_score": round(confidence, 4),
        "risk_score": round(float(X["risk_score_feat"].iloc[0]), 2),
        "recommendation": RECOMMENDATIONS.get(risk_level, RECOMMENDATIONS["Medium Risk"]),
        "explanation": explanation,
    }
