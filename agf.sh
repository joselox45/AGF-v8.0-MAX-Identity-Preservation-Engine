#!/bin/bash
# AGF v12.2 - Canonical Path (Composite 4-Layer Engine)
if [ "$#" -ne 3 ]; then
    echo "Uso: ./agf.sh <preservation|restoration> <img_original.jpg> <img_generada.jpg>"
    exit 1
fi
if [ ! -f "blaze_face_short_range.tflite" ] || [ ! -f "arcface.onnx" ]; then
    echo "❌ ERROR: Faltan modelos. Ejecuta: ./tools/fetch_models.sh"
    exit 1
fi
python tools/agf_composite_scorer.py "$2" "$3" blaze_face_short_range.tflite --mode "$1"
