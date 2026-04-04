#!/usr/bin/env python
"""Drift monitoring script for continuous model/data drift detection."""

import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

sys.path.insert(0, 'c:\\Users\\Dell\\Documents\\TraceCredit')

from app.services.drift_service import DriftDetectionService
from db.database import SessionLocal
from db.models import DriftEvent
from app.core.logger import get_logger

logger = get_logger(__name__)


def monitor_drift(baseline_month: int = 1, current_month: int = None):
    """
    Monitor feature drift between baseline and current data.
    
    Args:
        baseline_month: Month to use as baseline (default: month 1)
        current_month: Month to compare against (default: last month in data)
    """
    
    print("=" * 70)
    print("TraceCredit Drift Detection Monitor")
    print("=" * 70)
    
    try:
        # Load data
        data_path = "data/processed/credit_time_series.csv"
        df = pd.read_csv(data_path)
        
        print(f"\nLoaded data with {len(df)} records and {len(df.columns)} columns")
        print(f"Available months: {sorted(df['month'].unique())}")
        
        # Determine months to compare
        available_months = sorted(df['month'].unique())
        if current_month is None:
            current_month = available_months[-1] if len(available_months) > 1 else available_months[0]
        
        print(f"\nBaseline month: {baseline_month}")
        print(f"Current month: {current_month}")
        
        # Split data by month
        baseline_df = df[df['month'] == baseline_month].drop('month', axis=1)
        current_df = df[df['month'] == current_month].drop('month', axis=1)
        
        print(f"\nBaseline data: {len(baseline_df)} records")
        print(f"Current data: {len(current_df)} records")
        
        # Initialize drift detector
        drift_service = DriftDetectionService(threshold_percentage=20.0)
        
        # Key features to monitor
        monitored_features = [
            'credit_limit',
            'pay_status_m1',
            'bill_amt_m1',
            'pay_amt_m1',
            'age',
            'bill_amt_m2',
            'pay_amt_m2'
        ]
        
        # Detect drift
        print("\n" + "=" * 70)
        print("Drift Detection Results")
        print("=" * 70)
        
        drift_results = drift_service.detect_batch_drift(
            baseline_df, current_df,
            features=monitored_features
        )
        
        # Process results
        db = SessionLocal()
        drift_alerts = []
        
        try:
            for result in drift_results:
                feature_name = result['feature_name']
                drift_detected = result['drift_detected']
                severity = result['severity']
                psi_score = result['psi_score']
                mean_diff = result['mean_difference_pct']
                
                status = "⚠️ DRIFT" if drift_detected else "✓ OK"
                print(f"\n{feature_name:20} | {status:15} | PSI: {psi_score:.4f} | Mean Δ: {mean_diff:.2f}%")
                
                if drift_detected:
                    # Store in database
                    drift_event = DriftEvent(
                        month=current_month,
                        feature_name=feature_name,
                        drift_score=psi_score,
                        threshold=0.1,
                        drift_detected=True,
                        severity=severity,
                        created_at=datetime.utcnow()
                    )
                    db.add(drift_event)
                    drift_alerts.append({
                        'feature': feature_name,
                        'severity': severity,
                        'psi_score': psi_score
                    })
            
            if drift_alerts:
                db.commit()
                print(f"\n✓ Stored {len(drift_alerts)} drift events in database")
            
        finally:
            db.close()
        
        # Summary
        print("\n" + "=" * 70)
        total_features = len(drift_results)
        drifted_count = sum(1 for r in drift_results if r['drift_detected'])
        
        print(f"Summary: {drifted_count}/{total_features} features show drift")
        
        if drift_alerts:
            print("\nDrift Alerts:")
            for alert in drift_alerts:
                print(f"  - {alert['feature']}: {alert['severity']} (PSI: {alert['psi_score']:.4f})")
        else:
            print("\n✓ No significant drift detected!")
        
        return len(drift_alerts) == 0
        
    except Exception as e:
        print(f"\n✗ Error during drift monitoring: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = monitor_drift()
    sys.exit(0 if success else 1)
