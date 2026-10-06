# Mapeo AGF v9.0 (T21–T28) → APCE v8.1.0 — v2 (post-cierre Termux)

Cierre ejecutado 2026-10-06 en Termux real (`evidence/closure_t21_t26.json`):
- **T26 → TESTED**: firma Ed25519 RFC 8032 real, verificación determinista.
- **T27 → TESTED**: SPIFFE ID + did:key Ed25519 generados y verificados
  (`spiffe://akadi.local/agent-1635`, `did:key:z6Mkgd5Pw2UcVxPv…`).
- **T21/T22**: EVIDENCE_GAP acotado — numpy presente; onnxruntime sin wheel
  aarch64-Android. Fail-closed; cero PASS fabricado.

| AGF-ID | RELATIONSHIP | GAP | STATUS |
|---|---|---|---|
| T21 | PARTIAL-COMPATIBLE | EVIDENCE_GAP acotado (onnxruntime aarch64) | IMPLEMENTED-NOT-OPERATING |
| T22 | PARTIAL-COMPATIBLE | EVIDENCE_GAP acotado | IMPLEMENTED-NOT-OPERATING |
| T23 | DIRECT-COMPATIBLE | none | TESTED |
| T24 | DIRECT-COMPATIBLE | none | TESTED |
| T25 | DIRECT-COMPATIBLE | none | TESTED |
| T26 | DIRECT-COMPATIBLE | none | TESTED |
| T27 | DIRECT-COMPATIBLE | residual: anclaje producción | TESTED |
| T28 | DIRECT-COMPATIBLE | none | TESTED |

Score: 6/8 TESTED con evidencia en Termux. Restante: runtime ONNX biométrico
(ruta: wheel onnxruntime aarch64, o conversión del modelo a TFLite/NCNN).
