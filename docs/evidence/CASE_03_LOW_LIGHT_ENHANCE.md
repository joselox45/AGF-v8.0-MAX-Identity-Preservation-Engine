# 📂 CASO DE ESTUDIO 03: Iluminación Nocturna y Bloqueo por ArcFace

**Fecha:** 2026-10-29
**Modo:** RESTORATION
**Trigger:** /repara
**Veredicto:** BLOCKED (Hard Gate: ArcFace < 0.65)

## 1. Escenario
Se aplicó una mejora de iluminación (`LOW_LIGHT_ENHANCE`) a una foto nocturna con alto ruido, poca luz y rostro empastado. El objetivo era iluminar y limpiar sin alterar la identidad.

## 2. Metadata Forense (Capa 0)
- **Original:** Sin XMP, compresión Baseline (4 tablas Huffman). Foto de cámara estándar.
- **Generada:** Certificado XMP (`trainedAlgorithmicMedia`) de Meta AI. Compresión Progresiva (6 tablas Huffman). Rastro criptográfico de IA.

## 3. Color Fingerprint (Capa 5)
- **Colores Originales:** `#080B03` (H: 82.5°), `#8A887F` (H: 49.1°), `#463F2B` (H: 44.4°).
- **Colores Generada:** `#1C1B17` (H: 48.0°), `#C0C4CC` (H: 220.0°), `#80746C` (H: 24.0°).
- **ΔH (Diferencia de Matiz):** 53.01°. La IA cambió la camisa de gris cálido a azul frío. **PASS (tolerancia de restauración).**

## 4. Auditoría Compuesta (Capas 1-5)
```text
 [1] Identidad (ArcFace) [40%] : 0.6313  <-- HARD GATE FALLIDO
 [2] Firma de Frecuencia [30%] : 0.9918
 [3] Estructura (Shazam) [20%] : 0.1463
 [4] Píxeles (SSIM)      [10%] : 0.6004
 [5] Huella Cromática    [ 5%] : 0.7055 (ΔH=53.0°)
-------------------------------------------------------
 🚨 VEREDICTO: BLOCKED (Hard Gate: ArcFace 0.631 < 0.65)
