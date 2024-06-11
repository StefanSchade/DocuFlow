# File: step_02_ocr/utils_optimization.py

import os
import numpy as np
from PIL import Image
from step_02_ocr.utils_tesseract import tesseract_ocr
import logging

# Constants for fine orientation checks
DEFAULT_SMALL_ROTATION_STEP = 1  # degrees
DEFAULT_MAX_ROTATION_STEPS = 20  # steps
HIGH_CONFIDENCE_THRESHOLD = 95  # Set an appropriate threshold for high confidence

def rotate_image(image, angle, ocr_debug_dir):
    """Rotate the image by a specific angle without cropping."""
    rotated_image = image.rotate(angle, expand=True)
    if ocr_debug_dir is not None:
        rotated_image.save(os.path.join(ocr_debug_dir, f"angle_{angle}.jpg"))
    return rotated_image

def check_orientations(input_image, language, tessdata_dir_config, psm, check_orientation, ocr_debug_dir):
    if check_orientation == 'NONE':
        text, confidence, _ = tesseract_ocr(input_image, language, tessdata_dir_config, psm, ocr_debug_dir, 0)
        return text, 0, confidence

    orientations = [0, 90, 180, 270]
    best_text = ''
    highest_score = -1
    final_angle = 0
    max_text_length = 0

    logging.debug(f"Basic orientation check with psm={psm}, language={language}")

    # Basic orientation check
    results = []
    for angle in orientations:
        rotated_image = rotate_image(input_image, angle, ocr_debug_dir)
        text, confidence, text_length = tesseract_ocr(rotated_image, language, tessdata_dir_config, psm, ocr_debug_dir, angle)
        logging.debug(f"..... angle={angle} degrees, confidence={confidence}, text length={len(text)}")

        results.append((text, confidence, text_length, angle))
        if text_length > max_text_length:
            max_text_length = text_length

    # Calculate the score based on confidence and normalized text length
    for text, confidence, text_length, angle in results:
        normalized_length = text_length / max_text_length if max_text_length > 0 else 0
        score = confidence * normalized_length  # You can adjust this formula as needed
        logging.debug(f"..... angle={angle} degrees, score={score}")

        if score > highest_score:
            highest_score = score
            best_text = text
            final_angle = angle

    logging.debug(f"Basic orientation correction result: Score={highest_score}, orientation={final_angle}")

    if check_orientation == 'FINE':
        logging.debug(f"Fine orientation check around angle={final_angle}, direction 1")
        step = DEFAULT_SMALL_ROTATION_STEP

        # Fine adjustments in one direction
        improved = True
        while step <= DEFAULT_MAX_ROTATION_STEPS and improved:
            adjusted_angle = final_angle + step
            adjusted_image = rotate_image(input_image, adjusted_angle, ocr_debug_dir)
            adjusted_text, adjusted_confidence, adjusted_length = tesseract_ocr(adjusted_image, language, tessdata_dir_config, psm, ocr_debug_dir, adjusted_angle)
            normalized_length = adjusted_length / max_text_length if max_text_length > 0 else 0
            adjusted_score = adjusted_confidence * normalized_length
            logging.debug(f"Fine check at {adjusted_angle} degrees: Score={adjusted_score}, text length={len(adjusted_text)}")

            if adjusted_score > highest_score:
                highest_score = adjusted_score
                best_text = adjusted_text
                final_angle = adjusted_angle
                improved = True
            else:
                improved = False

            step += 1

        logging.debug(f"Fine orientation check around angle={final_angle}, direction 2")

        # If no improvement was found, try the other direction
        if not improved:
            step = DEFAULT_SMALL_ROTATION_STEP
            improved = True
            while step <= DEFAULT_MAX_ROTATION_STEPS and improved:
                adjusted_angle = final_angle - step
                adjusted_image = rotate_image(input_image, adjusted_angle, ocr_debug_dir)
                adjusted_text, adjusted_confidence, adjusted_length = tesseract_ocr(adjusted_image, language, tessdata_dir_config, psm, ocr_debug_dir, adjusted_angle)
                normalized_length = adjusted_length / max_text_length if max_text_length > 0 else 0
                adjusted_score = adjusted_confidence * normalized_length
                logging.debug(f"Fine check at {adjusted_angle} degrees: Score={adjusted_score}")

                if adjusted_score > highest_score:
                    highest_score = adjusted_score
                    best_text = adjusted_text
                    final_angle = adjusted_angle
                    improved = True
                else:
                    improved = False

                step += 1

    logging.info(f"Orientation correction result: Score={highest_score}, orientation={final_angle}")
    return best_text, final_angle, highest_score
