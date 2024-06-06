import os
import logging
import subprocess

# Constants
INPUT_DIRECTORY = '/workspace/data'
OCR_RESULT_FILE = 'ocr_result.txt'
LOG_FILE = '/workspace/data/pipeline.log'

# Setup logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command):
    """
    Helper function to run a shell command and handle logging.
    """
    logging.info(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    logging.info(f"Command output: {result.stdout}")
    if result.returncode != 0:
        logging.error(f"Command error: {result.stderr}")
    return result.returncode == 0

def ocr_step():
    """
    First step: OCR processing.
    """
    output_path = os.path.join(INPUT_DIRECTORY, OCR_RESULT_FILE)
    if os.path.exists(output_path):
        logging.info("OCR result already exists, skipping OCR step.")
        return True
    
    command = [
        'python', '/workspace/src/ocr_batch.py',
        INPUT_DIRECTORY,
        '--language', 'deu',  # Fixed for this example
        '--log-level', 'INFO',
        '--check-orientation', '1',  # Adjust based on requirement
        '--psm', '6',  # Fixed for this example
        '--threshold', '128',  # Example threshold
        '--sharpen'  # Apply sharpening
    ]
    return run_command(command)

def example_next_step():
    """
    Placeholder for additional processing step.
    """
    output_file = '/workspace/data/next_step_result.txt'  # Replace with actual file
    if os.path.exists(output_file):
        logging.info("Next step result already exists, skipping this step.")
        return True

    command = ['echo', 'Next step processing']  # Replace with actual command
    return run_command(command)

def main():
    """
    Main pipeline execution function.
    """
    logging.info("Starting pipeline execution")

    # Step 1: OCR
    if not ocr_step():
        logging.error("OCR step failed, stopping pipeline.")
        return

    # Step 2: Next processing step (example)
    if not example_next_step():
        logging.error("Next step failed, stopping pipeline.")
        return

    logging.info("Pipeline execution completed successfully")

if __name__ == "__main__":
    main()
