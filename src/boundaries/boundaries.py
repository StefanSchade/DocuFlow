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

            preprocessed_image = self.preprocess_image_for_boundary_recognition(image)
            bounding_boxes, quadrilaterals = self.detect_text_regions(preprocessed_image)
            
            print(f"Detected quadrilaterals: {len(quadrilaterals)}")

            # Draw bounding boxes on the original colored image
            image_with_boxes = self.draw_bounding_boxes(image, bounding_boxes)
            image_with_quadrilaterals = self.draw_quadrilaterals(image_with_boxes, quadrilaterals)

            output_path = os.path.join(output_dir, filename)
            cv2.imwrite(output_path, image_with_quadrilaterals)

            print(f"Processed {filename}, saved to {output_path}")

            # Save each bounding box as a separate image
            self.save_bounding_boxes(image, bounding_boxes, filename, output_dir)

    def draw_bounding_boxes(self, image, bounding_boxes):
        for i, (x, y, w, h) in enumerate(bounding_boxes):
            print(f"Drawing bounding box at ({x}, {y}), width: {w}, height: {h}")  # Debugging output
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Calculate the center of the bounding box
            center_x = x + w // 2
            center_y = y + h // 2

            # Determine the text size (80% of the bounding box height)
            text = str(i + 1)
            text_scale = min(w, h) * 0.8 / (cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][1])
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, text_scale, 2)

            text_width, text_height = text_size[0]
            text_offset_x = center_x - text_width // 2
            text_offset_y = center_y + text_height // 2

            # Draw the number centered in the bounding box
            cv2.putText(image, text, (text_offset_x, text_offset_y), cv2.FONT_HERSHEY_SIMPLEX, text_scale, (0, 255, 0), round(text_height/10), cv2.LINE_AA)
        return image


    def preprocess_image_for_boundary_recognition(self, image):
        # Convert to grayscale        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply adaptive thresholding
        block_size = self.args.block_size if self.args.block_size else 51
        constant = 3
        image = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, block_size, constant
        )
        image = cv2.GaussianBlur(image, (79, 79), 0)  # Adjusted to a more typical kernel size
        image = cv2.medianBlur(image, 29)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 13))
        image = cv2.dilate(image, kernel, iterations=1)
        
        return image
    
    def detect_text_regions(self, preprocessed_image):
        # Find contours
        contours, _ = cv2.findContours(preprocessed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bounding_boxes = []
        min_width, min_height = 50, 50  # Minimum size to consider
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Filter out too large or too small contours
            if w > min_width and h > min_height and w < preprocessed_image.shape[1] * 0.9 and h < preprocessed_image.shape[0] * 0.9:
                bounding_boxes.append((x, y, w, h))
  
        # Filter out boxes that are contained within other boxes
        filtered_boxes = []
        for i, box1 in enumerate(bounding_boxes):
            contained = False
            for j, box2 in enumerate(bounding_boxes):
                if i != j and is_contained(box1, box2):
                    contained = True
                    break
            if not contained:
                filtered_boxes.append(box1)
                
        # Sort the filtered boxes from top to bottom and then left to right
        filtered_boxes = sorted(filtered_boxes, key=lambda b: (b[1] // 50, b[0]))
        
        quadrilaterals = []
        for contour in contours:
            epsilon = 0.005 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            print(f"Approximated contour: {approx}")
            print(f"Contour length: {len(approx)}")
            if len(approx) == 4:
                quadrilaterals.append(approx)
                print(f"Detected quadrilateral: {approx}")

        return filtered_boxes, quadrilaterals
    
    def draw_quadrilaterals(self, image, quadrilaterals):
        for quadrilateral in quadrilaterals:
            print(f"Drawing quadrilateral: {quadrilateral}")
            if quadrilateral.shape == (4, 1, 2):
                quadrilateral = quadrilateral.reshape(4, 2)
            cv2.polylines(image, [quadrilateral], True, (255, 0, 0), 2)  # Draw quadrilaterals in blue
        return image
    
    def save_bounding_boxes(self, image, bounding_boxes, filename, output_dir):
        base_filename = os.path.splitext(filename)[0]
        num_boxes = len(bounding_boxes)
        for i, (x, y, w, h) in enumerate(bounding_boxes):
            box_image = image[y:y+h, x:x+w]
            box_filename = f"{base_filename}_{i+1:0{len(str(num_boxes))}d}.png"
            box_filepath = os.path.join(output_dir, box_filename)
            cv2.imwrite(box_filepath, box_image)
            print(f"Saved bounding box {i+1} to {box_filepath}")

    def process(self, image):
        bounding_boxes, quadrilaterals = self.detect_text_regions(image)
        image_with_boxes = self.draw_bounding_boxes(image, bounding_boxes)
        image_with_quadrilaterals = self.draw_quadrilaterals(image_with_boxes, quadrilaterals)
        return image_with_quadrilaterals

def is_contained(inner_box, outer_box):
    ix, iy, iw, ih = inner_box
    ox, oy, ow, oh = outer_box
    return ix >= ox and iy >= oy and (ix + iw) <= (ox + ow) and (iy + ih) <= (oy + oh)

