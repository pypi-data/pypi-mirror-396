import cv2
import numpy as np
import base64
import os

def preprocess_image(image_input):
    """
    Reads an image (path or base64) and preprocesses it for OCR.
    Returns the preprocessed image.
    """
    img = None
    
    # Check if input is a valid file path
    if os.path.isfile(image_input):
        img = cv2.imread(image_input)
    else:
        # Try to decode as base64
        try:
            # Remove header if present (e.g. "data:image/jpeg;base64,")
            if "," in image_input:
                image_input = image_input.split(",")[1]
                
            decoded_data = base64.b64decode(image_input)
            np_data = np.frombuffer(decoded_data, np.uint8)
            img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
        except Exception:
            pass
            
    if img is None:
        raise ValueError(f"Could not read image from input. Ensure it is a valid file path or base64 string.")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Resize image logic
    height, width = gray.shape[:2]
    
    if width < 1000:
        # Upscale for better OCR on small images
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    elif width > 2000:
        # Downscale for performance on very large images
        scale = 2000 / width
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    # Apply some noise reduction
    # GaussianBlur is good for removing Gaussian noise
    # blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # Return grayscale directly, let Tesseract handle thresholding
    
    # Morphological Opening is expensive and often unnecessary for high-res images
    # kernel = np.ones((2,2), np.uint8)
    # gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    
    return gray

def crop_mrz_region(image):
    """
    Attempts to crop the MRZ region from the passport image.
    This is a heuristic approach and might need tuning.
    For now, we'll return the bottom 25% of the image as a simple heuristic,
    as MRZ is usually at the bottom.
    """
    height, width = image.shape[:2]
    # MRZ is typically at the bottom. Let's take the bottom 30% to be safe.
    # A more robust way would be to use contours to find the text lines.
    start_row = int(height * 0.70)
    cropped = image[start_row:height, 0:width]
    return cropped
