from flask import Blueprint, request, jsonify, render_template, current_app
import os
from werkzeug.utils import secure_filename
import logging
from services.pdf_image_extractor import extract_images_from_pdf

main = Blueprint('main', __name__)

# Define the upload folder
UPLOAD_FOLDER = '../uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists

@main.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        logging.info("Received a file upload request.")

        if 'pdf' not in request.files:
            logging.error("No file part in the request.")
            return jsonify({'error': 'No file part in the request'}), 400

        file = request.files['pdf']
        logging.info(f"File received: {file.filename}")

        if file.filename == '':
            logging.error("No file was selected.")
            return jsonify({'error': 'No file was selected. Please select a file'}), 400

        if not file.filename.endswith('.pdf'):
            logging.error("Invalid file type. Only PDF files are allowed.")
            return jsonify({'error': 'Only PDF files are allowed'}), 400

        # Check for file size
        #max_size = current_app.config.get('MAX_CONTENT_LENGTH', 12 * 1024 * 1024)  # Default to 12 MB

        # if request.content_length is None:
        #     logging.error("Content length is missing. Unable to determine file size.")
        #     return jsonify({'error': 'Unable to determine file size. Please try again with a different file or browser.'}), 400
        
        # logging.info(f"Content Length: {request.content_length}")

        # if request.content_length > max_size:
        #     logging.error(f"File is too large: {request.content_length} bytes.")
        #     return jsonify({'error': 'File is too large. Maximum allowable size is 12 MB'}), 400

        # Save the file securely
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        logging.info(f"Saving file to: {save_path}")
        
        file.save(save_path)

        logging.info(f"File '{filename}' uploaded successfully.")
        return jsonify({'message': f"PDF '{filename}' uploaded successfully"}), 200

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return jsonify({'error': str(e)}), 500
    
@main.route('/process-pdf', methods=['POST'])
def process_pdf_endpoint():
    try:
        logging.info("Received a request to process the uploaded PDF file.")

        # Get the uploaded PDF filename
        pdf_filename = request.form.get('pdf_filename')
        logging.info(f"PDF filename: {pdf_filename}")

        # Extract images from the PDF
        extract_images_from_pdf(pdf_filename)

        logging.info("PDF processing complete.")
        return jsonify({'message': 'PDF processing complete'}), 200

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return jsonify({'error': str(e)}), 500