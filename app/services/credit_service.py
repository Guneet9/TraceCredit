from typing import Tuple
import numpy as np
from app.core.logger import get_logger

logger = get_logger(__name__)


class CreditService:
    def __init__(self, min_limit: float = 10000, max_limit: float = 100000):
        self.min_limit = min_limit
        self.max_limit = max_limit

    def calculate_recommended_limit(
        self,
        risk_probability: float,
        current_limit: float,
        utilization_ratio: float = 0.7
    ) -> float:
        base_multiplier = 1.0 - (risk_probability * 0.5)

        if utilization_ratio > 0.9:
            util_multiplier = 0.9
        elif utilization_ratio > 0.7:
            util_multiplier = 0.95
        else:
            util_multiplier = 1.05

        recommended = current_limit * base_multiplier * util_multiplier
        return float(np.clip(recommended, self.min_limit, self.max_limit))

    def apply_hardship_rules(self, recommended_limit: float, default_count: int) -> float:
        if default_count == 0:
            return recommended_limit
        reduction = max(1.0 - (0.1 * default_count), 0.3)
        return float(recommended_limit * reduction)

    def check_fraud_risk(self, pay_status_values: list, default_count: int) -> Tuple[bool, float]:
        fraud_score = 0.0
        consecutive = max_consecutive = 0

        for status in pay_status_values:
            if status < 0:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 0

        if max_consecutive >= 3:
            fraud_score += 0.5
        if default_count >= 4:
            fraud_score += 0.4

        return fraud_score >= 0.6, fraud_score

    def generate_explanation(
        self,
        risk_probability: float,
        utilization_ratio: float,
        default_count: int,
        pay_status_count_positive: int
    ) -> str:
        parts = []

        if risk_probability < 0.2:
            parts.append("low default risk")
        elif risk_probability < 0.5:
            parts.append("moderate default risk")
        else:
            parts.append("high default risk")

        if utilization_ratio > 0.8:
            parts.append("high card usage")
        elif utilization_ratio > 0.5:
            parts.append("moderate card usage")
        else:
            parts.append("low card usage")

        if default_count == 0:
            parts.append("clean payment history")
        elif default_count <= 2:
            parts.append("few missed payments")
        else:
            parts.append("multiple missed payments")

        positive_rate = pay_status_count_positive / 6.0 if pay_status_count_positive > 0 else 0
        if positive_rate >= 0.8:
            parts.append("mostly on-time payments")
        elif positive_rate >= 0.5:
            parts.append("mixed payment patterns")

        return "Account shows " + ", ".join(parts) + "."
