from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from db.database import get_db
from db.models import User, CreditDecision, FeatureSnapshot, ModelVersion, DriftEvent
from app.services.predictor import prediction_service
from app.services.drift import drift_detector, explanation_generator
from app.services.fairness import FairnessAnalyzer, ExplainabilityService
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["credit"])

fairness_analyzer = FairnessAnalyzer()
explainability_service = ExplainabilityService()


@router.post("/predict-limit")
def predict_credit_limit(
    user_id: int,
    age: int,
    gender: int,
    education: int,
    marital_status: int,
    income: float,
    risk_score: float,
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id, age=age, gender=gender, education=education,
                        marital_status=marital_status, income=income, risk_score=risk_score)
            db.add(user)
            db.commit()
            db.refresh(user)

        snapshot = FeatureSnapshot(
            user_id=user_id, month=datetime.utcnow().month,
            age=age, gender=gender, education=education,
            marital_status=marital_status, income=income, risk_score=risk_score
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)

        features = {
            'age': float(age), 'gender': float(gender),
            'education': float(education), 'marital_status': float(marital_status),
            'income': float(income), 'risk_score': float(risk_score)
        }

        result = prediction_service.predict(features)
        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error', 'Prediction failed'))

        risk_probability = result['risk_probability']
        predicted_limit = max(10000, min(100000, income * (1.0 - risk_probability * 0.5)))

        active_model = db.query(ModelVersion).filter(ModelVersion.is_active == True).first()

        previous = db.query(CreditDecision).filter(
            CreditDecision.user_id == user_id
        ).order_by(CreditDecision.created_at.desc()).first()

        previous_limit = previous.predicted_limit if previous else None
        drift_detected, delta, severity = False, 0.0, "none"

        if previous_limit:
            drift_detected, delta, severity = drift_detector.detect_limit_drift(previous_limit, predicted_limit)

        explanation = explanation_generator.generate_decision_explanation(
            {'predicted_limit': predicted_limit, 'features': features}, previous
        )

        decision = CreditDecision(
            user_id=user_id, feature_snapshot_id=snapshot.id,
            model_version_id=active_model.id if active_model else None,
            predicted_limit=predicted_limit, previous_limit=previous_limit,
            drift_detected=drift_detected, delta=delta,
            explanation=result, human_explanation=explanation
        )
        db.add(decision)
        db.commit()

        if drift_detected:
            db.add(DriftEvent(
                month=datetime.utcnow().month, feature_name="credit_limit",
                drift_score=abs(delta), threshold=previous_limit * 0.2 if previous_limit else 0,
                drift_detected=True, severity=severity
            ))
            db.commit()
            logger.warning(f"Drift detected for user {user_id}: {severity}")

        return {
            "success": True, "user_id": user_id,
            "predicted_limit": predicted_limit, "previous_limit": previous_limit,
            "delta": delta, "drift_detected": drift_detected, "drift_severity": severity,
            "decision_id": decision.id, "explanation": explanation,
            "model_version": result.get('model_version')
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/limit-history/{user_id}")
def get_limit_history(user_id: int, limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    decisions = db.query(CreditDecision).filter(
        CreditDecision.user_id == user_id
    ).order_by(CreditDecision.created_at.desc()).limit(limit).all()

    if not decisions:
        raise HTTPException(status_code=404, detail="No decisions found for this user")

    return {
        "success": True, "user_id": user_id, "history_count": len(decisions),
        "history": [{
            "decision_id": d.id,
            "predicted_limit": d.predicted_limit,
            "previous_limit": d.previous_limit,
            "delta": d.delta,
            "drift_detected": d.drift_detected,
            "model_version": d.model_version.version_name if d.model_version else None,
            "created_at": d.created_at.isoformat(),
            "explanation": d.human_explanation
        } for d in decisions]
    }


@router.get("/audit-trail/{decision_id}")
def get_audit_trail(decision_id: int, db: Session = Depends(get_db)):
    decision = db.query(CreditDecision).filter(CreditDecision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    s = decision.feature_snapshot
    return {
        "success": True, "decision_id": decision_id, "user_id": decision.user_id,
        "features": {
            "age": s.age if s else None, "gender": s.gender if s else None,
            "education": s.education if s else None, "marital_status": s.marital_status if s else None,
            "income": s.income if s else None, "risk_score": s.risk_score if s else None,
        },
        "prediction": decision.predicted_limit,
        "drift_detected": decision.drift_detected,
        "delta": decision.delta,
        "model_version": decision.model_version.version_name if decision.model_version else None,
        "explanation": decision.human_explanation,
        "created_at": decision.created_at.isoformat(),
        "full_trace": decision.explanation
    }


@router.get("/drift-events")
def get_drift_events(
    limit: int = Query(20, ge=1, le=100),
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(DriftEvent).order_by(DriftEvent.created_at.desc())
    if severity:
        query = query.filter(DriftEvent.severity == severity)

    events = query.limit(limit).all()
    return {
        "success": True, "event_count": len(events),
        "events": [{
            "event_id": e.id, "feature_name": e.feature_name,
            "drift_score": e.drift_score, "threshold": e.threshold,
            "severity": e.severity, "created_at": e.created_at.isoformat()
        } for e in events]
    }
