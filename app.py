from flask import Flask, request, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
PDF_FOLDER = 'pdfs'
STATIC_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

os.makedirs(PDF_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload PDF
@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file provided"}), 400
        
        f = request.files['file']
        
        if f.filename == '':
            return jsonify({"status": "error", "message": "No file selected"}), 400
        
        if not allowed_file(f.filename):
            return jsonify({"status": "error", "message": "Only PDF files are allowed"}), 400
        
        # Check file size
        f.seek(0, os.SEEK_END)
        file_size = f.tell()
        f.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({"status": "error", "message": "File too large (max 50MB)"}), 400
        
        filename = secure_filename(f.filename)
        filepath = os.path.join(PDF_FOLDER, filename)
        f.save(filepath)
        return jsonify({"status": "success", "filename": filename})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Serve PDF
@app.route('/pdfs/<filename>', methods=['GET', 'DELETE'])
def serve_pdf(filename):
    filename = secure_filename(filename)
    if request.method == 'DELETE':
        filepath = os.path.join(PDF_FOLDER, filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return jsonify({"status": "success", "message": "File deleted"})
            else:
                return jsonify({"status": "error", "message": "File not found"}), 404
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return send_from_directory(PDF_FOLDER, filename)

# List uploaded PDFs
@app.route('/list_pdfs', methods=['GET'])
def list_pdfs():
    try:
        files = os.listdir(PDF_FOLDER)
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        return jsonify({"status": "success", "files": pdf_files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Serve frontend
@app.route('/')
def index():
    return send_from_directory(STATIC_FOLDER, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
