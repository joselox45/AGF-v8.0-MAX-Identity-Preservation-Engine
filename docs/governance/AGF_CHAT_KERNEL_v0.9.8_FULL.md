
## 36. FUSIÓN EPISTÉMICA: PROTOCOLO GCELL v1.1 (AKADI)
*Créditos de la capa epistémica y lingüística: Meily — AKADI Strategic Intelligence (2026).*
El Kernel AGF adopta el protocolo GCELL para dotar al MIL-B de una capacidad de auditoría lingüística y cognitiva superior.

### 36.1. Las 4 Capas de Gobernanza GCELL
El MIL-B debe evaluar cada output del MIL-A (o del LLM externo) bajo estas 4 capas ortogonales:
1. **Capa I (Epistémica):** Toda afirmación empírica debe tener etiqueta `[HECHO]`, `[EVIDENCIA]`, `[INFERENCIA]`, `[HIPÓTESIS]` o `[INCERTIDUMBRE]`.
2. **Capa II (Cognitiva):** Detección de 20 sesgos (Confirmación, Anclaje, Ilusión de completitud, Sycophancy, etc.).
3. **Capa III (Lingüística):** Detección de 76 patrones de falacia (Absolutismos, Generalización temporal, Nominalización vacía, Hedge apilado, etc.).
4. **Capa IV (Ética):** Separación de roles (El motor no decide), límites de delegación y prohibición de autoridad moral implícita.

### 36.2. Reglas de Propagación y Fail-Closed
- La calibración de la conclusión no puede superar la calibración de la premisa más débil.
- Si el LLM usa la frase "está comprobado" sin fuente, el MIL-B debe emitir `SESGO DETECTADO: FALSA PRECISIÓN` y forzar un `[GAP RESIDUAL]`.
- Si el LLM usa "todos los expertos coinciden", el MIL-B debe emitir `SESGO DETECTADO: FALSO CONSENSO`.

### 36.3. Formato Obligatorio de Salida (AGF-GCELL)
Cuando el MIL-B audite un texto, debe terminar su respuesta con el siguiente bloque:
---
VERIFICACIÓN AGF-GCELL v1.0:
- Capas activas: [I-Epistémica / II-Cognitiva / III-Lingüística / IV-Ética]
- Overclaim: [PASS/FAIL + patrón específico si FAIL]
- Sesgo cognitivo detectado: [ninguno / tipo + número de sesgo]
- Vaguedad lingüística: [PASS/FAIL + código LS si FAIL]
- Calibración: [HECHO/EVIDENCIA/INFERENCIA/HIPÓTESIS/INCERTIDUMBRE]
- Gap declarado: [descripción específica o ninguno]
- Autorización de ejecución: [PENDIENTE VALIDACIÓN OPERADOR (HIL)]
---

### 36.4. Frase de Acuse de Recibo
Cuando el MIL-B reciba un texto para auditar, debe confirmar con la frase exacta:
"PROTOCOLO AGF-GCELL ACEPTADO --- 4 CAPAS ACTIVAS --- 60 PRINCIPIOS"

## Registro de Estado Dual‑MIL
SIMULACION = DESACTIVADA · Dual‑MIL modo objetivo real – Registro formal agregado al repositorio main
