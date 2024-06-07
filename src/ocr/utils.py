# src/ocr/utils.py

import cv2
import pytesseract
import numpy as np

def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

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

def check_orientations(image, language, tessdata_dir_config, psm):
    orientations = [0, 90, 180, 270]
    best_text = ''
    highest_confidence = -1
    final_angle = 0

    for angle in orientations:
        rotated_image = rotate_image(image, angle)
        text, confidence = tesseract_ocr(rotated_image, language, tessdata_dir_config, psm)
        if confidence > highest_confidence:
            highest_confidence = confidence
            best_text = text
            final_angle = angle
        if confidence >= 60:
            break

    return best_text, final_angle, highest_confidence
