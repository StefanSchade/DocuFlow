import cv2
import numpy as np
import os
from pipeline_step import PipelineStep

class Boundaries(PipelineStep):
    def __init__(self, args):
        self.args = args

    def run(self, input_data):
        input_dir = f"{input_data}/preprocessed"
        output_dir = f"{input_data}/boundaries"
        
        # Create the output directory if it does not exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for filename in os.listdir(input_dir):
            image_path = os.path.join(input_dir, filename)
            image = cv2.imread(image_path)
            
            if image is None:
                print(f"Failed to load image {image_path}")
                continue

            # Convert to grayscale for processing
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            preprocessed_image = self.preprocess_image(gray_image)
            bounding_boxes = self.detect_text_regions(preprocessed_image)

            # Draw bounding boxes on the original colored image
            image_with_boxes = self.draw_bounding_boxes(image, bounding_boxes)

            output_path = os.path.join(output_dir, filename)
            cv2.imwrite(output_path, image_with_boxes)

            print(f"Processed {filename}, saved to {output_path}")

    def preprocess_image(self, image):
        # Apply adaptive thresholding
        block_size = self.args.block_size if self.args.block_size else 51
        constant = 2
        binary_image = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, block_size, constant
        )
        return binary_image

    def detect_text_regions(self, preprocessed_image):
        # Find contours
        contours, _ = cv2.findContours(preprocessed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bounding_boxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Filter out too large or too small contours
            if w > 10 and h > 10 and w < preprocessed_image.shape[1] * 0.9 and h < preprocessed_image.shape[0] * 0.9:
                bounding_boxes.append((x, y, w, h))
        
        return bounding_boxes

    def draw_bounding_boxes(self, image, bounding_boxes):
        for (x, y, w, h) in bounding_boxes:
            print(f"Drawing bounding box at ({x}, {y}), width: {w}, height: {h}")  # Debugging output
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return image

    def process(self, image):
        bounding_boxes = self.detect_text_regions(image)
        image_with_boxes = self.draw_bounding_boxes(image, bounding_boxes)
        return image_with_boxes
