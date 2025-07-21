import os
import tempfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# PDF.co API kaliti
PDFCO_API_KEY = "oefen.uz@gmail.com_5UDt3xOMzK4KbsHaiXY6twp8jsjiygoiVESOcJlMTCoXFgUP5T6BnylqcTSyR48O"

@app.route("/")
def index():
    return "PDF.co Converter ishlayapti!"

@app.route("/ping")
def ping():
    return jsonify({"message": "pong"}), 200

@app.route("/api/compress", methods=["POST"])
def compress_file():
    if 'file' not in request.files:
        return jsonify({"error": "Fayl yuborilmadi"}), 400

    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    ext = os.path.splitext(filename)[1].lower()

    # Faqat ruxsat etilgan formatlar
    allowed = ['.pdf', '.jpg', '.jpeg', '.png', '.docx', '.pptx', '.xlsx']
    if ext not in allowed:
        return jsonify({"error": f"Bu fayl turi qo‘llab-quvvatlanmaydi: {ext}"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        uploaded_file.save(tmp.name)
        local_file_path = tmp.name

    try:
        # Faylni base64 formatga o‘girish
        with open(local_file_path, "rb") as f:
            file_data = f.read()
        file_base64 = file_data.encode("base64") if hasattr(file_data, "encode") else file_data

        # PDF.co endpoint — universal siqish uchun (PDF va rasmlar uchun)
        if ext == '.pdf':
            endpoint = "https://api.pdf.co/v1/pdf/optimize"
        elif ext in ['.jpg', '.jpeg', '.png']:
            endpoint = "https://api.pdf.co/v1/pdf/convert/from/image"
        elif ext == '.docx':
            endpoint = "https://api.pdf.co/v1/pdf/convert/from/doc"
        elif ext == '.pptx':
            endpoint = "https://api.pdf.co/v1/pdf/convert/from/ppt"
        elif ext == '.xlsx':
            endpoint = "https://api.pdf.co/v1/pdf/convert/from/xls"
        else:
            return jsonify({"error": "Qo‘llanmaydigan fayl turi"}), 400

        # PDF.co API chaqiruvi
        with open(local_file_path, 'rb') as f:
            response = requests.post(
                url=endpoint,
                headers={"x-api-key": PDFCO_API_KEY},
                files={"file": (filename, f)},
                data={}
            )

        if response.status_code != 200:
            return jsonify({"error": "PDF.co API chaqiruvida xatolik", "detail": response.text}), 500

        file_url = response.json().get("url")
        if not file_url:
            return jsonify({"error": "Natija URL topilmadi"}), 500

        # Natijani yuklab olish
        r = requests.get(file_url, stream=True)
        if r.status_code != 200:
            return jsonify({"error": "Siqilgan faylni yuklab olishda xatolik"}), 500

        output_path = os.path.join(tempfile.gettempdir(), "compressed_" + filename)
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": "Serverda xatolik", "detail": str(e)}), 500

    finally:
        if os.path.exists(local_file_path):
            os.remove(local_file_path)

if __name__ == "__main__":
    app.run(debug=True)
