#!/usr/bin/env python3
"""
Script to patch OmniParser for compatibility with Render deployment.
This script should be run after downloading the OmniParser repository.
"""

import os
import sys
import shutil
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("patch")

def patch_utils_file():
    """Patch the utils.py file to use EasyOCR by default"""
    utils_file = "OmniParser-master/util/utils.py"
    
    if not os.path.exists(utils_file):
        logger.error(f"Utils file not found: {utils_file}")
        return False
    
    # Backup the original file
    shutil.copy(utils_file, f"{utils_file}.bak")
    
    # Read the file
    with open(utils_file, 'r') as f:
        content = f.read()
    
    # Add default use_paddleocr parameter to check_ocr_box function
    if "def check_ocr_box(image, display_img=True, output_bb_format='xyxy', easyocr_args=None," in content:
        content = content.replace(
            "def check_ocr_box(image, display_img=True, output_bb_format='xyxy', easyocr_args=None,",
            "def check_ocr_box(image, display_img=True, output_bb_format='xyxy', easyocr_args=None, use_paddleocr=False,"
        )
        
        # Update function calls to pass the use_paddleocr parameter
        if "check_ocr_box(image, display_img=False, output_bb_format='xyxy', easyocr_args={'text_threshold': 0.8})" in content:
            content = content.replace(
                "check_ocr_box(image, display_img=False, output_bb_format='xyxy', easyocr_args={'text_threshold': 0.8})",
                "check_ocr_box(image, display_img=False, output_bb_format='xyxy', easyocr_args={'text_threshold': 0.8}, use_paddleocr=False)"
            )
    
    # Write the modified content back
    with open(utils_file, 'w') as f:
        f.write(content)
    
    logger.info(f"Successfully patched {utils_file}")
    return True

def main():
    logger.info("Patching OmniParser for Render compatibility...")
    
    # Patch utils.py file
    if not patch_utils_file():
        logger.error("Failed to patch utils.py file")
        return 1
    
    logger.info("Patching completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 