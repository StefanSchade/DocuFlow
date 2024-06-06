import argparse
import os
import pytesseract
from PIL import Image
import logging

# Constants for default paths
DEFAULT_TESSDATA_DIR = '/usr/share/tesseract-ocr/4.00/tessdata'
DEFAULT_LANGUAGE = 'eng'

def load_valid_languages(tessdata_dir):
    try:
        return [f.split('.')[0] for f in os.listdir(tessdata_dir) if f.endswith('.traineddata')]
    except FileNotFoundError:
        logging.error(f"Tessdata directory {tessdata_dir} not found.")
        return []

def validate_language(language, valid_languages):
    if language not in valid_languages:
        raise ValueError(f"Invalid language '{language}'. Valid options are: {', '.join(valid_languages)}")

def process_image(image_path, tessdata_dir, language, check_orientation, save_preprocessed, threshold):
    tessdata_dir_config = f'--tessdata-dir "{tessdata_dir}"'
    config = f'-l {language} {tessdata_dir_config}'

    # Open image and apply OCR
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, config=config)

    # Log or save the OCR result as needed
    logging.info(f'OCR result for {image_path}: {text}')

    # Save preprocessed image if needed
    if save_preprocessed:
        preprocessed_image_path = os.path.join(os.path.dirname(image_path), f'preprocessed_{os.path.basename(image_path)}')
        image.save(preprocessed_image_path)
        logging.info(f'Saved preprocessed image to {preprocessed_image_path}')

def main():
    parser = argparse.ArgumentParser(description='Process a batch of images with Tesseract OCR.')
    parser.add_argument('input_directory', type=str, help='Directory containing input images')
    parser.add_argument('--language', type=str, default=DEFAULT_LANGUAGE, help='Language for Tesseract OCR')
    parser.add_argument('--save-preprocessed', action='store_true', help='Save preprocessed images')
    parser.add_argument('--threshold', type=int, default=128, help='Threshold for binarization')
    parser.add_argument('--check-orientation', type=int, choices=[0, 1, 2], default=0, help='Check and correct orientation')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help='Set the logging level')

    args = parser.parse_args()

    # Set logging level
    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    # Log received arguments
    logging.debug(f"Received arguments: {args}")

    # Validate input directory
    if not os.path.isdir(args.input_directory):
        logging.error(f"Input directory {args.input_directory} does not exist")
        return

    # Set TESSDATA_PREFIX environment variable
    os.environ['TESSDATA_PREFIX'] = DEFAULT_TESSDATA_DIR

    # Load valid languages and validate the provided language
    valid_languages = load_valid_languages(DEFAULT_TESSDATA_DIR)
    try:
        validate_language(args.language, valid_languages)
    except ValueError as e:
        logging.error(e)
        return

    # Log processed arguments
    logging.debug(f"Processed arguments: {args}")

    # Process each image in the input directory
    for filename in os.listdir(args.input_directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(args.input_directory, filename)
            process_image(image_path, DEFAULT_TESSDATA_DIR, args.language, args.check_orientation, args.save_preprocessed, args.threshold)

if __name__ == "__main__":
    main()
