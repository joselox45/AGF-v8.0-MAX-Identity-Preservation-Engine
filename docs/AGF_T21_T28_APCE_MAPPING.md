# Mapeo AGF v9.0 (T21–T28) → APCE v8.1.0 — v6: 8/8 TESTED (expediente cerrado)

Cierre 2026-10-14:
- **T21 ArcFace → TESTED**: root cause (box coder SSD sin scales) corregido en
  commit 50e52b5. Re-cierre con alineacion BlazeFace: cosine **0.890083** PASS,
  evidence_hash 863576b0… (distinguido del hash del fallo previo cf1ba64c…).
  Diagnostico completo preservado en el historial: 0.4257 (sin alinear),
  1.0-colapso (recortes negros detectados por anti-replay).
- **T22 FaceNet → TESTED** (determinismo byte-a-byte verificado).
- 64/64 tests. fetch_weights.py PASS. CI doctor.yml activo (run 38606347003).
- Licencia MIT detectada por GitHub (API key:mit).

| AGF-ID | RELATIONSHIP | GAP | STATUS |
|---|---|---|---|
| T21 | DIRECT-COMPATIBLE | none | **TESTED** |
| T22 | DIRECT-COMPATIBLE | none | TESTED |
| T23–T26 | DIRECT-COMPATIBLE | none | TESTED |
| T27 | DIRECT-COMPATIBLE | residual: anclaje produccion | TESTED |
| T28 | DIRECT-COMPATIBLE | none | TESTED |

Score: **8/8 TESTED con evidencia real en Termux.**
Sin declaraciones OPERATING_EFFECTIVE (requiere attestation independiente).
Comparativa SOTA y matriz adversarial: protocolos publicados, ejecucion roadmap.
