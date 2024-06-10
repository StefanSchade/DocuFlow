import cv2
import numpy as np
from PIL import Image
from step_02_ocr.utils_tesseract import tesseract_ocr
import logging

# Constants for fine orientation checks
DEFAULT_SMALL_ROTATION_STEP = 1  # degrees
DEFAULT_MAX_ROTATION_STEPS = 10  # steps
HIGH_CONFIDENCE_THRESHOLD = 60  # Set an appropriate threshold for high confidence

def rotate_image(image, angle):
    image = np.array(image)  # Convert PIL Image to NumPy array
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(rotated)  # Convert back to PIL Image if necessary

def check_orientations(image, language, tessdata_dir_config, psm, check_orientation):
    if check_orientation == 'NONE':
        text, confidence = tesseract_ocr(image, language, tessdata_dir_config, psm)
        return text, 0, confidence

    orientations = [0, 90, 180, 270]
    best_text = ''
    highest_confidence = -1
    final_angle = 0

    logging.debug("Starting coarse orientation check")

    # Coarse orientation check
    for angle in orientations:
        rotated_image = rotate_image(image, angle)
        text, confidence = tesseract_ocr(rotated_image, language, tessdata_dir_config, psm)
        logging.debug(f"Coarse check at {angle} degrees: Confidence={confidence}")

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
            adjusted_image = rotate_image(image, adjusted_angle)
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

        # If no improvement was found, try the other direction
        if not improved:
            step = DEFAULT_SMALL_ROTATION_STEP
            improved = True
            while step <= DEFAULT_MAX_ROTATION_STEPS and improved:
                adjusted_angle = final_angle - step
                adjusted_image = rotate_image(image, adjusted_angle)
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
