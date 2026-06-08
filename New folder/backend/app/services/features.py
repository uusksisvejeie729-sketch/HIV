import pandas as pd

from app.schemas.prediction import PredictRequest


def engineer_features(data: PredictRequest) -> pd.DataFrame:
    bmi = data.bmi
    if bmi < 18.5:
        bmi_category = "underweight"
    elif bmi < 25:
        bmi_category = "normal"
    elif bmi < 30:
        bmi_category = "overweight"
    else:
        bmi_category = "obese"

    if data.age <= 25:
        age_group = "young"
    elif data.age <= 40:
        age_group = "adult"
    elif data.age <= 55:
        age_group = "middle"
    else:
        age_group = "senior"

    medical_risk_index = (
        data.sti_history * 2
        + data.behavioral_score * 0.8
        + (1 if data.cd4_count < 350 else 0) * 2
        + (0.5 if data.age > 50 else 0)
    )
    risk_score_feat = medical_risk_index + (0.5 if bmi > 30 else 0)

    return pd.DataFrame(
        [
            {
                "age": data.age,
                "gender": data.gender.lower(),
                "bmi": bmi,
                "sti_history": data.sti_history,
                "cd4_count": data.cd4_count,
                "behavioral_score": data.behavioral_score,
                "bmi_category": bmi_category,
                "age_group": age_group,
                "medical_risk_index": round(medical_risk_index, 2),
                "risk_score_feat": round(risk_score_feat, 2),
            }
        ]
    )
