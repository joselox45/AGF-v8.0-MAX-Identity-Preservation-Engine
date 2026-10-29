# AGF v12.2 - Identity Preservation Engine (INDUSTRIAL)
**Fail-Closed. Zero-Fabrication. Human-in-the-Loop.**

AGF es un motor de verificación de identidad de grado industrial diseñado para auditar imágenes generadas por IA (Meta AI, Grok, ChatGPT). No confía en lo que dice el LLM; verifica la geometría y la textura en local.

## 🚀 Arquitectura
El sistema usa un enfoque de dos capas:
1. Geometría (ArcFace ONNX): Mide la similitud de coseno de la identidad real. Inmune a cambios de ropa o fondo.
2. Textura (SSIM + BlazeFace): Detecta el rostro automáticamente, aplica transformación afín (rotación + escala) y calcula la integridad de la piel, ignorando el fondo.

## 🛠️ Instalación en Termux (Python 3.14)
pip install numpy pillow onnxruntime tflite-runtime
# Descargar modelos (no incluidos en el repo por peso)
curl -L -o blaze_face_short_range.tflite https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite
# Asegúrate de tener arcface.onnx (167MB) en la raíz.

## 🧠 Modos de Operación
### 1. PRESERVATION (Fotos Modernas)
Para cambios de ropa/fondo sin alterar la identidad.
* PASS: Cosine >= 0.79 Y SSIM >= 0.90
* HUMAN_REVIEW: Cosine >= 0.79 Y SSIM < 0.90 (La IA alteró la piel)
* BLOCKED: Cosine < 0.65

### 2. RESTORATION (Fotos Antiguas)
Para reparar moho, rayaduras, B/N y colorizar. El umbral de identidad es más flexible porque la imagen base está dañada.
* PASS: Cosine >= 0.65 Y SSIM >= 0.85
* HUMAN_REVIEW: Cosine >= 0.55 (La IA inventó rasgos)
* BLOCKED: Cosine < 0.55

## 🕹️ Uso (Script Maestro)
El Script Maestro calcula todo en un solo paso y te da el veredicto final:

# Modo Preservación
python tools/agf_master_score.py foto_original.jpg foto_generada.jpg blaze_face_short_range.tflite --mode preservation

# Modo Restauración
python tools/agf_master_score.py foto_vieja.jpg foto_restaurada.jpg blaze_face_short_range.tflite --mode restoration

## ⚠️ Reglas de Oro
1. Los LLMs mienten: Nunca confíes en un PASS que un chatbot se dé a sí mismo.
2. Verificación Local: Toda métrica debe ser calculada en Termux.
3. Human-in-the-Loop: Si el sistema dice HUMAN_REVIEW, tú tienes la última palabra.

*Repositorio Privado. Modelos biométricos en .gitignore.*

## 👥 Manejo de Fotos Grupales (Multi-Face)
AGF v12.2 está optimizado para 1 rostro (selfies, retratos). Para fotos con múltiples personas, el motor usa una estrategia de Fail-Closed:
1. El Kernel le exige al LLM devolver un array de cajas (faces_detected), una por cada rostro.
2. Si el LLM agrupa las caras en una sola caja (error común), AGF bloquea la validación.
3. En Termux, el detector BlazeFace busca la cara más grande o la de mayor confianza. Si la foto es muy antigua o las caras son muy pequeñas, BlazeFace puede fallar (Zero-Fabrication).

Recomendación: Para fotos grupales históricas, recorta la cara de interés antes de pasarla por agf_full_audit.py.
