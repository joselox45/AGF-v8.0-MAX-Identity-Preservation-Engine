cd ~/AGF-v8.0-MAX-Identity-Preservation-Engine
cat << 'EOF' > README.md
# AGF — Identity Preservation Engine (v8.0-MAX / v9.0-LIMBAL)

**Motor de preservación de identidad con ejecución estricta, decisión adaptativa y gobernanza Fail-Closed.**

> **AVISO DE OPERADOR (FAIL-CLOSED):** Este repositorio es un marco de verificación determinista. Los LLMs (ChatGPT, Gemini, Grok, Meta AI) no pueden ejecutar FaceNet ni validar sus propias salidas; pueden alucinar métricas. La única fuente de verdad es la ejecución local del motor (Termux/PC) y la evidencia criptográfica (SHA-256) generada por el operador.

## Estado Actual (Octubre 2026)
*   **Motor Canónico v3:** BlazeFace 2-layer + FaceNet 160px + alineación + median-of-3.
*   **Umbral Estricto:** `0.79` (Youden, provisional) — *Corregido del antiguo 0.65 en la auditoría H-01.*
*   **Evolución v9.0-LIMBAL:** Transición de procesamiento secuencial a un **Motor de Decisión Adaptativo** (Filtros condicionales y Regla de Aborto).
*   **Tests:** 114/114 pasando en el pipeline canónico.

## Arquitectura y Capas
El sistema opera en 5 capas de verificación para garantizar la integridad:

1.  **Deep Learning (FaceNet TFLite):** Verificación biométrica real (Cosine Similarity).
2.  **Classical CV (OpenCV/Haar Cascade):** Detección y alineación facial clásica (`tools/forensic_analyzer.py`).
3.  **Math Vectors (SciPy/NumPy):** Análisis matemático de píxeles (Distancia Euclidiana y Cosine de imagen completa).
4.  **Anillo Limbal (v9.0):** Motor de decisión que evalúa Pérdida, Incentivo y Evidencia antes de aplicar cualquier filtro (`src/agf_v9_limbal.py`).
5.  **Restauración Clásica:** Filtros matemáticos sin IA generativa (`tools/classic_restorer.py`).

## Uso Rápido (30 segundos en Termux)

```bash
git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine
python agf.py doctor    # Autodiagnóstico (9/9 OPERATIVO)
python agf.py go        # Genera el Prompt Kernel firmado
