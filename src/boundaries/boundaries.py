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

            preprocessed_image = self.preprocess_image_for_boundary_recoginition(image)
            bounding_boxes, quadrilaterals = self.detect_text_regions(preprocessed_image)
            
            print(f"quadrilaterals {quadrilaterals}")

            # Draw bounding boxes on the original colored image
            image_with_boxes = self.draw_bounding_boxes(image, bounding_boxes)
            image_with_quadrilaterals = self.draw_quadrilaterals(image_with_boxes, quadrilaterals)

            output_path = os.path.join(output_dir, filename)
            cv2.imwrite(output_path, image_with_quadrilaterals)

            print(f"Processed {filename}, saved to {output_path}")

    def preprocess_image_for_boundary_recoginition(self, image):
        # Convert to grayscale        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply adaptive thresholding
        block_size = self.args.block_size if self.args.block_size else 51
        constant = 3
        image = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, block_size, constant
        )
        image = cv2.GaussianBlur(image, (47, 47), 0)  # Adjusted to a more typical kernel size
        image = cv2.medianBlur(image, 13)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 13))
        image = cv2.dilate(image, kernel, iterations=1)
        
        return image

    def detect_text_regions(self, preprocessed_image):
        # Find contours
        contours, _ = cv2.findContours(preprocessed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bounding_boxes = []
        min_width, min_height = 40, 40  # Minimum size to consider
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Filter out too large or too small contours
            if w > min_width and h > min_height and w < preprocessed_image.shape[1] * 0.9 and h < preprocessed_image.shape[0] * 0.9:
                bounding_boxes.append((x, y, w, h))
        
        quadrilaterals = []
        for contour in contours:
            # Approximate the contour to a polygon
            epsilon = 0.01 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            # Filter for quadrilaterals
            if len(approx) == 4:
                quadrilaterals.append(approx)
        
        return bounding_boxes, quadrilaterals

    def draw_bounding_boxes(self, image, bounding_boxes):
        for (x, y, w, h) in bounding_boxes:
            print(f"Drawing bounding box at ({x}, {y}), width: {w}, height: {h}")  # Debugging output
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return image
    
    def draw_quadrilaterals(self, image, quadrilaterals):
        for quadrilateral in quadrilaterals:
            print(f"Drawing quadrilateral: {quadrilateral}")
            if quadrilateral.shape[0] == 4 and quadrilateral.shape[1] == 1 and quadrilateral.shape[2] == 2:
                quadrilateral = quadrilateral.reshape(4, 2)  # Reshape to the format expected by polylines
            cv2.polylines(image, [quadrilateral], True, (255, 0, 0), 2)  # Draw quadrilaterals in blue
        return image

    def process(self, image):
        bounding_boxes, quadrilaterals = self.detect_text_regions(image)
        image_with_boxes = self.draw_bounding_boxes(image, bounding_boxes)
        image_with_quadrilaterals = self.draw_quadrilaterals(image_with_boxes, quadrilaterals)
        return image_with_quadrilaterals
