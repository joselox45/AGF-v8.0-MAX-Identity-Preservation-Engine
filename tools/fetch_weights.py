#!/usr/bin/env python3
"""
AGF — fetch_weights.py (P1-Control, auditoria O0 2026-10-14).
Descarga los pesos PUBLICOS con verificacion SHA-256 fijada.
Sin pesos: el sistema opera en modo BLOCKED (fail-closed), nunca fabrica.

Uso:  python tools/fetch_weights.py [dest_dir]
"""
import hashlib
import json
import os
import sys
import urllib.request

WEIGHTS = {
    "facenet.tflite": {
        "url": "https://huggingface.co/spaces/projectimx/Face_embedding/"
               "resolve/f312d17db179df1b031bbf4a849b90657805e4f7/facenet.tflite",
        "sha256": "54660297ebad23b7106a8ccd05f2f2f616b3d39bf7d7e82e148cf8ed7e27ae1a",
        "licencia": "ver LICENSE-WEIGHTS.md (deepface-derived)",
    },
    "arcface_digidow.tflite": {
        "url": "https://www.digidow.eu/f/datasets/arcface-tensorflowlite/model.tflite",
        "sha256": "700ea787ab479a13ddf9c8225215569f88065748aa2b8f2b384735c5e6521bef",
        "licencia": "EUPL-1.2",
    },
    "blaze_face_short_range.tflite": {
        "url": "https://storage.googleapis.com/mediapipe-models/face_detector/"
               "blaze_face_short_range/float16/1/blaze_face_short_range.tflite",
        "sha256": "b4578f35940bf5a1a655214a1cce5cab13eba73c1297cd78e1a04c2380b0152f",
        "licencia": "Apache-2.0 (MediaPipe)",
    },
}


def fetch(name, spec, dest):
    path = os.path.join(dest, name)
    if os.path.exists(path):
        digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if digest == spec["sha256"]:
            print(f"[OK] {name}: ya presente y hash verificado")
            return True
        print(f"[WARN] {name}: hash local NO coincide; re-descargando")
    print(f"[..] {name}: descargando ({spec['licencia']})")
    urllib.request.urlretrieve(spec["url"], path)
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    if digest != spec["sha256"]:
        print(f"[FAIL] {name}: hash mismatch ({digest[:16]}... != {spec['sha256'][:16]}...)")
        return False
    print(f"[OK] {name}: sha256 verificado")
    return True


if __name__ == "__main__":
    dest = sys.argv[1] if len(sys.argv) > 1 else "."
    ok = all(fetch(n, s, dest) for n, s in WEIGHTS.items())
    print(json.dumps({"status": "PASS" if ok else "FAIL",
                      "nota": "sin pesos el sistema sigue en BLOCKED (fail-closed)"},
                     ensure_ascii=False))
    sys.exit(0 if ok else 1)
