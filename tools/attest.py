#!/usr/bin/env python3
"""
AGF — Attestation independiente (APCE).
Un tercero verifica un archivo de evidencia y lo firma con SU clave Ed25519.
Uso:
  python tools/attest.py evidence/t22.json [--seed HEX64] [--signer HANDLE]
Emite evidence/attestation_<archivo>.json con veredicto ATTESTED/REJECTED.
Requiere: pkg install python-cryptography
F-03 (auditoria 13): weights_sha256 verificado contra tabla de hashes fijados.
"""
import argparse, hashlib, json, os, sys
from datetime import datetime, timezone

ap = argparse.ArgumentParser()
ap.add_argument("evidence_file")
ap.add_argument("--seed", default=None, help="64 hex chars; si omite, genera")
ap.add_argument("--signer", default="anon",
                help="identidad del attestor (handle/nombre)")
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
wjson = json.dumps(ev)
chk("has_weights_sha256", "weights_sha256" in wjson)
PINNED = {
    "54660297ebad23b7106a8ccd05f2f2f616b3d39bf7d7e82e148cf8ed7e27ae1a": "facenet.tflite",
    "700ea787ab479a13ddf9c8225215569f88065748aa2b8f2b384735c5e6521bef": "arcface_digidow.tflite",
}
import re as _re
m = _re.search(r'"weights_sha256"\s*:\s*"([0-9a-f]{64})"', wjson)
if m:
    checks.append({"check": "weights_hash_pinned", "ok": m.group(1) in PINNED,
                   "detail": PINNED.get(m.group(1), "hash NO fijado")})
else:
    checks.append({"check": "weights_hash_pinned", "ok": False,
                   "detail": "weights_sha256 no parseable"})
wjson0 = json.dumps(ev)
chk("has_evidence_hash", ("evidence_hash" in wjson0) or ("L2_biometric" in wjson0))
ver = ev.get("verification") or {}
if "cosine" not in ver and isinstance(ev.get("verdict"), dict):
    vd = ev["verdict"]
    ver = {"cosine": vd.get("cosine"),
           "status": "PASS" if vd.get("L2_biometric") == "PASS" else "FAIL"}
chk("cosine_present", "cosine" in ver, f"cosine={ver.get('cosine')}")
chk("status_pass", ver.get("status") == "PASS", ver.get("status", "?"))
chk("file_sha512_recorded", len(file_sha) == 128)

sk = Ed25519PrivateKey.generate() if not a.seed else Ed25519PrivateKey.from_private_bytes(bytes.fromhex(a.seed))
pk = sk.public_key().public_bytes_raw().hex()

verdict = "ATTESTED" if all(c["ok"] for c in checks) else "REJECTED"
body = json.dumps({"evidence_file": a.evidence_file,
                   "file_sha512": file_sha,
                   "signer": a.signer,
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
