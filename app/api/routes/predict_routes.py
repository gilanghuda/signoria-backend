from fastapi import APIRouter, Depends
from app.model.predict import VectorInput, PredictionResponse, HealthCheckResponse
from app.services.predict_services import PredictService
from app.core.middleware.jwt import get_current_user

router = APIRouter(
    prefix="/api/predict",
    tags=["ML Prediction"],
    responses={503: {"description": "Service Unavailable - Model not loaded"}},
)

@router.get("/", tags=["Info"])
async def get_status():
    """Get API status and available endpoints"""
    return PredictService.get_api_status()

@router.post("/number", response_model=PredictionResponse)
async def predict_number(data: VectorInput):
    """Predict SIBI number from vector"""
    return PredictService.predict_vector("number", data.vector)

@router.post("/alphabet", response_model=PredictionResponse)
async def predict_alphabet(data: VectorInput):
    """Predict SIBI alphabet from vector"""
    return PredictService.predict_vector("alphabet", data.vector)

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Check model health status"""
    return PredictService.get_health_status()
