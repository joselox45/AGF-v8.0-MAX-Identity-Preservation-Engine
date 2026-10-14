# Protocolo de verificacion en capas (objetivo 2026-10-14)

Integra las pruebas existentes en UN punto reproducible y separa
estrictamente los niveles de afirmacion:

```
L1 FORMAL     PASS/FAIL/BLOCKED   (hashes, cobertura, evidencia presente)
L2 BIOMETRIC  PASS/FAIL/BLOCKED   (cosine >= umbral, anti-replay limpio)
L3 IDENTITY   SUPPORTED / NOT_DETERMINED / REFUTED   <- afirmacion SEMANTICA
```

## Regla central
Un PASS en L1 o L2 NUNCA implica L3 SUPPORTED. La "identidad preservada"
no es deducible de un cosine: exige L1 + L2 + procedencia declarada +
discriminacion cruzada (par distinto-sujeto que rechaza). Default: NOT_DETERMINED.
Un L2 FAIL implica L3 REFUTED.

## Como correr (reproducible)
python tools/verify_image.py ref.jpg candidato.jpg facenet.tflite facenet raw \
    blaze_face_short_range.tflite --provenance-declared --cross-tested

--provenance-declared : el candidato trae reporte [AGF_VERIFICATION_REPORT]
--cross-tested        : existe evidencia de rechazo de distinto sujeto (FAR)

Sin esas dos banderas, el veredicto L3 es NOT_DETERMINED aunque el cosine sea 0.99.
