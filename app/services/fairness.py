import pandas as pd
import numpy as np
from typing import Dict, List

from app.core.logger import get_logger

logger = get_logger(__name__)


class FairnessAnalyzer:
    def __init__(self):
        self.fairness_thresholds = {
            'avg_limit_gap': 2000.0,
            'median_limit_gap': 1500.0,
        }

    def compute_cohort_metrics(self, df: pd.DataFrame, cohort_column: str) -> Dict[str, Dict[str, float]]:
        results = {}
        for cohort_name, group in df.groupby(cohort_column):
            results[str(cohort_name)] = {
                'count': len(group),
                'avg_limit': float(group['predicted_limit'].mean()),
                'median_limit': float(group['predicted_limit'].median()),
                'std_limit': float(group['predicted_limit'].std()),
                'min_limit': float(group['predicted_limit'].min()),
                'max_limit': float(group['predicted_limit'].max()),
            }
        return results

    def detect_fairness_violations(self, cohort_metrics: Dict[str, Dict[str, float]]) -> List[Dict]:
        violations = []
        cohort_names = list(cohort_metrics.keys())

        if len(cohort_names) < 2:
            return violations

        for i, c1 in enumerate(cohort_names):
            for c2 in cohort_names[i + 1:]:
                m1, m2 = cohort_metrics[c1], cohort_metrics[c2]

                avg_gap = abs(m1['avg_limit'] - m2['avg_limit'])
                if avg_gap > self.fairness_thresholds['avg_limit_gap']:
                    violations.append({
                        'type': 'avg_limit_gap', 'cohort1': c1, 'cohort2': c2,
                        'gap': avg_gap, 'threshold': self.fairness_thresholds['avg_limit_gap'],
                        'severity': self._classify_severity(avg_gap, self.fairness_thresholds['avg_limit_gap'])
                    })

                median_gap = abs(m1['median_limit'] - m2['median_limit'])
                if median_gap > self.fairness_thresholds['median_limit_gap']:
                    violations.append({
                        'type': 'median_limit_gap', 'cohort1': c1, 'cohort2': c2,
                        'gap': median_gap, 'threshold': self.fairness_thresholds['median_limit_gap'],
                        'severity': self._classify_severity(median_gap, self.fairness_thresholds['median_limit_gap'])
                    })

        if violations:
            logger.warning(f"{len(violations)} fairness violations detected")

        return violations

    def _classify_severity(self, gap: float, threshold: float) -> str:
        ratio = gap / threshold
        if ratio > 3:
            return "critical"
        elif ratio > 2:
            return "high"
        elif ratio > 1.5:
            return "medium"
        return "low"

    def create_income_brackets(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['income_bracket'] = pd.cut(
            df['income'],
            bins=[0, 50000, 100000, 150000, float('inf')],
            labels=['low', 'medium', 'high', 'very_high']
        )
        return df

    def create_age_brackets(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['age_bracket'] = pd.cut(
            df['age'],
            bins=[0, 30, 40, 50, 60, 100],
            labels=['20-30', '30-40', '40-50', '50-60', '60+']
        )
        return df


class ExplainabilityService:
    def __init__(self):
        self.fairness_analyzer = FairnessAnalyzer()

    def compute_feature_importance(self, model, X: np.ndarray, feature_names: List[str], sample_idx: int = 0) -> Dict[str, float]:
        try:
            if hasattr(model, 'feature_importances_'):
                return {name: float(imp) for name, imp in zip(feature_names, model.feature_importances_)}

            if hasattr(model, 'coef_'):
                coefs = model.coef_[0] if model.coef_.ndim > 1 else model.coef_
                coefs = np.abs(coefs)
                total = coefs.sum() or 1.0
                return {name: float(c / total) for name, c in zip(feature_names, coefs)}

            return {}
        except Exception as e:
            logger.error(f"Feature importance failed: {e}")
            return {}

    def generate_shap_explanation(self, model, instance: np.ndarray, feature_names: List[str]) -> Dict:
        try:
            import shap
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(instance)
            if isinstance(shap_values, list):
                shap_values = shap_values[0]
            return {feature: float(value) for feature, value in zip(feature_names, shap_values[0])}
        except Exception as e:
            logger.warning(f"SHAP explanation failed: {e}")
            return {}

    def create_audit_trail(self, decision_id, user_id, features, prediction, explanation, model_version) -> Dict:
        return {
            'decision_id': decision_id,
            'user_id': user_id,
            'features': features,
            'prediction': prediction,
            'explanation': explanation,
            'model_version': model_version,
            'audit_timestamp': pd.Timestamp.utcnow().isoformat()
        }
