# tests/test_pipeline.py

import pytest
import os
from src.pipeline import run_pipeline
from argparse import Namespace

def test_pipeline():
    args = Namespace(
        grayscale=True,
        remove_noise=True,
        threshold=128,
        dilate=False,
        erode=False,
        opening=False,
        canny=False,
        deskew=False,
        language='eng',
        check_orientation=True,
        psm=6
    )

    input_data = "/tmp/test_pipeline_data"
    os.makedirs(input_data, exist_ok=True)
    
    # Create dummy images
    dummy_image_path = os.path.join(input_data, 'test_image.png')
    image = Image.fromarray(np.zeros((100, 100), dtype=np.uint8))
    image.save(dummy_image_path)

    run_pipeline(args)

    assert os.path.exists(os.path.join(input_data, 'preprocessed'))
    assert os.path.exists(os.path.join(input_data, 'preprocessed', 'test_image.png'))
    assert os.path.exists(os.path.join(input_data, 'ocr_result.txt'))
