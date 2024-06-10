import os
import pytest
from PIL import Image, ImageDraw, ImageFont
from step_02_ocr.ocr_step import OCRStep
from argparse import Namespace
import json

@pytest.mark.integration
def test_ocr_step_integration(tmpdir):
    # Setup test directories
    data_dir = tmpdir.mkdir("data")
    preprocessed_dir = data_dir.mkdir("preprocessed")
    ocr_result_dir = data_dir.mkdir("ocr_result")

    # Create a test image
    img_path = os.path.join(preprocessed_dir, "test_image.jpg")
    create_test_image(img_path, "This is a test image with text.", rotation_angle=273)

    # Setup arguments
    args = Namespace(
        language='eng',
        path_to_tesseract='/usr/share/tesseract-ocr/4.00/tessdata',
        check_orientation='FINE',
        psm=6,
        save_preprocessed=False
    )

    # Run OCR step
    ocr_step = OCRStep(args)
    ocr_step.run(str(data_dir))

    # Check if OCR results are written to the output file
    result_file = os.path.join(ocr_result_dir, 'ocr_result.json')
    assert os.path.exists(result_file)

    # Read and print results (for demonstration purposes, not typical for automated tests)
    if os.getenv("DEBUG_PRINTS", "false").lower() == "true":
        with open(result_file, 'r', encoding='utf-8') as file:
            for line in file:
                print(line)

    # Verify the OCR output
    with open(result_file, 'r', encoding='utf-8') as file:
        for line in file:
            result = json.loads(line)
            assert result["final_angle"] in [90, 270]  # Adjust this based on your final rotation logic
            assert "This is a test image with text." in " ".join(result["text_lines"])

def create_test_image(file_path, text, rotation_angle=0):
    """Creates a simple image with text for testing purposes."""
    # Create an image with white background
    image = Image.new('RGB', (300, 100), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Try to use a specific TTF font
    try:
        font_path = "/workspace/tests/data/arial.ttf"
        font = ImageFont.truetype(font_path, 20)
    except IOError:
        # Fall back to the default font if the specific font is not found
        font = ImageFont.load_default()

    # Add text to the image
    draw.text((10, 40), text, font=font, fill=(0, 0, 0))
    
    # Rotate the image
    if rotation_angle != 0:
        image = image.rotate(rotation_angle, expand=1)

    # Save the image
    image.save(file_path)
