# Terminos de pesos de modelos de terceros (LICENSE-WEIGHTS)

AMBITO DEL MIT (LICENSE): cubre UNICAMENTE el codigo original de este
repositorio (src/, tools/, tests/, agf.py, examples/*.py, docs/).
Los pesos de modelos de terceros NO estan cubiertos por el MIT.


El codigo de este repositorio es MIT (ver LICENSE-CODE). Los ARCHIVOS DE
PESOS (modelos .tflite/.onnx) son de terceros y se rigen por sus propias
licencias. Este repositorio NO distribuye pesos.

| Modelo | Origen | Licencia | Uso en AGF |
|---|---|---|---|
| facenet.tflite (128d) | Derivado de `deepface` (serengil), distribuido via HuggingFace `projectimx/Face_embedding` | Dependiente de la licencia del checkpoint de deepface (research; verificar uso comercial) | T22 (TESTED, cosine 0.9675) |
| arcface_digidow.tflite (R50, 512d) | `mobilesec/arcface-tensorflowlite` (digidow.eu) | EUPL-1.2 (copyleft, uso comercial permitido bajo condiciones) | T21 (gap: alineacion facial) |
| BlazeFace / MTCNN (futuro T21-ALIGN) | MediaPipe / davidsandberg | Apache-2.0 / MIT segun componente | Pendiente |

## Obligaciones del usuario comercial
1. Verificar la licencia vigente de cada peso ANTES de uso comercial.
2. EUPL-1.2: modificaciones al modelo deben publicarse bajo EUPL.
3. Conservar los SHA-256 de custodia (evidence/*.json) como trazabilidad.
4. deepface checkpoints: confirmar terminos con el autor para uso comercial.

AGF no otorga derechos sobre los pesos; solo sobre su propio codigo.
