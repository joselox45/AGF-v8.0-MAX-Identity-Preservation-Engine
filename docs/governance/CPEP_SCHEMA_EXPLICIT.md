# CPEP_SCHEMA_EXPLICIT — Trazabilidad Forense y Frontera Weak/Strong

## 0. Fundamento Tecnico: Por que el Chat no puede dar BBoxes Exactos
- **Imagen real:** Matriz de 3 millones de numeros RGB.
- **Base64:** Traduccion a texto ASCII.
- **ViT:** Corta en parches de 16x16 con positional embeddings. Ve patrones, no pixeles exactos.
- **LLM (Weak):** Predice la posicion (claimed_bbox, +-30px de error).
- **Termux (Strong):** PIL lee los numeros RGB reales e InsightFace devuelve el bbox exacto (real_bbox).

## 1. Contrato de 4 Estados (Input y Output)
El JSON Sidecar debe auditar tanto la entrada (lo que el LLM dijo ver) como la salida (lo que genero).

```json
{
  "input_audit": {
    "original_claimed_llm": {
      "face_bbox": [400, 310, 600, 570],
      "anchor_evidence": "ojos, nariz, boca"
    },
    "original_real_python": {
      "face_bbox": [410, 320, 590, 580],
      "iou_input": 0.91
    }
  },
  "output_audit": {
    "generated_claimed_llm": {
      "face_bbox": [480, 350, 520, 420],
      "distance_delta": "+40m"
    },
    "generated_real_python": {
      "face_bbox": [478, 348, 522, 418],
      "iou_output": 0.92,
      "pose": {"yaw": -104, "pitch": 20, "roll": 256},
      "detector": {"model": "insightface buffalo_l", "signature": "ed25519:abc..."}
    }
  }
}
```

## 2. Validacion IoU y Umbral Dinamico
- Si `iou_input` < 0.85: El LLM alucino la imagen original (BLOCKED).
- Si `iou_output` < 0.85: El LLM alucino la generacion (BLOCKED).
- **Umbral ArcFace dinamico por rotacion:** `|yaw| < 30 -> 0.60`, `< 90 -> 0.50`, `< 170 -> 0.40`, `>= 170 -> 0.35`.

## 3. Salto Disruptivo: No confiar en el generador
El generador no es un oraculo. Solo produce la imagen y su JSON claimed. La verdad (real_bbox) siempre se calcula fuera en Python (Termux/VPS).
