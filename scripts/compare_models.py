"""Script to compare multiple models and select the best one."""

import sys
from training.train_multiple_models import MultiModelTrainer


def main():
    """Run model comparison."""
    print("\n" + "="*70)
    print("TRACECREDIT - MODEL COMPARISON TOOL")
    print("="*70)
    print("\nThis script will train and compare the following models:")
    print("  1. Logistic Regression (baseline)")
    print("  2. Random Forest Classifier (ensemble tree-based)")
    print("  3. XGBoost Classifier (gradient boosting)")
    print("\nBest model will be saved as v2 and ranked by test accuracy.")
    print("="*70 + "\n")
    
    try:
        trainer = MultiModelTrainer()
        
        # Get available models (includes XGBoost if installed)
        available_models = list(trainer.get_available_models().keys())
        
        # Train and compare models
        results = trainer.train_and_compare(
            data_path="data/processed/credit_time_series.csv",
            models_to_train=available_models
        )
        
        # Save best model
        metadata = trainer.save_best_model(version="v2")
        
        # Print summary
        print("\n" + "="*70)
        print("MODEL SELECTION SUMMARY")
        print("="*70)
        print(f"\n✓ Trained {len(available_models)} different models")
        print(f"✓ Best model: {trainer.best_model_name.upper()}")
        print(f"\nPerformance (Test Set):")
        print(f"  Accuracy:  {metadata['metrics']['test_accuracy']:.2%}")
        print(f"  ROC-AUC:   {metadata['metrics']['test_roc_auc']:.4f}")
        print(f"  Precision: {metadata['metrics']['test_precision']:.2%}")
        print(f"  Recall:    {metadata['metrics']['test_recall']:.2%}")
        print(f"  F1 Score:  {metadata['metrics']['test_f1']:.4f}")
        
        # Show improvement over baseline
        baseline_accuracy = 0.7461
        improvement = (metadata['metrics']['test_accuracy'] - baseline_accuracy) * 100
        print(f"\n  Improvement over baseline: +{improvement:.2f} percentage points")
        
        print(f"\nModel saved to: models/v2/")
        print(f"To activate v2, run: python activate_model.py v2")
        print("="*70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error during model comparison:")
        print(f"  {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
