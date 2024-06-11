import os
import pytest
from PIL import Image
import numpy as np
from argparse import Namespace
from src.pipeline import run_pipeline

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
        psm=6,
        no_pause=True
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
