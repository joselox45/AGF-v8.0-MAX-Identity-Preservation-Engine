# Evaluación Externa del Repositorio AGF

**Fecha:** 2026-10-31
**Fuente:** Auditoría cruzada (CPEP vFinal + revisión de código).

## 1. Veredicto Cuantitativo
- **Concepto:** 8/10 (Arquitectura de gobernanza y fail-closed sólida).
- **Ejecución:** 4/10 (Lógica funcional, pero faltan benchmarks estandarizados).
- **Capital Semilla (As-Is):** 2.5/10 (No invertible sin infraestructura VPS/Docker).

## 2. Hallazgos Críticos (Zero-Fabrication)
- **Thresholds heurísticos:** El `agf_composite_scorer.py` usa umbrales empíricos (0.7825 PASS / 0.6325 REVIEW) basados en ~30 imágenes. Carece de curva ROC ni benchmark LFW.
- **Web UI SIL:** `agf_ui.html` simula métricas en el navegador. Es condicionamiento débil (weak_semantic).
- **Valor Real:** El core del repo es `agf.sh` + `arcface.onnx` (167MB). El resto es capa de gobernanza.

## 3. Propuesta de Licencia (Open-Core)
- **AGF-Governance (Público, MIT):** La capa de reglas, esquemas y validadores (este repo).
- **AGF-Kernel-HIL (Privado, BSL 1.1):** El motor de inferencia real en Termux/VPS con super-resolución.

## 4. Salto Disruptivo: No confiar en el generador
No pedirle honestidad al generador. Solo pedirle la imagen. Los bboxes se calculan siempre fuera (Termux/VPS) y se comparan con el claimed.

---
FIN DEL DOCUMENTO
