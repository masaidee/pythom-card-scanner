import re
from PIL import Image, ImageFilter, ImageOps
import pytesseract
from flask import Flask, request, jsonify
import os
import io  # <--- เพิ่มบรรทัดนี้
from deepface import DeepFace
import tempfile

app = Flask(__name__)

@app.route('/upload-card', methods=['POST'])
def upload_idcard():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # บันทึกไฟล์ชั่วคราว
    filepath = os.path.join('tmp', file.filename)
    os.makedirs('tmp', exist_ok=True)
    file.save(filepath)

    # --- ปรับภาพก่อน OCR ---
    img = Image.open(filepath).convert('L')  # Grayscale
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.SHARPEN)
    img = img.point(lambda x: 0 if x < 140 else 255, '1')  # Threshold

    text = pytesseract.image_to_string(img, lang='tha+eng')

    # print(text)
    return jsonify({
        "textall": text
    })

@app.route('/compare-face', methods=['POST'])
def compare_face():
    if 'selfie' not in request.files:
        return jsonify({"error": "ต้องแนบไฟล์ selfie"}), 400
    if 'thaiId' not in request.files:
        return jsonify({"error": "ต้องแนบไฟล์ thaiId"}), 400

    selfie_file = request.files['selfie']
    thaiId_file = request.files['thaiId']

    # Save selfie เป็นไฟล์ชั่วคราว
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as selfie_tmp, \
         tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as idcard_tmp:
        
        selfie_file.save(selfie_tmp.name)
        thaiId_file.save(idcard_tmp.name)

        try:
            result = DeepFace.verify(
                img1_path=idcard_tmp.name,
                img2_path=selfie_tmp.name,
                enforce_detection=True
            )
            return jsonify({
                "verified": result["verified"],
                "distance": result["distance"],
                "threshold": result["threshold"],
                "message": "ตรงกัน" if result["verified"] else "ไม่ตรงกัน"
            })
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return jsonify({"error": str(e)}), 400
        finally:
            os.remove(selfie_tmp.name)
            os.remove(idcard_tmp.name)


if __name__ == "__main__":
    # For Docker: allow host/port override via env vars
    host = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_RUN_PORT", 8000))
    app.run(host=host, port=port)
