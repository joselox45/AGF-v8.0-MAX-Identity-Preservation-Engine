# AGF v12.2 - Identity Preservation Engine (INDUSTRIAL)
**Fail-Closed. Zero-Fabrication. Human-in-the-Loop.**

AGF es un motor de verificacion de identidad de grado industrial disenado para auditar imagenes generadas por IA (Meta AI, Grok, ChatGPT). No confia en lo que dice el LLM; verifica la geometria (ArcFace) y la textura (Fourier/SSIM) en local.

## Instalacion Rapida (Clone & Run)
git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine
pip install numpy pillow onnxruntime tflite-runtime
./tools/fetch_models.sh

## Uso con Chatbots (LLMs) - Slash Triggers
Para evitar que los LLMs ignoren las reglas, debes usar los siguientes Triggers junto a tu imagen:
*   `/repara` -> Activa el MODO RESTORATION (Fotos antiguas, B/N, danadas). Aplica 6 pasos: Reparar, Reconstruir, Restaurar, Clarificar, Colorizar, Satinizar.
*   `/preserva` -> Activa el MODO PRESERVATION (Fotos modernas). LOCK: Rostro. ALLOW: Ropa/Fondo.

Si el LLM genera la imagen sin el Trigger, rechazala. El LLM debe devolver un JSON con `verification_status: PENDING_LOCAL_VERIFICATION`.

## Camino Canonico en Termux (El Juez Real)
El LLM solo genera. Termux audita con 4 capas forenses (ArcFace + Fourier + Shazam + SSIM).
./agf.sh preservation foto_original.jpg foto_generada.jpg
./agf.sh restoration foto_vieja.jpg foto_restaurada.jpg

## Interfaz Web (Manual Crop UI)
1. Inicia el servidor local: python -m http.server 8080
2. Abre en Chrome: http://localhost:8080/agf_ui.html
3. Sube las fotos, ajusta el recuadro y audita.

## Modos y Umbrales (Calibracion Humana)
### 1. PRESERVATION
* PASS: Score Ponderado >= 0.7825
* HUMAN_REVIEW: Score >= 0.6325
* BLOCKED: Score < 0.6325 o ArcFace < 0.6325

### 2. RESTORATION
* PASS: Score Ponderado >= 0.7825
* HUMAN_REVIEW: Score >= 0.6325
* BLOCKED: Score < 0.6325 o Fourier < 0.6825

## Reglas de Oro (Gobernanza)
1. Los LLMs mienten: Nunca confies en un PASS que un chatbot se de a si mismo.
2. Verificacion Local: Toda metrica debe ser calculada en Termux (ONNX/TFLite).
3. Human-in-the-Loop: Si el sistema dice HUMAN_REVIEW, tu tienes la ultima palabra.
