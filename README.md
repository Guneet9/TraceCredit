# TraceCredit

Transparent credit limit drift monitoring system. Predicts default risk from 6 months of payment history, recommends credit limits, and monitors model drift and fairness over time.

## Project structure

```
tracecredit/
  app/              FastAPI application
  db/               SQLAlchemy models and database session
  training/         Model training pipeline
  scripts/          Utility scripts
  jobs/             Monthly batch job
  tests/            Test suite
  frontend/         React + Vite UI
  startup.py        DB init + model registration (run before first start)
  config.py         App settings
  requirements.txt  Python dependencies
```

## Tech stack

**Backend:** FastAPI, SQLAlchemy, scikit-learn, SHAP, scipy, pandas, numpy  
**Frontend:** React 18, Vite

---

## Local development

### Backend

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train the model (requires data/processed/credit_time_series.csv)
python training/run_training.py

# 3. Initialise DB and register model
python startup.py

# 4. Start API
uvicorn app.main:app --reload
# API runs at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# UI runs at http://localhost:5173
```

The Vite dev server proxies `/api/*` to `http://localhost:8000` so the frontend talks to your local API automatically.

---

## Deploying to Render (backend)

### Step 1 — Push to GitHub

Make sure `models/v1/` (model.pkl, scaler.pkl, metadata.json) is committed.  
Check that `.gitignore` does not exclude `*.pkl`.

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/YOUR_USERNAME/tracecredit.git
git push -u origin main
```

### Step 2 — Create Web Service on Render

1. Go to render.com → New → Web Service
2. Connect your GitHub repo
3. Fill in:
   - **Environment:** Python
   - **Build command:** `pip install -r requirements.txt && python startup.py`
   - **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance type:** Free
4. Click Create Web Service

### Step 3 — Verify backend

Once deployed, visit:
- `https://your-app.onrender.com/health` → `{"status": "healthy"}`
- `https://your-app.onrender.com/docs` → Swagger UI

---

## Deploying frontend to Netlify (free)

### Step 1 — Point frontend at your Render URL

Open `frontend/src/App.jsx`, find this line near the top:

```js
const API_BASE = "https://your-app.onrender.com";
```

Replace with your actual Render URL.

### Step 2 — Build the frontend

```bash
cd frontend
npm install
npm run build
# Creates frontend/dist/
```

### Step 3 — Deploy to Netlify

**Option A — Drag and drop (easiest)**
1. Go to netlify.com → sign up
2. Drag the `frontend/dist/` folder into the deploy area
3. Done — Netlify gives you a live URL instantly

**Option B — Via GitHub**
1. Push the repo to GitHub (already done)
2. Netlify → New site → Import from GitHub
3. Set:
   - **Base directory:** `frontend`
   - **Build command:** `npm run build`
   - **Publish directory:** `frontend/dist`
4. Deploy

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| GET | /docs | Swagger UI |
| POST | /api/predict | Predict risk and recommended credit limit |
| GET | /api/models | List all model versions |
| GET | /api/models/{version} | Model details and metrics |
| POST | /api/models/{version}/activate | Switch active model |
| GET | /api/models/compare | Compare v1 vs v2 |
| GET | /api/drift-events | Recent drift events |
| GET | /api/alerts | Active monitoring alerts |
| GET | /api/limit-history/{user_id} | Credit limit history for a user |
| GET | /api/audit-trail/{decision_id} | Full audit trail for a decision |
