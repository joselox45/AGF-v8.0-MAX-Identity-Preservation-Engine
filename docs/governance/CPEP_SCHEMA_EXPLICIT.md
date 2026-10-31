# CPEP_SCHEMA_EXPLICIT — Trazabilidad Forense y Frontera Weak/Strong

## 0. Fundamento Técnico: Por qué el Chat no puede dar BBoxes Exactos
- **Imagen real:** Matriz de 3 millones de números RGB.
- **Base64:** Traducción a texto ASCII para que el LLM pueda leerlo.
- **ViT:** Corta en parches de 16x16 con positional embeddings. Ve patrones, no píxeles exactos.
- **LLM (Weak):** Predice que hay una cara a la izquierda (claimed_bbox, ±30px de error).
- **Termux (Strong):** PIL lee los números RGB reales e InsightFace devuelve el bbox exacto (real_bbox).

## 1. Trazabilidad de 3 Estados y Validación IoU
El JSON Sidecar debe contener:
1. `original`: Bboxes reales de la imagen de referencia.
2. `generated_claimed`: Bboxes que el LLM (o generador) *dice* que aplicó.
3. `generated_real`: Bboxes que Python *detecta* en la imagen generada.

Si el IoU entre `claimed` y `real` es < 0.85, el LLM alucinó la posición. El validador de Python marca **BLOCKED**.

## 2. Profundidad, Pose y Firma
- **Z (Profundidad):** Un bbox pequeño puede ser un niño cerca o un adulto a 40m. Requiere `depth_z`.
- **Pose (Yaw, Pitch, Roll):** Si el sujeto gira, ArcFace cae. Se requiere guardar el giro para no dar falsos negativos.
- **Firma (Ed25519):** Para garantizar que el `real_bbox` fue medido por Python y no inyectado.

## 3. Giros Drásticos y Umbral Dinámico
Cuando el sujeto rota (ej. de perfil o de espaldas), ArcFace baja naturalmente. El umbral de validación debe ajustarse:
- `|delta_yaw| < 30°` -> threshold 0.60
- `|delta_yaw| < 90°` -> threshold 0.50
- `|delta_yaw| < 170°` -> threshold 0.40
- `|delta_yaw| >= 170°` -> threshold 0.35

---
FIN DEL DOCUMENTO
