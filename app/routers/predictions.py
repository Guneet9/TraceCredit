"""API router for credit prediction endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from db.database import get_db
from db.models import User, CreditDecision, FeatureSnapshot, ModelVersion, DriftEvent
from app.schemas.prediction import (
    UserCreate, UserResponse, PredictionRequest, PredictionResponse, ErrorResponse
)
from app.services.prediction_service import prediction_service
from app.services.credit_service import CreditService
from app.services.drift_service import DriftDetectionService
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["predictions"])

# Initialize services
credit_service = CreditService()
drift_service = DriftDetectionService()


@router.post("/predict", response_model=PredictionResponse)
def predict_credit_limit(
    request: PredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Predict credit limit and default risk for a user.
    
    Receives user financial data, generates ML prediction, applies business rules,
    and stores decision in database.
    """
    try:
        # Step 1: Get or create user
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            user = User(
                id=request.user_id,
                age=request.age,
                gender=request.gender,
                education=request.education,
                marital_status=request.marital_status,
                income=None
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user {request.user_id}")
        
        # Step 2: Create feature snapshot
        feature_snapshot = FeatureSnapshot(
            user_id=request.user_id,
            month=datetime.utcnow().month,
            age=request.age,
            gender=request.gender,
            education=request.education,
            marital_status=request.marital_status,
            income=None,
            risk_score=None,
            bill_amount=request.bill_amt_m1,
            payment_amount=request.pay_amt_m1
        )
        db.add(feature_snapshot)
        db.commit()
        db.refresh(feature_snapshot)
        
        # Step 3: Prepare features for ML model
        features = {
            'age': float(request.age),
            'gender': float(request.gender),
            'education': float(request.education),
            'marital_status': float(request.marital_status),
            'pay_status_m1': float(request.pay_status_m1),
            'pay_status_m2': float(request.pay_status_m2),
            'pay_status_m3': float(request.pay_status_m3),
            'pay_status_m4': float(request.pay_status_m4),
            'pay_status_m5': float(request.pay_status_m5),
            'pay_status_m6': float(request.pay_status_m6),
            'bill_amt_m1': float(request.bill_amt_m1),
            'bill_amt_m2': float(request.bill_amt_m2),
            'bill_amt_m3': float(request.bill_amt_m3),
            'bill_amt_m4': float(request.bill_amt_m4),
            'bill_amt_m5': float(request.bill_amt_m5),
            'bill_amt_m6': float(request.bill_amt_m6),
            'pay_amt_m1': float(request.pay_amt_m1),
            'pay_amt_m2': float(request.pay_amt_m2),
            'pay_amt_m3': float(request.pay_amt_m3),
            'pay_amt_m4': float(request.pay_amt_m4),
            'pay_amt_m5': float(request.pay_amt_m5),
            'pay_amt_m6': float(request.pay_amt_m6),
            'credit_limit': float(request.current_credit_limit),
        }
        
        # Add engineered features
        bill_values = [request.bill_amt_m1, request.bill_amt_m2, request.bill_amt_m3,
                       request.bill_amt_m4, request.bill_amt_m5, request.bill_amt_m6]
        pay_values = [request.pay_amt_m1, request.pay_amt_m2, request.pay_amt_m3,
                      request.pay_amt_m4, request.pay_amt_m5, request.pay_amt_m6]
        
        avg_bill = sum(bill_values) / len(bill_values) if bill_values else 0
        avg_pay = sum(pay_values) / len(pay_values) if pay_values else 0
        max_bill = max(bill_values) if bill_values else 0
        
        features['avg_bill_6m'] = avg_bill
        features['avg_pay_6m'] = avg_pay
        features['max_bill_6m'] = max_bill
        features['utilization_ratio'] = max_bill / (request.current_credit_limit + 1)
        features['payment_to_bill_ratio'] = avg_pay / (avg_bill + 1)
        
        pay_status_values = [request.pay_status_m1, request.pay_status_m2, 
                            request.pay_status_m3, request.pay_status_m4,
                            request.pay_status_m5, request.pay_status_m6]
        default_count = sum(1 for s in pay_status_values if s < 0)
        features['default_status_count'] = float(default_count)
        
        # Step 4: Get ML prediction
        pred_result = prediction_service.predict(features)
        
        if not pred_result['success']:
            logger.error(f"Prediction failed: {pred_result.get('error')}")
            raise HTTPException(status_code=500, detail="Model prediction failed")
        
        risk_probability = pred_result['risk_probability']
        
        # Step 5: Apply business logic
        recommended_limit = credit_service.calculate_recommended_limit(
            risk_probability=risk_probability,
            current_limit=request.current_credit_limit,
            utilization_ratio=features['utilization_ratio']
        )
        
        # Apply hardship rules if needed
        if default_count > 0:
            recommended_limit = credit_service.apply_hardship_rules(
                recommended_limit, default_count
            )
        
        # Step 6: Store decision in database
        model_version = db.query(ModelVersion).filter(
            ModelVersion.is_active == True
        ).first()
        
        credit_decision = CreditDecision(
            user_id=request.user_id,
            feature_snapshot_id=feature_snapshot.id,
            model_version_id=model_version.id if model_version else None,
            predicted_limit=recommended_limit,
            previous_limit=request.current_credit_limit,
            explanation={
                "risk_probability": risk_probability,
                "utilization_ratio": features['utilization_ratio'],
                "default_history": default_count
            }
        )
        
        db.add(credit_decision)
        db.commit()
        db.refresh(credit_decision)
        
        logger.info(
            f"Prediction made for user {request.user_id}: "
            f"risk={risk_probability:.2%}, limit={recommended_limit:.0f}"
        )
        
        # Step 7: Return response
        return PredictionResponse(
            risk_probability=risk_probability,
            recommended_limit=recommended_limit,
            model_version=prediction_service.current_version or "v1",
            prediction_made_at=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/models")
def list_models(db: Session = Depends(get_db)):
    """Get all registered models and their metrics."""
    try:
        models = db.query(ModelVersion).all()
        
        return {
            "success": True,
            "total_models": len(models),
            "models": [
                {
                    "id": m.id,
                    "version": m.version_name,
                    "description": m.description,
                    "is_active": m.is_active,
                    "metrics": m.metrics,
                    "features_count": len(m.features) if m.features else 0,
                    "created_at": m.created_at.isoformat(),
                    "updated_at": m.updated_at.isoformat()
                }
                for m in sorted(models, key=lambda x: x.created_at, reverse=True)
            ]
        }
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve models")


@router.get("/models/{version}")
def get_model_details(version: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific model version."""
    try:
        model = db.query(ModelVersion).filter(
            ModelVersion.version_name == version
        ).first()
        
        if not model:
            raise HTTPException(status_code=404, detail=f"Model {version} not found")
        
        return {
            "success": True,
            "model": {
                "version": model.version_name,
                "description": model.description,
                "is_active": model.is_active,
                "metrics": model.metrics,
                "features": model.features,
                "model_path": model.model_path,
                "created_at": model.created_at.isoformat(),
                "updated_at": model.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model details: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve model")


@router.post("/models/{version}/activate")
def activate_model(version: str, db: Session = Depends(get_db)):
    """Activate a specific model version."""
    try:
        # Deactivate current active model
        current_active = db.query(ModelVersion).filter(
            ModelVersion.is_active == True
        ).first()
        
        if current_active:
            current_active.is_active = False
        
        # Activate new model
        model = db.query(ModelVersion).filter(
            ModelVersion.version_name == version
        ).first()
        
        if not model:
            raise HTTPException(status_code=404, detail=f"Model {version} not found")
        
        model.is_active = True
        db.commit()
        
        # Reload model in service
        prediction_service.switch_model_version(version)
        
        logger.info(f"Activated model version {version}")
        
        return {
            "success": True,
            "message": f"Model {version} is now active",
            "model": {
                "version": model.version_name,
                "is_active": model.is_active
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating model: {e}")
        raise HTTPException(status_code=500, detail="Failed to activate model")


@router.get("/models/compare", response_model=dict)
def compare_models(db: Session = Depends(get_db)):
    try:
        from app.services.model_comparator import ModelComparator

        available = prediction_service.list_available_models()
        if len(available) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 models to compare")

        version_names = [m.get("version") for m in available if m.get("version")]
        comparator = ModelComparator()
        comparison = comparator.compare_models(version_names)

        return {
            "status": "success",
            "comparison_date": datetime.now().isoformat(),
            "models_compared": len(version_names),
            "comparison": comparison
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing models: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare models")
