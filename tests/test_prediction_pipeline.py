import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import numpy as np

from app.services.prediction_service import ImprovedPredictionService
from app.services.credit_service import CreditService
from app.services.drift import DriftDetector


@pytest.fixture
def service_with_mock_model():
    with tempfile.TemporaryDirectory() as tmpdir:
        service = ImprovedPredictionService(model_dir=tmpdir)

        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([0])
        mock_model.predict_proba.return_value = np.array([[0.75, 0.25]])

        mock_scaler = MagicMock()
        mock_scaler.transform.return_value = np.zeros((1, 4))

        service.current_model = mock_model
        service.current_scaler = mock_scaler
        service.current_metadata = {"features": ["age", "gender", "education", "credit_limit"]}
        service.current_version = "v1"

        yield service


class TestPredictionPipeline:
    def test_predict_returns_risk_probability(self, service_with_mock_model):
        features = {"age": 35.0, "gender": 2.0, "education": 2.0, "credit_limit": 50000.0}
        result = service_with_mock_model.predict(features)
        assert result["success"] is True
        assert 0.0 <= result["risk_probability"] <= 1.0

    def test_predict_missing_features_uses_zero(self, service_with_mock_model):
        result = service_with_mock_model.predict({})
        assert result["success"] is True

    def test_credit_limit_calculated_from_risk(self):
        service = CreditService()
        low_risk_limit = service.calculate_recommended_limit(0.1, 50000, 0.5)
        high_risk_limit = service.calculate_recommended_limit(0.9, 50000, 0.5)
        assert low_risk_limit > high_risk_limit

    def test_drift_detection_in_pipeline(self):
        detector = DriftDetector()
        drifted, delta, severity = detector.detect_limit_drift(40000, 55000)
        assert drifted is True
        assert delta == 15000

    def test_full_pipeline_no_model_returns_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            service = ImprovedPredictionService(model_dir=tmpdir)
            result = service.predict({"age": 35.0})
            assert result["success"] is False

    def test_switch_to_nonexistent_version_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            service = ImprovedPredictionService(model_dir=tmpdir)
            success = service.switch_model_version("v999")
            assert success is False
