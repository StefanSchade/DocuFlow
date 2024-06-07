# src/pipeline.py

import os
import logging
from preprocess_step import PreprocessStep
from ocr_step import OCRStep

# Constants
INPUT_DIRECTORY = '/workspace/data'
LOG_FILE = '/workspace/data/pipeline.log'

# Setup logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_pipeline(args):
    logging.info("Starting pipeline execution")
    
    # Step 1: Preprocessing
    preprocess_step = PreprocessStep(args)
    preprocess_step.run(INPUT_DIRECTORY)

    # Allow user intervention here if needed
    input("Press Enter to continue to OCR step...")

    # Step 2: OCR
    ocr_step = OCRStep('eng', '/usr/share/tesseract-ocr/4.00/tessdata')
    ocr_step.run(os.path.join(INPUT_DIRECTORY, 'preprocessed'))

    logging.info("Pipeline execution completed successfully")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Run OCR pipeline')
    parser.add_argument('--grayscale', action='store_true', help='Convert image to grayscale')
    parser.add_argument('--remove-noise', action='store_true', help='Apply noise removal')
    parser.add_argument('--threshold', type=int, default=0, help='Threshold for binarization')
    parser.add_argument('--dilate', action='store_true', help='Apply dilation')
    parser.add_argument('--erode', action='store_true', help='Apply erosion')
    parser.add_argument('--opening', action='store_true', help='Apply opening (erosion followed by dilation)')
    parser.add_argument('--canny', action='store_true', help='Apply Canny edge detection')
    parser.add_argument('--deskew', action='store_true', help='Apply deskewing (skew correction)')
    args = parser.parse_args()
    run_pipeline(args)
