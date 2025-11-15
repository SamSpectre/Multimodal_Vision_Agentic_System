"""
Basic Vision Tools for image analysis.

These tools can be bound to LLMs and called automatically when needed.
Similar to VendorGuard's calculator tool, but for vision tasks!

BUSINESS USE CASES:
- Asset management systems
- Quality control
- File validation
- Brand monitoring
-Vision Agentic Systems
"""

import cv2
import numpy as np
from langchain_core.tools import tool
from typing import Dict, List, Any
from collections import Counter

from .vision_utils import (
    load_image_cv2,
    load_image_pil,
    get_image_dimensions,
    is_color_image,
    validate_image_file
)
from config.settings import settings

@tool
def get_image_properties(image_path: str) -> Dict[str, any]:
    """
    Get basic properties of an image file.
    
    Returns information about:
    - File size (KB)
    - Dimensions (width x height)
    - Color mode (RGB/Grayscale)
    - Format (JPEG, PNG, etc.)
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with image properties
        
    Business Use Case:
        Asset Management - "Check if uploaded product images meet our requirements"
        Quality Control - "Verify all images are high-resolution RGB"
        File Validation - "Ensure profile pictures are under 5MB"
    
    Example:
        >>> get_image_properties("product.jpg")
        {
            'file_size_kb': 250.5,
            'width': 1920,
            'height': 1080,
            'is_color': True,
            'format': 'JPEG',
            'megapixels': 2.07
        }   
    """
    #Validate image file
    is_valid, error_msg = validate_image_file(image_path)
    if not is_valid:
        raise ValueError(f"Invalid image: {error_msg}")
    
    #Load image
    pil_image = load_image_pil(image_path)
    if pil_image is None:
        raise ValueError(f"Failed to load image: {image_path}")

    #Dimensions
    width, height = pil_image.size
    #File size
    import os
    file_size = os.path.getsize(image_path) / 1024
    #Format
    format = pil_image.format or "Unknown"
    #Check if color
    is_color = is_color_image(image_path)
    #Megapixels
    megapixels = (width * height) / (1000 * 1000)
    return {
        "file_size_kb": round(file_size, 2),
        "width": width,
        "height": height,
        "is_color": is_color,
        "format": format,
        "megapixels": round(megapixels, 2),
        "aspect_ratio": f"{width}:{height}"
    }

@tool
def analyze_image_colors(image_path: str, top_n: int = 5) -> Dict[str, any]:
    """
    Analyze the colors in an image.
    Returns the most common colors and their percentages.
    Args:
        image_path: Path to the image file
        top_n: Number of top colors to return (default: 5)
    Returns:
        Dictionary with color analysis
    Business Use Case:
        - Color analysis for branding
        - Color matching for product images
        - Color palette generation

     Example:
        >>> analyze_image_colors("logo.png", top_n=3)
        {
            'dominant_colors': [
                {'color_name': 'blue', 'rgb': [0, 120, 215], 'percentage': 45.2},
                {'color_name': 'white', 'rgb': [255, 255, 255], 'percentage': 30.5},
                {'color_name': 'black', 'rgb': [0, 0, 0], 'percentage': 15.8}
            ],
            'is_monochrome': False,
            'color_diversity': 'high'
        }
    """
        # Validate image
    is_valid, error_msg = validate_image_file(image_path)
    if not is_valid:
        return {"error": error_msg}
    
    # Load image
    image = load_image_cv2(image_path)
    if image is None:
        return {"error": "Could not load image"}
    
    # Convert BGR to RGB (OpenCV uses BGR by default)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Reshape image to list of pixels
    pixels = image_rgb.reshape(-1, 3)
    
    # Convert to list of tuples for Counter
    pixel_tuples = [tuple(pixel) for pixel in pixels]
    
    # Count pixel frequencies
    color_counts = Counter(pixel_tuples)
    
    # Get top N colors
    top_colors = color_counts.most_common(top_n)
    
    total_pixels = len(pixel_tuples)
    
    # Format results
    dominant_colors = []
    for rgb, count in top_colors:
        percentage = (count / total_pixels) * 100
        color_name = get_color_name(rgb)
        dominant_colors.append({
            "color_name": color_name,
            "rgb": list(rgb),
            "hex": rgb_to_hex(rgb),
            "percentage": round(percentage, 2)
        })
    
    # Calculate color diversity (unique colors / total pixels)
    unique_colors = len(color_counts)
    diversity_ratio = unique_colors / total_pixels
    
    if diversity_ratio < 0.01:
        color_diversity = "low"
    elif diversity_ratio < 0.05:
        color_diversity = "medium"
    else:
        color_diversity = "high"
    
    # Check if monochrome (top color dominates >90%)
    is_monochrome = dominant_colors[0]["percentage"] > 90
    
    return {
        "dominant_colors": dominant_colors,
        "total_unique_colors": unique_colors,
        "is_monochrome": is_monochrome,
        "color_diversity": color_diversity
    }

@tool
def detect_image_quality_issues(image_path: str) -> Dict[str, any]:
    """
    Detect potential quality issues in an image.
    
    Checks for:
    - Low resolution
    - Blur
    - Low contrast
    - Over/under exposure
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with quality assessment
        
     Business Use Case:
        Quality Control - "Reject blurry product photos automatically"
        User Uploads - "Provide feedback on poor image quality"
        Content Review - "Flag low-quality images for manual review"
        
    Example:
        >>> detect_image_quality_issues("product.jpg")
        {
            'is_high_quality': False,
            'issues': ['low_resolution', 'blurry'],
            'resolution_score': 3.2,
            'blur_score': 45.8,
            'contrast_score': 82.1,
            'recommendations': ['Use higher resolution camera', 'Hold camera steady']
        }
    """
        # Validate image
    is_valid, error_msg = validate_image_file(image_path)
    if not is_valid:
        return {"error": error_msg}
    
    # Load image
    image = load_image_cv2(image_path)
    if image is None:
        return {"error": "Could not load image"}
    
    issues = []
    recommendations = []
    
    # 1. Check Resolution
    height, width = image.shape[:2]
    megapixels = (width * height) / 1_000_000
    
    if megapixels < 1.0:
        issues.append("low_resolution")
        recommendations.append("Use higher resolution camera (at least 1MP)")
    
    resolution_score = min(100, megapixels * 20)  # Score out of 100
    
    # 2. Check Blur (using Laplacian variance)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Lower variance = more blur
    blur_score = min(100, laplacian_var / 10)
    
    if laplacian_var < 100:
        issues.append("blurry")
        recommendations.append("Hold camera steady and ensure proper focus")
    
    # 3. Check Contrast
    contrast = gray.std()
    contrast_score = min(100, contrast / 0.8)
    
    if contrast < 30:
        issues.append("low_contrast")
        recommendations.append("Improve lighting conditions")
    
    # 4. Check Exposure (brightness)
    mean_brightness = gray.mean()
    
    if mean_brightness < 50:
        issues.append("underexposed")
        recommendations.append("Increase lighting or camera exposure")
    elif mean_brightness > 200:
        issues.append("overexposed")
        recommendations.append("Reduce lighting or camera exposure")
    
    # Overall quality assessment
    is_high_quality = len(issues) == 0
    
    return {
        "is_high_quality": is_high_quality,
        "issues": issues,
        "resolution_score": round(resolution_score, 1),
        "blur_score": round(blur_score, 1),
        "contrast_score": round(contrast_score, 1),
        "brightness": round(mean_brightness, 1),
        "recommendations": recommendations
    }


# Helper functions (not exposed as tools)

def get_color_name(rgb: tuple) -> str:
    """Get a human-readable color name from RGB values."""
    r, g, b = rgb
    
    # Simple color naming logic
    if r < 50 and g < 50 and b < 50:
        return "black"
    elif r > 200 and g > 200 and b > 200:
        return "white"
    elif r > 150 and g < 100 and b < 100:
        return "red"
    elif r < 100 and g > 150 and b < 100:
        return "green"
    elif r < 100 and g < 100 and b > 150:
        return "blue"
    elif r > 150 and g > 150 and b < 100:
        return "yellow"
    elif r > 150 and g < 100 and b > 150:
        return "magenta"
    elif r < 100 and g > 150 and b > 150:
        return "cyan"
    elif r > 150 and g > 100 and b < 100:
        return "orange"
    elif r > 100 and g < 100 and b > 100:
        return "purple"
    else:
        return "mixed"


def rgb_to_hex(rgb: tuple) -> str:
    """Convert RGB tuple to hex color code."""
    return "#{:02x}{:02x}{:02x}".format(*rgb)


# Export tools list for easy importing
basic_vision_tools = [
    get_image_properties,
    analyze_image_colors,
    detect_image_quality_issues
]


if __name__ == "__main__":
    print(" Testing basic vision tools...\n")
    
    # Create a simple test image
    import numpy as np
    test_image = np.zeros((200, 300, 3), dtype=np.uint8)
    test_image[:100, :] = [255, 0, 0]  # Red top half
    test_image[100:, :] = [0, 0, 255]  # Blue bottom half
    
    test_path = "test_image.png"
    cv2.imwrite(test_path, test_image)
    
    print(f" Created test image: {test_path}\n")
    
    print("1. Testing get_image_properties:")
    result = get_image_properties.invoke({"image_path": test_path})
    print(f"   {result}\n")
    
    print("2. Testing analyze_image_colors:")
    result = analyze_image_colors.invoke({"image_path": test_path})
    print(f"   {result}\n")
    
    print("3. Testing detect_image_quality_issues:")
    result = detect_image_quality_issues.invoke({"image_path": test_path})
    print(f"   {result}\n")
    
    print(" All basic vision tools working!")