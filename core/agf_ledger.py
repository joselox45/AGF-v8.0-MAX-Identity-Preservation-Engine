"""Integración del ledger hash-chain de akadi en el API del AGF."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evidence_ledger import EvidenceLedger
from evidence_verify import verify_ledger


def registrar_evidencia(acta_path, audit_data):
    """Registra la evidencia en el ledger hash-chain."""
    ledger_path = os.path.join("termux_sealed", "ledger.jsonl")
    led = EvidenceLedger(ledger_path)
    
    # Calcular el hash SHA-256 del contenido del acta
    import hashlib
    try:
        with open(acta_path, "rb") as af:
            hash_acta = hashlib.sha256(af.read()).hexdigest()
    except Exception:
        hash_acta = "ERROR_LECTURA"

    event = {
        "event_type": "audit_completed",
        "acta_path": acta_path,
        "acta_sha256": hash_acta,
        "verdict": audit_data.get("verdict"),
        "score": audit_data.get("agf_score"),
        "arcface": audit_data.get("metrics", {}).get("cosine"),
        "timestamp": audit_data.get("timestamp")
    }
    
    led.append(event)
    return ledger_path


def verificar_ledger():
    """Verifica la integridad del ledger."""
    ledger_path = os.path.join("termux_sealed", "ledger.jsonl")
    if not os.path.exists(ledger_path):
        return {"status": "NO_LEDGER"}
    return verify_ledger(ledger_path)
