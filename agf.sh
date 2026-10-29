#!/bin/bash
if [ "$#" -ne 3 ]; then
    echo "Uso: ./agf.sh <preservation|restoration> <img_original.jpg> <img_generada.jpg>"
    exit 1
fi
if [ ! -f "blaze_face_short_range.tflite" ] || [ ! -f "arcface.onnx" ]; then
    echo "❌ ERROR: Faltan modelos. Ejecuta: ./tools/fetch_models.sh"
    exit 1
fi
python tools/agf_full_audit.py "$2" "$3" --mode "$1"
