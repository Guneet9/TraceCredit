"""User and prediction schemas for API."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    
    age: int = Field(..., ge=18, le=120, description="User age")
    gender: int = Field(..., description="Gender code")
    education: int = Field(..., description="Education level code")
    marital_status: int = Field(..., description="Marital status code")
    income: Optional[float] = Field(None, ge=0, description="Annual income")
    
    class Config:
        json_schema_extra = {
            "example": {
                "age": 35,
                "gender": 2,
                "education": 2,
                "marital_status": 1,
                "income": 50000.0
            }
        }


class UserResponse(BaseModel):
    """User response model."""
    
    id: int
    age: int
    gender: int
    education: int
    marital_status: int
    income: Optional[float]
    risk_score: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PredictionRequest(BaseModel):
    """Request schema for credit limit prediction."""
    
    user_id: int = Field(..., description="User ID")
    age: int = Field(..., ge=18, le=120)
    gender: int = Field(...)
    education: int = Field(...)
    marital_status: int = Field(...)
    pay_status_m1: float = Field(..., description="Payment status month 1")
    pay_status_m2: float = Field(...)
    pay_status_m3: float = Field(...)
    pay_status_m4: float = Field(...)
    pay_status_m5: float = Field(...)
    pay_status_m6: float = Field(...)
    bill_amt_m1: float = Field(..., ge=0, description="Bill amount month 1")
    bill_amt_m2: float = Field(..., ge=0)
    bill_amt_m3: float = Field(..., ge=0)
    bill_amt_m4: float = Field(..., ge=0)
    bill_amt_m5: float = Field(..., ge=0)
    bill_amt_m6: float = Field(..., ge=0)
    pay_amt_m1: float = Field(..., ge=0, description="Payment amount month 1")
    pay_amt_m2: float = Field(..., ge=0)
    pay_amt_m3: float = Field(..., ge=0)
    pay_amt_m4: float = Field(..., ge=0)
    pay_amt_m5: float = Field(..., ge=0)
    pay_amt_m6: float = Field(..., ge=0)
    current_credit_limit: float = Field(..., ge=0, description="Current credit limit")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "age": 35,
                "gender": 2,
                "education": 2,
                "marital_status": 1,
                "pay_status_m1": 0,
                "pay_status_m2": 0,
                "pay_status_m3": 0,
                "pay_status_m4": 0,
                "pay_status_m5": 0,
                "pay_status_m6": 0,
                "bill_amt_m1": 5000,
                "bill_amt_m2": 4500,
                "bill_amt_m3": 5500,
                "bill_amt_m4": 6000,
                "bill_amt_m5": 5200,
                "bill_amt_m6": 4800,
                "pay_amt_m1": 2500,
                "pay_amt_m2": 2300,
                "pay_amt_m3": 2800,
                "pay_amt_m4": 3000,
                "pay_amt_m5": 2600,
                "pay_amt_m6": 2400,
                "current_credit_limit": 50000.0
            }
        }


class PredictionResponse(BaseModel):
    """Response schema for prediction endpoint."""
    
    risk_probability: float = Field(..., ge=0, le=1, description="Probability of default")
    recommended_limit: float = Field(..., ge=0, description="Recommended credit limit")
    model_version: str = Field(..., description="Model version used")
    prediction_made_at: datetime = Field(...)
    
    class Config:
        json_schema_extra = {
            "example": {
                "risk_probability": 0.32,
                "recommended_limit": 45000.0,
                "model_version": "v1",
                "prediction_made_at": "2024-02-22T10:00:00Z"
            }
        }


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Health status")
    database: str = Field(..., description="Database connection status")
    tables: int = Field(..., description="Number of database tables")
    timestamp: str = Field(..., description="UTC timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "database": "connected",
                "tables": 7,
                "timestamp": "2024-02-22T10:00:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    success: bool = False
    error: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Model not found",
                "details": {"version": "v1"}
            }
        }
