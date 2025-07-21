import os
import tempfile
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# ILovePDF API kalitlari (bevosita kodga kiritilgan)
PUBLIC_KEY = "project_public_75ac534f3100a01d912c0b16a62b4294_pn67M040b8b2ae23a4c254fcfb92cf0889ec8"
SECRET_KEY = "secret_key_cd62d359458853c2d2d90ff0c83a40f1_IQbCN31adb55313dbd7ef362e72bd55aa4f0d"

@app.route("/")
def index():
    return "ILovePDF Converter ishlayapti!"

@app.route("/ping")
def ping():
    return jsonify({"message": "pong"}), 200

@app.route("/api/compress", methods=["POST"])
def compress_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "Fayl yuborilmadi"}), 400

    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)

    # Faylni vaqtinchalik saqlash
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        uploaded_file.save(tmp.name)
        file_path = tmp.name

    try:
        # 1. Start compress task
        start_res = requests.post("https://api.ilovepdf.com/v1/start/compress", json={
            "public_key": PUBLIC_KEY
        })
        if start_res.status_code != 200:
            return jsonify({"error": "Start bosqichida xatolik", "detail": start_res.text}), 500

        task_data = start_res.json()
        server = task_data["server"]
        task = task_data["task"]

        # 2. Upload file
        with open(file_path, 'rb') as f:
            upload_res = requests.post(
                f"https://{server}/v1/upload",
                data={"task": task},
                files={"file": (filename, f)}
            )
        if upload_res.status_code != 200:
            return jsonify({"error": "Yuklashda xatolik", "detail": upload_res.text}), 500

        # 3. Process
        process_res = requests.post(
            f"https://{server}/v1/process",
            json={"task": task}
        )
        if process_res.status_code != 200:
            return jsonify({"error": "Process xatolik", "detail": process_res.text}), 500

        # 4. Download
        download_res = requests.get(
            f"https://{server}/v1/download/{task}",
            stream=True
        )
        if download_res.status_code != 200:
            return jsonify({"error": "Yuklab olishda xatolik", "detail": download_res.text}), 500

        # Faylni saqlash va yuborish
        output_path = os.path.join(tempfile.gettempdir(), "compressed_" + filename)
        with open(output_path, "wb") as f:
            for chunk in download_res.iter_content(chunk_size=1024):
                f.write(chunk)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": "Serverda xatolik", "detail": str(e)}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    app.run(debug=True)
