from pydantic import BaseModel
from typing import Dict

class VectorInput(BaseModel):
    vector: list

class PredictionResponse(BaseModel):
    label: str
    confidence: float
    top_3: Dict[str, float]

class HealthCheckResponse(BaseModel):
    number_model: str
    alphabet_model: str
