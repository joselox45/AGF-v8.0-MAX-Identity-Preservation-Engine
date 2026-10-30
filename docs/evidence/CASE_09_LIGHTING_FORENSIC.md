# 📂 CASO DE ESTUDIO 09: Lighting & Shadow Physics (Capa 10)

**Fecha:** 2026-10-30
**Hito:** Análisis de coherencia de iluminación en restauración de retratos.

## 1. El Concepto
Las IAs generativas suelen fallar en la física de la luz. Si pegan una cara nueva o cambian el fondo, la dirección de la luz (gradiente) y el contraste cambian de forma imposible en la realidad.

## 2. La Prueba (Boda)
Se analizaron los gradientes de luminancia (Sobel) en el rostro alineado a 256x256.
- **Cambio de Dirección X:** < 50% (Consistente)
- **Cambio de Dirección Y:** < 50% (Consistente)
- **Cambio de Contraste:** < 50% (Consistente)

## 3. Conclusión
La Capa 10 (Lighting Forensic) validó que Meta AI respetó la física de la luz original. Es una capa de diagnóstico avanzado que detectará alucinaciones de iluminación (sombras flotantes, reflejos invertidos).
