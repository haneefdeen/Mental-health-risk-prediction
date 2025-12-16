"""
MindScope AI - FastAPI Backend Application
Main application entry point for the mental health analysis platform
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
from pathlib import Path

# Import API routes
from api.routes import auth, analysis, admin, reports
from utils.auth import get_current_user
from models.text_analyzer import TextAnalyzer
from models.image_analyzer import ImageAnalyzer
from models.behavioral_analyzer import BehavioralAnalyzer
from models.fusion_model import FusionModel

# Initialize FastAPI app
app = FastAPI(
    title="MindScope AI",
    description="Multimodal Mental Health Analysis Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global model instances
text_analyzer = None
image_analyzer = None
behavioral_analyzer = None
fusion_model = None

@app.on_event("startup")
async def startup_event():
    """Initialize ML models on startup"""
    global text_analyzer, image_analyzer, behavioral_analyzer, fusion_model
    
    print("🧠 Initializing MindScope AI models...")
    
    try:
        # Initialize models
        text_analyzer = TextAnalyzer()
        image_analyzer = ImageAnalyzer()
        behavioral_analyzer = BehavioralAnalyzer()
        fusion_model = FusionModel()
        
        print("✅ All models loaded successfully")
        
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MindScope AI - Mental Health Analysis Platform",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_loaded": all([
            text_analyzer is not None,
            image_analyzer is not None,
            behavioral_analyzer is not None,
            fusion_model is not None
        ])
    }

# Include API routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

# Serve static files for frontend
if os.path.exists("frontend/dist"):
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")
    
    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        """Serve frontend for all non-API routes"""
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        file_path = Path("frontend/dist") / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        else:
            # Serve index.html for SPA routing
            return FileResponse("frontend/dist/index.html")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
