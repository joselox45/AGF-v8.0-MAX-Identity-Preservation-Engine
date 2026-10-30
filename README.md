# AGF v12.2 - Identity Preservation Engine (INDUSTRIAL)
**Fail-Closed. Zero-Fabrication. Human-in-the-Loop.**

AGF es un motor de verificacion forense de grado industrial disenado para auditar imagenes generadas por IA (Meta AI, Grok, ChatGPT).

## La Diferencia Tecnica: Semantica vs. Pixeles
- **El Chatbot (LLM):** Es un generador ciego. 'Ve' tokens latentes, no pixeles. Genera imagenes basandose en probabilidad semantica. No puede calcular metricas matematicas. Su unico trabajo es aplicar el Trigger /repara o /preserva.
- **El Humano (Termux):** Es el juez forense. Descomprime el archivo, lee la matriz real de pixeles y aplica 7 capas de matematicas (ONNX, Fourier, Laplaciano) para verificar la verdad historica.

## Instalacion Rapida
git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine
pip install numpy pillow onnxruntime tflite-runtime
./tools/fetch_models.sh

## Camino Canonico en Termux
./agf.sh preservation foto_original.jpg foto_generada.jpg
./agf.sh restoration foto_vieja.jpg foto_restaurada.jpg

## Arquitectura Forense de 7 Capas
1. Metadata (XMP): Detecta firmas de IA.
2. ArcFace: Geometria facial 3D. (Hard Gate < 0.6325)
3. Fourier 2D: Alucinaciones de textura. (Hard Gate < 0.6825)
4. Edge Shazam: Constelacion de bordes.
5. SSIM: Similitud de pixeles.
6. Color Fingerprint: Huella cromatica (HSV).
7. Flatness: Microtextura (Laplaciano).
8. Overlay Diff: Mapa de calor visual de alteraciones.

## Interfaz Web (Dashboard Visual)
python -m http.server 8080
Abrir en Chrome: http://localhost:8080/agf_ui.html

## Gobernanza
1. Los LLMs mienten (alucinan metricas).
2. Verificacion Local obligatoria.
3. Human-in-the-Loop para casos dudosos.

*Repositorio Privado. Modelos biometricos en .gitignore.*
