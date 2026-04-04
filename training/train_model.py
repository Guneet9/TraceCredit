import pickle
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from training.preprocess import DataPreprocessor
from training.evaluate import ModelEvaluator


class ModelTrainer:
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.preprocessor = DataPreprocessor()
        self.evaluator = ModelEvaluator()
        self.model = None
        self.scaler = None
        self.feature_names = None

    def train_baseline_model(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> Tuple[LogisticRegression, StandardScaler]:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_train)

        params = {'max_iter': 1000, 'random_state': 42, 'solver': 'lbfgs', 'class_weight': 'balanced'}
        params.update(kwargs)

        model = LogisticRegression(**params)
        model.fit(X_scaled, y_train)

        self.model = model
        self.scaler = scaler
        return model, scaler

    def train_and_save(self, data_path: str, version: str = "v1") -> Dict[str, Any]:
        print(f"Loading data from {data_path}")
        X_train, X_test, y_train, y_test, feature_names = self.preprocessor.prepare_training_data(data_path)
        self.feature_names = feature_names

        print(f"Training Logistic Regression ({version})")
        model, scaler = self.train_baseline_model(X_train, y_train)

        train_metrics = self.evaluator.evaluate(model, X_train[:1000], y_train[:1000], scaler)
        test_metrics = self.evaluator.evaluate(model, X_test, y_test, scaler)

        metrics = {
            'train': train_metrics,
            'test': test_metrics,
            'samples': {'train': len(X_train), 'test': len(X_test)}
        }

        model_path = self._save_model(model, scaler, version, feature_names, metrics)

        print(f"Test Accuracy: {test_metrics['accuracy']:.4f}")
        print(f"Test ROC-AUC: {test_metrics['roc_auc']:.4f}")

        return {
            'version': version,
            'model_path': str(model_path),
            'metrics': metrics,
            'features_used': feature_names,
            'training_date': datetime.utcnow().isoformat(),
            'samples_trained': len(X_train),
            'samples_tested': len(X_test)
        }

    def _save_model(self, model, scaler, version, feature_names, metrics) -> Path:
        version_dir = self.model_dir / version
        version_dir.mkdir(exist_ok=True)

        with open(version_dir / "model.pkl", 'wb') as f:
            pickle.dump(model, f)

        with open(version_dir / "scaler.pkl", 'wb') as f:
            pickle.dump(scaler, f)

        with open(version_dir / "metadata.json", 'w') as f:
            json.dump({
                'version': version,
                'created_at': datetime.utcnow().isoformat(),
                'model_type': 'LogisticRegression',
                'features': feature_names,
                'metrics': metrics,
            }, f, indent=2)

        return version_dir / "model.pkl"

    def load_model(self, version: str) -> Tuple[LogisticRegression, StandardScaler, Dict]:
        version_dir = self.model_dir / version
        with open(version_dir / "model.pkl", 'rb') as f:
            model = pickle.load(f)
        with open(version_dir / "scaler.pkl", 'rb') as f:
            scaler = pickle.load(f)
        with open(version_dir / "metadata.json", 'r') as f:
            metadata = json.load(f)
        return model, scaler, metadata
