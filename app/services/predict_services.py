import numpy as np
import logging
import traceback
from fastapi import HTTPException, status
from app.core.ml_loader import get_models

logger = logging.getLogger(__name__)

class PredictService:
    @staticmethod
    def predict_vector(model_name: str, vector: list) -> dict:
        """Predict using specified model"""
        models, label_maps, inv_label = get_models()
        
        if models[model_name] is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"{model_name} model not loaded"
            )
        
        try:
            logger.info(f"Predicting with {model_name} model. Vector length: {len(vector)}")
            
            # Convert to numpy array
            vec = np.array(vector, dtype=np.float32)
            
            # Validate vector shape
            if vec.ndim != 1:
                vec = vec.flatten()
            
            # Get predictions
            probs = models[model_name].predict_proba([vec])[0]
            idx = np.argmax(probs)
            label = inv_label[model_name][idx]
            confidence = float(probs[idx])
            
            # Get top 3 predictions
            top_3_indices = np.argsort(probs)[-3:][::-1]
            top_3 = {
                inv_label[model_name][i]: float(probs[i]) 
                for i in top_3_indices
            }
            
            logger.info(f"Prediction: {label} (confidence: {confidence:.2f})")
            
            return {
                "label": label,
                "confidence": confidence,
                "top_3": top_3
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    @staticmethod
    def get_health_status() -> dict:
        """Get model loading status"""
        models, _, _ = get_models()
        
        return {
            "number_model": "loaded" if models["number"] else "missing",
            "alphabet_model": "loaded" if models["alphabet"] else "missing"
        }
    
    @staticmethod
    def get_api_status() -> dict:
        """Get API status"""
        models, label_maps, _ = get_models()
        
        return {
            "message": "SIBI MLP Prediction API",
            "endpoints": ["/api/predict/number", "/api/predict/alphabet"],
            "status": {
                "number_model_loaded": models["number"] is not None,
                "alphabet_model_loaded": models["alphabet"] is not None,
                "number_classes": len(label_maps["number"]) if label_maps["number"] else 0,
                "alphabet_classes": len(label_maps["alphabet"]) if label_maps["alphabet"] else 0
            }
        }
