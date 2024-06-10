# src/ocr/ocr_step.py

import os
from PIL import Image
from pipeline_step import PipelineStep
from step_02_ocr.utils_optimization import check_orientations
from step_02_ocr.utils_tesseract import tesseract_ocr

class OCRStep(PipelineStep):
    def __init__(self, tessdata_dir, args):
        self.language = args.language
        self.tessdata_dir = args.tessdata_dir
        self.check_orientation = args.check_orientation
        self.psm = args.psm

    def run(self, input_data):
        tessdata_dir_config = f'--tessdata-dir "{self.tessdata_dir}"'
        image_files = [f for f in os.listdir(input_data) if f.endswith(('.jpeg', '.jpg', '.png'))]
        output_file = os.path.join(input_data, 'ocr_result.txt')

        with open(output_file, 'w', encoding='utf-8') as file_out:
            for image_file in image_files:
                img_path = os.path.join(input_data, image_file)
                img = Image.open(img_path)
                if self.check_orientation:
                    text, final_angle, confidence = check_orientations(img, self.language, tessdata_dir_config, self.psm)
                else:
                    text, confidence = tesseract_ocr(img, self.language, tessdata_dir_config, self.psm)
                file_out.write(text + '\n')
