# AGF v12.2 - Identity Preservation Engine (INDUSTRIAL)
**Fail-Closed. Zero-Fabrication. Human-in-the-Loop.**

AGF es un motor de verificacion forense de grado industrial disenado para auditar imagenes generadas por IA (Meta AI, Grok, ChatGPT).

## La Diferencia Tecnica: Semantica vs. Pixeles
- **El Chatbot (LLM):** Es un generador ciego. "Ve" tokens latentes, no pixeles. No puede calcular metricas matematicas. Su unico trabajo es aplicar el Trigger `/repara` o `/preserva` y declarar que no tiene hardware fisico.
- **El Humano (Termux):** Es el juez forense. Descomprime el archivo, lee la matriz real de pixeles y aplica 7 capas de matematicas para verificar la verdad historica.

## Instalacion Rapida
git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine
pip install numpy pillow onnxruntime tflite-runtime
./tools/fetch_models.sh

## Camino Canonico en Termux
./agf.sh preservation foto_original.jpg foto_generada.jpg
./agf.sh restoration foto_vieja.jpg foto_restaurada.jpg

## Arquitectura Forense (Jerarquia Soberana)
1. **Metadata (XMP):** Advertencia de origen sintetico (NO bloquea).
2. **ArcFace (Identidad):** Geometria facial 3D. (Veto Extremo: < 0.30).
3. **Fourier 2D (Frecuencia):** Alucinaciones de textura. (Veto Extremo: < 0.40).
4. **Shazam (Estructura):** Constelacion de bordes.
5. **SSIM (Pixeles):** Similitud estructural.
6. **Color Fingerprint (Cromatica):** Huella de matiz (HSV).
7. **Overlay Diff (Visual):** Mapa de calor de alteraciones.

**Ponderacion Soberana:** ArcFace 40%, Fourier 30%, Shazam 20%, SSIM 10%, Color 5%. 
*El Score final decide el PASS (>0.60 en Restoration) o BLOCKED.*

## Interfaz Web (Dashboard Visual)
python -m http.server 8080
Abrir en Chrome: http://localhost:8080/agf_ui.html

## Gobernanza
1. Los LLMs mienten (alucinan metricas).
2. Verificacion Local obligatoria.
3. Human-in-the-Loop para casos dudosos.

*Repositorio Privado. Modelos biometricos en .gitignore. Esquemas fisicos en schemas/.*
