# HIVCare AI

**Intelligent HIV/AIDS Risk Prediction and Support System Using Machine Learning**

Version 1.0 · Muhammad Umair (F24607102) · NUTECH — Department of Artificial Intelligence

> **Disclaimer:** This system supports healthcare awareness and decision-making. It is **not** a substitute for professional medical diagnosis.

---

## Architecture

```
React Frontend (Vite + Tailwind + Chart.js)
        ↓
FastAPI Backend (JWT, SQLAlchemy)
        ↓
Ensemble ML Model (model.pkl)
        ↓
PostgreSQL / SQLite
```

---

## Quick Start (Local)

### 1. Train the ML model

```powershell
cd ml
pip install -r requirements.txt
python train.py
```

Artifacts: `ml/artifacts/model.pkl`, `ml/artifacts/metrics.json`

Replace synthetic data with Kaggle/UCI CSV by adapting `train.py` `main()` to load your dataset.

### 2. Run the backend

```powershell
cd backend
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

**Default admin:** `admin@hivcare.ai` / `Admin@12345`

### 3. Run the frontend

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open http://localhost:5173

---

## API Endpoints (SRS §9)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register (name, email, password) |
| POST | `/auth/login` | Login → JWT |
| POST | `/auth/logout` | Logout |
| POST | `/auth/reset-password/request` | Password reset token |
| POST | `/predict` | HIV risk assessment |
| GET | `/history` | User prediction history |
| GET | `/analytics` | Dashboard metrics & charts |
| GET | `/admin/users` | Admin: list users |
| GET | `/admin/export/predictions` | Admin: CSV export |

---

## Functional Requirements Coverage

| ID | Feature | Status |
|----|---------|--------|
| FR-1 | User Registration | ✅ |
| FR-2 | JWT Login / Logout / Reset | ✅ |
| FR-3 | HIV Risk Assessment | ✅ |
| FR-4 | Recommendation Engine | ✅ |
| FR-5 | Prediction History | ✅ |
| FR-6 | Analytics Dashboard | ✅ |
| FR-7 | Admin Panel | ✅ |
| SHAP | Model explainability | ✅ |
| Reports | PDF report download | ✅ |
| §11 | API tests (pytest) | ✅ |
| §10 | Colab notebook | ✅ `ml/HIVCare_AI_Training.ipynb` |
| §9 | `/register`, `/login` aliases | ✅ |

---

## Additional Features

- **SHAP** feature importance on results page
- **PDF reports** — `GET /reports/prediction/{id}`
- **ROC curve** chart on analytics dashboard
- **Admin** delete predictions, CSV export
- **Kaggle/UCI CSV** — place file in `ml/data/hiv_dataset.csv`, run `python train.py --csv data/hiv_dataset.csv`
- **TensorFlow** optional MLP baseline (install tensorflow, retrain)
- **Docker** — `docker compose up` from project root
- **Alembic** — `cd backend && alembic upgrade head` (after initial `alembic revision --autogenerate`)

### Run tests

```powershell
cd backend
python -m pytest tests/ -v
```

---

## Deployment (SRS §10)

| Component | Platform |
|-----------|----------|
| Frontend | Vercel — set `VITE_API_URL` |
| Backend | Render — set `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS` |
| Database | Supabase PostgreSQL |

Copy `model.pkl` into the backend deploy bundle or mount from object storage.

---

## Project Structure

```
├── ml/                 # Training pipeline & artifacts
├── backend/            # FastAPI application
├── frontend/           # React SPA
└── README.md
```

---

## License & Ethics

Use responsibly. Validate models on real clinical datasets before any production healthcare use.
