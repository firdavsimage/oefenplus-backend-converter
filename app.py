import os
import tempfile
from flask import Flask, request, jsonify, send_file
from PIL import Image
from docx import Document
from pptx import Presentation
from PyPDF2 import PdfReader, PdfWriter
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# JPG/PNG siqish
def compress_jpg(input_path, output_path, quality=60):
    image = Image.open(input_path)
    image.save(output_path, optimize=True, quality=quality)

# DOCX/PPTX siqish (oddiy saqlash)
def compress_office(input_path, output_path):
    if input_path.endswith(".docx"):
        doc = Document(input_path)
        doc.save(output_path)
    elif input_path.endswith(".pptx"):
        pres = Presentation(input_path)
        pres.save(output_path)
    else:
        raise ValueError("Fayl formati noto‘g‘ri")

# PDF siqish
def compress_pdf(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Qo‘shimcha metadata va siqishni yoqish (agar kerak bo‘lsa)
    writer.add_metadata(reader.metadata)
    with open(output_path, "wb") as f:
        writer.write(f)

# Siqish endpoint
@app.route("/api/compress", methods=["POST"])
def compress_file():
    if 'file' not in request.files:
        return jsonify({"error": "Fayl topilmadi"}), 400

    file = request.files['file']
    ext = file.filename.lower().split('.')[-1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as input_temp:
        file.save(input_temp.name)

    output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
    output_temp.close()

    try:
        if ext in ['jpg', 'jpeg', 'png']:
            compress_jpg(input_temp.name, output_temp.name)
        elif ext in ['docx', 'pptx']:
            compress_office(input_temp.name, output_temp.name)
        elif ext == 'pdf':
            compress_pdf(input_temp.name, output_temp.name)
        else:
            return jsonify({"error": "Fayl turi qo‘llab-quvvatlanmaydi"}), 400

        return send_file(output_temp.name, as_attachment=True, download_name=f"compressed.{ext}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(input_temp.name)
        if os.path.exists(output_temp.name):
            os.remove(output_temp.name)

# Ping endpoint
@app.route("/ping", methods=["GET"])
def ping():
    return "pong"

if __name__ == "__main__":
    app.run(debug=True)
