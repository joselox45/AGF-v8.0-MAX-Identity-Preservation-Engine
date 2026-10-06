# Mapeo AGF v9.0 (T21–T28) → APCE v8.1.0 — v3 (post-cierre biométrico real)

Cierre 2026-10-06 en Termux real (`evidence/t21_tflite.json`):
- **T22 → TESTED**: FaceNet TFLite real, dos fotos del mismo rostro,
  cosine **0.9675** (umbral 0.65), weights_sha256 verificado contra el
  hash publicado (custodia completa).
- **T26/T27 → TESTED**: Ed25519 + did:key reales (corrida previa).
- **T21**: gap residual minimo — pipeline TFLite probado end-to-end;
  falta solo el archivo de pesos ArcFace (.tflite).

| AGF-ID | RELATIONSHIP | GAP | STATUS |
|---|---|---|---|
| T21 | PARTIAL-COMPATIBLE | residual: pesos ArcFace .tflite | IMPLEMENTED-NOT-OPERATING |
| T22 | DIRECT-COMPATIBLE | none | **TESTED** |
| T23 | DIRECT-COMPATIBLE | none | TESTED |
| T24 | DIRECT-COMPATIBLE | none | TESTED |
| T25 | DIRECT-COMPATIBLE | none | TESTED |
| T26 | DIRECT-COMPATIBLE | none | TESTED |
| T27 | DIRECT-COMPATIBLE | residual: anclaje produccion | TESTED |
| T28 | DIRECT-COMPATIBLE | none | TESTED |

Score: **7/8 TESTED**, uno con gap residual documentado y ruta de cierre conocida.
