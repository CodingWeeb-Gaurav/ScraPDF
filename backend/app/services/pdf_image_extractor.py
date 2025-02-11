import cv2
import numpy as np
import os
from pdf2image import convert_from_path
from fpdf import FPDF
import pytesseract
import shutil
# Preprocessing function
def preprocess(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
    img_thresh = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    img_dilated = cv2.dilate(img_thresh, np.ones((5, 5), np.uint8), iterations=1)
    return img_dilated

# Merging close contours to handle close regions
def merge_close_contours(contours, min_dist=8):
    merged_contours = []
    for cnt in contours:
        merged = False
        for i, mc in enumerate(merged_contours):
            x1, y1, w1, h1 = cv2.boundingRect(mc)
            x2, y2, w2, h2 = cv2.boundingRect(cnt)
            if abs(x1 - x2) < min_dist and abs(y1 - y2) < min_dist:
                merged_contours[i] = np.vstack((mc, cnt))
                merged = True
                break
        if not merged:
            merged_contours.append(cnt)
    return merged_contours

# Determine whether a region of interest (ROI) is a single line of text
def is_single_line_text(roi):
    text = pytesseract.image_to_string(roi)
    lines = text.split('\n')
    if len(lines) == 1 and len(lines[0].strip()) > 0:
        return True
    return False

# Get regions of interest from the image
def get_rois(img, pad=(5, 5, 5, 5)):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = merge_close_contours(contours)
    rois = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if 1450 < w * h < 200000 and 0.1 < w / h < 7:  # Adjusted area and aspect ratio thresholds
            rois.append((x - pad[0], y - pad[1], w + pad[2], h + pad[3]))
    return rois

# Scale regions of interest (ROIs)
def scale_rois(rois, scale_factor):
    scaled_rois = []
    for (x, y, w, h) in rois:
        scaled_rois.append((int(x * scale_factor), int(y * scale_factor), int(w * scale_factor), int(h * scale_factor)))
    return scaled_rois

# Merge intersecting bounding boxes
def merge_intersecting_boxes(boxes, min_overlap=0.5):
    def overlap_area(box1, box2):
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        if x_right < x_left or y_bottom < y_top:
            return 0
        return (x_right - x_left) * (y_bottom - y_top)

    def box_area(box):
        _, _, w, h = box
        return w * h

    merged_boxes = []
    used = [False] * len(boxes)
    for i, box1 in enumerate(boxes):
        if used[i]:
            continue
        merged_box = list(box1)
        for j, box2 in enumerate(boxes):
            if i != j and not used[j]:
                overlap = overlap_area(box1, box2)
                if overlap / box_area(box1) > min_overlap or overlap / box_area(box2) > min_overlap:
                    x1, y1, w1, h1 = merged_box
                    x2, y2, w2, h2 = box2
                    merged_box = [min(x1, x2), min(y1, y2), max(x1 + w1, x2 + w2) - min(x1, x2), max(y1 + h1, y2 + h2) - min(y1, y2)]
                    used[j] = True
        merged_boxes.append(tuple(merged_box))
    return merged_boxes

# Save the extracted diagrams and clear the folders before processing
def save_extracted_diagrams(img, rois, output_folder, page_number):
    os.makedirs(output_folder, exist_ok=True)
    
    # Merge intersecting ROIs
    rois = merge_intersecting_boxes(rois)
    
    # Sort ROIs by their top-left corner (y, x)
    rois.sort(key=lambda r: (r[1], r[0]))  # Sort by y first, then x
    
    for (x, y, w, h) in rois:
        roi = img[y:y + h, x:x + w]
        if not is_single_line_text(roi):  # Skip single line text
            # Format page number with leading zeros
            formatted_page_number = f"{page_number:03}"
            filename = f'{formatted_page_number},{y},{x}.png'
            cv2.imwrite(os.path.join(output_folder, filename), roi)

# Process the image, whiten regions, and add annotation text
def process_image(img, rois, page_number, output_path):
    for (x, y, w, h) in rois:
        # Whiten the area
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), thickness=cv2.FILLED)
        
        # Generate detail text
        detail_text = f'$${page_number},{y},{x}$$'
        
        # Determine the position for the text
        text_x = x + 50  # Slightly inset from the top-left corner
        text_y = y + 60  # Slightly inset from the top-left corner
        font_scale = 1.15
        font_thickness = 3
        font = cv2.FONT_HERSHEY_DUPLEX
        
        # Add text inside the white area
        cv2.putText(img, detail_text, (text_x, text_y), font, font_scale, (0, 0, 0), font_thickness)
    
    # Save the processed image
    cv2.imwrite(output_path, img)
    print(f"Processed image saved: {output_path}")

def clear_folders(*folders):
    for folder in folders:
        # Check if the folder exists
        if os.path.exists(folder):
            # Remove all files and subdirectories within the folder
            for root, dirs, files in os.walk(folder):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        os.remove(file_path)  # Delete the file
                    except Exception as e:
                        print(f"Error deleting file {file_path}: {e}")

                for dir in dirs:
                    try:
                        dir_path = os.path.join(root, dir)
                        shutil.rmtree(dir_path)  # Delete the subdirectory
                    except Exception as e:
                        print(f"Error deleting directory {dir_path}: {e}")

        # Ensure the folder is created if it doesn't already exist
        os.makedirs(folder, exist_ok=True)

# Main execution , function bana ke dusri jagah call krna hai
def extract_images_from_pdf(pdf_filename):

    print(f"Processing PDF: {pdf_filename}")

    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the current script
    print(f"Base directory: {base_dir}")

    uploads_dir = os.path.join(base_dir, '..', '..', '..', 'uploads')  # Go three levels up to access uploads
    uploads_dir = os.path.abspath(uploads_dir)  # Normalize the path
    print(f"Uploads directory: {uploads_dir}")

    pdf_path = os.path.join(uploads_dir, pdf_filename)
    print(f"Full PDF path: {pdf_path}")

    # Check if the file exists
    if not os.path.exists(pdf_path):
        print("⚠️ Error: PDF file not found at:", pdf_path)
    else:
        print("✅ PDF file found:", pdf_path)
    # The uploaded PDF file path

    output_clean_folder = os.path.join(base_dir, 'cleaned_pages')
    os.makedirs(output_clean_folder, exist_ok=True)

    output_diagram_folder = os.path.join(base_dir, 'extracted_diagrams')
    os.makedirs(output_diagram_folder, exist_ok=True)

    output_folder_50dpi = os.path.join(base_dir, 'extracted_pages_50dpi')
    os.makedirs(output_folder_50dpi, exist_ok=True)

    output_folder_300dpi = os.path.join(base_dir, 'extracted_pages_300dpi')
    os.makedirs(output_folder_300dpi, exist_ok=True)
    # #output_clean_pdf = os.path.join(base_dir, 'cleaned_pages.pdf')

    # Clear existing folders
    clear_folders(output_folder_50dpi, output_folder_300dpi, output_diagram_folder, output_clean_folder)

    # Convert PDF to images at 50 and 300 DPI
    images_50dpi = convert_from_path(pdf_path, dpi=50)
    images_300dpi = convert_from_path(pdf_path, dpi=300)

    # Process each page starting from page 1
    for i, (img_50dpi, img_300dpi) in enumerate(zip(images_50dpi[1:], images_300dpi[1:])):  # Skipping first page
        page_number = i + 1  # Since we skipped the first page, add 2 to align with the actual page number

        img_50dpi = np.array(img_50dpi)
        img_300dpi = np.array(img_300dpi)

        img_processed_50dpi = preprocess(img_50dpi)
        rois_50dpi = get_rois(img_processed_50dpi)

        # Scale ROIs to match 300 DPI
        scale_factor = 6  # 300 DPI / 50 DPI = 6
        img_height, img_width = img_300dpi.shape[:2]  # Get image dimensions

        # Ensure ROIs do not go beyond image boundaries
        rois_300dpi = [
            (max(0, x * scale_factor), 
            max(0, y * scale_factor), 
            min(img_width, (x + w) * scale_factor), 
            min(img_height, (y + h) * scale_factor)) 
            for x, y, w, h in rois_50dpi
        ]

        # Save extracted diagrams
        # Ensure all values are not None
        if img_300dpi is None or rois_300dpi is None or output_diagram_folder is None or page_number is None:
            print("⚠️ Error: One or more arguments passed to save_extracted_diagrams() are None!")
        else:
            save_extracted_diagrams(img_300dpi, rois_300dpi, output_diagram_folder, page_number)
        save_extracted_diagrams(img_300dpi, rois_300dpi, output_diagram_folder, page_number)

        # Process image and save it
        formatted_page_number = f"{page_number:03}"
        processed_output_path = os.path.join(output_clean_folder, f'page_{formatted_page_number}.png')
        process_image(img_300dpi, rois_300dpi, page_number, processed_output_path)
    print("All images processed, and diagrams saved")    
    # print(f"All images processed, diagrams saved, and PDF saved as: {output_clean_pdf}")