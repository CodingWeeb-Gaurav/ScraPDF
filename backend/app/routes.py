from flask import Flask, Blueprint, request, jsonify, render_template
from flask_cors import CORS
import os
import logging
from werkzeug.utils import secure_filename
from .services.pdf_image_extractor import extract_images_from_pdf

app=Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
main = Blueprint('main', __name__)


UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../uploads'))
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

        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        logging.info(f"Saving file to: {os.path.abspath(save_path)}")        
        file.save(save_path)

        logging.info(f"File '{filename}' uploaded successfully.")
        return jsonify({'message': f"PDF '{filename}' uploaded successfully", 'filename': filename}), 200

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/process-pdf', methods=['POST'])
def process_pdf_endpoint():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'Preflight request successful'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
    try:
        logging.info("Received a request to process the uploaded PDF file.")

        data = request.get_json()
        logging.info(f"Received data: {data}")

        pdf_filename = data.get('pdf_filename')
        logging.info(f"PDF filename: {pdf_filename}")

        if not pdf_filename:
            logging.error("No PDF filename provided.")
            return jsonify({'error': 'No PDF filename provided.'}), 400

        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        logging.info(f"Resolved PDF path: {os.path.abspath(pdf_path)}")

        if not os.path.exists(pdf_path):
            logging.error(f"File not found: {pdf_filename}")
            return jsonify({'error': f"File '{pdf_filename}' not found on the server."}), 404
        # print("pdf_path",pdf_path)
        print(f"Uploaded file: {pdf_filename}")
        extract_images_from_pdf(pdf_filename)

        logging.info("PDF processing complete.")
        return jsonify({'message': 'PDF processing complete.'}), 200

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return jsonify({'error': str(e)}), 500
