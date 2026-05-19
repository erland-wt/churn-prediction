from __future__ import annotations

from fastapi import FastAPI, HTTPException, Body
from typing import Dict, Any, Optional, Tuple, Literal
import joblib
import pandas as pd
import logging
import os
from pydantic import BaseModel, Field, conint, confloat
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- Pydantic model for encoded-feature endpoint (/predict) ----------
class Customer(BaseModel):
    SeniorCitizen: int = Field(..., alias="SeniorCitizen", ge=0, le=1)
    Partner: int = Field(..., alias="Partner")
    Dependents: int = Field(..., alias="Dependents")
    tenure: float = Field(..., alias="tenure", ge=0)
    PhoneService: int = Field(..., alias="PhoneService")
    PaperlessBilling: int = Field(..., alias="PaperlessBilling")
    MonthlyCharges: float = Field(..., alias="MonthlyCharges", ge=0)
    TotalCharges: float = Field(..., alias="TotalCharges", ge=0)
    AvgMonthlyCharges: float = Field(..., alias="AvgMonthlyCharges")
    TotalServices: float = Field(..., alias="TotalServices")
    gender_Male: int = Field(..., alias="gender_Male")
    MultipleLines_No_phone_service: int = Field(..., alias="MultipleLines_No phone service")
    MultipleLines_Yes: int = Field(..., alias="MultipleLines_Yes")
    InternetService_Fiber_optic: int = Field(..., alias="InternetService_Fiber optic")
    InternetService_No: int = Field(..., alias="InternetService_No")
    OnlineSecurity_No_internet_service: int = Field(..., alias="OnlineSecurity_No internet service")
    OnlineSecurity_Yes: int = Field(..., alias="OnlineSecurity_Yes")
    OnlineBackup_No_internet_service: int = Field(..., alias="OnlineBackup_No internet service")
    OnlineBackup_Yes: int = Field(..., alias="OnlineBackup_Yes")
    DeviceProtection_No_internet_service: int = Field(..., alias="DeviceProtection_No internet service")
    DeviceProtection_Yes: int = Field(..., alias="DeviceProtection_Yes")
    TechSupport_No_internet_service: int = Field(..., alias="TechSupport_No internet service")
    TechSupport_Yes: int = Field(..., alias="TechSupport_Yes")
    StreamingTV_No_internet_service: int = Field(..., alias="StreamingTV_No internet service")
    StreamingTV_Yes: int = Field(..., alias="StreamingTV_Yes")
    StreamingMovies_No_internet_service: int = Field(..., alias="StreamingMovies_No internet service")
    StreamingMovies_Yes: int = Field(..., alias="StreamingMovies_Yes")
    Contract_One_year: int = Field(..., alias="Contract_One year")
    Contract_Two_year: int = Field(..., alias="Contract_Two year")
    PaymentMethod_Credit_card_automatic: int = Field(..., alias="PaymentMethod_Credit card (automatic)")
    PaymentMethod_Electronic_check: int = Field(..., alias="PaymentMethod_Electronic check")
    PaymentMethod_Mailed_check: int = Field(..., alias="PaymentMethod_Mailed check")
    TenureBucket_Established: int = Field(..., alias="TenureBucket_Established")
    TenureBucket_Loyal: int = Field(..., alias="TenureBucket_Loyal")
    TenureBucket_New: int = Field(..., alias="TenureBucket_New")

    class Config:
        allow_population_by_field_name = True
        schema_extra = {"example": {
            "SeniorCitizen":0,"Partner":1,"Dependents":1,"tenure":1.3218,"PhoneService":1,"PaperlessBilling":0,
            "MonthlyCharges":0.9787,"TotalCharges":1.6598,"AvgMonthlyCharges":0.9431,"TotalServices":1.1081,
            "gender_Male":1,"MultipleLines_No phone service":0,"MultipleLines_Yes":1,"InternetService_Fiber optic":1,
            "InternetService_No":0,"OnlineSecurity_No internet service":0,"OnlineSecurity_Yes":1,"OnlineBackup_No internet service":0,
            "OnlineBackup_Yes":1,"DeviceProtection_No internet service":0,"DeviceProtection_Yes":1,"TechSupport_No internet service":0,
            "TechSupport_Yes":1,"StreamingTV_No internet service":0,"StreamingTV_Yes":0,"StreamingMovies_No internet service":0,
            "StreamingMovies_Yes":0,"Contract_One year":0,"Contract_Two year":0,"PaymentMethod_Credit card (automatic)":0,
            "PaymentMethod_Electronic check":1,"PaymentMethod_Mailed check":1,"TenureBucket_Established":0,"TenureBucket_Loyal":0,"TenureBucket_New":0
        }}

# ---------- Pydantic model for raw customer input ----------
class RawCustomer(BaseModel):
    gender: Literal["Female", "Male"]
    SeniorCitizen: int = Field(..., ge=0, le=1)
    Partner: Literal["Yes", "No"]
    Dependents: Literal["Yes", "No"]
    tenure: float = Field(..., ge=0)
    PhoneService: Literal["Yes", "No"]
    MultipleLines: Literal["No", "Yes", "No phone service"]
    InternetService: Literal["DSL", "Fiber optic", "No"]
    OnlineSecurity: Literal["No", "Yes", "No internet service"]
    OnlineBackup: Literal["No", "Yes", "No internet service"]
    DeviceProtection: Literal["No", "Yes", "No internet service"]
    TechSupport: Literal["No", "Yes", "No internet service"]
    StreamingTV: Literal["No", "Yes", "No internet service"]
    StreamingMovies: Literal["No", "Yes", "No internet service"]
    Contract: Literal["Month-to-month", "One year", "Two year"]
    PaperlessBilling: Literal["Yes", "No"]
    PaymentMethod: Literal[
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ]
    MonthlyCharges: float = Field(..., ge=0)
    TotalCharges: float = Field(..., ge=0)

    class Config:
        extra = "ignore"

# ---------- App & model loading ----------
app = FastAPI(title="Churn Prediction API")

MODEL_PATH = os.path.join("models", "churn_model.joblib")
PREPROC_PATH = os.path.join("models", "preprocessor.joblib")

def _extract_model_from_artifact(artifact: Any) -> Tuple[Optional[Any], float]:
    if isinstance(artifact, dict):
        for key in ("model", "estimator", "final_model", "pipeline"):
            if key in artifact:
                model = artifact[key]
                threshold = float(artifact.get("threshold", 0.5))
                return model, threshold
        return None, float(artifact.get("threshold", 0.5)) if "threshold" in artifact else 0.5
    else:
        return artifact, 0.5

# load model artifact
try:
    artifact = joblib.load(MODEL_PATH)
    model, threshold = _extract_model_from_artifact(artifact)
    if model is None:
        raise ValueError("Estimator not found in joblib artifact.")
    logger.info("Model loaded from %s", MODEL_PATH)
except Exception as e:
    model = None
    threshold = 0.5
    load_error = str(e)
    logger.exception("Failed to load model: %s", e)

# load preprocessor artifact
preproc = None
try:
    preproc = joblib.load(PREPROC_PATH)
    expected_columns = preproc.get("expected_columns")
    proc_scale_cols = preproc.get("scale_cols", [])
    proc_scaler = preproc.get("scaler", None)
    logger.info("Preprocessor loaded from %s", PREPROC_PATH)
except Exception:
    expected_columns = None
    proc_scale_cols = []
    proc_scaler = None
    logger.info("Preprocessor not loaded (predict_raw will fail until saved).")

# ---------- Preprocessing helpers ----------
def _tenure_bucket(tenure):
    if tenure <= 12:
        return "New"
    if tenure <= 24:
        return "Early"
    if tenure <= 48:
        return "Established"
    return "Loyal"

def preprocess_raw_record(rec: dict) -> pd.DataFrame:
    """
    Convert raw customer dict (strings like 'Yes'/'No', categorical labels, numeric) into
    encoded & scaled DataFrame matching training columns (expected_columns).
    """
    if expected_columns is None:
        raise RuntimeError("Preprocessor artifact not loaded (models/preprocessor.joblib).")

    df = pd.DataFrame([rec])

    # Feature engineering
    df["AvgMonthlyCharges"] = df["TotalCharges"] / df["tenure"]
    df["TenureBucket"] = df["tenure"].apply(_tenure_bucket)

    service_cols = ["PhoneService","OnlineSecurity","OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies"]
    df["TotalServices"] = df[service_cols].apply(lambda row: (row == "Yes").sum(), axis=1)

    # Binary mapping (Yes/No -> 1/0)
    for col in ["Partner","Dependents","PhoneService","PaperlessBilling"]:
        if col in df.columns:
            df[col] = df[col].map({"Yes": 1, "No": 0})
        else:
            df[col] = 0

    # One-hot encoding for categorical columns
    categorical_cols = [
        "gender","MultipleLines","InternetService","OnlineSecurity","OnlineBackup",
        "DeviceProtection","TechSupport","StreamingTV","StreamingMovies","Contract","PaymentMethod","TenureBucket"
    ]
    df = pd.get_dummies(df, columns=[c for c in categorical_cols if c in df.columns], drop_first=True).astype(int)

    # Align to expected columns from training
    df = df.reindex(columns=expected_columns, fill_value=0)

    # Scale numeric columns using saved scaler
    if proc_scaler is not None and proc_scale_cols:
        df[proc_scale_cols] = proc_scaler.transform(df[proc_scale_cols])

    return df

# ---------- Endpoints ----------
@app.get("/")
def root():
    return {"status": "ok", "model_loaded": model is not None, "model_error": globals().get("load_error", None)}

@app.get("/meta")
def meta():
    if model is None:
        raise HTTPException(status_code=500, detail=f"Model not loaded: {globals().get('load_error')}")
    feature_names = getattr(model, "feature_names_in_", None)
    return {
        "feature_names": list(feature_names) if feature_names is not None else expected_columns,
        "threshold": threshold,
        "preprocessor_loaded": expected_columns is not None
    }

@app.post("/predict")
def predict(customer: "Customer"):
    if model is None:
        raise HTTPException(status_code=500, detail=f"Model not loaded: {globals().get('load_error')}")
    try:
        payload = customer.dict(by_alias=True)
        df = pd.DataFrame([payload])

        expected = getattr(model, "feature_names_in_", None)
        if expected is not None:
            missing = set(expected) - set(df.columns)
            if missing:
                raise HTTPException(status_code=400, detail=f"Missing features: {sorted(list(missing))}")
            df = df[list(expected)]

        proba = float(model.predict_proba(df)[0, 1]) if hasattr(model, "predict_proba") else None
        pred = int(proba >= threshold) if proba is not None else int(model.predict(df)[0])

        return {"prediction": pred, "probability": proba, "threshold": threshold}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error during prediction: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict_raw")
def predict_raw(payload: RawCustomer = Body(...)):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    if expected_columns is None:
        raise HTTPException(status_code=500, detail="Preprocessor artifact not loaded (models/preprocessor.joblib)")

    try:
        X = preprocess_raw_record(payload.dict())
        proba = float(model.predict_proba(X)[0, 1]) if hasattr(model, "predict_proba") else None
        pred = int(proba >= threshold) if proba is not None else int(model.predict(X)[0])
        return {"prediction": pred, "probability": proba, "threshold": threshold}
    except Exception as e:
        logger.exception("Error predict_raw: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

