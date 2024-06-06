import argparse
import os
import pytesseract
from PIL import Image, ImageFilter
import logging
import json

# Constants for default paths
DEFAULT_TESSDATA_DIR = '/usr/share/tesseract-ocr/4.00/tessdata'
DEFAULT_LANGUAGE = 'eng'
DEFAULT_PSM = 6
DEFAULT_THRESHOLD = 0
DEFAULT_SMALL_ROTATION_STEP = 2  # degrees
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

def preprocess_image(image, threshold, apply_sharpening):
    if apply_sharpening:
        image = image.filter(ImageFilter.SHARPEN)
    if threshold > 0:
        image = image.convert('L')
        image = image.point(lambda p: p > threshold and 255)
    return image

def tesseract_ocr(image, language, tessdata_dir_config, psm):
    config = f'--psm {psm} -l {language} {tessdata_dir_config}'
    data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)

    lines = {}
    for i, word in enumerate(data['text']):
        if int(data['conf'][i]) > 30:  # Also consider mediocre results to avoid blanks
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
    orientations = [0, 90, 180, 270, 45, 135, 315]
    best_text = ''
    highest_confidence = -1
    best_confidence_found = -1
    final_angle = 0

    # Coarse orientation check
    for angle in orientations:
        rotated_image = image.rotate(angle, expand=True)
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
            adjusted_image = image.rotate(final_angle + direction * step, expand=True)
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

def process_images(input_dir, language, save_preprocessed, threshold, tessdata_dir, check_orientation, psm, apply_sharpening):
    tessdata_dir_config = f'--tessdata-dir "{tessdata_dir}"'
    output_file = os.path.join(input_dir, 'ocr_result.txt')

    image_files = sorted([f for f in os.listdir(input_dir) if f.endswith(('.jpeg', '.jpg', '.png'))])

    with open(output_file, 'w', encoding='utf-8') as file_out:
        for index, filename in enumerate(image_files, start=1):
            full_path = os.path.join(input_dir, filename)
            img = Image.open(full_path)
            img = preprocess_image(img, threshold, apply_sharpening)
            if check_orientation:
                text, final_angle, confidence = check_orientations(img, language, tessdata_dir_config, psm, check_orientation)
            else:
                text, confidence = tesseract_ocr(img, language, tessdata_dir_config, psm)
                final_angle = 0
            json_output = {"new_page": True, "number": index, "file": filename, "final_angle": final_angle, "confidence": confidence}
            file_out.write(f"'{json.dumps(json_output)}'\n{text}\n")
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

    process_images(args.input_directory, args.language, args.save_preprocessed, args.threshold, DEFAULT_TESSDATA_DIR, args.check_orientation, args.psm, args.sharpen)

if __name__ == "__main__":
    main()
