#!/bin/bash
echo "=== AGF MODEL FETCHER ==="
curl -L -o blaze_face_short_range.tflite https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite
if [ ! -f "arcface.onnx" ]; then
    echo "⚠️ ATENCIÓN: No se encontró 'arcface.onnx' (167MB)."
    echo "Debes descargarlo manualmente y colocarlo en la raíz."
fi
echo "✅ Modelos listos."
