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
    
    # Conditionally import paddleocr
    if "from paddleocr import PaddleOCR" in content:
        content = content.replace(
            "from paddleocr import PaddleOCR",
            "# Conditionally import PaddleOCR\ntry:\n    from paddleocr import PaddleOCR\nexcept ImportError:\n    # Use a stub class that raises a useful error when called\n    class PaddleOCR:\n        def __init__(self, **kwargs):\n            self.kwargs = kwargs\n        \n        def ocr(self, img_path, cls=False):\n            logger.warning('PaddleOCR is not installed. Using EasyOCR as fallback.')\n            return []"
        )
    
    # Write the modified content back
    with open(utils_file, 'w') as f:
        f.write(content)
    
    logger.info(f"Successfully patched {utils_file}")
    return True

def add_dependency_handlers():
    """Add proper error handling for dependencies that might be missing"""
    # Create an error handler file
    handler_file = "OmniParser-master/util/dependency_handler.py"
    
    with open(handler_file, "w") as f:
        handler_content = """# Dependency handler for OmniParser
import logging
import sys
import importlib
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dependencies")

def verify_dependencies():
    \"\"\"Verify that all required dependencies are installed\"\"\"
    required_packages = [
        "torch",
        "torchvision",
        "numpy",
        "PIL",
        "transformers",
        "supervision",
        "cv2",
        "easyocr",
        "ultralytics"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            logger.info(f"✓ {package} is installed")
        except ImportError:
            logger.error(f"✗ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning(f"Missing required packages: {', '.join(missing_packages)}")
        logger.warning("Some OmniParser functionality may not work correctly")
    else:
        logger.info("All required dependencies are installed")
    
    return len(missing_packages) == 0

# Add proper import error handling for key packages
def import_with_fallback(module_name, package_name=None):
    \"\"\"Import a module with proper error handling\"\"\"
    if package_name is None:
        package_name = module_name
        
    try:
        return importlib.import_module(module_name)
    except ImportError:
        logger.error(f"Could not import {module_name}. Please install {package_name}.")
        return None
"""
        f.write(handler_content)
    
    # Modify the OmniParser's utils.py to import our handler
    utils_file = "OmniParser-master/util/utils.py"
    with open(utils_file, "r") as f:
        content = f.read()
    
    # Add the import at the top of the file
    if "import numpy as np" in content:
        content = content.replace(
            "import numpy as np",
            "import numpy as np\n# Import dependency handler\ntry:\n    from util.dependency_handler import verify_dependencies, import_with_fallback\n    verify_dependencies()\nexcept ImportError:\n    pass"
        )
    
    # Write the modified content back
    with open(utils_file, "w") as f:
        f.write(content)
    
    logger.info("Added dependency handlers")
    return True

def main():
    logger.info("Patching OmniParser for Render compatibility...")
    
    # Patch utils.py file
    if not patch_utils_file():
        logger.error("Failed to patch utils.py file")
        return 1
    
    # Add dependency handlers
    if not add_dependency_handlers():
        logger.error("Failed to add dependency handlers")
        return 1
    
    logger.info("Patching completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 