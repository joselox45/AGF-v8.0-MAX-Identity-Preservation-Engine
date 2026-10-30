# 📂 CASO DE ESTUDIO 12: Flujo Canónico HIL (9 Capas)

**Fecha:** 2026-10-30
**Hito:** Primera ejecución exitosa del `agf_full.sh` (9 capas jerárquicas).

## 1. Flujo Ejecutado
1. **Normalización (PIL Lanczos):** Reescaló ambas imágenes a 1328x1904. Esto destruyó los metadatos originales de Meta AI (actuando como sanitizador).
2. **Filtros (No bloquean):** Metadata (limpia) y Tiling (detección de caras).
3. **Diagnóstico (No pondera):** Lighting (consistente, <8% de cambio) y Base64 (672 bloques analizados).
4. **Juez Final (Score Ponderado):** ArcFace 0.8229, Fourier 0.9909, SSIM 0.9779, Color 0.8027.

## 2. Resultado
- **AGF Score Ponderado:** 0.8045
- **Veredicto Final:** PASS

## 3. Conclusión
La arquitectura jerárquica funciona. El Juez Final (5 capas) dictamina el PASS sin verse afectado por los falsos positivos de Metadata. La normalización de escala previa actúa como un sanitizador de metadatos, eliminando la firma de IA.
