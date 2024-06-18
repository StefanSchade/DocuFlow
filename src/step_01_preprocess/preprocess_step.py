import cv2
import numpy as np
import os
from pipeline_step import PipelineStep

def wiener_filter(img, kernel, K):
    # Fourier Transform of the image
    img_fft = np.fft.fft2(img)
    img_fft_shift = np.fft.fftshift(img_fft)

    # Fourier Transform of the kernel
    kernel_fft = np.fft.fft2(kernel, s=img.shape)
    kernel_fft_shift = np.fft.fftshift(kernel_fft)

    # Apply Wiener filter
    wiener_filter = np.conj(kernel_fft_shift) / (np.abs(kernel_fft_shift)**2 + K)
    result_fft_shift = img_fft_shift * wiener_filter

    # Inverse Fourier Transform to get the result
    result_fft = np.fft.ifftshift(result_fft_shift)
    result = np.fft.ifft2(result_fft)
    result = np.abs(result)
    return result

class PreprocessStep(PipelineStep):
    def __init__(self, args):
        self.args = args

    def preprocess_image(self, image):
        if self.args.grayscale or self.args.threshold > 0:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if self.args.remove_noise:
            image = cv2.medianBlur(image, 5)
        if self.args.wiener_filter: # de-blurring with a wiener filter
            kernel = np.ones((5,5)) / 25  # Example kernel, adjust as needed
            K = 0.005  # Example noise-to-signal ratio, adjust as needed
            deblurred_image = wiener_filter(image, kernel, K)
            image = np.uint8(np.clip(deblurred_image, 0, 255))
        if self.args.enhanced_contrast:
            image = image.enhance_contrast(image)
        if self.args.adaptive_threshold:
           image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,self.args.block_size, 5)
        if self.args.threshold:
            _, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  
        if self.args.sharpen:
            kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
            image = cv2.filter2D(image, -1, kernel)     
        if self.args.dilate: # morphological operations
            kernel = np.ones((5, 5), np.uint8)
            image = cv2.dilate(image, kernel, iterations=1)
        if self.args.erode: # morphological operations
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

