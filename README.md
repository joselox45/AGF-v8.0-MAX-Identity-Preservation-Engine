# AGF v12.2 - Identity Preservation Engine (INDUSTRIAL)
**Fail-Closed. Zero-Fabrication. Human-in-the-Loop.**

AGF es un motor de verificacion forense disenado para auditar imagenes generadas por IA. Verifica Identidad (ArcFace), Frecuencia (Fourier), Estructura (Shazam), Pixeles (SSIM), Color (HSV) y Metadatos (XMP).

## Instalacion Rapida
git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine
pip install numpy pillow onnxruntime tflite-runtime
./tools/fetch_models.sh

## Uso con Chatbots (Kernel v0.8.2)
Debes usar los Triggers. El LLM te devolvera un JSON con los colores Hexadecimales de la imagen generada.
*   `/repara` -> MODO RESTORATION.
*   `/preserva` -> MODO PRESERVATION.

## Motor Canonico en Termux
Auditoria forense de 5 capas + metadatos.
1. Triaje de metadatos: `python tools/agf_metadata_forensic.py foto.jpg`
2. Auditoria completa: `./agf.sh restoration foto_original.jpg foto_generada.jpg`

## Interfaz Web
python -m http.server 8080
Abrir en Chrome: http://localhost:8080/agf_ui.html

## Reglas de Oro (Gobernanza)
1. Los LLMs mienten: Verifica siempre en Termux.
2. Zero-Fabrication: Si ArcFace < 0.6325 o Fourier < 0.6825 -> BLOCKED.
3. Human-in-the-Loop: Si el sistema dice HUMAN_REVIEW, tu decides.
