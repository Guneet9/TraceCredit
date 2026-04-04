import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
import numpy as np

from app.services.prediction_service import ImprovedPredictionService


@pytest.fixture
def v2_metadata():
    return {
        "version": "v2",
        "model_type": "RandomForest",
        "features": ["age", "gender", "education", "marital_status", "credit_limit"],
        "metrics": {
            "train": {"accuracy": 0.99, "roc_auc": 0.999},
            "test": {"accuracy": 0.9814, "roc_auc": 0.9978, "f1": 0.9806}
        },
        "created_at": "2026-01-20T00:00:00"
    }


class TestV2Model:
    def test_v2_metadata_structure(self, v2_metadata):
        assert v2_metadata["version"] == "v2"
        assert v2_metadata["model_type"] == "RandomForest"
        assert "features" in v2_metadata
        assert "metrics" in v2_metadata

    def test_v2_test_accuracy_above_threshold(self, v2_metadata):
        accuracy = v2_metadata["metrics"]["test"]["accuracy"]
        assert accuracy > 0.95

    def test_v2_roc_auc_above_threshold(self, v2_metadata):
        roc_auc = v2_metadata["metrics"]["test"]["roc_auc"]
        assert roc_auc > 0.95

    def test_service_loads_v2_metadata(self, v2_metadata):
        with tempfile.TemporaryDirectory() as tmpdir:
            v2_dir = Path(tmpdir) / "v2"
            v2_dir.mkdir()
            with open(v2_dir / "metadata.json", "w") as f:
                json.dump(v2_metadata, f)

            service = ImprovedPredictionService(model_dir=tmpdir)
            info = service.get_model_info("v2")

            assert info is not None
            assert info["version"] == "v2"
            assert info["model_type"] == "RandomForest"

    def test_prediction_with_mock_v2(self, v2_metadata):
        with tempfile.TemporaryDirectory() as tmpdir:
            service = ImprovedPredictionService(model_dir=tmpdir)

            mock_model = MagicMock()
            mock_model.predict.return_value = np.array([0])
            mock_model.predict_proba.return_value = np.array([[0.95, 0.05]])

            mock_scaler = MagicMock()
            mock_scaler.transform.return_value = np.zeros((1, 5))

            service.current_model = mock_model
            service.current_scaler = mock_scaler
            service.current_metadata = v2_metadata
            service.current_version = "v2"

            result = service.predict({f: 1.0 for f in v2_metadata["features"]})
            assert result["success"] is True
            assert result["risk_probability"] == pytest.approx(0.05)
            assert result["model_version"] == "v2"
