# TraceCredit

TraceCredit is a credit limit monitoring system built for fintech compliance use cases. It wraps a credit default risk model with drift detection, fairness analysis, and a complete audit trail — addressing the real problem that automated credit systems degrade silently and may treat demographic groups unequally without anyone noticing.

**Live demo:** [melodious-pavlova-f399ed.netlify.app](https://melodious-pavlova-f399ed.netlify.app)  
**API:** [tracecredit.onrender.com/docs](https://tracecredit.onrender.com/docs)

---

## Problem

Automated credit limit systems in production face three compounding issues:

1. **Model drift** — feature distributions shift over time. A model trained on 2023 data may silently degrade by 2025 because the applicant pool looks different.
2. **Fairness risk** — approval rates or credit limits may diverge across income, age, or demographic cohorts without triggering any explicit alert.
3. **Auditability gap** — regulators and compliance teams need to answer "why did this person receive this limit" for any historical decision. Most systems cannot.

TraceCredit addresses all three.

---

## How it works

### Credit decisions

Each prediction request contains 6 months of payment history (pay status, bill amounts, payment amounts), demographic information, and the current credit limit. The system computes six engineered features on top of the raw inputs:

- `avg_bill_6m` — average bill amount over 6 months
- `avg_pay_6m` — average payment amount over 6 months
- `max_bill_6m` — peak bill amount
- `default_status_count` — number of months with delayed payment
- `utilization_ratio` — peak bill as a fraction of credit limit
- `payment_to_bill_ratio` — average payment relative to average bill

These features are scaled using a `StandardScaler` fitted on training data and passed to a Logistic Regression model (v1) that outputs a default risk probability between 0 and 1. The recommended credit limit is then derived using business rules applied to the current limit and the risk score. Every decision — inputs, outputs, model version, timestamp — is written to the database.

### Drift detection

The system uses three independent statistical methods. Any one of them triggering is sufficient to flag drift:

**KS test (Kolmogorov-Smirnov)** — compares the cumulative distribution functions of the baseline and current feature values. A p-value below 0.05 indicates the distributions are statistically different.

**PSI (Population Stability Index)** — bins the baseline distribution, computes the same bins on current data, and measures the divergence using `sum((current% - baseline%) * log(current% / baseline%))`. PSI above 0.1 is considered significant drift.

**Mean difference** — if the current mean deviates from the baseline mean by more than 20%, drift is flagged regardless of the distributional tests.

This three-method approach catches different failure modes: KS is sensitive to shape changes, PSI to bin-level shifts, and mean difference to simple location shifts that might not move the CDF enough to trigger KS.

### Fairness monitoring

The system groups decisions into income brackets (low / medium / high / very_high) and age brackets (20-30, 30-40, etc.) using `pd.cut`. For each pair of cohorts, it computes the average and median credit limit. If the gap between any two cohorts exceeds $2,000 (average) or $1,500 (median), a fairness violation is recorded.

This is different from the 80% disparate impact rule (EEOC) which measures approval rates. The cohort gap approach is more appropriate here because the output is a continuous credit limit rather than a binary approval.

### Model versioning

Two model versions are registered in the database. v1 is Logistic Regression (74.6% accuracy, 0.755 ROC-AUC). v2 is Random Forest with 150 estimators (98.1% accuracy, 0.998 ROC-AUC). Models can be switched live via the API without redeploying the application. The active model is tracked per-decision in the audit trail.

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI 0.109, Uvicorn |
| ORM | SQLAlchemy 2.0, Alembic |
| Database | SQLite (dev), PostgreSQL (prod) |
| ML | scikit-learn — LogisticRegression, RandomForest, StandardScaler |
| Statistics | scipy — ks_2samp for KS test |
| Explainability | SHAP — TreeExplainer |
| Data | pandas, numpy |
| Validation | Pydantic v2 |
| Frontend | React 18, Vite |
| Testing | pytest, FastAPI TestClient |

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check with DB connectivity |
| POST | /api/predict | Predict default risk and recommended credit limit |
| GET | /api/models | List all registered model versions |
| GET | /api/models/{version} | Model details and metrics |
| POST | /api/models/{version}/activate | Switch the active model version |
| GET | /api/models/compare | Side-by-side metric comparison across versions |
| GET | /api/drift-events | Recent drift events with severity |
| GET | /api/alerts | Active monitoring alerts |
| GET | /api/limit-history/{user_id} | Full credit limit history for a user |
| GET | /api/audit-trail/{decision_id} | Complete feature snapshot and decision trace |
| GET | /api/v2/predict-limit | Alternative prediction endpoint (income + risk score input) |
| GET | /api/v2/drift-events | Drift events via v2 router |

---

## Database schema

Six tables capture the full system state:

- **users** — applicant profile (age, gender, education, marital status, income)
- **feature_snapshots** — every feature vector submitted, timestamped, linked to user
- **credit_decisions** — prediction output, previous limit, drift flag, delta, SHAP explanation, linked to feature snapshot and model version
- **model_versions** — registered models with metrics, feature list, active flag
- **drift_events** — per-feature drift detections with score, threshold, severity
- **fairness_metrics** — cohort-level metric comparisons with violation flag

All relationships are defined with SQLAlchemy ORM `relationship()` and `back_populates`. The audit trail endpoint traverses user → feature_snapshot → credit_decision → model_version in a single query.

---

## Project structure

```
app/
  main.py              FastAPI app, CORS, request logging middleware
  routers/             Primary API routes (/api/*)
  api/                 V2 routes (/api/v2/*)
  services/
    prediction_service.py   Model loading and inference
    credit_service.py        Business rules and limit calculation
    drift_service.py         Three-method drift detection
    drift.py                 Per-user limit drift detection
    fairness.py              Cohort fairness analysis and SHAP explainability
    monitoring.py            In-memory alert management
    model_comparator.py      Cross-version metric comparison
    rbac.py                  Role definitions and permission checks
  schemas/             Pydantic request and response models
  core/                Logger configuration
db/
  models.py            SQLAlchemy ORM table definitions
  database.py          Engine, session factory, get_db dependency
training/
  preprocess.py        Feature engineering and train/test split
  train_model.py       Logistic Regression training pipeline
  train_random_forest.py    Random Forest training pipeline
  evaluate.py          Metrics computation and model comparison
  run_training.py      Main training entrypoint
jobs/
  run_monthly_evaluation.py    Batch drift and fairness evaluation
scripts/
  activate_model.py    Switch active model version
  drift_monitor.py     Standalone drift detection script
  compare_models.py    Ad-hoc model comparison
tests/
  conftest.py          TestClient setup with in-memory SQLite
  test_api_endpoints.py
  test_prediction_service.py
  test_drift_service.py
  test_credit_service.py
  test_drift_advanced.py
  test_prediction_pipeline.py
  test_v2_model.py
  final_system_test.py
frontend/
  src/App.jsx          Single-page React UI
startup.py             DB initialisation and model registration
```

---

## Running locally

```bash
pip install -r requirements.txt
python training/run_training.py   # requires data/processed/credit_time_series.csv
python startup.py
uvicorn app.main:app --reload
```

```bash
cd frontend && npm install && npm run dev
```

---

## Disclaimer

This project uses a public credit card default dataset as a behavioural proxy. No real customer or financial institution data is used.