"""
Monthly batch credit limit evaluation job.

This simulates real bank processing by:
1. Loading all users and their current features
2. Running predictions for each user
3. Detecting drift
4. Checking fairness metrics
5. Storing results and alerts
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import DATABASE_URL
from db.models import Base, User, CreditDecision, FeatureSnapshot, ModelVersion, DriftEvent, FairnessMetric
from app.services.prediction_service import prediction_service
from app.services.drift import drift_detector
from app.services.fairness import FairnessAnalyzer, ExplainabilityService
from app.core.logger import get_logger

logger = get_logger(__name__)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

DATA_PATH = Path("data/processed/baseline_credit_limit.csv")


def run_monthly_evaluation():
    """Execute monthly batch evaluation."""
    
    logger.info("=" * 60)
    logger.info("Starting monthly batch credit evaluation")
    logger.info("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Load data
        logger.info("Loading baseline dataset...")
        df = pd.read_csv(DATA_PATH)
        
        # Get active model
        active_model = db.query(ModelVersion).filter(
            ModelVersion.is_active == True
        ).first()
        
        if not active_model:
            logger.error("No active model found")
            return
        
        logger.info(f"Using model: {active_model.version_name}")
        
        # Process each user
        evaluation_results = []
        drift_events = []
        
        for idx, row in df.iterrows():
            user_id = int(row['ID']) if 'ID' in row.index else idx
            
            try:
                # Get or create user
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    user = User(
                        id=user_id,
                        age=int(row.get('age', 25)),
                        gender=int(row.get('gender', 1)),
                        education=int(row.get('education', 1)),
                        marital_status=int(row.get('marital_status', 1)),
                        income=float(row.get('income', 50000)),
                        risk_score=float(row.get('risk_score', 5))
                    )
                    db.add(user)
                    db.commit()
                
                # Create feature snapshot
                feature_snapshot = FeatureSnapshot(
                    user_id=user_id,
                    month=datetime.utcnow().month,
                    age=int(row.get('age', 25)),
                    gender=int(row.get('gender', 1)),
                    education=int(row.get('education', 1)),
                    marital_status=int(row.get('marital_status', 1)),
                    income=float(row.get('income', 50000)),
                    risk_score=float(row.get('risk_score', 5)),
                    bill_amount=float(row.get('credit_limit', 0)) * np.random.uniform(0.1, 0.5),
                    payment_amount=float(row.get('credit_limit', 0)) * np.random.uniform(0.05, 0.3)
                )
                db.add(feature_snapshot)
                db.commit()
                
                # Make prediction
                features = {
                    'age': float(row.get('age', 25)),
                    'gender': float(row.get('gender', 1)),
                    'education': float(row.get('education', 1)),
                    'marital_status': float(row.get('marital_status', 1)),
                    'income': float(row.get('income', 50000)),
                    'risk_score': float(row.get('risk_score', 5))
                }
                
                result = prediction_service.predict(features)

                if not result['success']:
                    logger.warning(f"Prediction failed for user {user_id}: {result.get('error')}")
                    continue

                risk_probability = result['risk_probability']
                predicted_limit = max(10000, min(100000, features['income'] * (1.0 - risk_probability * 0.5)))
                
                # Get previous decision
                previous_decision = db.query(CreditDecision).filter(
                    CreditDecision.user_id == user_id
                ).order_by(CreditDecision.created_at.desc()).first()
                
                previous_limit = previous_decision.predicted_limit if previous_decision else None
                
                # Detect drift
                drift_detected = False
                delta = 0
                severity = "none"
                
                if previous_limit:
                    drift_detected, delta, severity = drift_detector.detect_limit_drift(
                        previous_limit,
                        predicted_limit
                    )
                
                # Store decision
                credit_decision = CreditDecision(
                    user_id=user_id,
                    feature_snapshot_id=feature_snapshot.id,
                    model_version_id=active_model.id,
                    predicted_limit=predicted_limit,
                    previous_limit=previous_limit,
                    drift_detected=drift_detected,
                    delta=delta,
                    explanation=result
                )
                db.add(credit_decision)
                db.commit()
                
                # Log drift event
                if drift_detected:
                    drift_event = DriftEvent(
                        month=datetime.utcnow().month,
                        feature_name="credit_limit",
                        drift_score=abs(delta),
                        threshold=previous_limit * 0.2 if previous_limit else 0,
                        drift_detected=True,
                        severity=severity
                    )
                    db.add(drift_event)
                    drift_events.append({
                        'user_id': user_id,
                        'severity': severity,
                        'delta': delta
                    })
                
                evaluation_results.append({
                    'user_id': user_id,
                    'predicted_limit': predicted_limit,
                    'drift_detected': drift_detected
                })
                
                if (idx + 1) % 100 == 0:
                    logger.info(f"Processed {idx + 1} users...")
                
            except Exception as e:
                logger.error(f"Error processing user {user_id}: {e}")
                continue
        
        db.commit()
        
        # Commit drift events
        if drift_events:
            logger.warning(f"Total drift events: {len(drift_events)}")
            for event in drift_events[:5]:
                logger.warning(f"  User {event['user_id']}: {event['severity']} drift (Δ={event['delta']:.2f})")
        
        # Compute fairness metrics
        logger.info("Computing fairness metrics...")
        compute_fairness_metrics(db, df)
        
        logger.info("=" * 60)
        logger.info(f"Batch evaluation complete. Processed {len(evaluation_results)} users.")
        logger.info(f"Drift events detected: {len(drift_events)}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Batch evaluation failed: {e}")
        raise
    finally:
        db.close()


def compute_fairness_metrics(db, df):
    """Compute and store fairness metrics."""
    try:
        analyzer = FairnessAnalyzer()
        
        # Create brackets
        df_analysis = analyzer.create_income_brackets(df)
        df_analysis = analyzer.create_age_brackets(df_analysis)
        
        # Compute metrics for income brackets
        income_metrics = analyzer.compute_cohort_metrics(df_analysis, 'income_bracket')
        
        for cohort_name, metrics in income_metrics.items():
            fairness_metric = FairnessMetric(
                cohort_name=f"income_{cohort_name}",
                metric_name="avg_limit",
                value=metrics['avg_limit'],
                threshold=80000.0
            )
            db.add(fairness_metric)
        
        # Detect violations
        violations = analyzer.detect_fairness_violations(income_metrics)
        
        if violations:
            logger.warning(f"Fairness violations detected: {len(violations)}")
            for v in violations[:3]:
                logger.warning(f"  {v['type']}: {v['cohort1']} vs {v['cohort2']} (gap={v['gap']:.2f})")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Fairness metrics computation failed: {e}")


if __name__ == "__main__":
    run_monthly_evaluation()
