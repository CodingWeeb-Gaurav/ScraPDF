#ye first page ke aage se diagram extraction start karega, supposing first page introduction hai
import cv2
import numpy as np
import os
from pdf2image import convert_from_path
from fpdf import FPDF
import pytesseract
import shutil

diagram_counter_a=1
diagram_counter_b=1

# all file paths
pdf_path = "C:/Users/gkg11/Downloads/applsci-14-07803.pdf"
output_clean_folder ="D:/Files/Internship/Server/intermediate/cleaned_pages"
output_diagram_folder = "D:/Files/Internship/Server/intermediate/extracted_diagrams"
output_folder_50dpi = "D:/Files/Internship/Server/intermediate/extracted_pages_50dpi"
output_folder_300dpi = "D:/Files/Internship/Server/intermediate/extracted_pages_300dpi"
output_clean_pdf = "D:/Files/Internship/Server/intermediate/cleaned_pages.pdf" 
metadata_file= "D:/Files/Internship/Server/intermediate/diagrams_info.txt"
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
    global diagram_counter_a
    # Merge intersecting ROIs
    rois = merge_intersecting_boxes(rois)    
    # Sort ROIs by their top-left corner (y, x)
    rois.sort(key=lambda r: (r[1], r[0]))  # Sort by y first, then x
    
    with open(metadata_file,"a") as f:
        for (x, y, w, h) in rois:
            roi = img[y:y + h, x:x + w]
            if not is_single_line_text(roi):  # Skip single line text
                #save diagram with counter format
                image_name=f'{diagram_counter_a:03}'
                
                # Format page number with leading zeros
                formatted_page_number = f"{page_number:03}"
                filename = f'{formatted_page_number},{y},{x}.png'
                cv2.imwrite(os.path.join(output_folder, filename), roi)
                
                diagram_info=f"{image_name} : ({formatted_page_number},{y},{x})\n"
                f.write(diagram_info)
                diagram_counter_a+=1

# Process the image, whiten regions, and add annotation text
def process_image(img, rois, page_number, output_path):
    rois.sort(key=lambda r: (r[1], r[0]))
    for (x, y, w, h) in rois:
        global diagram_counter_b
        # Whiten the area
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), thickness=cv2.FILLED)
        
        # Generate detail text
        detail_text = f"$${diagram_counter_b:03}$$"
        
        # Determine the position for the text
        text_x = x + 50  # Slightly inset from the top-left corner
        text_y = y + 60  # Slightly inset from the top-left corner
        font_scale = 1.15
        font_thickness = 3
        font = cv2.FONT_HERSHEY_DUPLEX
        diagram_counter_b+=1
        # Add text inside the white area
        cv2.putText(img, detail_text, (text_x, text_y), font, font_scale, (0, 0, 0), font_thickness)
    
    # Save the processed image
    cv2.imwrite(output_path, img)
    print(f"Processed image saved: {output_path}")

# Convert images to a PDF document
def images_to_pdf(image_folder, output_pdf_path):
    pdf = FPDF()
    for filename in sorted(os.listdir(image_folder)):
        if filename.endswith('.png'):
            image_path = os.path.join(image_folder, filename)
            img = cv2.imread(image_path)
            height, width, _ = img.shape
            pdf.add_page()
            # Scale the image to fit within the PDF page size (assuming A4, 210mm x 297mm)
            pdf.image(image_path, 0, 0, 210, 297)
    pdf.output(output_pdf_path)
    print(f"PDF created: {output_pdf_path}")

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

# Main execution

# Clear existing folders
clear_folders(output_folder_50dpi, output_folder_300dpi, output_diagram_folder, output_clean_folder)
# Clear metadata file before running
if os.path.exists(metadata_file):
    os.remove(metadata_file)
    
# Convert PDF to images at 50 and 300 DPI
images_50dpi = convert_from_path(pdf_path, dpi=50)
images_300dpi = convert_from_path(pdf_path, dpi=300)

# Process each page starting from page 2
for i, (img_50dpi, img_300dpi) in enumerate(zip(images_50dpi[1:], images_300dpi[1:])):  # Skipping first page
    # Set the page number correctly starting from page 2
    page_number = i + 2  # Since we skipped the first page, add 2 to align with the actual page number

    # Convert PIL images to OpenCV format
    img_50dpi = np.array(img_50dpi)
    img_300dpi = np.array(img_300dpi)

    # Preprocess the 50 DPI image
    img_processed_50dpi = preprocess(img_50dpi)
    rois_50dpi = get_rois(img_processed_50dpi)

    # Scale ROIs to match 300 DPI
    scale_factor = 6  # 300 DPI / 50 DPI = 6
    rois_300dpi = scale_rois(rois_50dpi, scale_factor)
    
    # Save the extracted diagrams
    save_extracted_diagrams(img_300dpi, rois_300dpi, output_diagram_folder, page_number=page_number)
    
    # Whiten areas and add annotation text in the 300 DPI image
    formatted_page_number = f"{page_number:03}"
    processed_output_path = os.path.join(output_clean_folder, f'page_{formatted_page_number}.png')
    process_image(img_300dpi, rois_300dpi, page_number=page_number, output_path=processed_output_path)


# Convert the cleaned images to a single PDF
images_to_pdf(output_clean_folder, output_clean_pdf)

print(f"All images processed, diagrams saved, and PDF saved as: {output_clean_pdf}")