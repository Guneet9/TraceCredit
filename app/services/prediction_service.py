import pickle
import json
from pathlib import Path
from typing import Dict, Optional, List
import numpy as np

from app.core.logger import get_logger
from config import settings

logger = get_logger(__name__)


class ImprovedPredictionService:
    def __init__(self, model_dir: str = None):
        self.model_dir = Path(model_dir or settings.model_dir)
        self.current_model = None
        self.current_scaler = None
        self.current_metadata = None
        self.current_version = None
        self._load_active_model()

    def _load_active_model(self) -> bool:
        version = settings.active_model_version
        success = self.load_model(version)
        if not success:
            logger.warning(f"Failed to load model version: {version}")
        return success

    def load_model(self, version: str) -> bool:
        try:
            version_dir = self.model_dir / version
            if not version_dir.exists():
                logger.error(f"Model directory not found: {version_dir}")
                return False

            with open(version_dir / "model.pkl", 'rb') as f:
                self.current_model = pickle.load(f)

            with open(version_dir / "scaler.pkl", 'rb') as f:
                self.current_scaler = pickle.load(f)

            with open(version_dir / "metadata.json", 'r') as f:
                self.current_metadata = json.load(f)

            self.current_version = version
            logger.info(f"Loaded model {version}")
            return True

        except Exception as e:
            logger.error(f"Failed to load model {version}: {e}")
            return False

    def predict(self, features: Dict[str, float]) -> Dict:
        if self.current_model is None:
            return {"success": False, "error": "No model loaded"}

        try:
            feature_names = self.current_metadata.get('features', [])
            X = np.array([[features.get(name, 0.0) for name in feature_names]])
            X_scaled = self.current_scaler.transform(X)

            risk_probability = float(self.current_model.predict_proba(X_scaled)[0, 1])
            prediction = int(self.current_model.predict(X_scaled)[0])

            return {
                "success": True,
                "risk_probability": risk_probability,
                "will_default": prediction == 1,
                "model_version": self.current_version,
                "features_used": feature_names
            }

        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {"success": False, "error": str(e)}

    def get_model_info(self, version: Optional[str] = None) -> Optional[Dict]:
        try:
            v = version or self.current_version
            metadata_path = self.model_dir / v / "metadata.json"
            if not metadata_path.exists():
                return None
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return None

    def list_available_models(self) -> List[Dict]:
        models = []
        if not self.model_dir.exists():
            return models
        for version_dir in sorted(self.model_dir.iterdir()):
            if not version_dir.is_dir():
                continue
            metadata_path = version_dir / "metadata.json"
            if metadata_path.exists():
                try:
                    with open(metadata_path, 'r') as f:
                        models.append(json.load(f))
                except Exception as e:
                    logger.error(f"Error reading metadata from {version_dir}: {e}")
        return models

    def switch_model_version(self, version: str) -> bool:
        return self.load_model(version)


prediction_service = ImprovedPredictionService()
