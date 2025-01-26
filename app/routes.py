from flask import Blueprint, render_template, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)


UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Create the folder if it doesn't exist

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload_pdf():
    
    if 'pdf' not in request.files: # Check if the POST request has the file part
        return jsonify({'error': 'No file part in the request'}), 400
    
    file=request.files['pdf']
    
    if file.filename == '': # Check if the file is empty
        return jsonify({'error': 'No file was selected. Please select a file'}), 400
    
    if not file.filename.endswith('.pdf'): # Check if the file is a PDF
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    if file.content_type!='application/pdf': # Check if the file's content is a PDF format
        return jsonify({'error': 'MIME type error, the .pdf file has non PDF content'}), 400
    
    filename=secure_filename(file.filename)
    
    if file.content_length > request.app.config['MAX_SIZE']: # Check if the file is too large
        return jsonify({'error': 'File is too large. Maximum allowable size is 12MB'}), 400
    
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'])
        file.save(save_path)
        return jsonify({'message': f"PDF '{filename}' uploaded successfully!"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500