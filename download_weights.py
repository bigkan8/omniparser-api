#!/usr/bin/env python3
"""
Script to download the OmniParser model weights from Hugging Face.
"""

import os
import sys
import logging
from huggingface_hub import hf_hub_download, snapshot_download
import shutil

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("download-weights")

def download_icon_detect_model():
    """Download the icon detection model"""
    logger.info("Downloading icon detection model...")
    os.makedirs("weights/icon_detect", exist_ok=True)
    
    try:
        file_path = hf_hub_download(
            repo_id="microsoft/OmniParser-v2.0",
            filename="icon_detect/model.pt",
            local_dir="weights"
        )
        logger.info(f"Icon detection model downloaded to: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error downloading icon detection model: {str(e)}")
        return False

def download_florence_model():
    """Download the Florence model (not needed with HF model)"""
    # We're using the HF model directly, so this is just for reference
    logger.info("Using Florence-2-base model directly from Hugging Face")
    return True

def main():
    logger.info("Downloading OmniParser model weights from Hugging Face...")
    
    # Create weights directory
    os.makedirs("weights", exist_ok=True)
    
    # Download icon detection model
    if not download_icon_detect_model():
        logger.error("Failed to download icon detection model")
        return 1
    
    # Florence model will be loaded directly from HF
    download_florence_model()
    
    logger.info("All model weights downloaded successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 