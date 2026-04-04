from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    gender = Column(Integer)
    education = Column(Integer)
    marital_status = Column(Integer)
    income = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    role = Column(String, default="customer")
    created_at = Column(DateTime, default=datetime.utcnow)

    credit_history = relationship("CreditDecision", back_populates="user")
    feature_snapshots = relationship("FeatureSnapshot", back_populates="user")


class FeatureSnapshot(Base):
    __tablename__ = "feature_snapshots"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    month = Column(Integer)
    age = Column(Integer)
    gender = Column(Integer)
    education = Column(Integer)
    marital_status = Column(Integer)
    income = Column(Float)
    risk_score = Column(Float)
    bill_amount = Column(Float, nullable=True)
    payment_amount = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feature_snapshots")
    credit_decisions = relationship("CreditDecision", back_populates="feature_snapshot")


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True)
    version_name = Column(String, unique=True)
    description = Column(Text, nullable=True)
    metrics = Column(JSON)
    model_path = Column(String)
    features = Column(JSON)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    credit_decisions = relationship("CreditDecision", back_populates="model_version")


class CreditDecision(Base):
    __tablename__ = "credit_decisions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    feature_snapshot_id = Column(Integer, ForeignKey("feature_snapshots.id"))
    model_version_id = Column(Integer, ForeignKey("model_versions.id"))
    predicted_limit = Column(Float)
    previous_limit = Column(Float, nullable=True)
    drift_detected = Column(Boolean, default=False)
    delta = Column(Float, nullable=True)
    explanation = Column(JSON, nullable=True)
    human_explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="credit_history")
    model_version = relationship("ModelVersion", back_populates="credit_decisions")
    feature_snapshot = relationship("FeatureSnapshot", back_populates="credit_decisions")


class DriftEvent(Base):
    __tablename__ = "drift_events"

    id = Column(Integer, primary_key=True)
    month = Column(Integer)
    feature_name = Column(String)
    drift_score = Column(Float)
    threshold = Column(Float)
    drift_detected = Column(Boolean)
    severity = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class FairnessMetric(Base):
    __tablename__ = "fairness_metrics"

    id = Column(Integer, primary_key=True)
    cohort_name = Column(String)
    metric_name = Column(String)
    value = Column(Float)
    threshold = Column(Float, nullable=True)
    violation = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
