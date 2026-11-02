# Caso de Estudio: Contradicción Real MIL vs HIL (Identidad Fabricada)

**Fecha de Prueba:** 2026-11-02
**Fase:** MIL (Chat) -> HIL (Termux)
**Objetivo:** Demostrar por qué el veredicto del LLM (MIL) no puede certificar identidad frente a la medición de píxeles (HIL).

## 1. El Escenario
Se subieron dos imágenes a la ventana de chat:
1. `original.jpg`: Retrato antiguo en blanco y negro.
2. `generada.jpg`: Restauración creada por una IA generativa (Meta AI / Grok).

## 2. Fase MIL (Model-in-the-Loop) - Chatbot
*   **Trigger:** `/preserva`
*   **Condicionamiento:** `weak_semantic` (sin acceso a píxeles).
*   **Resultado:** El LLM emitió un JSON con `verdict: PENDING_LOCAL_VERIFICATION`, `pixel_access: false` y `metrics_missing: ["arcface", ...]`.
*   **Conclusión MIL:** El Chatbot obedeció el Kernel (Zero-Fabrication), negándose a inventar métricas biométricas.

## 3. Fase HIL (Hardware-in-the-Loop) - Termux
Se ejecutó el motor forense real:
`./agf.sh preservation original.jpg generada.jpg`

**Resultados Matemáticos (ArcFace + Fourier):**
*   [1] Identidad (ArcFace): **0.0806** (Fallo crítico)
*   [2] Firma de Frecuencia: **0.9935** (Textura preservada)
*   [3] Estructura (Shazam): **0.4747**
*   [4] Píxeles (SSIM): **0.7420**
*   [5] Huella Cromática: **0.7966**
*   [7] Overlay Diff: **64.06%** (Alteración visual masiva)

**Veredicto Final:** `🚨 BLOCKED (Hard Gate Identidad: ArcFace 0.081 < 0.65)`

## 4. Prueba de Control (Falso Positivo)
Para validar la integridad del motor HIL, se comparó `original.jpg` contra `original.jpg`:
`./agf.sh preservation original.jpg original.jpg`
*   **Resultado:** Todos los scores `1.0000`.
*   **Veredicto:** `✅ PASS (Identidad y Textura Blindadas)`.
*   **Conclusión de Control:** El motor no está sesgado a bloquear; solo bloquea alteraciones reales.

## 5. Conclusión Epistémica
La IA generativa alteró la estructura de la cara (ArcFace 0.08) mientras mantuvo el ruido y la textura del papel (Fourier 0.99). Un humano o un LLM desprevenido habría dado un PASS por la apariencia "antigua". El Juez Puro (HIL) y el Kernel v0.9.8 atraparon la fabricación de identidad.

Evidencia cruda generada en:
- `termux_sealed/composite_audit.json`
- `~/storage/downloads/agf_overlay_diff.png` (Mapa de calor visual)
