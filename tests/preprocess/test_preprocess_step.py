# tests/preprocess/test_preprocess_step.py

import cv2
import numpy as np
import pytest
from src.preprocess.preprocess_step import PreprocessStep

class Args:
    grayscale = True
    remove_noise = True
    threshold = 128
    dilate = False
    erode = False
    opening = False
    canny = False
    deskew = False

def test_preprocess_image():
    args = Args()
    step = PreprocessStep(args)

    # Create a dummy image
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    preprocessed_image = step.preprocess_image(image)
    
    assert preprocessed_image is not None
    assert preprocessed_image.shape == (100, 100)
