from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import cv2
from werkzeug.utils import secure_filename

from utils.preprocess import process_image
from utils.ocr import extract_text
from utils.parser import parse_ktp

# ==========================================
# Flask Config
# ==========================================

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER

# ==========================================
# Serve Static Files
# ==========================================

@app.route("/uploads/<path:filename>")
def serve_uploads(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/processed/<path:filename>")
def serve_processed(filename):
    return send_from_directory(app.config["PROCESSED_FOLDER"], filename)


# ==========================================
# Home
# ==========================================

@app.route("/")
def index():
    return render_template("index.html")


# ==========================================
# Scan KTP
# ==========================================

@app.route("/scan", methods=["POST"])
def scan():

    if "image" not in request.files:
        return jsonify({
            "success": False,
            "message": "Tidak ada gambar."
        })

    file = request.files["image"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "File kosong."
        })

    filename = secure_filename(file.filename)

    upload_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(upload_path)

    # --------------------------------------
    # Image Processing
    # --------------------------------------

    process_result = process_image(
        upload_path,
        app.config["PROCESSED_FOLDER"]
    )

    # --------------------------------------
    # OCR (dual pass untuk akurasi maksimal)
    # --------------------------------------

    # Pass 1: OCR pada gambar original (untuk menangkap NIK yang mungkin terpotong)
    raw_text_original = extract_text(
        process_result["original"]
    )

    # Pass 2: OCR pada gambar CLAHE (untuk teks yang lebih jelas)
    raw_text_clahe = extract_text(
        process_result["clahe"]
    )

    # Gabungkan hasil kedua OCR
    raw_text = raw_text_original + "\n" + raw_text_clahe

    # --------------------------------------
    # Parser
    # --------------------------------------

    data = parse_ktp(raw_text)

    # --------------------------------------
    # Response
    # --------------------------------------

    return jsonify({

        "success": True,

        "message": "Scan berhasil.",

        "images": {

            "original": process_result["original"],

            "blur": process_result["blur"],

            "gray": process_result["gray"],

            "clahe": process_result["clahe"],

            "threshold": process_result["threshold"]

        },

        "raw_text": raw_text,

        "data": data

    })


# ==========================================
# Run
# ==========================================

if __name__ == "__main__":
    app.run(
        debug=True
    )