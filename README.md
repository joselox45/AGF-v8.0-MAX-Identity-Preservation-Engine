# AGF v12.2 - Identity Preservation Engine (INDUSTRIAL)
**Fail-Closed. Zero-Fabrication. Human-in-the-Loop.**

AGF es un motor de verificacion forense de grado industrial disenado para auditar imagenes generadas por IA (Meta AI, Grok, ChatGPT). No confia en lo que dice el LLM; verifica la identidad, la textura, la estructura y los metadatos en local.

## Instalacion Rapida (Clone & Run)
git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine
pip install numpy pillow onnxruntime tflite-runtime
./tools/fetch_models.sh

## Camino Canonico en Termux
El LLM solo genera. Termux audita con 6 capas forenses. El sistema sellara todo en termux_sealed/.
./agf.sh preservation foto_original.jpg foto_generada.jpg
./agf.sh restoration foto_vieja.jpg foto_restaurada.jpg

## Arquitectura Forense de 6 Capas
1. Capa 0 (Metadata): Detecta la firma XMP de IA (trainedAlgorithmicMedia).
2. Capa 1 (ArcFace): Compara la geometria facial 3D. (Hard Gate: < 0.6325 -> BLOCKED)
3. Capa 2 (Fourier 2D): Detecta texturas sinteticas y alucinaciones. (Hard Gate: < 0.6825 -> BLOCKED)
4. Capa 3 (Edge Shazam): Compara la constelacion de bordes faciales.
5. Capa 4 (SSIM): Evalua la similitud estructural de los pixeles.
6. Capa 5 (Color Fingerprint): Detecta cambios de paleta cromatica (HSV).
7. Capa 6 (Flatness): Detecta satinado o perdida de microtextura (Laplaciano).

## Interfaz Web (Dashboard Visual)
Para un analisis rapido con recorte manual y deteccion de piel:
1. Inicia el servidor: python -m http.server 8080
2. Abre en Chrome: http://localhost:8080/agf_ui.html
3. Sube las fotos, ajusta el recuadro verde y presiona Auditoria Forense.

## Uso con Chatbots (Kernel v0.8.2)
Para evitar que los LLMs ignoren las reglas, usa los Slash Triggers. El LLM debe devolver un JSON con los colores Hexadecimales de la imagen generada.
* /repara -> Activa MODO RESTORATION.
* /preserva -> Activa MODO PRESERVATION.

## Modos y Umbrales (Score Ponderado)
* PASS: Score >= 0.7825
* HUMAN_REVIEW: Score >= 0.6325
* BLOCKED: Score < 0.6325 o fallo en Hard Gate (ArcFace/Fourier).

## Reglas de Oro (Gobernanza)
1. Los LLMs mienten: Nunca confies en un PASS que un chatbot se de a si mismo.
2. Verificacion Local: Toda metrica debe ser calculada en Termux.
3. Human-in-the-Loop: Si el sistema dice HUMAN_REVIEW, tu decides.

*Repositorio Privado. Modelos biometricos en .gitignore. Documentacion completa en docs/governance/.*
