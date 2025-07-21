import os
import tempfile
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# ILovePDF API kalitlari
PUBLIC_KEY = "project_public_75ac534f3100a01d912c0b16a62b4294_pn67M040b8b2ae23a4c254fcfb92cf0889ec8"
SECRET_KEY = "secret_key_cd62d359458853c2d2d90ff0c83a40f1_IQbCN31adb55313dbd7ef362e72bd55aa4f0d"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ping")
def ping():
    return jsonify({"message": "ILovePDF backend ishlayapti"}), 200

@app.route("/api/compress", methods=["POST"])
def compress_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "Fayl yuborilmadi"}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)

    # Faylni vaqtinchalik saqlash
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        file.save(tmp_file.name)
        tmp_file_path = tmp_file.name

    output_path = os.path.join(tempfile.gettempdir(), "compressed_" + filename)

    try:
        # 1. Task yaratish
        start_res = requests.post("https://api.ilovepdf.com/v1/start/compress", data={"public_key": PUBLIC_KEY})
        if start_res.status_code != 200:
            return jsonify({"error": "Task yaratishda xatolik", "response": start_res.text}), 500

        start_data = start_res.json()
        task = start_data["task"]
        server = start_data["server"]

        # 2. Faylni yuklash
        upload_url = f"https://{server}/v1/upload"
        with open(tmp_file_path, "rb") as f:
            upload_res = requests.post(upload_url, data={"task": task}, files={"file": f})
        if upload_res.status_code != 200:
            return jsonify({"error": "Faylni yuklashda xatolik", "response": upload_res.text}), 500

        uploaded_data = upload_res.json()
        server_filename = uploaded_data["server_filename"]

        # 3. Siqishni boshlash
        process_url = f"https://{server}/v1/process"
        process_res = requests.post(process_url, data={
            "task": task,
            "tool": "compress",
            "files": server_filename
        })
        if process_res.status_code != 200:
            return jsonify({"error": "Faylni siqishda xatolik", "response": process_res.text}), 500

        # 4. Siqilgan faylni yuklab olish
        download_url = f"https://{server}/v1/download/{task}"
        download_res = requests.get(download_url, stream=True)
        if download_res.status_code != 200:
            return jsonify({"error": "Siqilgan faylni yuklab olishda xatolik", "response": download_res.text}), 500

        with open(output_path, "wb") as out_file:
            for chunk in download_res.iter_content(1024):
                out_file.write(chunk)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": "Xatolik yuz berdi", "detail": str(e)}), 500

    finally:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == "__main__":
    app.run(debug=True)
