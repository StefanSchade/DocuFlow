import cv2
import pytesseract
import numpy as np
from PIL import Image

def tesseract_ocr(image, language, tessdata_dir_config, psm):
    config = f'--psm {psm} -l {language} {tessdata_dir_config}'
    data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)

    lines = {}
    for i, word in enumerate(data['text']):
        if int(data['conf'][i]) > 45:
            line_num = data['line_num'][i]
            if line_num in lines:
                lines[line_num].append(word)
            else:
                lines[line_num] = [word]

    text = '\n'.join([' '.join(lines[line]) for line in sorted(lines.keys())])
    average_confidence = sum(data['conf']) / len(data['conf']) if len(data['conf']) > 0 else 0
    return text, average_confidence

