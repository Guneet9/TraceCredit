import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test_tracecredit.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    Path("test_tracecredit.db").unlink(missing_ok=True)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def example_features():
    return {
        'age': 35.0,
        'gender': 2.0,
        'education': 2.0,
        'marital_status': 1.0,
        'pay_status_m1': 0.0,
        'pay_status_m2': 0.0,
        'pay_status_m3': 0.0,
        'pay_status_m4': 0.0,
        'pay_status_m5': 0.0,
        'pay_status_m6': 0.0,
        'bill_amt_m1': 5000.0,
        'bill_amt_m2': 4500.0,
        'bill_amt_m3': 5500.0,
        'bill_amt_m4': 6000.0,
        'bill_amt_m5': 5200.0,
        'bill_amt_m6': 4800.0,
        'pay_amt_m1': 2500.0,
        'pay_amt_m2': 2300.0,
        'pay_amt_m3': 2800.0,
        'pay_amt_m4': 3000.0,
        'pay_amt_m5': 2600.0,
        'pay_amt_m6': 2400.0,
        'credit_limit': 50000.0,
        'avg_bill_6m': 5166.67,
        'avg_pay_6m': 2600.0,
        'max_bill_6m': 6000.0,
        'default_status_count': 0.0,
        'utilization_ratio': 0.12,
        'payment_to_bill_ratio': 0.504
    }
