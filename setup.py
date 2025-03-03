#!/usr/bin/env python3
"""
Setup script to download the OmniParser repository and prepare for deployment.
"""

import os
import sys
import shutil
import subprocess
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("setup")

def download_omniparser():
    """Download the OmniParser repository"""
    logger.info("Cloning OmniParser repository...")
    
    if os.path.exists("OmniParser-master"):
        logger.info("OmniParser directory already exists, removing...")
        shutil.rmtree("OmniParser-master")
    
    try:
        subprocess.run(
            ["git", "clone", "https://github.com/microsoft/OmniParser.git", "OmniParser-master"],
            check=True
        )
        logger.info("OmniParser repository cloned successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error cloning OmniParser repository: {str(e)}")
        return False

def main():
    logger.info("Setting up OmniParser API for Render deployment...")
    
    # Download OmniParser repository
    if not download_omniparser():
        logger.error("Failed to download OmniParser repository")
        return 1
    
    # Download model weights
    try:
        logger.info("Downloading model weights...")
        subprocess.run(["python", "download_weights.py"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error downloading model weights: {str(e)}")
        return 1
    
    logger.info("Setup completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 