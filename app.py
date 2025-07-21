import os
import tempfile
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# API kalitlaringiz
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

    # Faylni vaqtinchalik saqlash
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        file.save(tmp_file.name)
        tmp_file_path = tmp_file.name

    try:
        # ILovePDF API bilan sessiyani boshlash
        start_res = requests.post(
            "https://api.ilovepdf.com/v1/start/compress",
            json={"public_key": PUBLIC_KEY}
        )
        start_data = start_res.json()

        if start_res.status_code != 200 or "server" not in start_data:
            return jsonify({"error": "ILovePDF bilan ulanishda muammo", "response": start_data}), 500

        server = start_data["server"]
        task = start_data["task"]

        # Faylni yuklash
        with open(tmp_file_path, "rb") as f:
            upload_res = requests.post(
                f"https://{server}/v1/upload",
                data={"task": task},
                files={"file": (file.filename, f)}
            )
        upload_data = upload_res.json()
        if upload_res.status_code != 200 or "server_filename" not in upload_data:
            return jsonify({"error": "Faylni yuklashda xatolik", "response": upload_data}), 500

        server_filename = upload_data["server_filename"]

        # Siqishni boshlash
        process_res = requests.post(
            f"https://{server}/v1/process",
            json={
                "task": task,
                "tool": "compress",
                "files": [{"server_filename": server_filename, "filename": file.filename}],
                "compression_level": "recommended"
            }
        )
        process_data = process_res.json()
        if process_res.status_code != 200 or "status" not in process_data:
            return jsonify({"error": "Siqishda xatolik", "response": process_data}), 500

        # Natijani yuklab olish
        download_res = requests.get(
            f"https://{server}/v1/download/{task}",
            stream=True
        )
        output_path = os.path.join(tempfile.gettempdir(), "compressed_" + file.filename)
        with open(output_path, "wb") as f:
            for chunk in download_res.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": "Xatolik yuz berdi", "detail": str(e)}), 500
    finally:
        os.remove(tmp_file_path)

if __name__ == "__main__":
    app.run(debug=True)
