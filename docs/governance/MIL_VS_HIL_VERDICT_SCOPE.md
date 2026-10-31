# MIL vs HIL — Alcance del veredicto PASS

## Objetivo

Clarificar en que fases del AGF el veredicto `PASS` es valido y en
cuales esta prohibido. Evita confundir la restriccion del kernel v0.9.5
(MIL) con el scorer HIL.

## Fases y validez de PASS

| Fase | Donde corre | PASS permitido | Razon |
|---|---|---|---|
| MIL | Ventana de chat (LLM) | NO | Kernel v0.9.5 seccion 6 |
| SIL | Simulacion software | NO | Misma regla que MIL (fail-closed) |
| PIL | API local + ONNX (sin hardware humano) | Requiere HIL final | Metricas reales pero sin humano verificando |
| HIL | Termux + arcface.onnx + humano | SI | Unica fase donde la verdad puede certificarse |

## Kernel v0.9.5 — Aplicabilidad

El kernel v0.9.5 (PASS prohibido, enum `{HUMAN_REVIEW, PENDING_LOCAL_VERIFICATION, BLOCKED}`) aplica **solo a MIL** (chatbot). Es una regla para forzar al LLM a no fabricar veredictos sin hardware.

El scorer `tools/agf_composite_scorer.py` corre en **HIL** (Termux + `arcface.onnx` real + `blaze_face_short_range.tflite`). Puede emitir `PASS` legitimamente cuando:

- ArcFace cosine >= umbral del modo (preservation 0.65, restoration 0.55)
- Fourier >= 0.40 (no alucinacion total)
- AGF score >= umbral del modo (preservation 0.7825, restoration 0.60)

En cualquier caso, el humano sigue siendo el juez final (kernel seccion 5).

## Cambio relacionado (2026-10-31)

Fix de integridad de exit codes en `tools/agf_full_9_layers.py`:

- Antes: el orquestador siempre salia con exit 0, ignorando el verdict real del scorer
- Ahora: lee `termux_sealed/composite_audit.json` y devuelve exit 2 si BLOCKED, exit 0 si PASS

Esto NO cambia la semantica del PASS en HIL. Solo garantiza que el exit code refleje el veredicto real (para CI/scripts que dependen de el).

## Referencias

- Kernel v0.9.5 seccion 1: MIL vs HIL cognitive warning
- Kernel v0.9.5 seccion 5: HIL es el unico juez
- Kernel v0.9.5 seccion 6: Regla de oro del SIL_SCORE
- `tools/agf_composite_scorer.py`: logica de veredicto HIL
- `tools/agf_full_9_layers.py`: orquestador (fix 2026-10-31)
- `IDENTITY_LOCK_v1.5.md` Anexo C: weak_semantic vs strong_pixel vs HIL
