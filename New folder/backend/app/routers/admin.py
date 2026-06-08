import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_admin_user
from app.models.activity_log import ActivityLog
from app.models.prediction import Prediction
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    return [UserResponse.model_validate(u) for u in db.query(User).all()]


@router.get("/predictions")
def list_predictions(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    rows = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(500).all()
    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "prediction": r.prediction,
            "risk_score": r.risk_score,
            "confidence_score": r.confidence_score,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.get("/activity")
def system_activity(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    logs = db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(200).all()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "activity": log.activity,
            "details": log.details,
            "timestamp": log.created_at.isoformat(),
        }
        for log in logs
    ]


@router.delete("/predictions/{prediction_id}")
def delete_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    row = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Prediction not found")
    db.delete(row)
    db.add(
        ActivityLog(
            user_id=admin.id,
            activity="admin_delete_prediction",
            details=f"Deleted prediction {prediction_id}",
        )
    )
    db.commit()
    return {"message": "Prediction deleted", "id": prediction_id}


@router.get("/export/predictions")
def export_predictions(db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    rows = db.query(Prediction).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "PredictionID",
            "UserID",
            "Age",
            "Gender",
            "RiskScore",
            "Prediction",
            "Confidence",
            "Timestamp",
        ]
    )
    for r in rows:
        writer.writerow(
            [
                r.id,
                r.user_id,
                r.age,
                r.gender,
                r.risk_score,
                r.prediction,
                r.confidence_score,
                r.created_at.isoformat(),
            ]
        )
    output.seek(0)
    filename = f"hivcare_predictions_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
