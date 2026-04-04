"""Simple script to train Random Forest model as v2."""

import sys
import pickle
import json
from datetime import datetime
from pathlib import Path
from training.preprocess import DataPreprocessor
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, f1_score


def main():
    """Train and save Random Forest model as v2."""
    print("\n" + "="*70)
    print("TRAINING RANDOM FOREST MODEL (v2)")
    print("="*70 + "\n")
    
    # Load data
    print("Loading data...")
    preprocessor = DataPreprocessor()
    X_train, X_test, y_train, y_test, feature_names = \
        preprocessor.prepare_training_data("data/processed/credit_time_series.csv")
    
    print(f"  Training samples: {len(X_train):,}")
    print(f"  Test samples: {len(X_test):,}")
    print(f"  Features: {len(feature_names)}\n")
    
    # Scale features
    print("Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest
    print("\nTraining Random Forest (150 estimators)...")
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=25,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced',
        verbose=1
    )
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    print("\nEvaluating model...")
    X_test_pred = model.predict(X_test_scaled)
    X_test_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    metrics = {
        'test_accuracy': float(accuracy_score(y_test, X_test_pred)),
        'test_precision': float(precision_score(y_test, X_test_pred, zero_division=0)),
        'test_recall': float(recall_score(y_test, X_test_pred, zero_division=0)),
        'test_roc_auc': float(roc_auc_score(y_test, X_test_pred_proba)),
        'test_f1': float(f1_score(y_test, X_test_pred, zero_division=0)),
    }
    
    # Train evaluation
    X_train_pred = model.predict(X_train_scaled)
    metrics['train_accuracy'] = float(accuracy_score(y_train, X_train_pred))
    
    print(f"\n  Train Accuracy: {metrics['train_accuracy']:.2%}")
    print(f"  Test Accuracy:  {metrics['test_accuracy']:.2%}")
    print(f"  Test ROC-AUC:   {metrics['test_roc_auc']:.4f}")
    print(f"  Test F1 Score:  {metrics['test_f1']:.4f}")
    
    # Save model
    print("\nSaving model as v2...")
    version_dir = Path("models") / "v2"
    version_dir.mkdir(parents=True, exist_ok=True)
    
    # Save model
    with open(version_dir / "model.pkl", 'wb') as f:
        pickle.dump(model, f)
    
    # Save scaler
    with open(version_dir / "scaler.pkl", 'wb') as f:
        pickle.dump(scaler, f)
    
    # Save metadata
    metadata = {
        'version': 'v2',
        'model_type': 'random_forest',
        'created_at': datetime.now().isoformat(),
        'metrics': metrics,
        'features': feature_names,
        'feature_count': len(feature_names),
        'description': 'Random Forest with 150 estimators - significantly improved over Logistic Regression'
    }
    
    with open(version_dir / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nModel saved to: {version_dir}/")
    print(f"  - model.pkl")
    print(f"  - scaler.pkl")
    print(f"  - metadata.json")
    
    # Print summary
    print("\n" + "="*70)
    print("MODEL COMPARISON SUMMARY")
    print("="*70)
    print(f"\nLogistic Regression (v1): 74.61% accuracy")
    print(f"Random Forest (v2):       {metrics['test_accuracy']:.2%} accuracy")
    improvement = (metrics['test_accuracy'] - 0.7461) * 100
    print(f"\nImprovement:              +{improvement:.2f} percentage points")
    print(f"ROC-AUC Score:            {metrics['test_roc_auc']:.4f}")
    print("\n" + "="*70)
    print("To activate v2, run: python activate_model.py v2")
    print("="*70 + "\n")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
