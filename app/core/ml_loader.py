import os
import logging
import traceback
import joblib
import numpy as np
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global models storage
models = {
    "number": None,
    "alphabet": None
}
label_maps = {
    "number": None,
    "alphabet": None
}
inv_label = {
    "number": None,
    "alphabet": None
}

def get_ml_directory():
    """Get ML models directory path"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'ml')

def load_model_safe():
    """Load models safely - can be called from main.py startup"""
    global models, label_maps, inv_label
    
    try:
        ml_dir = get_ml_directory()
        logger.info(f"📁 ML directory: {ml_dir}")
        
        # Load number model
        try:
            logger.info("🔹 Loading Number model...")
            number_model_path = os.path.join(ml_dir, 'signoria_number_model.pkl')
            number_label_path = os.path.join(ml_dir, 'signoria_number_label.npy')
            
            if not os.path.exists(number_model_path):
                logger.error(f"Number model file not found at {number_model_path}")
            else:
                models["number"] = joblib.load(number_model_path)
                label_maps["number"] = np.load(number_label_path, allow_pickle=True).item()
                inv_label["number"] = {v: k for k, v in label_maps["number"].items()}
                logger.info(f"Loaded number model ({len(label_maps['number'])} classes)")
        except Exception as e:
            logger.error(f"Failed to load NUMBER model: {e}")
            traceback.print_exc()

        # Load alphabet model
        try:
            logger.info("🔹 Loading Alphabet model...")
            alphabet_model_path = os.path.join(ml_dir, 'signoria_alphabet_model.pkl')
            alphabet_label_path = os.path.join(ml_dir, 'signoria_alphabet_label.npy')
            
            if not os.path.exists(alphabet_model_path):
                logger.error(f"Alphabet model file not found at {alphabet_model_path}")
            else:
                models["alphabet"] = joblib.load(alphabet_model_path)
                label_maps["alphabet"] = np.load(alphabet_label_path, allow_pickle=True).item()
                inv_label["alphabet"] = {v: k for k, v in label_maps["alphabet"].items()}
                logger.info(f"Loaded alphabet model ({len(label_maps['alphabet'])} classes)")
        except Exception as e:
            logger.error(f"Failed to load ALPHABET model: {e}")
            traceback.print_exc()
            
    except Exception as e:
        logger.error(f"Error in load_model_safe: {e}")
        traceback.print_exc()

def get_models():
    """Get loaded models"""
    return models, label_maps, inv_label
