from flask import Flask, request, send_file, jsonify
import tempfile
import os
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from docx import Document
from pptx import Presentation

app = Flask(__name__)

def compress_image(input_path, output_path, quality=60):
    img = Image.open(input_path)
    img.save(output_path, optimize=True, quality=quality)

def compress_pdf(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)

def compress_docx(input_path, output_path):
    doc = Document(input_path)
    for shape in doc.inline_shapes:
        if shape.type == 3:
            shape.width = int(shape.width * 0.7)
            shape.height = int(shape.height * 0.7)
    doc.save(output_path)

def compress_pptx(input_path, output_path):
    prs = Presentation(input_path)
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.shape_type == 13:
                shape.width = int(shape.width * 0.7)
                shape.height = int(shape.height * 0.7)
    prs.save(output_path)

def compress_file(input_path, output_path):
    ext = input_path.lower().split('.')[-1]
    if ext in ['jpg', 'jpeg', 'png']:
        compress_image(input_path, output_path)
    elif ext == 'pdf':
        compress_pdf(input_path, output_path)
    elif ext == 'docx':
        compress_docx(input_path, output_path)
    elif ext == 'pptx':
        compress_pptx(input_path, output_path)
    else:
        raise ValueError("Fayl turini aniqlab bo‘lmadi")

@app.route("/api/compress", methods=["POST"])
def compress_endpoint():
    if 'file' not in request.files:
        return jsonify({"error": "Fayl topilmadi"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Fayl tanlanmagan"}), 400

    ext = file.filename.rsplit('.', 1)[-1].lower()

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, f"input.{ext}")
        output_path = os.path.join(tmpdir, f"output.{ext}")
        file.save(input_path)

        try:
            compress_file(input_path, output_path)
            return send_file(output_path, as_attachment=True, download_name=f"compressed.{ext}")
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route("/ping")
def ping():
    return "pong"
