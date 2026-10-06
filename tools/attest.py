#!/usr/bin/env python3
"""
AGF — Attestation independiente (APCE).
Un tercero verifica un archivo de evidencia y lo firma con SU clave Ed25519.
Uso:
  python tools/attest.py evidence/t21_tflite.json [--seed HEX64]
Emite evidence/attestation_<archivo>.json con veredicto ATTESTED/REJECTED.
Requiere: pkg install python-cryptography
"""
import argparse, hashlib, json, os, sys
from datetime import datetime, timezone

ap = argparse.ArgumentParser()
ap.add_argument("evidence_file")
ap.add_argument("--seed", default=None, help="64 hex chars; si omite, genera")
a = ap.parse_args()

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
except ImportError:
    print(json.dumps({"status": "BLOCKED",
                      "reason": "python-cryptography requerido: pkg install python-cryptography"}))
    sys.exit(2)

raw = open(a.evidence_file, "rb").read()
file_sha = hashlib.sha512(raw).hexdigest()
try:
    ev = json.loads(raw)
except json.JSONDecodeError:
    print(json.dumps({"verdict": "REJECTED", "reason": "JSON invalido"})); sys.exit(1)

checks = []
def chk(name, ok, detail=""):
    checks.append({"check": name, "ok": bool(ok), "detail": detail})

chk("json_parseable", True)
chk("has_weights_sha256", "weights_sha256" in json.dumps(ev))
chk("has_evidence_hash", "evidence_hash" in json.dumps(ev))
ver = ev.get("verification", {})
chk("cosine_present", "cosine" in ver, f"cosine={ver.get('cosine')}")
chk("status_pass", ver.get("status") == "PASS", ver.get("status", "?"))
chk("file_sha512_recorded", len(file_sha) == 128)

sk = Ed25519PrivateKey.generate() if not a.seed else Ed25519PrivateKey.from_private_bytes(bytes.fromhex(a.seed))
pk = sk.public_key().public_bytes_raw().hex()

verdict = "ATTESTED" if all(c["ok"] for c in checks) else "REJECTED"
body = json.dumps({"evidence_file": a.evidence_file,
                   "file_sha512": file_sha,
                   "checks": checks, "verdict": verdict,
                   "ts": datetime.now(timezone.utc).isoformat()},
                  sort_keys=True).encode()
out = json.loads(body)
out["attestor_ed25519"] = pk
out["signature"] = sk.sign(body).hex()

os.makedirs("evidence", exist_ok=True)
dst = f"evidence/attestation_{os.path.basename(a.evidence_file)}"
json.dump(out, open(dst, "w"), indent=2)
print(json.dumps(out, indent=2, ensure_ascii=False))
print(f"[attestation] -> {dst}")
print(f"[attestor_pubkey] {pk}  (conservar para verificacion futura)")


def verify_attestation(path):
    """Verificacion: cualquiera con el JSON y la clave publica lo comprueba."""
    d = json.load(open(path))
    body = {k: v for k, v in d.items() if k not in ("attestor_ed25519", "signature")}
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    pk = Ed25519PublicKey.from_public_bytes(bytes.fromhex(d["attestor_ed25519"]))
    return pk.verify(bytes.fromhex(d["signature"]),
                     json.dumps(body, sort_keys=True).encode()) is None
