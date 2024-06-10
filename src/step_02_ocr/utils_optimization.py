import cv2
import pytesseract
import numpy as np
from PIL import Image

def rotate_image(image, angle):
    image = np.array(image)  # Convert PIL Image to NumPy array
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(rotated)  # Convert back to PIL Image if necessary

def check_orientations(image, language, tessdata_dir_config, psm):
    orientations = [0, 90, 180, 270]
    best_text = ''
    highest_confidence = -1
    final_angle = 0

    for angle in orientations:
        rotated_image = rotate_image(image, angle)
        text, confidence = tesseract_ocr(rotated_image, language, tessdata_dir_config, psm)
        if confidence > highest_confidence:
            highest_confidence = confidence
            best_text = text
            final_angle = angle
        if confidence >= 60:
            break

    return best_text, final_angle, highest_confidence
