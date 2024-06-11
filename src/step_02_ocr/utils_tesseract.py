# File: step_02_ocr/utils_tesseract.py
import pytesseract
import logging
import os
import json

# Constants
MIN_WORD_LENGTH_FOR_CONFIDENCE = 3
MIN_WORD_COUNT_FOR_CONFIDENCE = 3
MIN_CONFIDENCE_FOR_WORD = 60

def tesseract_ocr(image, language, tessdata_dir_config, psm, ocr_debug_dir, angle):
    config = f'--psm {psm} -l {language} {tessdata_dir_config}'
    data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)

    lines = {}
    confidences = []

    for i, word in enumerate(data['text']):
        conf = int(data['conf'][i])
        if conf > MIN_CONFIDENCE_FOR_WORD:  # Only consider confident recognitions
            line_num = data['line_num'][i]
            if line_num in lines:
                lines[line_num].append(word)
            else:
                lines[line_num] = [word]
            if len(word) >= MIN_WORD_LENGTH_FOR_CONFIDENCE:
                confidences.append(conf)

    text = '\n'.join([' '.join(lines[line]) for line in sorted(lines.keys())])
    
    if len(confidences) < MIN_WORD_COUNT_FOR_CONFIDENCE:
        average_confidence = 0
    else:
        average_confidence = sum(confidences) / len(confidences)

    if ocr_debug_dir is not None:
        debug_file_path = os.path.join(ocr_debug_dir, f"ocr_debug_data_angle_{angle}.json")
        with open(debug_file_path, 'a', encoding='utf-8') as debug_file:
            json.dump(data, debug_file, ensure_ascii=False, indent=4)
            debug_file.write('\n')

    return text, average_confidence, len(data['text'])
