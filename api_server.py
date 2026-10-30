from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
import uuid
import subprocess

app = Flask(__name__)
CORS(app)

@app.route("/")
def health_check():
    return jsonify({"status": "AGF API is running", "version": "v12.2", "engine": "Flask"})

@app.route("/api/v1/verify", methods=["POST"])
def verify_images():
    # Verificar que las imágenes llegaron en la petición
    if "original" not in request.files or "generated" not in request.files:
        return jsonify({"error": "Faltan las imágenes 'original' o 'generated'"}), 400

    file_orig = request.files["original"]
    file_gen = request.files["generated"]
    mode = request.form.get("mode", "preservation")

    # Guardar archivos temporalmente
    orig_path = f"temp_orig_{uuid.uuid4().hex}.jpg"
    gen_path = f"temp_gen_{uuid.uuid4().hex}.jpg"
    file_orig.save(orig_path)
    file_gen.save(gen_path)

    try:
        # Ejecutar el motor forense
        cmd = [
            sys.executable, "tools/agf_composite_scorer.py",
            orig_path, gen_path, "blaze_face_short_range.tflite", "--mode", mode
        ]
        subprocess.run(cmd, capture_output=True, text=True)

        # Leer el JSON de resultado
        json_path = "termux_sealed/composite_audit.json"
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                result = json.load(f)
            return jsonify(result)
        else:
            return jsonify({"error": "No se generó el archivo de auditoría"}), 500

    finally:
        # Limpieza de archivos temporales
        if os.path.exists(orig_path): os.remove(orig_path)
        if os.path.exists(gen_path): os.remove(gen_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
