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
