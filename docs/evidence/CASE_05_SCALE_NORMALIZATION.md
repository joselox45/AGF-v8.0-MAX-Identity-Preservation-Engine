# 📂 CASO DE ESTUDIO 05: Normalización de Escala (Scale Normalization)

**Fecha:** 2026-10-30
**Contexto:** Auditar una foto restaurada por Meta AI (Boda).

## 1. El Problema (Falsos Negativos por Resolución)
La imagen original y la generada por la IA tenían resoluciones ligeramente distintas (512x705 vs 551x680). Al calcular el SSIM y Shazam directamente, las métricas caían drásticamente porque las cuadrículas de píxeles no coincidían.
- *SSIM original:* 0.5145 (Bajo)
- *Shazam original:* 0.4169 (Bajo)

## 2. La Solución (Pre-procesamiento con PIL)
Se implementó `tools/agf_scale_normalizer.py`. Este script usa el filtro LANCZOS (el estándar de oro) para forzar a ambas imágenes a tener exactamente el mismo tamaño (705x551) antes de la auditoría.

## 3. Resultados (Justicia Matemática)
Tras normalizar la escala:
- *SSIM normalizado:* 0.9507 (Subió 43 puntos)
- *Shazam normalizado:* 0.6842 (Subió 26 puntos)
- *AGF Score Final:* 0.8782 (PASS rotundo)

## 4. Conclusión de Gobernanza
El motor ArcFace ya era robusto a la resolución, pero las métricas de textura (SSIM/Shazam) necesitaban igualdad de cuadrícula. **Regla añadida:** Para imágenes generadas por IA, el recorte y la normalización de escala (con PIL) son pasos previos obligatorios en Termux.
