# 📂 CASO DE ESTUDIO 06: Full-Stack Web-API (Real-Time Inference)

**Fecha:** 2026-10-30
**Hito:** Eliminación de la simulación web y conexión con el motor ONNX real.

## 1. Arquitectura Implementada
- **Frontend:** `agf_ui.html` recorta las imágenes y las envía vía `fetch()` (POST).
- **Backend:** `api_server.py` (Flask) recibe las imágenes, ejecuta el motor forense y devuelve el JSON.
- **Engine:** `agf_composite_scorer.py` calcula ArcFace, Fourier, Shazam, SSIM y Color.

## 2. Resultados de la Prueba (Boda)
```json
{
  "agf_score": 0.8505,
  "metrics": {
    "cosine": 0.7756,
    "fourier": 0.9927,
    "shazam": 0.6638,
    "ssim": 0.9678,
    "color": 0.3917
  },
  "verdict": "PASS"
}
