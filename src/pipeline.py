import os
import logging
from step_01_preprocess.preprocess_step import PreprocessStep
from step_02_ocr.ocr_step import OCRStep

# Constants
INPUT_DIRECTORY = '/workspace/data'
LOG_FILE = '/workspace/data/pipeline.log'
PATH_TO_TESSERACT = '/usr/share/tesseract-ocr/4.00/tessdata'

def run_pipeline(args):
    logging.info("Starting pipeline execution")
    
    # Add PATH_TO_TESSERACT to args
    args.path_to_tesseract = PATH_TO_TESSERACT
    
    # Step 1: Preprocessing
    step_01 = PreprocessStep(args)
    step_01.run(INPUT_DIRECTORY)

    # Step 2: OCR
    preprocessed_directory = os.path.join(INPUT_DIRECTORY, 'preprocessed')
    step_02 = OCRStep(args)
    step_02.run(preprocessed_directory)

    logging.info("Pipeline execution completed successfully")

    # Step 3: Postprocessing (placeholder for future steps)

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
    parser.add_argument('--language', type=str, default='eng', help='Language for Tesseract OCR')
    parser.add_argument('--check-orientation', type=str, choices=['NONE', 'BASIC', 'FINE'], default='NONE', help='Check and correct orientation')
    parser.add_argument('--psm', type=int, choices=list(range(14)), default=6, help='Tesseract Page Segmentation Mode (PSM)')
    parser.add_argument('--save-preprocessed', action='store_true', help='Save preprocessed images')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help='Set the logging level')
    
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(filename=LOG_FILE, level=getattr(logging, args.log_level.upper()), format='%(asctime)s - %(levelname)s - %(message)s')

    run_pipeline(args)
