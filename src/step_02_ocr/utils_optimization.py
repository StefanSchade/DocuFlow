import os
import cv2
import numpy as np
from PIL import Image
from step_02_ocr.utils_tesseract import tesseract_ocr
import logging

# Constants for fine orientation checks
DEFAULT_SMALL_ROTATION_STEP = 1  # degrees
DEFAULT_MAX_ROTATION_STEPS = 20  # steps
HIGH_CONFIDENCE_THRESHOLD = 60  # Set an appropriate threshold for high confidence

def rotate_image(image, angle, ocr_debug_dir):
    """Rotate the image by a specific angle without cropping."""
    width, height = image.size
    diagonal = int(np.sqrt(width**2 + height**2))
    new_image = Image.new("RGB", (diagonal, diagonal), (255, 255, 255))
    new_image.paste(image, ((diagonal - width) // 2, (diagonal - height) // 2))
    rotated_image = new_image.rotate(angle, expand=True)
    if ocr_debug_dir is not None:
        rotated_image.save(os.path.join(ocr_debug_dir, f"angle_{angle}.jpg"))
    return rotated_image

def check_orientations(image, language, tessdata_dir_config, psm, check_orientation, ocr_debug_dir):
    if check_orientation == 'NONE':
        text, confidence, _ = tesseract_ocr(image, language, tessdata_dir_config, psm)
        return text, 0, confidence

    orientations = [0, 90, 180, 270, 45, 135, 315]
    best_text = ''
    highest_confidence = -1
    final_angle = 0
    baseline_length = 0

    logging.debug("Starting coarse orientation check")

    # Coarse orientation check
    for angle in orientations:
        rotated_image = rotate_image(image, angle, ocr_debug_dir)
        text, confidence, text_length = tesseract_ocr(rotated_image, language, tessdata_dir_config, psm)
        logging.debug(f"Basic check at {angle} degrees: Confidence={confidence}, Text: {text}")

        if confidence > highest_confidence:
            highest_confidence = confidence
            best_text = text
            final_angle = angle
            baseline_length = text_length

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
            adjusted_image = rotate_image(image, adjusted_angle, ocr_debug_dir)
            adjusted_text, adjusted_confidence, adjusted_length = tesseract_ocr(adjusted_image, language, tessdata_dir_config, psm)
            # Penalize the confidence if the length of the text deviates significantly from the baseline
            length_penalty = abs(baseline_length - adjusted_length) / baseline_length
            adjusted_confidence -= length_penalty * adjusted_confidence
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
                adjusted_image = rotate_image(image, adjusted_angle, ocr_debug_dir)
                adjusted_text, adjusted_confidence, adjusted_length = tesseract_ocr(adjusted_image, language, tessdata_dir_config, psm)
                length_penalty = abs(baseline_length - adjusted_length) / baseline_length
                adjusted_confidence -= length_penalty * adjusted_confidence
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