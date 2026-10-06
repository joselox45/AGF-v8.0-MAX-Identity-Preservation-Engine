# Mapeo AGF v9.0 (T21–T28) → APCE v8.1.0 — con evidencia parcial

Autoridad: APCE v8.1.0 CANONICAL. AGF = evaluation plane, jamás promueve por sí mismo.
Formato: 14 campos del contrato AGF-APCE-PRODUCTION-PACK §2. Gaps marcados explícitos (fail-closed).

| AGF-ID | RELATIONSHIP | GAP | STATUS |
|---|---|---|---|
| T21 | PARTIAL-COMPATIBLE | EVIDENCE_GAP: pesos ArcFace no operados en produccion | IMPLEMENTED-NOT-OPERATING |
| T22 | PARTIAL-COMPATIBLE | EVIDENCE_GAP: pesos FaceNet no operados en produccion | IMPLEMENTED-NOT-OPERATING |
| T23 | DIRECT-COMPATIBLE | none | TESTED |
| T24 | DIRECT-COMPATIBLE | none | TESTED |
| T25 | DIRECT-COMPATIBLE | none | TESTED |
| T26 | PARTIAL-COMPATIBLE | EVIDENCE_GAP: Ed25519 no operado en Termux (sin cryptography | IMPLEMENTED-NOT-OPERATING |
| T27 | PARTIAL-COMPATIBLE | EVIDENCE_GAP: anclaje did:web/SVID a produccion no operado;  | IMPLEMENTED-NOT-OPERATING |
| T28 | DIRECT-COMPATIBLE | none | TESTED |

## Resumen de aseguramiento

- DIRECT-COMPATIBLE con evidencia: T23, T24, T25, T28 (4)
- PARTIAL-COMPATIBLE con EVIDENCE_GAP declarado: T21, T22, T26, T27 (4)
- Ningún control en OPERATING_EFFECTIVE; máximo alcanzado: TESTED (interno).
- Cierran los gaps: pesos ONNX biométricos en Termux (T21/T22), Ed25519 en Termux (T26),
  anclaje did:web/SVID a producción (T27), y evidencia operacional independiente (todo).