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

def create_openai_mock():
    """Create a mock OpenAI module to handle imports"""
    # Create a directory for our mock modules
    os.makedirs("OmniParser-master/mocks", exist_ok=True)
    
    # Create an __init__.py file
    with open("OmniParser-master/mocks/__init__.py", "w") as f:
        f.write("# Mock modules package\n")
    
    # Create a mock openai module
    with open("OmniParser-master/mocks/openai.py", "w") as f:
        f.write("""# Mock OpenAI module
class OpenAI:
    def __init__(self, api_key=None, **kwargs):
        self.api_key = api_key
        
    def chat(self):
        return ChatCompletions()

class ChatCompletions:
    def create(self, *args, **kwargs):
        return {"choices": [{"message": {"content": "This is a mock response from the OpenAI API."}}]}
""")
    
    # Create a mock patch for sys.modules
    with open("OmniParser-master/util/openai_patch.py", "w") as f:
        f.write("""# OpenAI patch for OmniParser
import sys
import importlib.util
import os

# Add the mocks directory to sys.path
mocks_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mocks")
sys.path.insert(0, mocks_dir)

# Check if openai is already imported
if "openai" not in sys.modules:
    try:
        # Try to import the real openai module
        import openai
    except ImportError:
        # If it fails, use our mock
        import mocks.openai as openai
        sys.modules["openai"] = openai
""")
    
    # Modify the OmniParser's utils.py to import our patch
    utils_file = "OmniParser-master/util/utils.py"
    with open(utils_file, "r") as f:
        content = f.read()
    
    # Add the import at the top of the file
    if "import numpy as np" in content:
        content = content.replace(
            "import numpy as np",
            "import numpy as np\n# Import OpenAI patch\ntry:\n    from util.openai_patch import *\nexcept ImportError:\n    pass"
        )
    
    # Write the modified content back
    with open(utils_file, "w") as f:
        f.write(content)
    
    logger.info("Created OpenAI mock and patch")
    return True

def main():
    logger.info("Patching OmniParser for Render compatibility...")
    
    # Patch utils.py file
    if not patch_utils_file():
        logger.error("Failed to patch utils.py file")
        return 1
    
    # Create OpenAI mock
    if not create_openai_mock():
        logger.error("Failed to create OpenAI mock")
        return 1
    
    logger.info("Patching completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 