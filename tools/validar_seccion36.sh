#!/bin/bash
# VALIDACIÓN DEFINITIVA SECCIÓN 36 – AGF‑GCELL v1.0
# Commit referencia congelado: 42fc6f1
# Hash MAPEO referencia: 3eccf26d413733cfe62f41d61d55e0e37fc155ed4959f38390042c74e95133fb
# SUPUESTO 1: Bloque "VALIDACIÓN ESTRUCTURAL: SECCIÓN 36" contiene EXACTAMENTE 1 separador ============================================================= entre metadatos y transcripción
# SUPUESTO 2: Ejecutado sobre MAPEO_KERNEL_AGF.txt generado en ese commit

MAPEO="MAPEO_KERNEL_AGF.txt"

echo "=== 1. Tamaño del MAPEO ==="
ls -lh "$MAPEO"

echo ""
echo "=== 2. Metadatos del bloque Sección 36 ==="
grep -A 10 "VALIDACIÓN ESTRUCTURAL: SECCIÓN 36" "$MAPEO" | head -n 12

echo ""
echo "=== 3. INICIO transcripción (salta separador – primeras 20 líneas) ==="
awk '
    /VALIDACIÓN ESTRUCTURAL: SECCIÓN 36/ { in_block=1 }
    in_block && /^============================================================$/ { count++ }
    in_block && count == 1 { next }
    in_block && count >= 1 { print; lines++ }
    lines >= 20 { exit }
' "$MAPEO"

echo ""
echo "=== 4. FINAL transcripción (últimas 10 líneas archivo) ==="
tail -n 10 "$MAPEO"

echo ""
echo "=== 5. Confirmación commit ==="
git log --oneline -1

echo ""
echo "=== 6. Hash actual MAPEO ==="
sha256sum "$MAPEO"
