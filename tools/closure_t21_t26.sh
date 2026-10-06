#!/bin/sh
# AGF Closure — T21/T26/T27 en Termux
set -e
cd ~/AGF-v8.0-MAX-Identity-Preservation-Engine

echo "== [1/3] dependencias =="
pkg install -y python-cryptography python-numpy || true
pip install onnxruntime 2>/dev/null || echo "onnxruntime sin wheel aarch64 (esperado; T21 sigue BLOCKED)"

echo "== [2/3] corrida de cierre =="
python tools/closure_t21_t26.py

echo "== [3/3] commit de evidencia =="
git add evidence/closure_t21_t26.json
git commit -m "evidence: closure T21/T26/T27 (Ed25519+did:key reales en Termux)"
git push origin main
echo "Listo. Pega la salida de [2/3] para actualizar el mapping."
