#!/usr/bin/env python3
"""
AGF API Server v12.4.7.8-STRONG
================================
Endpoint HTTP para auditoría forense de imágenes generadas por IA.
Expone el motor agf_full.sh a través de Flask.

MAXCAP implementado en código:
  - Input texto: 200 caracteres (N10)
  - Imágenes: 10 MB por archivo
  - Respuesta JSON: 5 KB
  - Timeout del motor: 60 segundos
"""

import os
import subprocess
import hashlib
import json
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS
from tools.acta_final import generar_acta, guardar_acta
from core.agf_ledger import registrar_evidencia
from core.governance_middleware import GovernanceMiddleware

app = Flask(__name__)
governance = GovernanceMiddleware(maxcap_chars=MAXCAP_INPUT_CHARS)
CORS(app)

# ─────────────────────────────────────────────────────────────
# MAXCAP: CONSTANTES DE LÍMITES DE CAPACIDAD
# ─────────────────────────────────────────────────────────────
MAXCAP_INPUT_CHARS = 200              # N10: texto de entrada
MAXCAP_IMAGEN_BYTES = 10 * 1024 * 1024  # 10 MB por imagen
MAXCAP_OUTPUT_BYTES = 5120            # 5 KB para JSON de respuesta
MAXCAP_TIMEOUT_SEG = 60               # 60 segundos máximo del motor

# Rutas
ENGINE_SCRIPT = "./agf_full.sh"
EVIDENCE_DIR = "./termux_sealed"


# ─────────────────────────────────────────────────────────────
# VALIDACIÓN DE MAXCAP
# ─────────────────────────────────────────────────────────────
def validar_input(form_data, files):
    """
    Valida que el input no exceda los MAXCAP definidos.
    Retorna (ok, error_response).
    """
    # 1. Validar texto del formulario (N10)
    total_form = sum(len(str(v)) for v in form_data.values())
    if total_form > MAXCAP_INPUT_CHARS:
        return False, {
            "status": "BLOCKED",
            "reason": "ACTA_FUERA_DE_LIMITE",
            "detalle": f"Texto de entrada ({total_form} chars) "
                       f"excede MAXCAP de {MAXCAP_INPUT_CHARS} caracteres (N10)."
        }

    # 2. Validar imágenes (10 MB cada una)
    for img, name in [(f, k) for k, f in files.items()]:
        img.seek(0, os.SEEK_END)
        size = img.tell()
        img.seek(0)
        if size > MAXCAP_IMAGEN_BYTES:
            return False, {
                "status": "BLOCKED",
                "reason": "ACTA_FUERA_DE_LIMITE",
                "detalle": f"Imagen '{name}' ({size} bytes) "
                           f"excede MAXCAP de {MAXCAP_IMAGEN_BYTES} bytes (10 MB)."
            }

    return True, None


def validar_output(response_data):
    """
    Valida que la respuesta JSON no exceda el MAXCAP de salida.
    Retorna (ok, error_response).
    """
    response_json = json.dumps(response_data)
    size = len(response_json.encode('utf-8'))
    if size > MAXCAP_OUTPUT_BYTES:
        return False, {
            "status": "BLOCKED",
            "reason": "ACTA_FUERA_DE_LIMITE",
            "detalle": f"Respuesta de {size} bytes "
                       f"excede MAXCAP de {MAXCAP_OUTPUT_BYTES} bytes (5 KB)."
        }
    return True, None


# ─────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    """Health check para Docker/Kubernetes."""
    return jsonify({
        "status": "healthy",
        "engine": "AGF v12.4.7.8-STRONG",
        "kernel": "v0.9.8",
        "maxcap": {
            "input_chars": MAXCAP_INPUT_CHARS,
            "imagen_bytes": MAXCAP_IMAGEN_BYTES,
            "output_bytes": MAXCAP_OUTPUT_BYTES,
            "timeout_seg": MAXCAP_TIMEOUT_SEG
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


@app.route("/audit", methods=["POST"])
def audit():
    """
    Recibe dos imágenes (original + generated) y ejecuta el motor forense.
    Valida MAXCAP antes y después de procesar.
    """
    # ─────────────────────────────────────────────────────────
    # 1. VALIDAR INPUT (MAXCAP)
    # ─────────────────────────────────────────────────────────
    if "original" not in request.files or "generated" not in request.files:
        return jsonify({
            "status": "BLOCKED",
            "reason": "FALTAN_IMAGENES",
            "detalle": "Se requieren 'original' y 'generated'."
        }), 400

    # 1. Validar con el middleware de gobernanza (código, no solo prompt)
    input_str = str(request.form) + str(request.files)
    ok, error = governance.validate_input(input_str)
    if not ok:
        return jsonify(error), 413

    # 2. Validar con la función local (imágenes)
    ok, error = validar_input(request.form, request.files)
    if not ok:
        return jsonify(error), 413

    # ─────────────────────────────────────────────────────────
    # 2. GUARDAR IMÁGENES TEMPORALMENTE
    # ─────────────────────────────────────────────────────────
    # Directorio temporal configurable (portable: Termux, Linux, VPS)
    AUDIT_TMP = os.environ.get(
        "AGF_AUDIT_TMP",
        os.path.join(os.path.expanduser("~"), "tmp", "agf_audit")
    )
    os.makedirs(AUDIT_TMP, exist_ok=True)
    original_path = os.path.join(AUDIT_TMP, "original.jpg")
    generated_path = os.path.join(AUDIT_TMP, "generated.jpg")

    request.files["original"].save(original_path)
    request.files["generated"].save(generated_path)

    # ─────────────────────────────────────────────────────────
    # 3. EJECUTAR MOTOR (con MAXCAP de tiempo)
    # ─────────────────────────────────────────────────────────
    try:
        result = subprocess.run(
            [ENGINE_SCRIPT, original_path, generated_path, "preservation"],
            capture_output=True,
            text=True,
            timeout=MAXCAP_TIMEOUT_SEG
        )
        log_output = result.stdout + result.stderr

    except subprocess.TimeoutExpired:
        return jsonify({
            "status": "BLOCKED",
            "reason": "ACTA_FUERA_DE_LIMITE",
            "detalle": f"Motor excedió MAXCAP de {MAXCAP_TIMEOUT_SEG} segundos."
        }), 504

    except FileNotFoundError:
        return jsonify({
            "status": "BLOCKED",
            "reason": "MOTOR_NO_ENCONTRADO",
            "detalle": f"No se encontró {ENGINE_SCRIPT}."
        }), 500

    # ─────────────────────────────────────────────────────────
    # 4. LEER EVIDENCIA
    # ─────────────────────────────────────────────────────────
    out_path = os.path.join(EVIDENCE_DIR, "composite_audit.json")
    if not os.path.exists(out_path):
        return jsonify({
            "status": "BLOCKED",
            "reason": "SIN_EVIDENCIA",
            "detalle": "El motor no generó composite_audit.json.",
            "log_tail": log_output[-500:]
        }), 500

    with open(out_path) as f:
        data = json.load(f)

    # ─────────────────────────────────────────────────────────
    # 5. SELLAR CON SHA-256
    # ─────────────────────────────────────────────────────────
    hash_evidencia = hashlib.sha256(
        json.dumps(data, sort_keys=True).encode()
    ).hexdigest()

    # ─────────────────────────────────────────────────────────
    # 6. CONSTRUIR RESPUESTA
    # ─────────────────────────────────────────────────────────
    response_data = {
        "verdict": data.get("verdict"),
        "score": data.get("agf_score"),
        "arcface": data.get("metrics", {}).get("cosine"),
        "reason": data.get("reason"),
        "hash_sha256": hash_evidencia,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # ─────────────────────────────────────────────────────────
    # 7. GENERAR ACTA FINAL (certificado de auditoría)
    # ─────────────────────────────────────────────────────────
    try:
        original_hash = hashlib.sha256(open(original_path, "rb").read()).hexdigest()
        generated_hash = hashlib.sha256(open(generated_path, "rb").read()).hexdigest()
        
        acta = generar_acta(
            veredicto=data.get("verdict"),
            score=data.get("agf_score"),
            arcface=data.get("metrics", {}).get("cosine"),
            reason=data.get("reason"),
            original_hash=original_hash,
            generated_hash=generated_hash
        )
        acta_path = guardar_acta(acta)
        response_data["acta_final"] = {
            "hash_acta": acta["hash_acta"],
            "archivo": os.path.basename(acta_path)
        }
        
        # Registrar en el ledger hash-chain
        try:
            ledger_path = registrar_evidencia(acta_path, data)
            response_data["ledger"] = {
                "registrado": True,
                "path": os.path.basename(ledger_path)
            }
        except Exception as e:
            response_data["ledger"] = {"error": str(e)}
    except Exception as e:
        # Si falla el acta, no bloqueamos la respuesta principal
        response_data["acta_final"] = {
            "error": f"No se pudo generar el acta: {str(e)}"
        }

    # ─────────────────────────────────────────────────────────
    # 8. VALIDAR OUTPUT (MAXCAP)
    # ─────────────────────────────────────────────────────────
    ok, error = validar_output(response_data)
    if not ok:
        return jsonify(error), 500

    return jsonify(response_data), 200


if __name__ == "__main__":
    print(f"AGF API Server")
    print(f"  MAXCAP input:   {MAXCAP_INPUT_CHARS} chars")
    print(f"  MAXCAP imagen:  {MAXCAP_IMAGEN_BYTES} bytes")
    print(f"  MAXCAP output:  {MAXCAP_OUTPUT_BYTES} bytes")
    print(f"  MAXCAP timeout: {MAXCAP_TIMEOUT_SEG} seg")
    print(f"  Escuchando en http://0.0.0.0:8000")
    app.run(host="0.0.0.0", port=8000, debug=False)
