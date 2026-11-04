#!/data/data/com.termux/files/usr/bin/bash
# tools/update_protocol_state.sh – Reemplazo línea / Inserción multilínea después de coincidencia
set -euo pipefail

RUTA_ARCHIVO="docs/governance/AGF_CHAT_KERNEL_v0.9.8_FULL.md"
CARPETA_EVIDENCIA="docs/evidence"
ARCHIVO_KERNEL_CHECK="tools/check_kernel.py"

mostrar_ayuda() {
  echo "Modo 1 (reemplazar línea): $0 \"CADENA_BUSQUEDA\" \"NUEVA_LÍNEA_COMPLETA\" \"MENSAJE_COMMIT\""
  echo "Modo 2 (insertar bloque después): $0 --insert-after-match \"CADENA_BUSQUEDA\" ruta_bloque.txt \"MENSAJE_COMMIT\""
  exit 1
}

MODO_REEMPLAZAR=1
if [[ $# -ge 1 && "${1:-}" == "--insert-after-match" ]]; then
  MODO_REEMPLAZAR=0
  shift
fi

if [[ "${MODO_REEMPLAZAR}" -eq 1 && $# -ne 3 ]]; then mostrar_ayuda; fi
if [[ "${MODO_REEMPLAZAR}" -eq 0 && $# -ne 3 ]]; then mostrar_ayuda; fi

BUSQUEDA="$1"
ARG2="$2"
MENSAJE_COMMIT="$3"

echo "🔍 Validando integridad kernel protegido (PUBLIC_LIMITED.md)..."
python3 "${ARCHIVO_KERNEL_CHECK}"

LINEA_REF=$(grep -nF "${BUSQUEDA}" "${RUTA_ARCHIVO}" || true)
if [[ -z "${LINEA_REF}" ]]; then
  echo "⚠️ No se encontró coincidencia para: ${BUSQUEDA}"
  exit 1
fi
NUM_LINEA_REF="${LINEA_REF%%:*}"
TEXTO_REF="${LINEA_REF#*:}"
echo "✅ Línea referencia encontrada (línea ${NUM_LINEA_REF}): ${TEXTO_REF}"
read -p "¿Continuar con la operación? si/no: " CONFIRMAR
if [[ "${CONFIRMAR,,}" != "si" ]]; then exit 0; fi

if [[ "${MODO_REEMPLAZAR}" -eq 1 ]]; then
  sed -i "${NUM_LINEA_REF}s|${TEXTO_REF}|${ARG2}|g" "${RUTA_ARCHIVO}"
  TEXTO_CAMBIO="${ARG2}"
  TIPO_CAMBIO="Reemplazo línea"
else
  if [[ ! -f "${ARG2}" ]]; then
    echo "❌ Archivo bloque no existe: ${ARG2}"
    exit 1
  fi
  sed -i "${NUM_LINEA_REF}r ${ARG2}" "${RUTA_ARCHIVO}"
  TEXTO_CAMBIO="Bloque cargado desde ${ARG2}"
  TIPO_CAMBIO="Inserción multilínea después línea ${NUM_LINEA_REF}"
fi

HASH_ACTUAL=$(git rev-parse HEAD)
FECHA_ACTUAL=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
mkdir -p "${CARPETA_EVIDENCIA}"
RUTA_EVIDENCIA="${CARPETA_EVIDENCIA}/evidence_${HASH_ACTUAL:0:7}_estado_protocolo.md"

cat > "${RUTA_EVIDENCIA}" <<INNEREOF
# Evidencia – Cambio estado protocolo (FULL.md)
Fecha UTC: ${FECHA_ACTUAL}
Hash pre‑cambio: ${HASH_ACTUAL}
Archivo modificado: ${RUTA_ARCHIVO}
Tipo cambio: ${TIPO_CAMBIO}
Línea referencia: ${TEXTO_REF}
Contenido aplicado: ${TEXTO_CAMBIO}
✅ Kernel protegido PUBLIC_LIMITED.md: Integridad confirmada (hash NO modificado)
INNEREOF

echo "📝 Preparando commit..."
git add "${RUTA_ARCHIVO}" "${RUTA_EVIDENCIA}"
git commit -m "${MENSAJE_COMMIT}"
echo "✅ Cambio aplicado + evidencia generada | Kernel protegido intacto"
