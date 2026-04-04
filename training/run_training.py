#!/usr/bin/env python
"""Main script to train and register credit risk model."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from training.train_model import ModelTrainer
from db.database import SessionLocal
from db.models import ModelVersion
from datetime import datetime
import json

def main():
    """Train model and register in database."""
    
    print("=" * 70)
    print("TraceCredit Model Training Pipeline")
    print("=" * 70)
    
    # Step 1: Train model
    trainer = ModelTrainer(model_dir="models")
    
    try:
        results = trainer.train_and_save(
            data_path="data/processed/credit_time_series.csv",
            version="v1"
        )
        
        print("\n" + "=" * 70)
        print("Training Results:")
        print("=" * 70)
        print(f"Model Version: {results['version']}")
        print(f"Training Date: {results['training_date']}")
        print(f"Model Path: {results['model_path']}")
        print(f"\nMetrics:")
        print(f"  Train Accuracy: {results['metrics']['train']['accuracy']:.4f}")
        print(f"  Test Accuracy: {results['metrics']['test']['accuracy']:.4f}")
        print(f"  Test Precision: {results['metrics']['test']['precision']:.4f}")
        print(f"  Test Recall: {results['metrics']['test']['recall']:.4f}")
        print(f"  Test ROC-AUC: {results['metrics']['test']['roc_auc']:.4f}")
        print(f"\nFeatures Used: {len(results['features_used'])} features")
        print("=" * 70)
        
        # Step 2: Register model in database
        db = SessionLocal()
        try:
            # Check if version already exists
            existing = db.query(ModelVersion).filter(
                ModelVersion.version_name == results['version']
            ).first()
            
            if existing:
                print(f"\nModel version {results['version']} already exists. Skipping DB registration.")
                db.close()
                return
            
            # Create model version entry
            model_version = ModelVersion(
                version_name=results['version'],
                description="Logistic Regression baseline model for credit risk",
                metrics=results['metrics'],
                model_path=results['model_path'],
                features=results['features_used'],
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.add(model_version)
            db.commit()
            db.refresh(model_version)
            
            print(f"\n✓ Model version {results['version']} registered in database (ID: {model_version.id})")
            print(f"✓ Set as active model: {model_version.is_active}")
            
        finally:
            db.close()
        
        print("\n✓ Training and registration complete!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error during training: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
