import sys
import json
from pathlib import Path
from db.database import SessionLocal
from db.models import ModelVersion


def activate_model(version: str) -> bool:
    model_path = Path("models") / version / "metadata.json"
    if not model_path.exists():
        print(f"Model {version} not found at {model_path}")
        return False

    with open(model_path, 'r') as f:
        metadata = json.load(f)

    db = SessionLocal()
    try:
        db.query(ModelVersion).update({'is_active': False})

        model = db.query(ModelVersion).filter(ModelVersion.version_name == version).first()
        if not model:
            print(f"Model {version} not found in database. Run startup.py first.")
            return False

        model.is_active = True
        db.commit()

        metrics = metadata.get('metrics', {})
        test_metrics = metrics.get('test', metrics)
        accuracy = test_metrics.get('accuracy', metrics.get('test_accuracy', 0))
        roc_auc = test_metrics.get('roc_auc', metrics.get('test_roc_auc', 0))

        print(f"Activated model {version}")
        print(f"  Type:     {metadata.get('model_type', 'unknown')}")
        print(f"  Accuracy: {accuracy:.2%}")
        print(f"  ROC-AUC:  {roc_auc:.4f}")
        return True

    except Exception as e:
        print(f"Error activating model: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python activate_model.py <version>")
        print("Example: python activate_model.py v2")
        sys.exit(1)

    success = activate_model(sys.argv[1])
    sys.exit(0 if success else 1)
