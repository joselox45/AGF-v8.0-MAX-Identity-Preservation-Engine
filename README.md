# AGF v12.2 - Identity Preservation Engine (INDUSTRIAL)
**Fail-Closed. Zero-Fabrication. Human-in-the-Loop.**

AGF es un motor de verificación de identidad de grado industrial diseñado para auditar imágenes generadas por IA (Meta AI, Grok, ChatGPT). No confía en lo que dice el LLM; verifica la geometría (ArcFace) y la textura (SSIM) en local.

## 🚀 Instalación Rápida (Clone & Run)
git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine
pip install numpy pillow onnxruntime tflite-runtime
./tools/fetch_models.sh

## 🕹️ Camino Canónico (Single-Command)
./agf.sh preservation foto_original.jpg foto_generada.jpg
./agf.sh restoration foto_vieja.jpg foto_restaurada.jpg

## 🧠 Modos y Umbrales
### 1. PRESERVATION (Identity-First)
*   PASS: Cosine >= 0.79 Y SSIM >= 0.90
*   HUMAN_REVIEW: Cosine >= 0.79 Y SSIM < 0.90
*   BLOCKED: Cosine < 0.65

### 2. RESTORATION (Historic)
*   PASS: Cosine >= 0.65 Y SSIM >= 0.85
*   HUMAN_REVIEW: Cosine >= 0.55
*   BLOCKED: Cosine < 0.55

## ⚠️ Reglas de Oro (Gobernanza)
1. Los LLMs mienten: Nunca confíes en un PASS que un chatbot se dé a sí mismo.
2. Verificación Local: Toda métrica debe ser calculada en Termux.
3. Human-in-the-Loop: Si el sistema dice HUMAN_REVIEW, tú tienes la última palabra.

## 🖥️ Interfaz Web (Manual Crop UI)
Para una experiencia visual rápida (Dashboard), AGF incluye una interfaz web ligera que funciona directamente en el navegador usando Canvas API:
1. Inicia el servidor local en Termux: `python -m http.server 8080`
2. Abre en Chrome: `http://localhost:8080/agf_ui.html`
3. Sube la foto original y la generada.
4. Usa el botón **"Auto-Alinear por Ojos"** para centrar el recorte geométricamente, o el botón **"Auto-Detectar Piel"** para ajustar el recorte a la textura de la piel.
5. Presiona **"Auditar Zona"** y descarga el JSON de evidencia.

*Nota: La interfaz web es un dashboard visual rápido. El veredicto forense definitivo (ONNX ArcFace + BlazeFace) se ejecuta siempre en Termux con `./agf.sh`.*
