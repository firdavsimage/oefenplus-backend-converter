import os
import tempfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# PDF.co API KEY
PDFCO_API_KEY = "oefen.uz@gmail.com_5UDt3xOMzK4KbsHaiXY6twp8jsjiygoiVESOcJlMTCoXFgUP5T6BnylqcTSyR48O"

@app.route("/")
def index():
    return "PDF.co Compress Converter ishlayapti!"

@app.route("/ping")
def ping():
    return jsonify({"message": "pong"}), 200

@app.route("/api/compress", methods=["POST"])
def compress_file():
    if 'file' not in request.files:
        return jsonify({"error": "Fayl yuborilmadi"}), 400

    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
        uploaded_file.save(tmp.name)
        input_path = tmp.name

    try:
        # Faylni PDF.co serveriga yuborish
        with open(input_path, 'rb') as f:
            response = requests.post(
                "https://api.pdf.co/v1/pdf/convert/to/pdf",
                headers={"x-api-key": PDFCO_API_KEY},
                files={"file": (filename, f)},
                data={"name": "compressed-output.pdf"}
            )

        if response.status_code != 200 or not response.json().get("url"):
            return jsonify({"error": "Siqish vaqtida xatolik", "detail": response.text}), 500

        # Siqilgan faylni yuklab olish
        download_url = response.json()["url"]
        download_response = requests.get(download_url, stream=True)

        if download_response.status_code != 200:
            return jsonify({"error": "Yuklab olishda xatolik", "detail": download_response.text}), 500

        output_path = os.path.join(tempfile.gettempdir(), "compressed_" + filename + ".pdf")
        with open(output_path, "wb") as f:
            for chunk in download_response.iter_content(chunk_size=1024):
                f.write(chunk)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": "Server xatosi", "detail": str(e)}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

if __name__ == "__main__":
    app.run(debug=True)
