import pytest
import os
from PIL import Image, ImageDraw, ImageFont
from step_01_preprocess.preprocess_step import PreprocessStep
from argparse import Namespace

@pytest.mark.integration
def test_preprocess_step_integration(tmpdir):
    # Setup test directories
    input_dir = tmpdir.mkdir("data")
    preprocessed_dir = input_dir.mkdir("preprocessed")

    # Create a test image
    img_path = os.path.join(input_dir, "test_image.jpg")
    create_test_image(img_path, "This is a test image.")

    # Setup arguments
    args = Namespace(
        grayscale=True,
        remove_noise=True,
        threshold=128,
        dilate=False,
        erode=False,
        opening=False,
        canny=False,
        deskew=False
    )

    # Run Preprocess step
    preprocess_step = PreprocessStep(args)
    preprocess_step.run(str(input_dir))

    # Check if preprocessed images are created
    processed_files = os.listdir(str(preprocessed_dir))
    assert len(processed_files) > 0

    # Read and print results (for demonstration purposes, not typical for automated tests)
    if os.getenv("DEBUG_PRINTS", "false").lower() == "true":
        for processed_file in processed_files:
            print(processed_file)

def create_test_image(file_path, text):
    """Creates a simple image with text for testing purposes."""
    # Create an image with white background
    image = Image.new('RGB', (200, 100), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Use a basic font
    font = ImageFont.load_default()

    # Add text to the image
    draw.text((10, 40), text, font=font, fill=(0, 0, 0))

    # Save the image
    image.save(file_path)
