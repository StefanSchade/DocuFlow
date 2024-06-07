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

def run_pipeline():
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
    run_pipeline()
