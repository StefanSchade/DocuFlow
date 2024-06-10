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

    # Fine orientation check
    if check_orientation > 1:
        logging.debug("Starting fine orientation check")
        best_confidence_found = highest_confidence
        step = DEFAULT_SMALL_ROTATION_STEP
        improved = True

        while step <= DEFAULT_MAX_ROTATION_STEPS and improved:
            # Fine adjustments clockwise
            adjusted_angle_clockwise = final_angle + step
            adjusted_image_clockwise = rotate_image(image, adjusted_angle_clockwise)
            adjusted_text_clockwise, adjusted_confidence_clockwise = tesseract_ocr(adjusted_image_clockwise, language, tessdata_dir_config, psm)
            logging.debug(f"Fine check at {adjusted_angle_clockwise} degrees: Confidence={adjusted_confidence_clockwise}")

            # Fine adjustments counter-clockwise
            adjusted_angle_counterclockwise = final_angle - step
            adjusted_image_counterclockwise = rotate_image(image, adjusted_angle_counterclockwise)
            adjusted_text_counterclockwise, adjusted_confidence_counterclockwise = tesseract_ocr(adjusted_image_counterclockwise, language, tessdata_dir_config, psm)
            logging.debug(f"Fine check at {adjusted_angle_counterclockwise} degrees: Confidence={adjusted_confidence_counterclockwise}")

            # Determine the best fine-tuned angle
            if adjusted_confidence_clockwise > best_confidence_found:
                best_confidence_found = adjusted_confidence_clockwise
                best_text = adjusted_text_clockwise
                final_angle = adjusted_angle_clockwise
                improved = True
            elif adjusted_confidence_counterclockwise > best_confidence_found:
                best_confidence_found = adjusted_confidence_counterclockwise
                best_text = adjusted_text_counterclockwise
                final_angle = adjusted_angle_counterclockwise
                improved = True
            else:
                improved = False
            
            step += 1

    logging.info(f"Orientation correction result: Confidence={best_confidence_found}, orientation={final_angle}")
    return best_text, final_angle, best_confidence_found
