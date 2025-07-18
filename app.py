import os
import hashlib
import requests
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

CONVERT_API_SECRET = "secret_key_585ab4d86b672f4a7cf317577eeed234_o1iAu2ae4130c0faea3f83fb367acc19c247d"

@app.route("/compress", methods=["POST"])
def compress():
    if "file" not in request.files:
        return "Fayl yuborilmadi", 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[-1].lower()
    hash_name = hashlib.md5(file.read()).hexdigest()
    file.seek(0)  # qayta o'qish uchun

    cache_path = os.path.join(CACHE_DIR, f"{hash_name}.pdf")
    if os.path.exists(cache_path):
        return send_file(cache_path, as_attachment=True)

    form_data = {"file": (filename, file.stream)}
    url = f"https://v2.convertapi.com/convert/{ext}/to/pdf?Secret={CONVERT_API_SECRET}"

    r = requests.post(url, files=form_data)
    if r.status_code != 200:
        return f"Xatolik: {r.text}", 500

    result = r.json()
    if "Files" not in result or not result["Files"]:
        return "ConvertAPI javobi noto‘g‘ri", 500

    pdf_url = result["Files"][0]["Url"]
    pdf_data = requests.get(pdf_url)
    with open(cache_path, "wb") as f:
        f.write(pdf_data.content)

    return send_file(cache_path, as_attachment=True)
