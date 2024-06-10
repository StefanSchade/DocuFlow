import cv2
import numpy as np
import os
from pipeline_step import PipelineStep

class PreprocessStep(PipelineStep):
    def __init__(self, args):
        self.args = args

    def preprocess_image(self, image):
        if self.args.grayscale or self.args.threshold > 0:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if self.args.remove_noise:
            image = cv2.medianBlur(image, 5)
        if self.args.threshold > 0:
            _, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if self.args.dilate:
            kernel = np.ones((5, 5), np.uint8)
            image = cv2.dilate(image, kernel, iterations=1)
        if self.args.erode:
            kernel = np.ones((5, 5), np.uint8)
            image = cv2.erode(image, kernel, iterations=1)
        if self.args.opening:
            kernel = np.ones((5, 5), np.uint8)
            image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        if self.args.canny:
            image = cv2.Canny(image, 100, 200)
        return image

    def run(self, input_data):
        image_files = [f for f in os.listdir(input_data) if f.endswith(('.jpeg', '.jpg', '.png'))]
        os.makedirs(os.path.join(input_data, 'preprocessed'), exist_ok=True)
        for image_file in image_files:
            img_path = os.path.join(input_data, image_file)
            img = cv2.imread(img_path)
            processed_img = self.preprocess_image(img)
            cv2.imwrite(os.path.join(input_data, 'preprocessed', image_file), processed_img)
