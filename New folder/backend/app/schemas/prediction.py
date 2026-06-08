from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    age: int = Field(ge=1, le=120)
    gender: str
    bmi: float = Field(ge=10, le=60)
    cd4_count: int = Field(ge=0, le=2000)
    sti_history: int = Field(ge=0, le=1)
    behavioral_score: int = Field(default=0, ge=0, le=5)


class PredictResponse(BaseModel):
    risk_level: str
    confidence_score: float
    risk_score: float
    recommendation: str
    explanation: dict[str, Any] | None = None
    prediction_id: int | None = None


class PredictionHistoryItem(BaseModel):
    id: int
    age: int
    gender: str
    risk_score: float
    prediction: str
    confidence_score: float
    recommendation: str
    created_at: datetime

    model_config = {"from_attributes": True}
