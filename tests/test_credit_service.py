import pytest
from app.services.credit_service import CreditService


@pytest.fixture
def credit_service():
    return CreditService(min_limit=10000, max_limit=100000)


class TestCreditService:
    def test_low_risk_increases_limit(self, credit_service):
        limit = credit_service.calculate_recommended_limit(
            risk_probability=0.05,
            current_limit=50000,
            utilization_ratio=0.4
        )
        assert limit > 50000

    def test_high_risk_reduces_limit(self, credit_service):
        limit = credit_service.calculate_recommended_limit(
            risk_probability=0.95,
            current_limit=50000,
            utilization_ratio=0.5
        )
        assert limit < 50000

    def test_limit_never_below_minimum(self, credit_service):
        limit = credit_service.calculate_recommended_limit(
            risk_probability=0.99,
            current_limit=5000,
            utilization_ratio=0.95
        )
        assert limit >= credit_service.min_limit

    def test_limit_never_above_maximum(self, credit_service):
        limit = credit_service.calculate_recommended_limit(
            risk_probability=0.01,
            current_limit=500000,
            utilization_ratio=0.1
        )
        assert limit <= credit_service.max_limit

    def test_high_utilization_reduces_multiplier(self, credit_service):
        low_util = credit_service.calculate_recommended_limit(0.2, 50000, 0.3)
        high_util = credit_service.calculate_recommended_limit(0.2, 50000, 0.95)
        assert low_util > high_util

    def test_hardship_rules_zero_defaults_unchanged(self, credit_service):
        limit = credit_service.apply_hardship_rules(50000, 0)
        assert limit == 50000

    def test_hardship_rules_reduces_for_defaults(self, credit_service):
        limit = credit_service.apply_hardship_rules(50000, 3)
        assert limit < 50000

    def test_hardship_rules_minimum_floor(self, credit_service):
        limit = credit_service.apply_hardship_rules(50000, 100)
        assert limit >= 50000 * 0.3

    def test_fraud_no_risk_clean_history(self, credit_service):
        pay_statuses = [0, 0, 0, 0, 0, 0]
        is_fraud, score = credit_service.check_fraud_risk(pay_statuses, 0)
        assert is_fraud is False
        assert score == 0.0

    def test_fraud_detected_consecutive_defaults(self, credit_service):
        pay_statuses = [-1, -1, -1, -1, 0, 0]
        is_fraud, score = credit_service.check_fraud_risk(pay_statuses, 4)
        assert is_fraud is True
        assert score >= 0.6

    def test_generate_explanation_low_risk(self, credit_service):
        explanation = credit_service.generate_explanation(0.1, 0.3, 0, 5)
        assert "low default risk" in explanation
        assert "clean payment history" in explanation

    def test_generate_explanation_high_risk(self, credit_service):
        explanation = credit_service.generate_explanation(0.8, 0.9, 4, 1)
        assert "high default risk" in explanation
        assert "multiple missed payments" in explanation
