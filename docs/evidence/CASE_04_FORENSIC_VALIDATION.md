# 📂 CASO DE ESTUDIO 04: Validación Cruzada (Web Simulada vs. Termux Real)

**Fecha:** 2026-10-30
**Objetivo:** Demostrar empíricamente que la interfaz web (Canvas API) es solo una aproximación visual y que el motor en Termux (ONNX/TFLite) es el único juez forense real.

## 1. El Problema de la Web
La interfaz `agf_ui.html` no puede cargar el modelo `arcface.onnx` (167MB) por limitaciones del navegador. Por lo tanto, simula el Cosine con `Math.random()`.
- **Peligro:** Puede dar un falso `PASS` visual en imágenes que en realidad no coinciden geométricamente.

## 2. La Prueba de Fuego (Termux Real)
Se realizaron dos auditorías con el motor real en Termux usando recortes manuales.

### Test A: La Misma Persona (Novia Original vs. Novia Generada)
- **ArcFace:** `0.8049` (Identidad confirmada)
- **Fourier:** `0.9915` (Textura biológica)
- **AGF Score:** `0.8979`
- **Veredicto:** `✅ PASS`

### Test B: Personas Distintas (Novia vs. Señor de la Gorra)
- **ArcFace:** `-0.0788` (Vectores ortogonales, distinta persona)
- **Fourier:** `0.9907` (El señor también es real)
- **AGF Score:** `0.4342`
- **Veredicto:** `🚨 BLOCKED (Hard Gate Extremo)`

## 3. Conclusión Forense
1. **Termux es la Verdad Absoluta:** El modelo matemático diferencia con precisión quirúrgica entre la misma persona (PASS) y personas distintas (BLOCKED).
2. **El Recorte Manual es Vital:** En fotos grupales, BlazeFace falla. El recorte manual del rostro (hecho por el humano) es lo que permite que ArcFace haga su trabajo con precisión.
3. **La Web es Descartable:** El `PASS` de la Web no tiene valor legal. Solo el `PASS` de Termux (respaldado por el `composite_audit.json`) tiene validez forense.
