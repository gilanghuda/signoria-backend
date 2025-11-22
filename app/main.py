import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
from app.api.routes.auth_routes import router as auth_router
from app.api.routes.user_routes import router as user_router
from app.api.routes.predict_routes import router as predict_router
from app.core.ml_loader import load_model_safe

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Signoria API",
    description="Signoria Backend API",
    version="1.0.0"
)

# Get configuration from environment
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
USE_HTTPS = os.getenv("USE_HTTPS", "false").lower() == "true"
SSL_CERTFILE = os.getenv("SSL_CERTFILE")
SSL_KEYFILE = os.getenv("SSL_KEYFILE")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Signoria API is running"}

# Include routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(predict_router)

@app.on_event("startup")
async def startup_event():
    """Load ML models on application startup"""
    load_model_safe()

if __name__ == "__main__":
    ssl_keyfile = SSL_KEYFILE if USE_HTTPS else None
    ssl_certfile = SSL_CERTFILE if USE_HTTPS else None
    
    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile
    )
