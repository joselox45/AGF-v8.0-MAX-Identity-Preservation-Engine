# Protocolo de Attestation Independiente (APCE)

## Rol del tercero
Cualquier parte independiente puede atestar evidencia AGF sin confianza previa:

```bash
git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine
pkg install -y python-cryptography python-tflite-runtime python-numpy python-pillow

# 1. Reproducir la medición (opcional pero recomendado)
python tools/closure_t21_tflite.py <fotoA> <fotoB> <modelo.tflite> facenet raw

# 2. Atestar el archivo de evidencia (firma Ed25519 propia)
python tools/attest.py evidence/t21_tflite.json
# -> evidence/attestation_t21_tflite.json + tu clave pública (conservarla)
```

## Qué firma el tercero
- SHA-512 del archivo de evidencia completo
- Checks estructurales (cosine presente, status PASS, hashes presentes)
- Veredicto ATTESTED / REJECTED
- Firma Ed25519 con SU clave privada (jamás compartida)

## Verificación posterior (cualquiera)
`tools/attest.py` incluye `verify_attestation(path)`: con el JSON y la clave pública
del attestor, cualquiera comprueba que el archivo no fue alterado desde la attestation.

## T30: benchmark de robustez
```bash
python tools/bio_benchmark.py --spec pares.json --embedder facenet.tflite
# pares.json: [{"a": "f1.jpg", "b": "f2.jpg", "same": true}, ...]
# Métricas: TAR (mismo aceptado), FAR (distinto aceptado) @ umbral 0.65
```
Con detector BlazeFace (opcional): `--detector blaze.tflite` (MediaPipe face_detection_front, 128x128).
