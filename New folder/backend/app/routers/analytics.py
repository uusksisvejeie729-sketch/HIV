from collections import Counter
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.prediction import Prediction
from app.models.user import User
from app.services.ml_engine import load_metrics

router = APIRouter(tags=["Analytics"])


@router.get("/analytics")
def analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    metrics = load_metrics()
    base_query = db.query(Prediction)
    if current_user.role != "admin":
        base_query = base_query.filter(Prediction.user_id == current_user.id)

    predictions = base_query.all()
    distribution = Counter(p.prediction for p in predictions)

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    trends = (
        db.query(
            func.date(Prediction.created_at).label("day"),
            func.count(Prediction.id).label("count"),
        )
        .filter(Prediction.created_at >= thirty_days_ago)
        .group_by(func.date(Prediction.created_at))
        .order_by(func.date(Prediction.created_at))
        .all()
    )

    user_stats = {
        "total_predictions": len(predictions),
        "user_id": current_user.id,
    }
    if current_user.role == "admin":
        user_stats["total_users"] = db.query(func.count(User.id)).scalar()

    return {
        "prediction_distribution": dict(distribution),
        "user_statistics": user_stats,
        "risk_trends": [{"date": str(t.day), "count": t.count} for t in trends],
        "model_metrics": {
            "accuracy": metrics.get("accuracy"),
            "precision": metrics.get("precision"),
            "recall": metrics.get("recall"),
            "f1_score": metrics.get("f1_score"),
            "roc_auc": metrics.get("roc_auc"),
            "neural_network_accuracy": metrics.get("neural_network_accuracy"),
        },
        "charts": {
            "confusion_matrix": metrics.get("confusion_matrix"),
            "roc_curves": metrics.get("roc_curves"),
        },
    }
