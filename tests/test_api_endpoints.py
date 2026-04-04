import pytest


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert "tables" in data

    def test_root_returns_api_info(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert data["version"] == "2.0.0"


class TestModelsEndpoint:
    def test_list_models_returns_list(self, client):
        response = client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert "total_models" in data

    def test_get_nonexistent_model_returns_404(self, client):
        response = client.get("/api/models/v99")
        assert response.status_code == 404

    def test_activate_nonexistent_model_returns_404(self, client):
        response = client.post("/api/models/v99/activate")
        assert response.status_code == 404


class TestAlertsEndpoint:
    def test_alerts_returns_summary(self, client):
        response = client.get("/api/alerts")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "summary" in data
        assert "alerts" in data

    def test_alerts_filter_by_type(self, client):
        response = client.get("/api/alerts?alert_type=drift")
        assert response.status_code == 200


class TestDriftEventsEndpoint:
    def test_drift_events_returns_list(self, client):
        response = client.get("/api/drift-events")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "events" in data

    def test_drift_events_severity_filter(self, client):
        response = client.get("/api/drift-events?severity=high")
        assert response.status_code == 200
        data = response.json()
        for event in data["events"]:
            assert event["severity"] == "high"

    def test_drift_events_limit_param(self, client):
        response = client.get("/api/drift-events?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) <= 5


class TestPredictEndpoint:
    def test_predict_missing_fields_returns_422(self, client):
        response = client.post("/api/predict", json={"user_id": 1, "age": 35})
        assert response.status_code == 422

    def test_predict_invalid_age_returns_422(self, client):
        response = client.post("/api/predict", json={
            "user_id": 1, "age": 5,
            "gender": 2, "education": 2, "marital_status": 1,
            "pay_status_m1": 0, "pay_status_m2": 0, "pay_status_m3": 0,
            "pay_status_m4": 0, "pay_status_m5": 0, "pay_status_m6": 0,
            "bill_amt_m1": 5000, "bill_amt_m2": 5000, "bill_amt_m3": 5000,
            "bill_amt_m4": 5000, "bill_amt_m5": 5000, "bill_amt_m6": 5000,
            "pay_amt_m1": 2500, "pay_amt_m2": 2500, "pay_amt_m3": 2500,
            "pay_amt_m4": 2500, "pay_amt_m5": 2500, "pay_amt_m6": 2500,
            "current_credit_limit": 50000
        })
        assert response.status_code == 422


class TestLimitHistoryEndpoint:
    def test_nonexistent_user_returns_404(self, client):
        response = client.get("/api/limit-history/99999")
        assert response.status_code == 404

    def test_limit_param_respected(self, client):
        response = client.get("/api/limit-history/1?limit=5")
        assert response.status_code in [200, 404]


class TestAuditTrailEndpoint:
    def test_nonexistent_decision_returns_404(self, client):
        response = client.get("/api/audit-trail/99999")
        assert response.status_code == 404
