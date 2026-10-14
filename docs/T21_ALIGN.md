# T21-ALIGN — Detector + alineación (cierre del gap ArcFace)

## Descarga del detector (una vez)
```bash
curl -L -o /sdcard/Download/blaze_face_short_range.tflite   "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite"
sha256sum /sdcard/Download/blaze_face_short_range.tflite   # anotar en evidencia
```

## Re-cierre T21 con alineación (el gap medido: 0.4257 -> esperado > 0.7)
```bash
python tools/closure_t21_tflite.py     /sdcard/Pictures/1788328458643.jpg     /sdcard/Pictures/file_0000000041a0820eb5eee20d710f488f.jpg     /sdcard/Download/arcface_digidow.tflite arcface div255     /sdcard/Download/blaze_face_short_range.tflite
```

## Qué hace el pipeline
1. BlazeFace (896 anchors, NMS) -> bbox + 6 keypoints
2. Similitud 3pt (ojo izq/der + nariz) -> template ArcFace 112x112
3. Embedder ArcFace (div255) sobre recorte alineado
4. Comparador coseno + anti-replay + evidencia SHA-512
