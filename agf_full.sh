#!/bin/bash
# AGF v12.4.7.7-STRONG - Full 9-Layer Audit (Standalone)
if [ "$#" -lt 3 ]; then
    echo "Uso: ./agf_full.sh <orig> <gen> <mode: preservation|restoration>"
    exit 1
fi
python tools/agf_full_9_layers.py "$1" "$2" "$3"
