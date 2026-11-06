#!/usr/bin/env python3
"""
Acta Final Sellada — Certificado de Auditoría AGF
==================================================
Genera un JSON firmado con hash SHA-256 que certifica el veredicto
del motor forense. Es el documento oficial para el cliente de suscripción.
"""

import json
import hashlib
import os
from datetime import datetime, timezone


MAXCAP_ACTA_BYTES = 10240  # 10 KB máximo para el acta


def generar_acta(veredicto, score, arcface, reason, original_hash, generated_hash):
    """
    Genera el Acta Final con todos los campos requeridos.
    
    Args:
        veredicto: PASS / BLOCKED / HUMAN_REVIEW
        score: float (agf_score del motor)
        arcface: float (cosine similarity)
        reason: string (razón del veredicto)
        original_hash: sha256 de la imagen original
        generated_hash: sha256 de la imagen generada
    
    Returns:
        dict con el acta completa
    """
    # 1. Timestamp UTC
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # 2. Cuerpo del acta (sin hash)
    acta = {
        "acta_version": "1.0",
        "tipo_documento": "ACTA_FINAL_SELLADA_CLOSED",
        "timestamp": timestamp,
        "veredicto": veredicto,
        "metricas": {
            "agf_score": score,
            "arcface_similarity": arcface
        },
        "razon": reason,
        "hashes": {
            "original_sha256": original_hash,
            "generated_sha256": generated_hash
        },
        "motor": {
            "engine": "AGF v12.4.7.8-STRONG",
            "kernel": "v0.9.8"
        },
        "certificado_por": "AGF-API-Server"
    }
    
    # 3. Calcular hash del acta (sin el campo hash_acta)
    acta_str = json.dumps(acta, sort_keys=True, ensure_ascii=False)
    hash_acta = hashlib.sha256(acta_str.encode()).hexdigest()
    
    # 4. Añadir el hash del acta al final
    acta["hash_acta"] = hash_acta
    
    # 5. Validar MAXCAP
    acta_json = json.dumps(acta, ensure_ascii=False, indent=2)
    if len(acta_json.encode()) > MAXCAP_ACTA_BYTES:
        raise ValueError(f"Acta excede MAXCAP ({MAXCAP_ACTA_BYTES} bytes)")
    
    return acta


def guardar_acta(acta, output_dir="./termux_sealed/actas"):
    """
    Guarda el acta en disco con un nombre único.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Nombre: ACTA_<timestamp>_<hash_corto>.json
    ts = acta["timestamp"].replace(":", "").replace("-", "").replace(".", "")[:15]
    hash_corto = acta["hash_acta"][:8]
    filename = f"ACTA_{ts}_{hash_corto}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(acta, f, indent=2, ensure_ascii=False)
    
    return filepath


def verificar_acta(filepath):
    """
    Verifica que un acta no haya sido alterada.
    Recalcula el hash y lo compara con el campo hash_acta.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        acta = json.load(f)
    
    hash_declarado = acta.pop("hash_acta", None)
    if not hash_declarado:
        return False, "Acta sin hash_acta"
    
    acta_str = json.dumps(acta, sort_keys=True, ensure_ascii=False)
    hash_calculado = hashlib.sha256(acta_str.encode()).hexdigest()
    
    if hash_calculado != hash_declarado:
        return False, f"Hash no coincide: declarado={hash_declarado[:8]}, calculado={hash_calculado[:8]}"
    
    return True, "Acta válida"


if __name__ == "__main__":
    # Test rápido
    print("Test del Acta Final:")
    acta = generar_acta(
        veredicto="PASS",
        score=0.9900,
        arcface=1.0000,
        reason="Identidad y Textura Blindadas",
        original_hash="abc123",
        generated_hash="def456"
    )
    print(f"  Veredicto: {acta['veredicto']}")
    print(f"  Hash acta: {acta['hash_acta'][:16]}...")
    
    filepath = guardar_acta(acta, "./termux_sealed/actas_test")
    print(f"  Guardada en: {filepath}")
    
    valida, msg = verificar_acta(filepath)
    print(f"  Verificación: {msg}")
