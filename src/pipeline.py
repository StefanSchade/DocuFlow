import os
import logging
from step_01_preprocess.preprocess_step import PreprocessStep
from step_02_ocr.ocr_step import OCRStep

# Constants
INPUT_DIRECTORY = '/workspace/data'
LOG_FILE = '/workspace/data/pipeline.log'
PATH_TO_TESSERACT= '/usr/share/tesseract-ocr/4.00/tessdata'

# Add PATH_TO_TESSERACT to args
args.path_to_tesseract = PATH_TO_TESSERACT

# Setup logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_pipeline(args):
    logging.info("Starting pipeline execution")
    
    # Step 1: Preprocessing
    step_01 = PreprocessStep(args)
    step_01.run(INPUT_DIRECTORY)

    # Step 2: OCR
    step_02 = OCRStep(PATH_TO_TESSERACT, args)
    step_02.run(os.path.join(INPUT_DIRECTORY, 'preprocessed'))

    logging.info("Pipeline execution completed successfully")

    # Step 3: ...
    

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
    parser.add_argument('--check-orientation', type=int, choices=[0, 1], default=0, help='Check and correct orientation')
    parser.add_argument('--psm', type=int, choices=list(range(14)), default=6, help='Tesseract Page Segmentation Mode (PSM)')
    args = parser.parse_args()
    run_pipeline(args)
