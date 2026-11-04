#!/bin/bash
# BUSCAR ARCHIVOS CANDIDATOS PARA EL PRÓXIMO COMMIT
# HIL VERIFICADO

cd ~/AGF‑v8.0‑MAX‑Identity‑Preservation‑Engine

echo "=== Archivos candidatos detectados (VERIFICADO HIL) ==="
ls -la README.md 2>/dev/null || echo "README.md: NO EXISTE"

echo ""
echo "--- Búsqueda de HTML ---"
find . -iname "*.html" -o -iname "*.htm" 2>/dev/null | grep -v ".git/" || echo "No hay archivos HTML."

echo ""
echo "--- Búsqueda de archivos MAIN ---"
find . -iname "*main*" -type f 2>/dev/null | grep -v ".git/" | head -10 || echo "No hay archivos MAIN."

echo ""
echo "--- Archivos de gobernanza ---"
find ./docs/governance -type f 2>/dev/null
