import pytest
import numpy as np
import pandas as pd
from app.services.drift_service import DriftDetectionService


@pytest.fixture
def drift_service():
    return DriftDetectionService(threshold_percentage=20.0)


@pytest.fixture
def sample_data():
    np.random.seed(42)
    baseline = np.random.normal(loc=50, scale=10, size=1000)
    shifted = np.random.normal(loc=65, scale=10, size=1000)
    stable = np.random.normal(loc=50, scale=10, size=1000)
    return baseline, shifted, stable


class TestDriftDetectionService:
    def test_mean_difference_detects_shift(self, drift_service, sample_data):
        baseline, shifted, _ = sample_data
        diff = drift_service.calculate_mean_difference(baseline, shifted)
        assert diff > 20

    def test_mean_difference_stable(self, drift_service, sample_data):
        baseline, _, stable = sample_data
        diff = drift_service.calculate_mean_difference(baseline, stable)
        assert diff < 5

    def test_mean_difference_zero_baseline(self, drift_service):
        baseline = np.zeros(100)
        current = np.ones(100)
        assert drift_service.calculate_mean_difference(baseline, current) == 0.0

    def test_psi_low_for_similar_distributions(self, drift_service, sample_data):
        baseline, _, stable = sample_data
        psi = drift_service.calculate_psi(baseline, stable)
        assert psi < 0.1

    def test_psi_high_for_different_distributions(self, drift_service, sample_data):
        baseline, shifted, _ = sample_data
        psi = drift_service.calculate_psi(baseline, shifted)
        assert psi > 0.1

    def test_psi_empty_arrays_returns_zero(self, drift_service):
        assert drift_service.calculate_psi(np.array([]), np.array([])) == 0.0

    def test_ks_detects_drift(self, drift_service, sample_data):
        baseline, shifted, _ = sample_data
        ks_stat, p_value = drift_service.calculate_ks_statistic(baseline, shifted)
        assert ks_stat > 0
        assert p_value < 0.05

    def test_ks_no_drift_stable(self, drift_service, sample_data):
        baseline, _, stable = sample_data
        _, p_value = drift_service.calculate_ks_statistic(baseline, stable)
        assert p_value > 0.05

    def test_detect_feature_drift_flags_shifted(self, drift_service, sample_data):
        baseline, shifted, _ = sample_data
        result = drift_service.detect_feature_drift("income", baseline, shifted)
        assert result["drift_detected"] is True
        assert result["feature_name"] == "income"
        assert result["severity"] in ["low", "medium", "high"]

    def test_detect_feature_drift_stable_not_flagged(self, drift_service, sample_data):
        baseline, _, stable = sample_data
        result = drift_service.detect_feature_drift("age", baseline, stable)
        assert result["drift_detected"] is False

    def test_detect_batch_drift_returns_list(self, drift_service, sample_data):
        baseline, shifted, _ = sample_data
        baseline_df = pd.DataFrame({"income": baseline, "age": baseline})
        current_df = pd.DataFrame({"income": shifted, "age": baseline})
        results = drift_service.detect_batch_drift(baseline_df, current_df)
        assert len(results) == 2
        income_result = next(r for r in results if r["feature_name"] == "income")
        assert income_result["drift_detected"] is True

    def test_get_drift_alerts_filters_drifted(self, drift_service, sample_data):
        baseline, shifted, stable = sample_data
        results = [
            drift_service.detect_feature_drift("income", baseline, shifted),
            drift_service.detect_feature_drift("age", baseline, stable),
        ]
        alerts = drift_service.get_drift_alerts(results)
        assert len(alerts) == 1
        assert alerts[0]["feature"] == "income"

    def test_set_baseline_stores_stats(self, drift_service):
        data = pd.DataFrame({"income": np.random.normal(50000, 10000, 100)})
        drift_service.set_baseline(data)
        assert "income" in drift_service.baseline_statistics
        stats = drift_service.baseline_statistics["income"]
        assert all(k in stats for k in ["mean", "std", "min", "max", "median"])
