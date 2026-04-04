import pytest
import numpy as np
from app.services.drift_service import DriftDetectionService
from app.services.drift import DriftDetector


class TestDriftDetector:
    def test_no_drift_within_threshold(self):
        detector = DriftDetector(threshold_percentage=20.0)
        drifted, delta, severity = detector.detect_limit_drift(50000, 55000)
        assert drifted is False
        assert delta == 5000
        assert severity == "none"

    def test_drift_detected_above_threshold(self):
        detector = DriftDetector(threshold_percentage=20.0)
        drifted, delta, severity = detector.detect_limit_drift(50000, 70000)
        assert drifted is True
        assert delta == 20000
        assert severity in ["medium", "high", "critical"]

    def test_severity_critical_50_plus(self):
        detector = DriftDetector(threshold_percentage=20.0)
        drifted, _, severity = detector.detect_limit_drift(10000, 60000)
        assert drifted is True
        assert severity == "critical"

    def test_severity_high_30_to_50(self):
        detector = DriftDetector(threshold_percentage=20.0)
        drifted, _, severity = detector.detect_limit_drift(10000, 14000)
        assert drifted is True
        assert severity in ["medium", "high"]

    def test_zero_previous_limit_no_crash(self):
        detector = DriftDetector(threshold_percentage=20.0)
        drifted, delta, severity = detector.detect_limit_drift(0, 50000)
        assert drifted is False
        assert severity == "none"

    def test_negative_delta_decrease(self):
        detector = DriftDetector(threshold_percentage=20.0)
        drifted, delta, severity = detector.detect_limit_drift(50000, 25000)
        assert drifted is True
        assert delta == -25000

    def test_feature_drift_detects_large_change(self):
        detector = DriftDetector(threshold_percentage=20.0)
        prev = {"income": 50000.0, "risk_score": 5.0}
        curr = {"income": 80000.0, "risk_score": 5.0}
        changes = detector.detect_feature_drift(prev, curr)
        assert changes["income"][0] is True

    def test_feature_drift_stable_not_flagged(self):
        detector = DriftDetector(threshold_percentage=20.0)
        prev = {"income": 50000.0}
        curr = {"income": 51000.0}
        changes = detector.detect_feature_drift(prev, curr)
        assert changes["income"][0] is False


class TestConceptDrift:
    def test_covariate_shift_detected_by_ks(self):
        service = DriftDetectionService()
        np.random.seed(0)
        baseline = np.random.normal(35, 8, 500)
        current = np.random.normal(50, 8, 500)
        result = service.detect_feature_drift("age", baseline, current)
        assert result["drift_detected"] is True
        assert result["ks_pvalue"] < 0.05

    def test_stable_distribution_not_flagged(self):
        service = DriftDetectionService()
        np.random.seed(0)
        baseline = np.random.normal(50000, 10000, 500)
        current = np.random.normal(50000, 10000, 500)
        result = service.detect_feature_drift("income", baseline, current)
        assert result["psi_score"] < 0.1

    def test_severity_classification_high(self):
        service = DriftDetectionService()
        np.random.seed(0)
        baseline = np.random.normal(0, 1, 1000)
        current = np.random.normal(5, 1, 1000)
        result = service.detect_feature_drift("feature", baseline, current)
        assert result["severity"] in ["medium", "high"]
