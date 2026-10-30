# AGF v12.2 - Identity Preservation Engine (INDUSTRIAL)
**Fail-Closed. Zero-Fabrication. Human-in-the-Loop.**

AGF es un motor de verificacion forense de grado industrial disenado para auditar imagenes generadas por IA (Meta AI, Grok, ChatGPT).

## La Diferencia Tecnica: Semantica vs. Pixeles
- **El Chatbot (LLM):** Es un generador ciego. "Ve" tokens latentes, no pixeles. No puede calcular metricas matematicas. Su unico trabajo es aplicar el Trigger `/repara` o `/preserva`.
- **El Humano (Termux):** Es el juez forense. Descomprime el archivo, lee la matriz real de pixeles y aplica las metricas para verificar la verdad historica.

## Instalacion Rapida
git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine
pip install numpy pillow onnxruntime tflite-runtime
./tools/fetch_models.sh

## Camino Canonico en Termux
./agf.sh preservation foto_original.jpg foto_generada.jpg
./agf.sh restoration foto_vieja.jpg foto_restaurada.jpg

## Arquitectura Forense Real (5 Metricas + 2 Diagnosticos)
El motor principal calcula la Ponderacion Soberana sobre 5 capas matematicas:
1. **ArcFace (40%):** Identidad 3D. (Veto Extremo: < 0.30).
2. **Fourier (30%):** Frecuencia. (Veto Extremo: < 0.40).
3. **Shazam (20%):** Bordes.
4. **SSIM (10%):** Pixeles.
5. **Color (5%):** Huella cromatica.

Ademas, cuenta con 2 capas de diagnostico complementario:
- **Metadata (XMP):** Advierte si la imagen tiene firma de IA (no bloquea).
- **Overlay Diff:** Genera un mapa de calor visual para el humano (no suma al score).

## Interfaz Web (Dashboard Visual)
python -m http.server 8080
Abrir en Chrome: http://localhost:8080/agf_ui.html

## Gobernanza
1. Los LLMs mienten (alucinan metricas).
2. Verificacion Local obligatoria.
3. Human-in-the-Loop para casos dudosos.

*Repositorio Privado. Modelos biometricos en .gitignore. Esquemas fisicos en schemas/.*
