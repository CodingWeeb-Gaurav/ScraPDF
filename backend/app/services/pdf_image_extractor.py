import cv2
import numpy as np
import os
from pdf2image import convert_from_path
import pytesseract
import shutil
# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
# Preprocessing function
def preprocess(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
    img_thresh = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    img_dilated = cv2.dilate(img_thresh, np.ones((5, 5), np.uint8), iterations=1)
    return img_dilated

# Get regions of interest from the image
def get_rois(img, pad=(5, 5, 5, 5)):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rois = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if 1450 < w * h < 200000 and 0.1 < w / h < 7:  # Adjusted area and aspect ratio thresholds
            rois.append((x - pad[0], y - pad[1], w + pad[2], h + pad[3]))
    return rois

# Save the extracted diagrams
def save_extracted_diagrams(img, rois, output_folder, image_counter):
    os.makedirs(output_folder, exist_ok=True)
    filenames = []
    for (x, y, w, h) in rois:
        roi = img[y:y + h, x:x + w]
        if not is_single_line_text(roi):  # Skip single line text
            filename = f'image_{image_counter}.png'
            cv2.imwrite(os.path.join(output_folder, filename), roi)
            filenames.append(filename)
            image_counter += 1
    return filenames, image_counter

# Determine whether a region of interest (ROI) is a single line of text
def is_single_line_text(roi):
    text = pytesseract.image_to_string(roi)
    lines = text.split('\n')
    if len(lines) == 1 and len(lines[0].strip()) > 0:
        return True
    return False

# Clear folders before processing
def clear_folders(*folders):
    for folder in folders:
        if os.path.exists(folder):
            for root, dirs, files in os.walk(folder):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting file {file_path}: {e}")
                for dir in dirs:
                    try:
                        dir_path = os.path.join(root, dir)
                        shutil.rmtree(dir_path)
                    except Exception as e:
                        print(f"Error deleting directory {dir_path}: {e}")
        os.makedirs(folder, exist_ok=True)

# Main function to extract diagrams from PDF
def extract_images_from_pdf(pdf_filename):
    print(f"Processing PDF: {pdf_filename}")

    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(base_dir, '..', '..', '..', 'uploads')
    uploads_dir = os.path.abspath(uploads_dir)
    pdf_path = os.path.join(uploads_dir, pdf_filename)

    if not os.path.exists(pdf_path):
        print("⚠️ Error: PDF file not found at:", pdf_path)
        return []

    app_dir = os.path.dirname(base_dir)
    output_diagram_folder = os.path.join(app_dir, 'static', 'extracted_diagrams')
    output_folder_50dpi = os.path.join(base_dir, 'extracted_pages_50dpi')
    output_folder_300dpi = os.path.join(base_dir, 'extracted_pages_300dpi')

    # Clear existing folders
    clear_folders(output_folder_50dpi, output_folder_300dpi, output_diagram_folder)

    # Convert PDF to images at 50 and 300 DPI
    images_50dpi = convert_from_path(pdf_path, dpi=50)
    images_300dpi = convert_from_path(pdf_path, dpi=300)
    extracted_images = []
    image_counter = 1  # Counter for naming images

    # Process each page starting from page 1
    for i, (img_50dpi, img_300dpi) in enumerate(zip(images_50dpi[1:], images_300dpi[1:])):  # Skipping first page
        img_50dpi = np.array(img_50dpi)
        img_300dpi = np.array(img_300dpi)

        # Preprocess and get ROIs at 50 DPI
        img_processed_50dpi = preprocess(img_50dpi)
        rois_50dpi = get_rois(img_processed_50dpi)

        # Scale ROIs to match 300 DPI
        scale_factor = 6  # 300 DPI / 50 DPI = 6
        img_height, img_width = img_300dpi.shape[:2]
        rois_300dpi = [
            (max(0, x * scale_factor), max(0, y * scale_factor),
             min(img_width, (x + w) * scale_factor), min(img_height, (y + h) * scale_factor))
            for x, y, w, h in rois_50dpi
        ]

        # Save extracted diagrams
        if img_300dpi is not None and rois_300dpi is not None:
            filenames, image_counter = save_extracted_diagrams(img_300dpi, rois_300dpi, output_diagram_folder, image_counter)
            extracted_images.extend(filenames)

    print("All images processed, and diagrams saved")
    return extracted_images
