import os
import tempfile
import requests
from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# API kalitlar
TINIFY_API_KEY = os.getenv("TINIFY_API_KEY")
CLOUDMERSIVE_API_KEY = os.getenv("CLOUDMERSIVE_API_KEY")
ILOVEPDF_PUBLIC_KEY = os.getenv("ILOVEPDF_PUBLIC_KEY")

@app.route("/ping")
def ping():
    return "pong", 200

def compress_jpg(file_path, output_path):
    endpoint = "https://api.tinify.com/shrink"
    auth = requests.auth.HTTPBasicAuth("api", TINIFY_API_KEY)
    with open(file_path, 'rb') as f:
        response = requests.post(endpoint, auth=auth, data=f)
    response.raise_for_status()
    result_url = response.json()['output']['url']
    result = requests.get(result_url)
    with open(output_path, 'wb') as out:
        out.write(result.content)

def compress_pdf(file_path, output_path):
    # 1. Start task
    start_url = "https://api.ilovepdf.com/v1/start/compress"
    start_res = requests.post(start_url, data={"public_key": ILOVEPDF_PUBLIC_KEY})
    start_res.raise_for_status()
    task_info = start_res.json()
    server = task_info["server"]
    task = task_info["task"]

    # 2. Upload file
    with open(file_path, "rb") as f:
        upload_res = requests.post(f"https://{server}/v1/upload", data={"task": task}, files={"file": f})
    upload_res.raise_for_status()

    # 3. Process
    process_res = requests.post(f"https://{server}/v1/process", data={"task": task})
    process_res.raise_for_status()

    # 4. Download
    download_res = requests.get(f"https://{server}/v1/download/{task}", stream=True)
    download_res.raise_for_status()

    with open(output_path, "wb") as out_file:
        for chunk in download_res.iter_content(chunk_size=8192):
            out_file.write(chunk)

def compress_office(file_path, output_path):
    ext = file_path.lower().split('.')[-1]
    endpoint_map = {
        "docx": "https://api.cloudmersive.com/convert/docx/compress",
        "pptx": "https://api.cloudmersive.com/convert/pptx/compress"
    }
    if ext not in endpoint_map:
        raise ValueError("Fayl turi qo‘llab-quvvatlanmaydi.")
    endpoint = endpoint_map[ext]
    headers = {"Apikey": CLOUDMERSIVE_API_KEY}
    files = {'inputFile': open(file_path, 'rb')}
    response = requests.post(endpoint, headers=headers, files=files)
    response.raise_for_status()
    with open(output_path, 'wb') as out:
        out.write(response.content)

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
            elif ext == 'pdf':
                compress_pdf(input_temp.name, output_temp.name)
            elif ext in ['docx', 'pptx']:
                compress_office(input_temp.name, output_temp.name)
            else:
                return jsonify({"error": "Qo‘llab-quvvatlanmaydigan fayl turi"}), 400

            return send_file(output_temp.name, as_attachment=True, download_name=f"compressed.{ext}")

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            os.remove(input_temp.name)
            if os.path.exists(output_temp.name):
                os.remove(output_temp.name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
