# 📂 CASO DE ESTUDIO 10: Tiling Detection para Fotos de Cuerpo Entero

**Fecha:** 2026-10-30
**Hito:** Implementación de la Capa 0 (Tiling Detector).

## 1. El Problema
BlazeFace (`short_range`) está diseñado para selfies. En fotos de cuerpo entero o grupales, las caras son muy pequeñas (ej. 30x30 píxeles). El detector reduce la imagen a 128x128 y la cara desaparece, devolviendo `BLOCKED`.

## 2. La Solución (Capa 0)
Se implementó `tools/agf_tiling_detector.py`. El motor divide la imagen en un mosaico de 3x3 (con 25% de solapamiento). Detecta caras en cada mosaico, aplica NMS (Non-Maximum Suppression) para eliminar duplicados, y un filtro de varianza para descartar manchas o fondos.

## 3. Resultados
- El Tiling detectó las caras en una foto de cuerpo entero donde la detección directa fallaba.
- Si el Tiling encuentra una cara borrosa (mancha), el filtro de varianza la descarta, evitando falsos positivos.
- Si no hay caras válidas, el sistema mantiene el Fail-Closed (`BLOCKED`).
