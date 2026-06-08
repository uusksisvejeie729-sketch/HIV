from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.prediction import Prediction
from app.models.user import User
from app.services.reports import build_prediction_pdf

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/prediction/{prediction_id}")
def download_prediction_report(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    if prediction.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    user = db.query(User).filter(User.id == prediction.user_id).first()
    pdf_bytes = build_prediction_pdf(prediction, user)
    filename = f"hivcare_report_{prediction_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
