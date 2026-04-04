"""
predictor.py — legacy model registry used by the v2 API router.

This wraps ImprovedPredictionService from prediction_service.py so both
routers use the same underlying service instance and loaded model.
"""
from app.services.prediction_service import prediction_service, ImprovedPredictionService

__all__ = ["prediction_service", "ImprovedPredictionService"]
