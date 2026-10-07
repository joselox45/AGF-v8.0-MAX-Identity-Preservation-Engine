# Mapeo AGF v9.0 (T21–T28) → APCE v8.1.0 — v4 (post-cierre biométrico riguroso)

Corrida 2026-10-06 con parche de normalización aplicado (modos arcface/raw/div255):

- **T22 FaceNet → TESTED**: cosine 0.967478, `evidence_hash` idéntico en dos
  corridas independientes → **determinismo verificado** (custodia fuerte).
- **T21 ArcFace → gap caracterizado con datos**: FAIL 0.4257 con preproceso
  spec-correcto (div255) sobre imagen completa. ArcFace exige alineación facial.
  El PASS previo (0.7730) correspondía a normalización no especificada —
  el fail-closed impidió registrarlo como cierre. Ruta: T30 (BlazeFace) + re-cierre.

| AGF-ID | RELATIONSHIP | GAP | STATUS |
|---|---|---|---|
| T21 | PARTIAL-COMPATIBLE | alineación facial pendiente (T30) | IMPLEMENTED-NOT-OPERATING |
| T22 | DIRECT-COMPATIBLE | none (determinismo verificado) | TESTED |
| T23–T26 | DIRECT-COMPATIBLE | none | TESTED |
| T27 | DIRECT-COMPATIBLE | residual: anclaje producción | TESTED |
| T28 | DIRECT-COMPATIBLE | none | TESTED |

Score: 7/8 TESTED; T21 con gap medido y ruta de cierre precisa.
Lección de aseguramiento: un FAIL honesto con datos > un PASS dudoso.
