import os
import tempfile
from flask import Flask, request, send_file, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Frontend integratsiyasi uchun

# ILovePDF API kalit
ILOVEPDF_SECRET = "secret_key_585ab4d86b672f4a7cf317577eeed234_o1iAu2ae4130c0faea3f83fb367acc19c247d"
BASE_URL = "https://api.ilovepdf.com/v1"

# Health check yo‘li - UptimeRobot uchun
@app.route("/ping")
def ping():
    return "pong", 200

# HTML interfeysni ochish
@app.route('/')
def home():
    return render_template("index.html")

# ILovePDF bilan fayl siqish
@app.route('/compress', methods=['POST'])
def compress_file():
    file = request.files['file']
    ext = file.filename.split('.')[-1].lower()

    if ext == "pdf":
        tool = "compress"
    elif ext in ["jpg", "jpeg", "png"]:
        tool = "imagecompress"
    elif ext in ["docx", "pptx"]:
        tool = "officepdf"
    else:
        return "Qo‘llab-quvvatlanmaydigan format", 400

    # Boshlanish task
    task = requests.post(f"{BASE_URL}/start/{tool}", data={"public_key": ILOVEPDF_SECRET}).json()

    # Faylni vaqtincha saqlash va yuklash
    upload_url = task["server"]
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        file.save(tmp.name)
        response = requests.post(
            f"{upload_url}/v1/upload",
            files={"file": open(tmp.name, "rb")},
            data={"task": task["task"]}
        )
    file_data = response.json()

    # Agar office bo‘lsa, PDFga aylantiriladi, so‘ng siqiladi
    if tool == "officepdf":
        requests.post(f"{upload_url}/v1/process", data={"task": task["task"]}).json()

        # Yangi compress task
        task2 = requests.post(f"{BASE_URL}/start/compress", data={"public_key": ILOVEPDF_SECRET}).json()
        upload_url2 = task2["server"]
        response2 = requests.post(
            f"{upload_url2}/v1/upload",
            files={"file": open(tmp.name, "rb")},
            data={"task": task2["task"]}
        )
        requests.post(f"{upload_url2}/v1/process", data={"task": task2["task"]})
        download_info = requests.get(f"{upload_url2}/v1/download/{task2['task']}").json()
    else:
        requests.post(f"{upload_url}/v1/process", data={"task": task["task"]})
        download_info = requests.get(f"{upload_url}/v1/download/{task['task']}").json()

    # Yuklab olish
    file_url = download_info['download_url']
    response = requests.get(file_url)
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    with open(output_file.name, 'wb') as f:
        f.write(response.content)

    return send_file(output_file.name, as_attachment=True, download_name="compressed.pdf")

if __name__ == '__main__':
    app.run(debug=True)
