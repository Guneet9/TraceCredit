"""
startup.py — run this before launching the API on a fresh deploy.

It initialises the database tables and registers the trained model in the
model_versions table so the API can find an active model on startup.

Usage:
    python startup.py
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from db.database import engine, SessionLocal
from db.models import Base, ModelVersion
from app.core.logger import get_logger

logger = get_logger("startup")

MODEL_DIR = Path("models")


def init_db():
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables ready")


def register_models():
    db = SessionLocal()
    try:
        version_dirs = [d for d in sorted(MODEL_DIR.iterdir()) if d.is_dir() and (d / "metadata.json").exists()]

        if not version_dirs:
            logger.error(f"No model directories found in {MODEL_DIR}/. Run training first.")
            return False

        for version_dir in version_dirs:
            version_name = version_dir.name
            metadata_path = version_dir / "metadata.json"

            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            existing = db.query(ModelVersion).filter(ModelVersion.version_name == version_name).first()
            if existing:
                logger.info(f"Model {version_name} already registered, skipping")
                continue

            model_version = ModelVersion(
                version_name=version_name,
                description=metadata.get('description', f"{metadata.get('model_type', 'Model')} — {version_name}"),
                metrics=metadata.get('metrics', {}),
                model_path=str(version_dir / "model.pkl"),
                features=metadata.get('features', []),
                is_active=False
            )
            db.add(model_version)
            db.commit()
            logger.info(f"Registered model {version_name}")

        # Set the latest version as active if none is active
        active = db.query(ModelVersion).filter(ModelVersion.is_active == True).first()
        if not active:
            latest = db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).first()
            if latest:
                latest.is_active = True
                db.commit()
                logger.info(f"Set {latest.version_name} as active model")

        return True

    except Exception as e:
        logger.error(f"Model registration failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("=== TraceCredit startup ===")

    init_db()
    success = register_models()

    if not success:
        logger.error("Startup failed — check that models/ directory contains trained model files")
        logger.error("Run: python training/run_training.py")
        sys.exit(1)

    logger.info("=== Startup complete — ready to serve ===")
