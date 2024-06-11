import os
import cv2
import numpy as np
from PIL import Image
from step_02_ocr.utils_tesseract import tesseract_ocr
import logging

# Constants for fine orientation checks
DEFAULT_SMALL_ROTATION_STEP = 2  # degrees
DEFAULT_MAX_ROTATION_STEPS = 11  # steps
HIGH_CONFIDENCE_THRESHOLD = 90  # Set an appropriate threshold for high confidence

def rotate_image(image, angle, ocr_debug_dir):
    """Rotate the image by a specific angle without cropping."""
    width, height = image.size
    diagonal = int(np.sqrt(width**2 + height**2))
    new_image = Image.new("RGB", (diagonal, diagonal), (255, 255, 255))
    new_image.paste(image, ((diagonal - width) // 2, (diagonal - height) // 2))
    rotated_image = new_image.rotate(angle, expand=True)
    
    if ocr_debug_dir is not None:
        debug_image_path = os.path.join(ocr_debug_dir, f"angle_{angle}.jpg")
        rotated_image_cv = np.array(rotated_image)
        rotated_image_cv = cv2.cvtColor(rotated_image_cv, cv2.COLOR_RGB2BGR)
        cv2.imwrite(debug_image_path, rotated_image_cv)
        
    return rotated_image


def check_orientations(input_image, language, tessdata_dir_config, psm, check_orientation, ocr_debug_dir):
    if check_orientation == 'NONE':
        text, confidence = tesseract_ocr(input_image, language, tessdata_dir_config, psm)
        return text, 0, confidence

    orientations = [0, 90, 180, 270, 45, 135, 315]
    best_text = ''
    highest_confidence = -1
    final_angle = 0

    logging.debug("Starting coarse orientation check")

    # Basic orientation check
    for angle in orientations:
        rotated_image = rotate_image(input_image, angle, ocr_debug_dir)
        text, confidence = tesseract_ocr(rotated_image, language, tessdata_dir_config, psm)
        logging.debug(f"Basic check at {angle}, degrees: Confidence={confidence}, Text: {text}")

        if confidence > highest_confidence:
            highest_confidence = confidence
            best_text = text
            final_angle = angle

        # Early stopping if confidence is high enough
        if confidence >= HIGH_CONFIDENCE_THRESHOLD:
            logging.debug(f"High confidence {confidence} at {angle} degrees, stopping coarse check early.")
            break

    logging.debug(f"Basic orientation correction result: Confidence={highest_confidence}, orientation={final_angle}")

    if check_orientation == 'FINE':
        logging.debug("Starting fine orientation check")
        step = DEFAULT_SMALL_ROTATION_STEP

        # Fine adjustments in one direction
        improved = True
        while step <= DEFAULT_MAX_ROTATION_STEPS and improved:
            adjusted_angle = final_angle + step
            adjusted_image = rotate_image(input_image, adjusted_angle, ocr_debug_dir)
            adjusted_text, adjusted_confidence = tesseract_ocr(adjusted_image, language, tessdata_dir_config, psm)
            logging.debug(f"Fine check at {adjusted_angle} degrees: Confidence={adjusted_confidence}, Text={adjusted_text}")

            if adjusted_confidence > highest_confidence:
                highest_confidence = adjusted_confidence
                best_text = adjusted_text
                final_angle = adjusted_angle
                improved = True
            else:
                improved = False

            step += 1

        # If no improvement was found, try the other direction
        if not improved:
            step = DEFAULT_SMALL_ROTATION_STEP
            improved = True
            while step <= DEFAULT_MAX_ROTATION_STEPS and improved:
                adjusted_angle = final_angle - step
                adjusted_image = rotate_image(input_image, adjusted_angle, ocr_debug_dir)
                adjusted_text, adjusted_confidence = tesseract_ocr(adjusted_image, language, tessdata_dir_config, psm)
                logging.debug(f"Fine check at {adjusted_angle} degrees: Confidence={adjusted_confidence}")

                if adjusted_confidence > highest_confidence:
                    highest_confidence = adjusted_confidence
                    best_text = adjusted_text
                    final_angle = adjusted_angle
                    improved = True
                else:
                    improved = False

                step += 1

    logging.info(f"Orientation correction result: Confidence={highest_confidence}, orientation={final_angle}")
    return best_text, final_angle, highest_confidence
