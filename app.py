import os
import tempfile
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, origins=["https://oefenplus.uz"])

@app.route("/api/compress", methods=["POST"])
def compress():
    return jsonify({"message": "Compress endpoint is working"})


# ILovePDF API kalitlari
ILOVEPDF_SECRET = "secret_key_585ab4d86b672f4a7cf317577eeed234_o1iAu2ae4130c0faea3f83fb367acc19c247d"
BASE_URL = "https://api.ilovepdf.com/v1"

@app.route("/ping")
def ping():
    return "pong", 200

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/compress', methods=['POST'])
def compress_file():
    uploaded_file = request.files['file']
    filename = uploaded_file.filename
    ext = filename.rsplit('.', 1)[-1].lower()

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
        return "Qo‘llab-quvvatlanmaydigan format", 400

    # Start task
    task = requests.post(f"{BASE_URL}/start/{tool}", data={"public_key": ILOVEPDF_SECRET}).json()
    upload_url = task["server"]

    # Faylni vaqtincha saqlash
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        uploaded_file.save(tmp.name)
        tmp_file_path = tmp.name

    # Upload
    with open(tmp_file_path, "rb") as f:
        response = requests.post(
            f"{upload_url}/v1/upload",
            files={"file": f},
            data={"task": task["task"]}
        )
    if response.status_code != 200:
        return "Yuklashda xatolik", 500

    # Process
    requests.post(f"{upload_url}/v1/process", data={"task": task["task"]})

    # Download
    download_info = requests.get(f"{upload_url}/v1/download/{task['task']}").json()
    file_url = download_info['download_url']

    # Final download
    response = requests.get(file_url)
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix=output_ext)
    with open(output_file.name, 'wb') as f:
        f.write(response.content)

    return send_file(output_file.name, as_attachment=True, download_name=f"compressed{output_ext}")

if __name__ == '__main__':
    app.run(debug=True)
