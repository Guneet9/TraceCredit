from typing import Dict, List, Optional
from app.core.logger import get_logger

logger = get_logger(__name__)


def _get_metric(metrics: dict, key: str) -> float:
    """
    Safely extract a metric from the nested metrics dict saved by training.

    Training saves:  {"train": {"accuracy": ...}, "test": {"accuracy": ...}}
    Some older runs save flat: {"test_accuracy": ...}
    """
    if not metrics:
        return 0.0
    # Nested format (current training pipeline)
    test = metrics.get("test", {})
    if test and key in test:
        return float(test[key])
    # Flat format fallback
    flat_key = f"test_{key}"
    if flat_key in metrics:
        return float(metrics[flat_key])
    return 0.0


class ModelComparator:
    def __init__(self):
        pass

    def compare_models(self, version_names: Optional[List[str]] = None) -> Dict:
        from db.database import SessionLocal
        from db.models import ModelVersion

        db = SessionLocal()
        try:
            if version_names:
                models = db.query(ModelVersion).filter(
                    ModelVersion.version_name.in_(version_names)
                ).all()
            else:
                models = db.query(ModelVersion).all()

            if not models:
                return {"error": "No models found"}

            model_data = []
            for m in models:
                metrics = m.metrics or {}
                model_data.append({
                    "version": m.version_name,
                    "is_active": m.is_active,
                    "created_at": m.created_at.isoformat(),
                    "description": m.description,
                    "test_accuracy": _get_metric(metrics, "accuracy"),
                    "test_roc_auc": _get_metric(metrics, "roc_auc"),
                    "test_precision": _get_metric(metrics, "precision"),
                    "test_recall": _get_metric(metrics, "recall"),
                    "test_f1": _get_metric(metrics, "f1"),
                    "train_accuracy": float(metrics.get("train", {}).get("accuracy", 0)),
                })

            model_data_sorted = sorted(model_data, key=lambda x: x["test_accuracy"], reverse=True)

            result = {
                "total_models": len(model_data),
                "best_model": model_data_sorted[0]["version"],
                "rankings": {
                    "by_accuracy": [m["version"] for m in model_data_sorted],
                    "by_roc_auc": max(model_data, key=lambda x: x["test_roc_auc"])["version"],
                    "by_f1": max(model_data, key=lambda x: x["test_f1"])["version"],
                },
                "comparison": model_data_sorted,
            }

            if len(model_data_sorted) > 1:
                best = model_data_sorted[0]
                second = model_data_sorted[1]
                result["improvement_over_second"] = {
                    "accuracy_delta": round(best["test_accuracy"] - second["test_accuracy"], 4),
                    "roc_auc_delta": round(best["test_roc_auc"] - second["test_roc_auc"], 4),
                    "f1_delta": round(best["test_f1"] - second["test_f1"], 4),
                }

            logger.info(f"Model comparison complete: best={result['best_model']}")
            return result

        except Exception as e:
            logger.error(f"Model comparison error: {e}")
            return {"error": str(e)}
        finally:
            db.close()

    def get_comparison_summary(self) -> Dict:
        from db.database import SessionLocal
        from db.models import ModelVersion

        db = SessionLocal()
        try:
            models = db.query(ModelVersion).all()
            if not models:
                return {"error": "No models found"}

            summary = {"total_models": len(models), "active_model": None, "models": []}

            for m in models:
                metrics = m.metrics or {}
                summary["models"].append({
                    "version": m.version_name,
                    "is_active": m.is_active,
                    "accuracy": f"{_get_metric(metrics, 'accuracy'):.2%}",
                    "roc_auc": f"{_get_metric(metrics, 'roc_auc'):.4f}",
                    "f1_score": f"{_get_metric(metrics, 'f1'):.4f}",
                })
                if m.is_active:
                    summary["active_model"] = m.version_name

            return summary

        except Exception as e:
            logger.error(f"Summary error: {e}")
            return {"error": str(e)}
        finally:
            db.close()
