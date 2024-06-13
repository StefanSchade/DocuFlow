# File: pipeline.py
import os
import logging
from step_01_preprocess.preprocess_step import PreprocessStep
from step_02_ocr.ocr_step import OCRStep

# Constants
INPUT_DIRECTORY = '/workspace/data'
LOG_FILE = '/workspace/data/pipeline.log'
PATH_TO_TESSERACT = '/usr/share/tesseract-ocr/4.00/tessdata'

# List of steps
STEPS = [
    ('PreprocessStep', PreprocessStep),
    ('OCRStep', OCRStep),
#    ('SanitizationStep', SanitizationStep)
]

def list_data_directory():
    data_dir = "/workspace/data"
    print(f"Listing contents of {data_dir}:")
    for root, dirs, files in os.walk(data_dir):
        for name in files:
            print(os.path.join(root, name))
        for name in dirs:
            print(os.path.join(root, name))          

def run_pipeline(args):
    logging.info("Starting pipeline execution")
    
    start_index = 0
    end_index = len(STEPS)

    if args.from_step:
        start_index = next((i for i, (name, _) in enumerate(STEPS) if name == args.from_step), 0)

    if args.to_step:
        end_index = next((i for i, (name, _) in enumerate(STEPS) if name == args.to_step), len(STEPS)) + 1

    # Ensure the indices are within the valid range
    start_index = max(start_index, 0)
    end_index = min(end_index, len(STEPS))

    # Ensure the indices are within the valid range
    start_index = max(start_index, 0)
    end_index = min(end_index, len(STEPS))

    # Execute the steps in the specified range
    for name, step_class in STEPS[start_index:end_index]:
        logging.info(f"Running {name}")
        step_instance = step_class(args)
        step_instance.run(INPUT_DIRECTORY)
  

    logging.info("Pipeline execution completed successfully")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Run OCR pipeline')
    parser.add_argument('--from_step', type=str, help='Step to start from')
    parser.add_argument('--to_step', type=str, help='Step to end at')
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

    print("Pipeline script started")
    print(f"Received arguments: {args}")
    list_data_directory()

    # Add PATH_TO_TESSERACT to args
    args.path_to_tesseract = PATH_TO_TESSERACT

    # Setup logging
    logging.basicConfig(filename=LOG_FILE, level=getattr(logging, args.log_level.upper()), format='%(asctime)s - %(levelname)s - %(message)s')

    logging.debug(f"Running Pipeline args={args}")    

    run_pipeline(args)
