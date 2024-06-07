# src/ocr_step.py

import pytesseract
import os
from PIL import Image
from pipeline_step import PipelineStep

class OCRStep(PipelineStep):
    def __init__(self, language, tessdata_dir):
        self.language = language
        self.tessdata_dir = tessdata_dir

    def run(self, input_data):
        tessdata_dir_config = f'--tessdata-dir "{self.tessdata_dir}"'
        image_files = [f for f in os.listdir(input_data) if f.endswith(('.jpeg', '.jpg', '.png'))]
        output_file = os.path.join(input_data, 'ocr_result.txt')

        with open(output_file, 'w', encoding='utf-8') as file_out:
            for image_file in image_files:
                img_path = os.path.join(input_data, image_file)
                img = Image.open(img_path)
                text = pytesseract.image_to_string(img, lang=self.language, config=tessdata_dir_config)
                file_out.write(text)
