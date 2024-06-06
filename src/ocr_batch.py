import argparse
import os
import pytesseract
from PIL import Image
import cv2
import numpy as np
import logging

# Constants for default paths
DEFAULT_TESSDATA_DIR = '/usr/share/tesseract-ocr/4.00/tessdata'
DEFAULT_LANGUAGE = 'eng'
DEFAULT_PSM = 6
DEFAULT_THRESHOLD = 0
DEFAULT_SMALL_ROTATION_STEP = 1  # degrees
DEFAULT_MAX_ROTATION_STEPS = 10  # steps

def load_valid_languages(tessdata_dir):
    try:
        return [f.split('.')[0] for f in os.listdir(tessdata_dir) if f.endswith('.traineddata')]
    except FileNotFoundError:
        logging.error(f"Tessdata directory {tessdata_dir} not found.")
        return []

def validate_language(language, valid_languages):
    if language not in valid_languages:
        raise ValueError(f"Invalid language '{language}'. Valid options are: {', '.join(valid_languages)}")

def preprocess_image(image, args):
    # Convert to grayscale
    if args.grayscale:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Noise removal
    if args.remove_noise:
        image = cv2.medianBlur(image, 5)
    
    # Thresholding
    if args.threshold > 0:
        _, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Dilation
    if args.dilate:
        kernel = np.ones((5, 5), np.uint8)
        image = cv2.dilate(image, kernel, iterations=1)
    
    # Erosion
    if args.erode:
        kernel = np.ones((5, 5), np.uint8)
        image = cv2.erode(image, kernel, iterations=1)
    
    # Opening (erosion followed by dilation)
    if args.opening:
        kernel = np.ones((5, 5), np.uint8)
        image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    
    # Canny edge detection
    if args.canny:
        image = cv2.Canny(image, 100, 200)
    
    # Deskewing
    if args.deskew:
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        image = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    return image

def tesseract_ocr(image, language, tessdata_dir_config, psm):
    config = f'--psm {psm} -l {language} {tessdata_dir_config}'
    data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)

    lines = {}
    for i, word in enumerate(data['text']):
        if int(data['conf'][i]) > 45:  # Only consider confident recognitions
            line_num = data['line_num'][i]
            if line_num in lines:
                lines[line_num].append(word)
            else:
                lines[line_num] = [word]

    text = '\n'.join([' '.join(lines[line]) for line in sorted(lines.keys())])
    average_confidence = sum(data['conf']) / len(data['conf']) if len(data['conf']) > 0 else 0
    logging.debug(f"Processed text with average confidence: {average_confidence}")
    return text, average_confidence

def check_orientations(image, language, tessdata_dir_config, psm, check_orientation):
    orientations = [0, 90, 180, 270]
    best_text = ''
    highest_confidence = -1
    best_confidence_found = -1
    final_angle = 0

    # Coarse orientation check
    for angle in orientations:
        rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE if angle == 90 else 
                                            cv2.ROTATE_180 if angle == 180 else 
                                            cv2.ROTATE_90_COUNTERCLOCKWISE if angle == 270 else 0)
        text, confidence = tesseract_ocr(rotated_image, language, tessdata_dir_config, psm)
        if confidence > highest_confidence:
            highest_confidence = confidence
            best_text = text
            final_angle = angle
            if confidence > 60:  # High confidence threshold to stop early
                break

    best_confidence_found = highest_confidence
    logging.debug(f"Basic orientation correction result: Confidence={highest_confidence}, orientation={final_angle}")

    # Fine orientation check
    if check_orientation > 1:
        direction = 1
        step = DEFAULT_SMALL_ROTATION_STEP
        while step <= DEFAULT_MAX_ROTATION_STEPS:
            adjusted_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE if angle == 90 else 
                                               cv2.ROTATE_180 if angle == 180 else 
                                               cv2.ROTATE_90_COUNTERCLOCKWISE if angle == 270 else 0)
            adjusted_image = cv2.rotate(adjusted_image, direction * step)
            adjusted_text, adjusted_confidence = tesseract_ocr(adjusted_image, language, tessdata_dir_config, psm)
            if adjusted_confidence > best_confidence_found:
                best_confidence_found = adjusted_confidence
                final_angle += direction * step
                best_text = adjusted_text
                step += 1
            else:
                # Switch direction if no improvement
                direction *= -1
                step = 1 if direction == -1 else step
                if direction == -1:
                    break

    logging.info(f"Orientation correction result: Confidence={best_confidence_found}, orientation={final_angle}")
    return best_text, final_angle, best_confidence_found

def save_preprocessed_image(image, input_path, args):
    filename, ext = os.path.splitext(os.path.basename(input_path))
    arg_str = '_'.join([f'{k}-{v}' for k, v in vars(args).items() if v is not None and k not in ['input_directory', 'log_level', 'save_preprocessed']])
    save_path = os.path.join(os.path.dirname(input_path), f'{filename}_preprocessed_{arg_str}{ext}')
    cv2.imwrite(save_path, image)
    logging.debug(f"Saved preprocessed image to: {save_path}")

def process_images(input_dir, language, save_preprocessed, threshold, tessdata_dir, check_orientation, psm, args):
    tessdata_dir_config = f'--tessdata-dir "{tessdata_dir}"'
    output_file = os.path.join(input_dir, 'ocr_result.txt')

    image_files = sorted([f for f in os.listdir(input_dir) if f.endswith(('.jpeg', '.jpg', '.png'))])

    with open(output_file, 'w', encoding='utf-8') as file_out:
        for index, filename in enumerate(image_files, start=1):
            full_path = os.path.join(input_dir, filename)
            img = cv2.imread(full_path)
            img = preprocess_image(img, args)

            if save_preprocessed:
                save_preprocessed_image(img, full_path, args)

            if check_orientation:
                text, final_angle, confidence = check_orientations(img, language, tessdata_dir_config, psm, check_orientation)
            else:
                text, confidence = tesseract_ocr(img, language, tessdata_dir_config, psm)
                final_angle = 0

            json_output = {"new_page": True, "number": index, "file": filename, "final_angle": final_angle, "confidence": confidence}
            file_out.write(f"'{json_output}'\n{text}\n")
            logging.debug(f"Processed {filename} with final angle: {final_angle}")

def main():
    parser = argparse.ArgumentParser(description='Process a batch of images with Tesseract OCR.')
    parser.add_argument('input_directory', type=str, help='Directory containing input images')
    parser.add_argument('--language', type=str, default=DEFAULT_LANGUAGE, help='Language for Tesseract OCR')
    parser.add_argument('--save-preprocessed', action='store_true', help='Save preprocessed images')
    parser.add_argument('--threshold', type=int, default=DEFAULT_THRESHOLD, help='Threshold for binarization')
    parser.add_argument('--check-orientation', type=int, choices=[0, 1, 2], default=0, help='Check and correct orientation')
    parser.add_argument('--psm', type=int, choices=list(range(14)), default=DEFAULT_PSM, help='Tesseract Page Segmentation Mode (PSM)')
    parser.add_argument('--sharpen', action='store_true', help='Apply sharpening filter before OCR')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help='Set the logging level')
    parser.add_argument('--grayscale', action='store_true', help='Convert image to grayscale')
    parser.add_argument('--remove-noise', action='store_true', help='Apply noise removal')
    parser.add_argument('--dilate', action='store_true', help='Apply dilation')
    parser.add_argument('--erode', action='store_true', help='Apply erosion')
    parser.add_argument('--opening', action='store_true', help='Apply opening (erosion followed by dilation)')
    parser.add_argument('--canny', action='store_true', help='Apply Canny edge detection')
    parser.add_argument('--deskew', action='store_true', help='Apply deskewing (skew correction)')

    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    logging.debug(f"Received arguments: {args}")

    if not os.path.isdir(args.input_directory):
        logging.error(f"Input directory {args.input_directory} does not exist")
        return

    os.environ['TESSDATA_PREFIX'] = DEFAULT_TESSDATA_DIR

    valid_languages = load_valid_languages(DEFAULT_TESSDATA_DIR)
    try:
        validate_language(args.language, valid_languages)
    except ValueError as e:
        logging.error(e)
        return

    logging.debug(f"Processed arguments: {args}")

    process_images(args.input_directory, args.language, args.save_preprocessed, args.threshold, DEFAULT_TESSDATA_DIR, args.check_orientation, args.psm, args)

if __name__ == "__main__":
    main()
