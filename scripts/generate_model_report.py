"""Generate automated model update and improvement reports."""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import sys
import pandas as pd
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.logger import get_logger
from app.services.prediction_service import ImprovedPredictionService
from app.services.model_comparator import ModelComparator

logger = get_logger(__name__)


class ModelReportGenerator:
    """Generate comprehensive model update reports."""
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize report generator.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.predictor = ImprovedPredictionService()
        self.comparator = ModelComparator()
    
    def generate_model_comparison_report(self) -> Dict:
        """Generate comprehensive model comparison report."""
        try:
            available_versions_list = self.predictor.list_available_models()
            available_versions = [m["version"] for m in available_versions_list]
            
            if len(available_versions) < 1:
                logger.warning("No models available for reporting")
                return {}
            
            report = {
                "generated_at": datetime.now().isoformat(),
                "report_type": "Model Comparison",
                "total_models": len(available_versions),
                "models": []
            }
            
            # Get metrics for each model
            for version in available_versions:
                try:
                    model_info = self.predictor.get_model_info(version)
                    if model_info:
                        report["models"].append({
                            "version": version,
                            "type": model_info.get("model_type", "unknown"),
                            "accuracy": model_info.get("metrics", {}).get("accuracy", 0),
                            "roc_auc": model_info.get("metrics", {}).get("roc_auc", 0),
                            "f1_score": model_info.get("metrics", {}).get("f1_score", 0),
                            "precision": model_info.get("metrics", {}).get("precision", 0),
                            "recall": model_info.get("metrics", {}).get("recall", 0),
                            "trained_at": model_info.get("trained_at", "unknown")
                        })
                except Exception as e:
                    logger.warning(f"Error getting info for model {version}: {e}")
                    continue
            
            # Add comparison summary if multiple models
            if len(report["models"]) >= 2:
                # Sort by accuracy descending
                sorted_models = sorted(
                    report["models"],
                    key=lambda x: x.get("accuracy", 0),
                    reverse=True
                )
                
                best_model = sorted_models[0]
                second_best = sorted_models[1] if len(sorted_models) > 1 else None
                
                report["summary"] = {
                    "best_model": best_model["version"],
                    "best_accuracy": best_model["accuracy"],
                    "improvement_over_second": (
                        best_model["accuracy"] - second_best["accuracy"]
                        if second_best else 0
                    ) if second_best else 0,
                    "active_model": self.predictor.current_version,
                    "recommendation": self._get_recommendation(best_model, sorted_models)
                }
            
            return report
        
        except Exception as e:
            logger.error(f"Error generating model comparison report: {e}")
            return {}
    
    def generate_performance_improvement_report(self) -> Dict:
        """Generate report on performance improvements over time."""
        try:
            available_versions_list = self.predictor.list_available_models()
            available_versions = [m["version"] for m in available_versions_list]
            
            report = {
                "generated_at": datetime.now().isoformat(),
                "report_type": "Performance Improvement",
                "improvements": []
            }
            
            # Get metrics for all versions
            metrics_list = []
            for version in available_versions:
                try:
                    info = self.predictor.get_model_info(version)
                    if info:
                        metrics_list.append({
                            "version": version,
                            "accuracy": info.get("metrics", {}).get("accuracy", 0),
                            "roc_auc": info.get("metrics", {}).get("roc_auc", 0),
                            "f1_score": info.get("metrics", {}).get("f1_score", 0)
                        })
                except Exception:
                    continue
            
            # Calculate improvements
            if len(metrics_list) >= 2:
                sorted_by_accuracy = sorted(
                    metrics_list,
                    key=lambda x: x["accuracy"]
                )
                
                for i in range(1, len(sorted_by_accuracy)):
                    current = sorted_by_accuracy[i]
                    previous = sorted_by_accuracy[i-1]
                    
                    accuracy_improvement = (
                        current["accuracy"] - previous["accuracy"]
                    )
                    roc_auc_improvement = (
                        current["roc_auc"] - previous["roc_auc"]
                    )
                    f1_improvement = (
                        current["f1_score"] - previous["f1_score"]
                    )
                    
                    report["improvements"].append({
                        "from_version": previous["version"],
                        "to_version": current["version"],
                        "accuracy_improvement": accuracy_improvement,
                        "accuracy_improvement_pct": (
                            accuracy_improvement / max(abs(previous["accuracy"]), 0.01) * 100
                        ) if previous["accuracy"] > 0 else 0,
                        "roc_auc_improvement": roc_auc_improvement,
                        "f1_improvement": f1_improvement
                    })
            
            return report
        
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {}
    
    def _get_recommendation(self, best_model: Dict, all_models: List[Dict]) -> str:
        """Generate recommendation based on best model."""
        best_version = best_model["version"]
        active_version = self.predictor.current_version
        
        if best_version == active_version:
            return (
                f"Current active model ({active_version}) is the best performer. "
                "No action needed."
            )
        else:
            improvement = best_model["accuracy"] - next(
                (m["accuracy"] for m in all_models if m["version"] == active_version),
                0
            )
            return (
                f"Consider switching to model {best_version} for {improvement:.2%} "
                f"accuracy improvement over current active model ({active_version})."
            )
    
    def save_report(self, report_name: str, report_data: Dict) -> str:
        """
        Save report to file.
        
        Args:
            report_name: Name of the report
            report_data: Report data dictionary
            
        Returns:
            Path to saved report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_name}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            logger.info(f"Report saved to {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            return ""
    
    def generate_all_reports(self) -> Dict[str, str]:
        """Generate all available reports."""
        reports = {}
        
        try:
            # Generate model comparison report
            comparison = self.generate_model_comparison_report()
            if comparison:
                path = self.save_report("model_comparison", comparison)
                reports["model_comparison"] = path
            
            # Generate performance improvement report
            improvement = self.generate_performance_improvement_report()
            if improvement:
                path = self.save_report("performance_improvement", improvement)
                reports["performance_improvement"] = path
            
            logger.info(f"Generated {len(reports)} reports")
            return reports
        
        except Exception as e:
            logger.error(f"Error generating reports: {e}")
            return {}


def main():
    """Generate and save all reports."""
    generator = ModelReportGenerator()
    
    print("\n" + "="*60)
    print("TraceCredit Model Report Generator")
    print("="*60)
    
    # Generate all reports
    reports = generator.generate_all_reports()
    
    print(f"\nGenerated {len(reports)} reports:\n")
    for report_type, filepath in reports.items():
        print(f"✓ {report_type}: {filepath}")
    
    # Display summary
    comparison = generator.generate_model_comparison_report()
    if "summary" in comparison:
        summary = comparison["summary"]
        print("\n" + "-"*60)
        print("SUMMARY:")
        print(f"  Best Model: {summary['best_model']}")
        print(f"  Accuracy: {summary['best_accuracy']:.2%}")
        print(f"  Active Model: {summary['active_model']}")
        print(f"  Recommendation: {summary['recommendation']}")
        print("-"*60)


if __name__ == "__main__":
    main()
