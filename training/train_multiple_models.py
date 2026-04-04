"""Advanced model comparison and selection for credit risk prediction."""

import pickle
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    roc_auc_score, f1_score, confusion_matrix
)

from training.preprocess import DataPreprocessor
from training.evaluate import ModelEvaluator


class MultiModelTrainer:
    """Trains and compares multiple machine learning models."""

    def __init__(self, model_dir: str = "models"):
        """
        Initialize multi-model trainer.
        
        Args:
            model_dir: Directory to save trained models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.preprocessor = DataPreprocessor()
        self.evaluator = ModelEvaluator()
        self.results = {}
        self.best_model = None
        self.best_model_name = None

    def get_available_models(self) -> Dict[str, callable]:
        """
        Get dictionary of available model factories.
        
        Returns:
            Dict mapping model names to model instantiation functions
        """
        models = {
            'logistic_regression': lambda: LogisticRegression(
                max_iter=1000,
                random_state=42,
                solver='lbfgs',
                class_weight='balanced'
            ),
            'random_forest': lambda: RandomForestClassifier(
                n_estimators=150,
                max_depth=25,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'
            ),
        }
        
        # Try to add XGBoost if available
        try:
            import xgboost as xgb
            models['xgboost'] = lambda: xgb.XGBClassifier(
                n_estimators=150,
                max_depth=5,
                learning_rate=0.05,
                random_state=42,
                scale_pos_weight=3,
                n_jobs=-1,
                verbosity=0
            )
        except ImportError:
            pass
        
        return models

    def train_model(
        self,
        model_name: str,
        X_train: np.ndarray,
        y_train: np.ndarray,
        scaler: StandardScaler = None
    ) -> Tuple[Any, StandardScaler]:
        """
        Train a single model.
        
        Args:
            model_name: Name of model to train
            X_train: Training features
            y_train: Training labels
            scaler: Existing scaler or None to create new
            
        Returns:
            Tuple of (trained_model, fitted_scaler)
        """
        # Create or use scaler
        if scaler is None:
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
        else:
            X_train_scaled = scaler.transform(X_train)
        
        # Get model factory
        models = self.get_available_models()
        if model_name not in models:
            raise ValueError(f"Unknown model: {model_name}")
        
        # Create and train model
        print(f"  Training {model_name}...", end=" ", flush=True)
        model = models[model_name]()
        model.fit(X_train_scaled, y_train)
        print("✓")
        
        return model, scaler

    def evaluate_model(
        self,
        model: Any,
        X_test: np.ndarray,
        y_test: np.ndarray,
        scaler: StandardScaler,
        set_name: str = "test"
    ) -> Dict[str, float]:
        """
        Evaluate a trained model.
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels
            scaler: Fitted scaler
            set_name: Name of dataset (e.g., "test", "train")
            
        Returns:
            Dictionary with evaluation metrics
        """
        X_test_scaled = scaler.transform(X_test)
        y_pred = model.predict(X_test_scaled)
        
        # Get probability predictions for ROC-AUC
        if hasattr(model, 'predict_proba'):
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        else:
            # Some sklearn models might not have predict_proba
            y_pred_proba = model.decision_function(X_test_scaled)
            # Normalize to [0, 1]
            y_pred_proba = (y_pred_proba - y_pred_proba.min()) / \
                          (y_pred_proba.max() - y_pred_proba.min() + 1e-8)
        
        metrics = {
            f'{set_name}_accuracy': accuracy_score(y_test, y_pred),
            f'{set_name}_precision': precision_score(y_test, y_pred, zero_division=0),
            f'{set_name}_recall': recall_score(y_test, y_pred, zero_division=0),
            f'{set_name}_f1': f1_score(y_test, y_pred, zero_division=0),
            f'{set_name}_roc_auc': roc_auc_score(y_test, y_pred_proba),
        }
        
        return metrics

    def train_and_compare(
        self,
        data_path: str,
        models_to_train: List[str] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Train all models and compare performance.
        
        Args:
            data_path: Path to training data
            models_to_train: List of model names to train (None = train all)
            
        Returns:
            Dictionary with results for each model
        """
        print(f"\n{'='*70}")
        print(f"MULTI-MODEL TRAINING & COMPARISON")
        print(f"{'='*70}\n")
        
        # Load data
        print("Loading and preprocessing data...")
        X_train, X_test, y_train, y_test, feature_names = \
            self.preprocessor.prepare_training_data(data_path)
        
        print(f"  Training samples: {len(X_train):,}")
        print(f"  Test samples: {len(X_test):,}")
        print(f"  Features: {len(feature_names)}")
        print(f"  Default rate: {y_train.mean():.2%}\n")
        
        # Get models to train
        available = self.get_available_models()
        if models_to_train is None:
            models_to_train = list(available.keys())
        
        # Train and evaluate each model
        results = {}
        for model_name in models_to_train:
            print(f"Training {model_name}:")
            
            # Train model
            model, scaler = self.train_model(model_name, X_train, y_train)
            
            # Evaluate on train and test
            train_metrics = self.evaluate_model(model, X_train, y_train, scaler, "train")
            test_metrics = self.evaluate_model(model, X_test, y_test, scaler, "test")
            
            # Combine metrics
            all_metrics = {**train_metrics, **test_metrics}
            results[model_name] = all_metrics
            
            # Print results
            print(f"    Train Accuracy: {train_metrics['train_accuracy']:.2%}")
            print(f"    Test Accuracy:  {test_metrics['test_accuracy']:.2%}")
            print(f"    Test ROC-AUC:   {test_metrics['test_roc_auc']:.4f}")
            print(f"    Test F1:        {test_metrics['test_f1']:.4f}\n")
            
            self.results[model_name] = {
                'model': model,
                'scaler': scaler,
                'metrics': all_metrics,
                'feature_names': feature_names
            }
        
        # Find and print best model
        print(f"{'='*70}")
        print("COMPARISON SUMMARY")
        print(f"{'='*70}\n")
        
        # Create comparison table
        comparison_df = pd.DataFrame({
            model: metrics
            for model, metrics in results.items()
        }).T
        
        # Sort by test accuracy
        comparison_df = comparison_df.sort_values('test_accuracy', ascending=False)
        print(comparison_df[['test_accuracy', 'test_roc_auc', 'test_f1', 'test_precision', 'test_recall']].to_string())
        
        # Identify best model
        best_model = comparison_df.index[0]
        best_accuracy = comparison_df.loc[best_model, 'test_accuracy']
        
        print(f"\n{'='*70}")
        print(f"🏆 BEST MODEL: {best_model}")
        print(f"   Test Accuracy: {best_accuracy:.2%}")
        print(f"{'='*70}\n")
        
        self.best_model_name = best_model
        
        return results

    def save_best_model(
        self,
        version: str = "v2"
    ) -> Dict[str, Any]:
        """
        Save the best trained model to disk.
        
        Args:
            version: Model version identifier
            
        Returns:
            Dictionary with save metadata
        """
        if self.best_model_name is None:
            raise ValueError("No model trained yet. Run train_and_compare first.")
        
        best_result = self.results[self.best_model_name]
        model = best_result['model']
        scaler = best_result['scaler']
        metrics = best_result['metrics']
        feature_names = best_result['feature_names']
        
        # Create version directory
        version_dir = self.model_dir / version
        version_dir.mkdir(exist_ok=True)
        
        # Save model
        model_path = version_dir / "model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Save scaler
        scaler_path = version_dir / "scaler.pkl"
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
        
        # Save metadata
        metadata = {
            'version': version,
            'model_type': self.best_model_name,
            'created_at': datetime.now().isoformat(),
            'metrics': {
                'train_accuracy': float(metrics['train_accuracy']),
                'test_accuracy': float(metrics['test_accuracy']),
                'test_precision': float(metrics['test_precision']),
                'test_recall': float(metrics['test_recall']),
                'test_roc_auc': float(metrics['test_roc_auc']),
                'test_f1': float(metrics['test_f1']),
            },
            'features': feature_names,
            'feature_count': len(feature_names),
        }
        
        metadata_path = version_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Model saved to {version_dir}/")
        print(f"  - model.pkl")
        print(f"  - scaler.pkl")
        print(f"  - metadata.json")
        
        return metadata


def main():
    """Run model comparison and training."""
    trainer = MultiModelTrainer()
    
    # Train and compare all available models
    results = trainer.train_and_compare(
        data_path="data/processed/credit_time_series.csv",
        models_to_train=None  # Train all available models
    )
    
    # Save the best model as v2
    metadata = trainer.save_best_model(version="v2")
    
    print(f"\n✓ Training complete!")
    print(f"  Best model: {trainer.best_model_name}")
    print(f"  Accuracy: {metadata['metrics']['test_accuracy']:.2%}")
    print(f"  ROC-AUC: {metadata['metrics']['test_roc_auc']:.4f}")


if __name__ == "__main__":
    main()
