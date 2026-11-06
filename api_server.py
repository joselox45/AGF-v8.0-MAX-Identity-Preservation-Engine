#!/usr/bin/env python3
"""
AGF API Server — Endpoint HTTP para auditoría forense.
Expone el motor agf_full.sh a través de Flask.
"""
import os
import subprocess
import hashlib
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ENGINE_SCRIPT = "./agf_full.sh"
EVIDENCE_DIR = "./termux_sealed"
MAXCAP_IMAGEN_BYTES = 10 * 1024 * 1024  # 10 MB
MAXCAP_INPUT_CHARS = 200  # N10
MAXCAP_OUTPUT_BYTES = 5120  # 5 KB para el JSON de respuesta  # 10 MB


@app.route("/health", methods=["GET"])
def health():
    """Health check para Docker/Kubernetes."""
    return jsonify({
        "status": "healthy",
        "engine": "AGF v12.4.7.8-STRONG",
        "kernel": "v0.9.8",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200


@app.route("/audit", methods=["POST"])
def audit():
    """Recibe dos imágenes y ejecuta el motor forense."""
    # MAXCAP: Validar que el request no exceda el límite
    total_form = sum(len(str(v)) for v in request.form.values())
    total_files = sum(f.content_length or 0 for f in request.files.values())
    total_input = total_form + total_files
    if total_input > MAXCAP_OUTPUT_BYTES * 2:
        return jsonify({
            "status": "BLOCKED",
            "reason": "ACTA_FUERA_DE_LIMITE",
            "detalle": f"Input de {total_input} bytes excede MAXCAP"
        }), 413

    if "original" not in request.files or "generated" not in request.files:
        return jsonify({"error": "Faltan las imágenes 'original' y 'generated'"}), 400

    original = request.files["original"]
    generated = request.files["generated"]

    # MAXCAP: Validar tamaño de las imágenes
    for img, name in [(original, "original"), (generated, "generated")]:
        img.seek(0, os.SEEK_END)
        size = img.tell()
        img.seek(0)
        if size > MAXCAP_IMAGEN_BYTES:
            return jsonify({"error": f"Imagen '{name}' excede MAXCAP (10MB)"}), 413

    # Guardar temporalmente
    os.makedirs("/tmp/agf_audit", exist_ok=True)
    original_path = "/tmp/agf_audit/original.jpg"
    generated_path = "/tmp/agf_audit/generated.jpg"
    original.save(original_path)
    generated.save(generated_path)

    # Ejecutar el motor
    try:
        result = subprocess.run(
            [ENGINE_SCRIPT, original_path, generated_path, "preservation"],
            capture_output=True, text=True, timeout=60
        )
        log_output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Motor excedió MAXCAP de 60 segundos"}), 504

    # Leer el contenedor OUT
    out_path = os.path.join(EVIDENCE_DIR, "composite_audit.json")
    if os.path.exists(out_path):
        with open(out_path) as f:
            data = json.load(f)
    else:
        return jsonify({"error": "No se generó evidencia", "log": log_output[-500:]}), 500

    # Sellar con hash
    hash_evidencia = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    response_data = {
        "verdict": data.get("verdict"),
        "score": data.get("agf_score"),
        "arcface": data.get("metrics", {}).get("cosine"),
        "reason": data.get("reason"),
        "hash_sha256": hash_evidencia,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    # MAXCAP: Validar que la respuesta no exceda 5KB
    response_json = json.dumps(response_data)
    if len(response_json.encode()) > MAXCAP_OUTPUT_BYTES:
        return jsonify({
            "status": "BLOCKED",
            "reason": "ACTA_FUERA_DE_LIMITE",
            "detalle": f"Respuesta de {len(response_json)} bytes excede MAXCAP"
        }), 500
    return jsonify(response_data), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
