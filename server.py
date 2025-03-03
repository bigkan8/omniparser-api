#!/usr/bin/env python3
"""
OmniParser Server for Render Deployment
This server loads the OmniParser models and exposes endpoints to parse screenshots.
"""

import os
import sys
import time
import base64
import logging
from typing import Dict, List, Optional, Union, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OmniParser-API")

# Add the OmniParser directory to the path
omniparser_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "OmniParser-master")
sys.path.append(omniparser_dir)

# Configuration
SOM_MODEL_PATH = os.environ.get("SOM_MODEL_PATH", "weights/icon_detect/model.pt")
CAPTION_MODEL_NAME = os.environ.get("CAPTION_MODEL_NAME", "florence2")
CAPTION_MODEL_PATH = os.environ.get("CAPTION_MODEL_PATH", "microsoft/Florence-2-base")
DEVICE = os.environ.get("DEVICE", "cpu")
BOX_THRESHOLD = float(os.environ.get("BOX_THRESHOLD", "0.05"))

# For debug purposes, print all environment variables
print("DEBUG: All environment variables:")
for key, value in os.environ.items():
    if "OMNIPARSER" in key or "MODEL" in key:
        print(f"  {key}: {value}")

# Initialize FastAPI app
app = FastAPI(
    title="OmniParser API",
    description="API for parsing screenshots into structured elements for VerifiedX",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable for OmniParser
omniparser = None

class ParseRequest(BaseModel):
    base64_image: str = Field(..., description="Base64 encoded image data")

def load_omniparser():
    """Load the OmniParser models"""
    global omniparser
    
    try:
        # Import OmniParser here to avoid circular imports
        from util.omniparser import Omniparser
        
        logger.info(f"Loading OmniParser with SOM model from {SOM_MODEL_PATH}")
        logger.info(f"Using caption model: {CAPTION_MODEL_NAME} from {CAPTION_MODEL_PATH}")
        
        config = {
            'som_model_path': SOM_MODEL_PATH,
            'caption_model_name': CAPTION_MODEL_NAME,
            'caption_model_path': CAPTION_MODEL_PATH,
            'device': DEVICE,
            'BOX_TRESHOLD': BOX_THRESHOLD,
            'use_paddleocr': False  # Force using EasyOCR instead of PaddleOCR
        }
        
        # Initialize the OmniParser
        omniparser = Omniparser(config)
        logger.info("OmniParser loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error loading OmniParser: {str(e)}")
        # Allow server to start anyway so we can investigate/debug through API
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize OmniParser when the server starts"""
    load_omniparser()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "OmniParser API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if omniparser is None:
        # OmniParser failed to load but server is running
        return JSONResponse(
            status_code=503,  # Service Unavailable
            content={
                "status": "unavailable", 
                "message": "OmniParser not loaded. Check logs for details.",
                "models": {
                    "som_model_path": SOM_MODEL_PATH,
                    "caption_model_name": CAPTION_MODEL_NAME,
                    "caption_model_path": CAPTION_MODEL_PATH
                }
            }
        )
    else:
        # Everything is working
        return JSONResponse(
            content={
                "status": "healthy",
                "models": {
                    "som_model_path": SOM_MODEL_PATH,
                    "caption_model_name": CAPTION_MODEL_NAME,
                    "caption_model_path": CAPTION_MODEL_PATH
                },
                "device": DEVICE
            }
        )

@app.post("/parse")
async def parse(request: ParseRequest):
    """Parse a screenshot using OmniParser"""
    if omniparser is None:
        raise HTTPException(
            status_code=503,
            detail="OmniParser is not loaded. Please check the service logs."
        )
    
    try:
        print('Start parsing...')
        start = time.time()
        dino_labeled_img, parsed_content_list = omniparser.parse(request.base64_image)
        latency = time.time() - start
        print(f'Parse completed in {latency:.2f} seconds')
        
        return {
            "success": True, 
            "som_image_base64": dino_labeled_img, 
            "elements": parsed_content_list, 
            "latency": latency
        }
    except Exception as e:
        logger.error(f"Error parsing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error parsing image: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    
    # Load OmniParser before starting the server
    load_omniparser()
    
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False) 