import os
import tempfile
from flask import Flask, request, send_file, render_template_string, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, origins=["https://oefenplus.uz"])

# ILovePDF API kalitlari
ILOVEPDF_PUBLIC_KEY = "project_public_002668c65677139b50439696e90805e5_JO_Lt06e53e5275b342ceea0429acfc79f0d2"
ILOVEPDF_SECRET_KEY = "secret_key_cb327f74110b4e506fec5ac629878293_SkxGg3f96e8bcdd9594d8e575c15d3dab7b99"
BASE_URL = "https://api.ilovepdf.com/v1"

@app.route("/ping")
def ping():
    return "pong", 200

@app.route("/")
def index():
    return render_template_string("<h1>ILovePDF backend ishlayapti</h1>")

@app.route("/api/compress", methods=["POST"])
def compress_file():
    if 'file' not in request.files:
        return jsonify({"error": "Fayl topilmadi"}), 400

    uploaded_file = request.files['file']
    filename = uploaded_file.filename
    ext = filename.rsplit('.', 1)[-1].lower()

    # ILovePDF vositasi tanlanadi
    if ext == "pdf":
        tool = "compress"
        output_ext = ".pdf"
    elif ext in ["jpg", "jpeg", "png"]:
        tool = "imagecompress"
        output_ext = f".{ext}"
    elif ext in ["docx", "pptx"]:
        tool = "officepdf"
        output_ext = ".pdf"
    else:
        return jsonify({"error": "Qo‘llab-quvvatlanmaydigan format"}), 400

    try:
        # Task yaratish
        start_response = requests.post(f"{BASE_URL}/start/{tool}", data={"public_key": ILOVEPDF_PUBLIC_KEY})
        start_response.raise_for_status()
        task = start_response.json()
        upload_url = task["server"]

        # Faylni vaqtincha saqlash
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            uploaded_file.save(tmp.name)
            tmp_file_path = tmp.name

        # Faylni yuklash
        with open(tmp_file_path, "rb") as f:
            upload_response = requests.post(
                f"{upload_url}/v1/upload",
                files={"file": f},
                data={"task": task["task"]}
            )
        upload_response.raise_for_status()

        # Ishlov berish
        process_response = requests.post(
            f"{upload_url}/v1/process",
            data={"task": task["task"]}
        )
        process_response.raise_for_status()

        # Yuklab olish linki
        download_info = requests.get(f"{upload_url}/v1/download/{task['task']}")
        download_info.raise_for_status()
        file_url = download_info.json()['download_url']

        # Final faylni yuklab olish
        final_response = requests.get(file_url)
        final_response.raise_for_status()
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=output_ext)
        with open(output_file.name, 'wb') as f:
            f.write(final_response.content)

        return send_file(output_file.name, as_attachment=True, download_name=f"compressed{output_ext}")

    except requests.RequestException as e:
        return jsonify({"error": f"ILovePDF bilan aloqa xatosi: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Noma’lum xatolik: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
