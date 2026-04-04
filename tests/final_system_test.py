import pytest
import numpy as np
from unittest.mock import MagicMock

from app.services.prediction_service import ImprovedPredictionService
from app.services.drift_service import DriftDetectionService
from app.services.fairness import FairnessAnalyzer
from app.services.credit_service import CreditService
from app.services.monitoring import AlertManager


class TestSystemIntegration:
    def test_prediction_to_drift_pipeline(self):
        credit = CreditService()
        detector = DriftDetectionService()

        risk_prob = 0.2
        current_limit = 50000.0
        new_limit = credit.calculate_recommended_limit(risk_prob, current_limit, 0.4)

        baseline = np.random.normal(50000, 5000, 500)
        current = np.array([new_limit] * 100)
        result = detector.detect_feature_drift("credit_limit", baseline, current)

        assert "drift_detected" in result
        assert "severity" in result

    def test_alert_manager_creates_and_resolves(self):
        manager = AlertManager()
        alert = manager.create_drift_alert(
            user_id=1, severity="high",
            delta=10000, previous_limit=50000, new_limit=60000
        )
        assert alert["type"] == "drift"
        assert alert["resolved"] is False

        resolved = manager.resolve_alert(alert["alert_id"], "reviewed and accepted")
        assert resolved is True
        assert len(manager.get_active_alerts()) == 0

    def test_fairness_analyzer_detects_gap(self):
        import pandas as pd
        analyzer = FairnessAnalyzer()

        df = pd.DataFrame({
            "income": [30000] * 50 + [100000] * 50,
            "predicted_limit": [15000] * 50 + [80000] * 50
        })

        df = analyzer.create_income_brackets(df)
        metrics = analyzer.compute_cohort_metrics(df, "income_bracket")
        violations = analyzer.detect_fairness_violations(metrics)

        assert len(violations) > 0
        assert any(v["type"] == "avg_limit_gap" for v in violations)

    def test_health_endpoint_integration(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_full_monitoring_summary(self):
        manager = AlertManager()
        manager.create_drift_alert(1, "medium", 5000, 50000, 55000)
        manager.create_fairness_alert("income_low", "income_high", "avg_limit", 18000, 2000)

        summary = manager.get_alert_summary()
        assert summary["total_active"] == 2
        assert summary["by_type"]["drift"] == 1
        assert summary["by_type"]["fairness"] == 1
