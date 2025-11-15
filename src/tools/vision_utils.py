"""
Utility functions for vision processing.
Helper functions used by vision tools.
"""

import base64
from pathlib import Path
from typing import Optional, Tuple
import cv2
import numpy as np
from PIL import Image
from langchain_core.messages import HumanMessage
from config.settings import settings


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode an image file to base64 string.
    
    This is needed to send images to VLMs (Vision-Language Models)
    like GPT-4o and Claude.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded string of the image
        
    Business Use Case:
        - Sending images to APIs
        - Storing images in databases
        - Embedding images in JSON/HTML
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Failed to encode image {image_path}: {e}")
    
def load_image_cv2(image_path: str) -> Optional[np.ndarray]:
    """
    Load an image using OpenCV. OpenCV loads image as Numpy array. Returns None if image cannot be loaded.
    Args:
        image_path: Path to the image file

    Returns:
        Numpy array of the image or None if image cannot be loaded
    """
    try:
        return cv2.imread(image_path)
    except Exception as e:
        print(f"Failed to load image {image_path}: {e}")
        return None
    
def load_image_pil(image_path: str) -> Optional[Image.Image]:
    """
    Load an image using PIL ( Python Imaging Library). PIL is better for image metadata like size, format, and color space.
    Args:
        image_path: Path to the image file
        
    Returns:
        PIL Image object of the image or None if image cannot be loaded
    """
    try:
        return Image.open(image_path)
    except Exception as e:
        print(f"Failed to load image {image_path}: {e}")
        return None
    
def get_image_dimensions(image_path: str) -> Optional[Tuple[int, int]]:
    """
    Get the dimensions (width and height) of an image.
    This is useful for checking if an image is too large for a model.
    It also helps in resizing images to fit the model's input requirements.
    Args:
        image_path: Path to the image file

    Returns:
        Tuple of width and height or None if image cannot be loaded

    Business Use Case:
        - Validating image sizes for uploads
        - Checking resolution requirements
        - Asset management systems
    """
    image = load_image_pil(image_path)
    if image:
        return image.size  # returns (width, height)
    return None

def is_color_image(image_path: str) -> bool:
    """
    Check if an image is color (RGB) or grayscale.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        True if color, False if grayscale
        
    Business Use Case:
        - Document processing (receipts are often grayscale)
        - Quality control (products should be in color)
        - Compression optimization (grayscale uses less space)
    """
    image = load_image_cv2(image_path)
    if image is None:
        return False
    
    return len(image.shape) == 3 and image.shape[2] == 3 #returns True if color, False if grayscale
    
def resize_image_if_needed(image_path: str, max_size: int = None) -> Optional[str]:
    """
    Resize an image if it's too large to fit in memory.
    Args:
        image_path: Path to the image file
        max_size: Maximum size (width or height) for the resized image

    Returns:
        Path to resized image, or original path if no resize needed

    Business Use Case:
        - Optimizing images for web display
        - Meeting API size requirements
        - Reducing storage costs
    """
    if max_size is None:
        max_size = settings.max_image_size


    image = load_image_pil(image_path)
    if image is None:
        return None
    
    width, height = image.size
    
    # Check if resize is needed
    if width <= max_size and height <= max_size:
        return image_path
    
    # Calculate new dimensions (maintain aspect ratio)
    if width > height:
        new_width = max_size
        new_height = int(height * (max_size / width))
    else:
        new_height = max_size
        new_width = int(width * (max_size / height))
    
    # Resize and save
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create new filename
    path = Path(image_path)
    new_path = path.parent / f"{path.stem}_resized{path.suffix}"
    
    resized.save(new_path)
    print(f"Resized {width}x{height} -> {new_width}x{new_height}")
    print(f"Saved to: {new_path}")
    
    return str(new_path)

def validate_image_file(image_path: str) -> Tuple[bool, str]:
    """
    Validate if a file is a supported image format.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Business Use Case:
        - File upload validation
        - Security (prevent malicious files)
        - User feedback
    """
    path = Path(image_path)
    
    # Check if file exists
    if not path.exists():
        return False, f"File not found: {image_path}"
    
    # Check if it's a file (not a directory)
    if not path.is_file():
        return False, f"Not a file: {image_path}"
    
    # Check file extension
    supported_extensions = ['.' + fmt for fmt in settings.supported_image_formats]
    if path.suffix.lower() not in supported_extensions:
        return False, f"Unsupported format: {path.suffix}. Supported: {settings.supported_image_formats}"
    
    # Try to load the image
    image = load_image_pil(image_path)
    if image is None:
        return False, "Could not load image (file may be corrupted)"
    
    return True, "Valid image file"

def create_vision_message(text: str, image_path: str) -> HumanMessage:
    """
    Create a multimodal HumanMessage with text and image.
    
    This uses LangChain's new content_blocks format (v1.0).
    
    Args:
        text: Text prompt/question about the image
        image_path: Path to the image file
        
    Returns:
        HumanMessage with multimodal content
        
    Note:
    This is how we send images to VLMs!
    The content is a LIST with both text and image parts.
    
    Example:
        msg = create_vision_message("What's in this image?", "cat.jpg")
        # Can now be sent to GPT-4o for analysis
    """
    is_valid, error_msg = validate_image_file(image_path)
    if not is_valid:
        raise ValueError(f"Invalid image: {error_msg}")
    
    # Encode image to base64
    base64_image = encode_image_to_base64(image_path)


    # Determine MIME type from extension
    ext = Path(image_path).suffix.lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp'
    }
    mime_type = mime_types.get(ext, 'image/jpeg')
    
    # Create multimodal message using content_blocks
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": text
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{base64_image}"
                }
            }
        ]
    )
    
    return message

if __name__ == "__main__":
    print("Testing vision utilities...\n")

    # Create a test image
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    test_image[:, :] = [0, 255, 0]  # Green image
    test_path = "test_green.png"
    cv2.imwrite(test_path, test_image)

    print(f"Created test image: {test_path}")
    print(f"Dimensions: {get_image_dimensions(test_path)}")
    print(f"Is color: {is_color_image(test_path)}")
    print(f"Validation: {validate_image_file(test_path)}")

    print("\nAll utility functions working!")