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

    return jsonify({
        "verdict": data.get("verdict"),
        "score": data.get("agf_score"),
        "arcface": data.get("metrics", {}).get("cosine"),
        "reason": data.get("reason"),
        "hash_sha256": hash_evidencia,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
