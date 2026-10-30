# 📂 CASO DE ESTUDIO 11: SIL (Chatbot) vs HIL (Termux)

**Fecha:** 2026-10-30
**Hito:** Validación de que el SIL_SCORE (Chatbot) no reemplaza al HIL_SCORE (Termux).

## 1. Declaración del Chatbot (Fase MIL/SIL)
El chatbot, aplicando el Kernel v0.9.4, declaró:
- `phase`: "MIL"
- `metrics_missing`: ["arcface"]
- `sil_score.weighted`: 0.895
- `verdict`: "HUMAN_REVIEW" (porque no puede verificar ArcFace)

## 2. Verificación en Termux (Fase HIL)
El motor real, con ArcFace (167MB), dictó:
- Identidad (ArcFace): 0.8229
- Firma (Fourier): 0.9909
- Píxeles (SSIM): 0.9779
- **AGF Score Ponderado: 0.8045**
- **Veredicto: PASS**

## 3. Conclusión de Gobernanza
El chatbot tenía razón en su límite (no podía verificar ArcFace) y Termux tenía la verdad geométrica. El SIL_SCORE (0.895) y el HIL_SCORE (0.8045) son diferentes porque el chatbot simuló el SSIM/Fourier sin los modelos reales. **Solo el HIL es válido para certificar identidad.**
