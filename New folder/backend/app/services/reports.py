"""PDF report generation for predictions (SRS Report Generation)."""
from __future__ import annotations

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.prediction import Prediction
from app.models.user import User


def build_prediction_pdf(prediction: Prediction, user: User) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>HIVCare AI — Risk Assessment Report</b>", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 16))
    story.append(Paragraph("<b>Patient / User</b>", styles["Heading2"]))
    story.append(Paragraph(f"Name: {user.name}<br/>Email: {user.email}", styles["Normal"]))
    story.append(Spacer(1, 12))

    rows = [
        ["Field", "Value"],
        ["Age", str(prediction.age)],
        ["Gender", prediction.gender],
        ["BMI", str(prediction.bmi)],
        ["CD4 Count", str(prediction.cd4_count)],
        ["STI History", "Yes" if prediction.sti_history else "No"],
        ["Behavioral Score", str(prediction.behavioral_score)],
        ["Risk Category", prediction.prediction],
        ["Risk Score", str(prediction.risk_score)],
        ["Confidence", f"{prediction.confidence_score * 100:.1f}%"],
        ["Assessment Date", prediction.created_at.strftime("%Y-%m-%d %H:%M")],
    ]
    table = Table(rows, colWidths=[180, 300])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7c3aed")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 16))
    story.append(Paragraph("<b>Recommendation</b>", styles["Heading2"]))
    story.append(Paragraph(prediction.recommendation.replace("\n", "<br/>"), styles["Normal"]))
    story.append(Spacer(1, 20))
    story.append(
        Paragraph(
            "<i>Disclaimer: This report supports healthcare awareness only and is not "
            "a substitute for professional medical diagnosis.</i>",
            styles["Italic"],
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
