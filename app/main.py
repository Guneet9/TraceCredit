from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import inspect
import pandas as pd
import time

from db.database import get_db, SessionLocal, engine
from db.models import Base
from app.routers.predictions import router as predictions_router
from app.api.predictions import router as predictions_v2_router
from app.services.monitoring import alert_manager
from app.core.logger import get_logger
from config import settings

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.time()
        method = request.method
        path = request.url.path
        client = request.client.host if request.client else "unknown"

        try:
            response = await call_next(request)
            duration = time.time() - start
            msg = f"{method} {path} | {client} | {response.status_code} | {duration:.3f}s"

            if response.status_code >= 500:
                logger.error(msg)
            elif response.status_code >= 400:
                logger.warning(msg)
            else:
                logger.info(msg)

            return response
        except Exception as e:
            logger.error(f"{method} {path} | {client} | ERROR: {e} | {time.time() - start:.3f}s")
            raise


app = FastAPI(
    title="TraceCredit API",
    version="2.0.0",
    description="Transparent Credit Limit Drift Monitoring System",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

Base.metadata.create_all(bind=engine)

logger.info(f"TraceCredit starting — env={settings.environment}, model={settings.active_model_version}")

app.include_router(predictions_router)
app.include_router(predictions_v2_router)


@app.get("/")
def root():
    return {
        "message": "TraceCredit API",
        "version": "2.0.0",
        "environment": settings.environment,
        "docs": "/docs"
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        tables = inspect(engine).get_table_names()
        return {
            "status": "healthy",
            "database": "connected",
            "tables": len(tables),
            "timestamp": str(pd.Timestamp.utcnow()),
            "environment": settings.environment
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(status_code=503, content={"status": "unhealthy", "error": str(e)})


@app.get("/api/alerts")
def get_alerts(alert_type: str = None):
    try:
        return {
            "success": True,
            "summary": alert_manager.get_alert_summary(),
            "alerts": alert_manager.get_active_alerts(alert_type)
        }
    except Exception as e:
        logger.error(f"Error retrieving alerts: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@app.on_event("startup")
def startup_event():
    logger.info("TraceCredit API ready")


@app.on_event("shutdown")
def shutdown_event():
    logger.info("TraceCredit API shutting down")
    SessionLocal.close_all()
