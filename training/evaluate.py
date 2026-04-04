from typing import Dict, Any
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    roc_auc_score, f1_score, confusion_matrix
)
from sklearn.preprocessing import StandardScaler


class ModelEvaluator:
    def evaluate(self, model, X: np.ndarray, y: np.ndarray, scaler: StandardScaler = None) -> Dict[str, float]:
        if scaler is not None:
            X = scaler.transform(X)

        y_pred = model.predict(X)
        y_proba = model.predict_proba(X)[:, 1]
        tn, fp, fn, tp = confusion_matrix(y, y_pred).ravel()

        return {
            'accuracy': accuracy_score(y, y_pred),
            'precision': precision_score(y, y_pred, zero_division=0),
            'recall': recall_score(y, y_pred, zero_division=0),
            'f1': f1_score(y, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y, y_proba),
            'specificity': tn / (tn + fp) if (tn + fp) > 0 else 0,
            'sensitivity': tp / (tp + fn) if (tp + fn) > 0 else 0,
            'confusion_matrix': {'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp)}
        }

    def compare_models(self, models: Dict[str, Any], X: np.ndarray, y: np.ndarray,
                       scalers: Dict[str, StandardScaler] = None) -> Dict[str, Dict[str, float]]:
        return {
            name: self.evaluate(model, X, y, scalers.get(name) if scalers else None)
            for name, model in models.items()
        }

    def get_best_model(self, results: Dict[str, Dict[str, float]], metric: str = 'roc_auc') -> str:
        return max(results.items(), key=lambda x: x[1].get(metric, 0))[0]

    def print_metrics(self, metrics: Dict[str, float], model_name: str = "") -> None:
        if model_name:
            print(f"\n{'='*50}\nModel: {model_name}\n{'='*50}")
        for key in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc', 'specificity', 'sensitivity']:
            print(f"{key.capitalize():<14} {metrics.get(key, 0):.4f}")
