import os
from PIL import Image
from pipeline_step import PipelineStep
from step_02_ocr.utils_optimization import check_orientations
from step_02_ocr.utils_tesseract import tesseract_ocr
import json
import logging

class OCRStep(PipelineStep):
    def __init__(self, args):
        self.language = args.language
        self.tessdata_dir = args.path_to_tesseract
        self.check_orientation = args.check_orientation
        self.psm = args.psm
        self.save_preprocessed = args.save_preprocessed
        self.log_level = args.log_level.upper()

    def run(self, main_directory):
        preprocessed_dir = os.path.join(main_directory, 'preprocessed')
        ocr_result_dir = os.path.join(main_directory, 'ocr_result')
        ocr_debug_dir = None
        
        if self.log_level == 'DEBUG':
            ocr_debug_dir = os.path.join(main_directory, 'ocr_debug')
            os.makedirs(ocr_debug_dir, exist_ok=True)
        
        os.makedirs(ocr_result_dir, exist_ok=True)
        tessdata_dir_config = f'--tessdata-dir "{self.tessdata_dir}"'
        image_files = [f for f in os.listdir(preprocessed_dir) if f.endswith(('.jpeg', '.jpg', '.png'))]
        output_file = os.path.join(ocr_result_dir, 'ocr_result.json')

        # Delete the output file if it exists
        try:
            os.remove(output_file)
            logging.info(f"Deleted existing file: {output_file}")
        except FileNotFoundError:
            logging.info(f"No existing file to delete: {output_file}")

        ocr_results = []

        for index, image_file in enumerate(image_files, start=1):
            img_path = os.path.join(preprocessed_dir, image_file)
            logging.info(f"Starting analysis of file: {image_file}")
            img = Image.open(img_path)
            text, final_angle, confidence = check_orientations(img, self.language, tessdata_dir_config, self.psm, self.check_orientation, ocr_debug_dir )
            text_lines = text.split('\n')

            json_output = {
                "page_number": index,
                "source_file": image_file,
                "final_angle": final_angle,
                "confidence": confidence,
                "text_lines": text_lines
            }
            ocr_results.append(json_output)
            logging.debug(f"Processed {image_file} with final angle: {final_angle}")

            # Save processed image if required
            if self.save_preprocessed:
                img.save(os.path.join(ocr_result_dir, f"processed_{image_file}"))

        # Write all results to the output file as a single JSON array
        with open(output_file, 'w', encoding='utf-8') as file_out:
            json.dump(ocr_results, file_out, ensure_ascii=False, indent=4)
        logging.info(f"Saved all OCR results to {output_file}")
