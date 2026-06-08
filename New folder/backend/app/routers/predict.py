import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.activity_log import ActivityLog
from app.models.prediction import Prediction
from app.models.user import User
from app.schemas.prediction import PredictRequest, PredictResponse, PredictionHistoryItem
from app.services.ml_engine import predict_risk

router = APIRouter(tags=["Prediction"])


@router.post("/predict", response_model=PredictResponse)
def predict(
    payload: PredictRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = predict_risk(payload)
    record = Prediction(
        user_id=current_user.id,
        age=payload.age,
        gender=payload.gender.lower(),
        bmi=payload.bmi,
        sti_history=payload.sti_history,
        cd4_count=payload.cd4_count,
        behavioral_score=payload.behavioral_score,
        risk_score=result["risk_score"],
        prediction=result["risk_level"],
        confidence_score=result["confidence_score"],
        recommendation=result["recommendation"],
        shap_summary=json.dumps(result.get("explanation")),
    )
    db.add(record)
    db.add(
        ActivityLog(
            user_id=current_user.id,
            activity="prediction",
            details=f"Risk: {result['risk_level']}",
        )
    )
    db.commit()
    return PredictResponse(
        risk_level=result["risk_level"],
        confidence_score=result["confidence_score"],
        risk_score=result["risk_score"],
        recommendation=result["recommendation"],
        explanation=result.get("explanation"),
        prediction_id=record.id,
    )


@router.get("/history", response_model=list[PredictionHistoryItem])
def history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .limit(100)
        .all()
    )
    return [PredictionHistoryItem.model_validate(r) for r in rows]
