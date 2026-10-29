# AGF v12.2 - Identity Preservation Engine (INDUSTRIAL)
**Fail-Closed. Zero-Fabrication. Human-in-the-Loop.**

AGF es un motor de verificacion de identidad de grado industrial disenado para auditar imagenes generadas por IA. No confia en lo que dice el LLM; verifica la geometria (ArcFace) y la textura (SSIM) en local.

## Instalacion Rapida (Clone & Run)
git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine
pip install numpy pillow onnxruntime tflite-runtime
./tools/fetch_models.sh

## Camino Canonico (Single-Command)
El sistema sellara, auditara y archivara todo el linaje en 'termux_sealed/'.
./agf.sh preservation foto_original.jpg foto_generada.jpg
./agf.sh restoration foto_vieja.jpg foto_restaurada.jpg

## Interfaz Web (Manual Crop UI)
1. Inicia el servidor local: python -m http.server 8080
2. Abre en Chrome: http://localhost:8080/agf_ui.html
3. Sube las fotos. Usa 'Auto-Alinear por Ojos' y 'Auto-Detectar Piel'.

## Modos y Umbrales (Calibracion Humana)
### 1. PRESERVATION (Identity-First)
* PASS: Cosine >= 0.79 Y SSIM >= 0.90
* HUMAN_REVIEW: Cosine >= 0.79 Y SSIM < 0.90
* BLOCKED: Cosine < 0.65

### 2. RESTORATION (Historic)
* PASS: Cosine >= 0.65 Y SSIM >= 0.60 (Tolerancia humana)
* HUMAN_REVIEW: Cosine >= 0.55
* BLOCKED: Cosine < 0.55

## Reglas de Oro (Gobernanza)
1. Los LLMs mienten: Nunca confies en un PASS que un chatbot se de a si mismo.
2. Verificacion Local: Toda metrica debe ser calculada en Termux (ONNX/TFLite).
3. Human-in-the-Loop: Si el sistema dice HUMAN_REVIEW, tu tienes la ultima palabra.
