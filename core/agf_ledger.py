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
    
    event = {
        "event_type": "audit_completed",
        "acta_path": acta_path,
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
