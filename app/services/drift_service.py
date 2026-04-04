import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from scipy import stats
from app.core.logger import get_logger

logger = get_logger(__name__)


class DriftDetectionService:
    MONITORED_FEATURES = ['credit_limit', 'pay_status_m1', 'bill_amt_m1', 'pay_amt_m1', 'age']

    def __init__(self, threshold_percentage: float = 20.0):
        self.threshold_percentage = threshold_percentage
        self.baseline_statistics = None

    def calculate_mean_difference(self, baseline: np.ndarray, current: np.ndarray) -> float:
        baseline_mean = np.mean(baseline)
        if baseline_mean == 0:
            return 0.0
        return abs(np.mean(current) - baseline_mean) / abs(baseline_mean) * 100

    def calculate_psi(self, baseline: np.ndarray, current: np.ndarray, bins: int = 10) -> float:
        baseline = baseline[~np.isnan(baseline)]
        current = current[~np.isnan(current)]

        if len(baseline) == 0 or len(current) == 0:
            return 0.0

        breakpoints = np.percentile(baseline, np.linspace(0, 100, bins + 1))
        breakpoints[0] = -np.inf
        breakpoints[-1] = np.inf

        baseline_hist, _ = np.histogram(baseline, bins=breakpoints)
        current_hist, _ = np.histogram(current, bins=breakpoints)

        baseline_pct = baseline_hist / len(baseline)
        current_pct = current_hist / len(current)

        eps = 1e-10
        psi = np.sum(
            (current_pct - baseline_pct) * np.log((current_pct + eps) / (baseline_pct + eps))
        )
        return float(psi)

    def calculate_ks_statistic(self, baseline: np.ndarray, current: np.ndarray) -> Tuple[float, float]:
        baseline = baseline[~np.isnan(baseline)]
        current = current[~np.isnan(current)]

        if len(baseline) == 0 or len(current) == 0:
            return 0.0, 1.0

        try:
            ks_stat, p_value = stats.ks_2samp(baseline, current)
            return float(ks_stat), float(p_value)
        except Exception as e:
            logger.warning(f"KS test failed: {e}")
            return 0.0, 1.0

    def detect_feature_drift(
        self,
        feature_name: str,
        baseline_values: np.ndarray,
        current_values: np.ndarray
    ) -> Dict:
        mean_diff = self.calculate_mean_difference(baseline_values, current_values)
        psi = self.calculate_psi(baseline_values, current_values)
        ks_stat, ks_p = self.calculate_ks_statistic(baseline_values, current_values)

        drift_detected = mean_diff > self.threshold_percentage or psi > 0.1 or ks_p < 0.05

        if psi > 0.25 or ks_stat > 0.3:
            severity = "high"
        elif psi > 0.1 or ks_stat > 0.15:
            severity = "medium"
        else:
            severity = "low"

        return {
            "feature_name": feature_name,
            "drift_detected": drift_detected,
            "mean_difference_pct": mean_diff,
            "psi_score": psi,
            "ks_statistic": ks_stat,
            "ks_pvalue": ks_p,
            "severity": severity,
            "detected_at": datetime.utcnow().isoformat()
        }

    def detect_batch_drift(
        self,
        baseline_df: pd.DataFrame,
        current_df: pd.DataFrame,
        features: Optional[List[str]] = None
    ) -> List[Dict]:
        if features is None:
            features = list(set(baseline_df.columns) & set(current_df.columns))

        results = []
        for feature in features:
            if feature not in baseline_df.columns or feature not in current_df.columns:
                continue
            baseline_vals = baseline_df[feature].dropna().values
            current_vals = current_df[feature].dropna().values
            if len(baseline_vals) == 0 or len(current_vals) == 0:
                continue
            results.append(self.detect_feature_drift(feature, baseline_vals, current_vals))

        return results

    def set_baseline(self, data: pd.DataFrame, features: Optional[List[str]] = None) -> None:
        if features is None:
            features = data.select_dtypes(include=[np.number]).columns.tolist()

        self.baseline_statistics = {}
        for feature in features:
            if feature not in data.columns:
                continue
            vals = data[feature].dropna().values
            self.baseline_statistics[feature] = {
                "mean": float(np.mean(vals)),
                "std": float(np.std(vals)),
                "min": float(np.min(vals)),
                "max": float(np.max(vals)),
                "median": float(np.median(vals))
            }
        logger.info(f"Baseline set for {len(self.baseline_statistics)} features")

    def get_drift_alerts(self, drift_results: List[Dict]) -> List[Dict]:
        return [
            {
                "feature": r["feature_name"],
                "severity": r["severity"],
                "psi_score": r["psi_score"],
                "mean_difference": r["mean_difference_pct"],
                "timestamp": r["detected_at"]
            }
            for r in drift_results if r["drift_detected"]
        ]
