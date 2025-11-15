"""
OCR Tools for text extraction from images using EasyOCR and Tesseract.

These tools enable the agent to extract and analyze text from images,
supporting document processing, receipt scanning, and text recognition.
"""

import easyocr
import pytesseract
from PIL import Image
import numpy as np
import cv2
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

# Initialize EasyOCR reader (supports multiple languages)
# We'll use English by default, but you can add more languages as needed
_reader = None


def get_easyocr_reader(languages: List[str] = None) -> easyocr.Reader:
    """
    Get or initialize the EasyOCR reader (singleton pattern for efficiency).

    Args:
        languages: List of language codes (default: ['en'])

    Returns:
        easyocr.Reader instance
    """
    global _reader
    if _reader is None:
        if languages is None:
            languages = ['en']
        _reader = easyocr.Reader(languages, gpu=False)  # Set gpu=True if CUDA available
    return _reader


def extract_text_from_image(image_path: str, method: str = "easyocr") -> str:
    """
    Extract all text content from an image using OCR.

    This tool reads text from images including documents, screenshots, signs,
    receipts, forms, and any image containing readable text. It's ideal for:
    - Document digitization
    - Receipt/invoice processing
    - Screenshot text extraction
    - Sign and label reading
    - Form data extraction

    Args:
        image_path: Path to the image file containing text
        method: OCR method to use ("easyocr" or "tesseract")

    Returns:
        Extracted text as a string, with line breaks preserved.
        Returns error message if extraction fails.

    Example:
        >>> extract_text_from_image("receipt.jpg")
        'STORE NAME\\nItem 1: $10.00\\nItem 2: $5.00\\nTotal: $15.00'
    """
    try:
        # Validate image path
        if not Path(image_path).exists():
            return f"Error: Image file not found at {image_path}"

        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return f"Error: Could not load image from {image_path}"

        if method.lower() == "easyocr":
            # Use EasyOCR (more accurate, supports multiple languages)
            reader = get_easyocr_reader()
            results = reader.readtext(image_path)

            if not results:
                return "No text detected in the image."

            # Extract text and join with line breaks
            extracted_text = "\n".join([result[1] for result in results])

            # Add confidence info
            avg_confidence = sum(result[2] for result in results) / len(results)
            return f"{extracted_text}\n\n[OCR Confidence: {avg_confidence:.2%}]"

        elif method.lower() == "tesseract":
            # Use Tesseract (faster, good for clear text)
            pil_image = Image.open(image_path)
            text = pytesseract.image_to_string(pil_image)

            if not text.strip():
                return "No text detected in the image."

            return text.strip()

        else:
            return f"Error: Unknown OCR method '{method}'. Use 'easyocr' or 'tesseract'."

    except Exception as e:
        return f"Error during text extraction: {str(e)}"


def detect_text_regions(image_path: str, include_confidence: bool = True) -> str:
    """
    Detect and locate text regions in an image with bounding boxes and confidence scores.

    This tool identifies where text appears in an image and provides detailed
    information about each detected text region including:
    - Text content
    - Bounding box coordinates
    - Confidence score
    - Spatial layout information

    Useful for:
    - Document layout analysis
    - Form field detection
    - Multi-region text extraction
    - Text localization tasks
    - Quality assessment

    Args:
        image_path: Path to the image file
        include_confidence: Whether to include confidence scores in output

    Returns:
        JSON string containing detected text regions with their locations and properties.

    Example output:
        {
            "total_regions": 3,
            "image_size": {"width": 800, "height": 600},
            "regions": [
                {
                    "text": "Hello World",
                    "bbox": [[10, 20], [100, 20], [100, 40], [10, 40]],
                    "confidence": 0.95,
                    "center": {"x": 55, "y": 30}
                }
            ]
        }
    """
    try:
        # Validate image path
        if not Path(image_path).exists():
            return json.dumps({"error": f"Image file not found at {image_path}"})

        # Load image to get dimensions
        image = cv2.imread(image_path)
        if image is None:
            return json.dumps({"error": f"Could not load image from {image_path}"})

        height, width = image.shape[:2]

        # Use EasyOCR for text detection with bounding boxes
        reader = get_easyocr_reader()
        results = reader.readtext(image_path)

        if not results:
            return json.dumps({
                "total_regions": 0,
                "image_size": {"width": width, "height": height},
                "regions": [],
                "message": "No text detected in the image."
            })

        # Process results into structured format
        regions = []
        for bbox, text, confidence in results:
            # Calculate center point
            center_x = sum(point[0] for point in bbox) / 4
            center_y = sum(point[1] for point in bbox) / 4

            region_info = {
                "text": text,
                "bbox": [[int(x), int(y)] for x, y in bbox],
                "center": {"x": int(center_x), "y": int(center_y)}
            }

            if include_confidence:
                region_info["confidence"] = round(confidence, 3)

            regions.append(region_info)

        # Sort regions by vertical position (top to bottom)
        regions.sort(key=lambda r: r["center"]["y"])

        result = {
            "total_regions": len(regions),
            "image_size": {"width": width, "height": height},
            "regions": regions,
            "average_confidence": round(sum(r.get("confidence", 0) for r in regions) / len(regions), 3) if include_confidence else None
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error during text region detection: {str(e)}"})


def analyze_document_structure(image_path: str) -> str:
    """
    Analyze the structure and layout of a document image.

    This tool provides high-level analysis of document structure including:
    - Text density and distribution
    - Estimated reading order
    - Document type hints (receipt, form, article, etc.)
    - Language detection
    - Text orientation

    Useful for:
    - Document classification
    - Layout understanding
    - Reading order determination
    - Multi-language document processing

    Args:
        image_path: Path to the document image

    Returns:
        JSON string with document structure analysis
    """
    try:
        # Validate image path
        if not Path(image_path).exists():
            return json.dumps({"error": f"Image file not found at {image_path}"})

        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return json.dumps({"error": f"Could not load image from {image_path}"})

        height, width = image.shape[:2]

        # Get text regions
        reader = get_easyocr_reader()
        results = reader.readtext(image_path)

        if not results:
            return json.dumps({
                "document_type": "unknown",
                "text_regions": 0,
                "message": "No text detected for structure analysis"
            })

        # Analyze structure
        total_text_length = sum(len(text) for _, text, _ in results)
        avg_confidence = sum(conf for _, _, conf in results) / len(results)

        # Calculate text density (characters per 1000 pixels)
        text_density = (total_text_length / (width * height)) * 1000

        # Analyze vertical distribution
        y_positions = [sum(point[1] for point in bbox) / 4 for bbox, _, _ in results]
        top_heavy = sum(1 for y in y_positions if y < height / 3) / len(y_positions)

        # Simple document type heuristic
        if len(results) < 10 and text_density < 0.5:
            doc_type = "sign_or_label"
        elif text_density < 1.0 and top_heavy > 0.6:
            doc_type = "receipt_or_invoice"
        elif text_density > 2.0:
            doc_type = "dense_document"
        else:
            doc_type = "standard_document"

        # Create reading order (top to bottom, left to right)
        reading_order = []
        for bbox, text, conf in sorted(results, key=lambda r: (r[0][0][1], r[0][0][0])):
            reading_order.append({
                "text": text,
                "confidence": round(conf, 3)
            })

        analysis = {
            "document_type": doc_type,
            "total_text_regions": len(results),
            "total_characters": total_text_length,
            "text_density": round(text_density, 2),
            "average_confidence": round(avg_confidence, 3),
            "image_dimensions": {"width": width, "height": height},
            "reading_order": reading_order[:10],  # First 10 items
            "layout_hints": {
                "top_heavy": top_heavy > 0.5,
                "multi_column": False  # Could be enhanced with column detection
            }
        }

        return json.dumps(analysis, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error during document analysis: {str(e)}"})


# Tool metadata for LangChain integration
TOOL_DESCRIPTIONS = {
    "extract_text_from_image": "Extract all text from an image (documents, receipts, screenshots, signs)",
    "detect_text_regions": "Detect and locate text regions with bounding boxes and confidence scores",
    "analyze_document_structure": "Analyze document layout, structure, and reading order"
}
