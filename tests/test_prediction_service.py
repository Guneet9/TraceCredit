import pytest
import json
import pickle
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
import numpy as np

from app.services.prediction_service import ImprovedPredictionService


@pytest.fixture
def temp_model_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_model_dir(temp_model_dir):
    """Create a fake model directory with metadata only (no actual pkl)."""
    path = Path(temp_model_dir)
    v1 = path / "v1"
    v1.mkdir()

    metadata = {
        "version": "v1",
        "model_type": "LogisticRegression",
        "features": ["age", "gender", "education", "credit_limit"],
        "metrics": {
            "train": {"accuracy": 0.75, "roc_auc": 0.80},
            "test": {"accuracy": 0.74, "roc_auc": 0.76}
        },
        "created_at": "2025-12-15T00:00:00"
    }

    with open(v1 / "metadata.json", "w") as f:
        json.dump(metadata, f)

    return temp_model_dir


class TestImprovedPredictionService:
    def test_list_models_empty_dir(self, temp_model_dir):
        service = ImprovedPredictionService(model_dir=temp_model_dir)
        assert service.list_available_models() == []

    def test_load_nonexistent_model_returns_false(self, temp_model_dir):
        service = ImprovedPredictionService(model_dir=temp_model_dir)
        assert service.load_model("v_nonexistent") is False

    def test_get_model_info_nonexistent_returns_none(self, temp_model_dir):
        service = ImprovedPredictionService(model_dir=temp_model_dir)
        assert service.get_model_info("v_nonexistent") is None

    def test_predict_no_model_loaded_returns_error(self, temp_model_dir):
        service = ImprovedPredictionService(model_dir=temp_model_dir)
        service.current_model = None
        result = service.predict({"age": 35.0})
        assert result["success"] is False
        assert "error" in result

    def test_list_models_reads_metadata(self, mock_model_dir):
        service = ImprovedPredictionService(model_dir=mock_model_dir)
        models = service.list_available_models()
        assert len(models) == 1
        assert models[0]["version"] == "v1"

    def test_get_model_info_returns_metadata(self, mock_model_dir):
        service = ImprovedPredictionService(model_dir=mock_model_dir)
        info = service.get_model_info("v1")
        assert info is not None
        assert info["version"] == "v1"
        assert info["model_type"] == "LogisticRegression"

    def test_predict_with_mock_model(self, temp_model_dir):
        service = ImprovedPredictionService(model_dir=temp_model_dir)

        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([0])
        mock_model.predict_proba.return_value = np.array([[0.82, 0.18]])

        mock_scaler = MagicMock()
        mock_scaler.transform.return_value = np.array([[1.0, 2.0, 3.0, 4.0]])

        service.current_model = mock_model
        service.current_scaler = mock_scaler
        service.current_metadata = {"features": ["age", "gender", "education", "credit_limit"]}
        service.current_version = "v1"

        result = service.predict({"age": 35.0, "gender": 2.0, "education": 2.0, "credit_limit": 50000.0})

        assert result["success"] is True
        assert result["risk_probability"] == pytest.approx(0.18)
        assert result["will_default"] is False
        assert result["model_version"] == "v1"
