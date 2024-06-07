# tests/ocr/test_ocr_step.py

import pytest
from PIL import Image
import numpy as np
from src.ocr.ocr_step import OCRStep

class DummyArgs:
    language = 'eng'
    tessdata_dir = '/usr/share/tesseract-ocr/4.00/tessdata'
    check_orientation = True
    psm = 6

def test_ocr_step():
    args = DummyArgs()
    step = OCRStep(args.language, args.tessdata_dir, args.check_orientation, args.psm)
    
    # Create a dummy image
    image = Image.fromarray(np.zeros((100, 100), dtype=np.uint8))
    input_data = "/tmp/test_images"
    os.makedirs(input_data, exist_ok=True)
    image.save(os.path.join(input_data, 'test_image.png'))
    
    step.run(input_data)
    
    assert os.path.exists(os.path.join(input_data, 'ocr_result.txt'))
