# 📂 RESPUESTA A LA AUDITORÍA AKADI 22.0

**Fecha:** 2026-10-30
**Estado:** P0 Parches Aplicados.

## Parches P0 Aplicados

### P0-1: API devolvía PASS viejo
- **Fix:** `api_server.py` ahora genera una ruta única por petición (`audit_{uuid}.json`).
- **Fix:** Verifica el `returncode` de subprocess. Si es != 0, devuelve `BLOCKED`.
- **Fix:** CORS restringido a localhost (ya no es `*`).

### P0-2: Crash en vez de BLOCKED
- **Fix:** `compute_all_metrics` envuelto en `try/except`. Si falla, el script hace `sys.exit(1)`.
- **Fix:** La API detecta el error y devuelve `BLOCKED`.

### P0-3: PASS sin piso de identidad
- **Fix:** Los pesos ahora suman 1.00 (Fourier bajó de 0.30 a 0.25).
- **Fix:** Se añadió `IDENTITY_FLOOR`: 0.65 (Preservation) y 0.55 (Restoration). Si ArcFace cae por debajo, es `BLOCKED` sin importar las otras métricas.

### P0-4: Privacidad del repositorio
- **Acción pendiente:** El humano debe verificar que el repo está en modo Privado en GitHub. Si es público, se debe reescribir la historia o eliminar archivos sensibles.

### P0-5: Firma SHA-256 falsa
- **Fix:** Se eliminó el archivo `AGF_v12.2_FIRMA_SHA256.txt` (estaba desactualizado).
- **Fix:** El README ya no afirma "cryptographically signed". Ahora dice la verdad: usa Git tags.

## Pendientes (P1 / Futuro)
- Rediseñar Fourier para alinear el rostro antes de la FFT.
- Calibrar umbrales con ROC/FAR/FRR.
- Añadir tests al camino canónico (scorer, API).
