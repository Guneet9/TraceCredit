import numpy as np
from typing import Dict, Tuple, Optional

from app.core.logger import get_logger

logger = get_logger(__name__)


class DriftDetector:
    def __init__(self, threshold_percentage: float = 20.0):
        self.threshold_percentage = threshold_percentage

    def detect_limit_drift(self, previous_limit: float, new_limit: float) -> Tuple[bool, float, str]:
        if previous_limit == 0:
            return False, new_limit, "none"

        delta_pct = abs((new_limit - previous_limit) / previous_limit) * 100
        delta = new_limit - previous_limit

        if delta_pct > self.threshold_percentage:
            severity = self._classify_severity(delta_pct)
            logger.warning(f"Limit drift: {previous_limit:.0f} -> {new_limit:.0f} ({delta_pct:.1f}%, {severity})")
            return True, delta, severity

        return False, delta, "none"

    def detect_feature_drift(
        self,
        previous_features: Dict[str, float],
        new_features: Dict[str, float]
    ) -> Dict[str, Tuple[bool, float]]:
        changes = {}
        for key in new_features:
            if key not in previous_features:
                continue
            prev = previous_features[key]
            curr = new_features[key]
            delta_pct = abs((curr - prev) / prev) * 100 if prev != 0 else 0
            threshold = self._get_feature_threshold(key)
            changes[key] = (delta_pct > threshold, curr - prev)
        return changes

    def _classify_severity(self, delta_pct: float) -> str:
        if delta_pct > 50:
            return "critical"
        elif delta_pct > 30:
            return "high"
        elif delta_pct > 20:
            return "medium"
        return "low"

    def _get_feature_threshold(self, feature_name: str) -> float:
        thresholds = {
            'income': 15.0,
            'risk_score': 30.0,
            'bill_amount': 25.0,
            'payment_amount': 25.0,
        }
        return thresholds.get(feature_name, 20.0)


class ExplanationGenerator:
    def __init__(self):
        self.drift_detector = DriftDetector()

    def generate_decision_explanation(self, decision: Dict, previous_decision=None) -> str:
        predicted_limit = decision.get('predicted_limit', 0)
        features = decision.get('features', {})

        lines = [f"Your credit limit has been set to ${predicted_limit:.2f} based on:"]
        for feature, value in features.items():
            lines.append(self._explain_feature(feature, value))

        if previous_decision:
            prev_limit = (
                previous_decision.predicted_limit
                if hasattr(previous_decision, 'predicted_limit')
                else previous_decision.get('predicted_limit', 0)
            )
            if prev_limit and prev_limit != predicted_limit:
                delta = predicted_limit - prev_limit
                direction = "increased" if delta > 0 else "decreased"
                lines.append(f"\nYour limit {direction} by ${abs(delta):.2f} from the previous assessment.")

        return "\n".join(lines)

    def _explain_feature(self, feature: str, value: float) -> str:
        explanations = {
            'age': f"Age ({int(value)}) indicates stable credit patterns.",
            'income': f"Income (${value:.0f}) supports your credit access level.",
            'risk_score': f"Risk score ({value:.1f}/10) reflects your credit behavior.",
            'education': "Education background contributes to creditworthiness.",
            'marital_status': "Marital status is factored into stability evaluation.",
        }
        return explanations.get(feature, f"{feature}: {value:.2f}")

    def generate_drift_explanation(
        self,
        previous_features: Dict[str, float],
        new_features: Dict[str, float],
        drift_delta: float
    ) -> str:
        changes = self.drift_detector.detect_feature_drift(previous_features, new_features)
        lines = ["Your credit limit changed due to:"]
        for feature, (drifted, delta) in changes.items():
            if drifted:
                direction = "increased" if delta > 0 else "decreased"
                lines.append(f"- {feature}: {direction} by {abs(delta):.2f}")
        return "\n".join(lines)


drift_detector = DriftDetector()
explanation_generator = ExplanationGenerator()
