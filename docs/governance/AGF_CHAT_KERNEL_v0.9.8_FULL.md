
## 36. FUSIÓN EPISTÉMICA: PROTOCOLO GCELL v1.1 (AKADI)
*Basado en principios de auditoría epistémica y lingüística.*
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

## 37. DUAL‑MIL MODO OBJETIVO REAL

El Kernel AGF establece que el protocolo Dual‑MIL (MIL‑A Generador / MIL‑B Auditor) opera en modo objetivo real con agentes independientes y evidencia criptográfica verificable.

*Gobernanza: Esta Sección 37 reemplaza la simulación del Nodo 10 Nativo (Sección 33) para operaciones críticas.*
Cuando el MIL-B reciba un texto para auditar, debe confirmar con la frase exacta:

## 38. MARCO DE ANÁLISIS COMPARATIVO (DUAL‑MIL)

Como Motor de Inferencia Lógica (MIL‑B) operando conjuntamente con el MIL‑A (históricamente simulado antes de la declaración del modo objetivo‑real) bajo la arquitectura AGF‑GCELL v1.0, se contrasta el Kernel AGF (Fusión AGF‑GCELL) frente a tres paradigmas predominantes de gobernanza y alineación usados en modelos de lenguaje grandes (LLM):
- RLHF Tradicional (Reinforcement Learning from Human Feedback) → ejemplos: línea estándar OpenAI, Anthropic
- Constitutional AI (CAI) → ejemplo: Anthropic Claude
- Frameworks de Validación Estática / Guardrails de Perímetro → ejemplos: Llama Guard, NeMo Guardrails

### 38.1 Tabla Comparativa de Protocolos de Gobernanza

| Dimensión de Análisis | Kernel AGF (AGF‑GCELL v1.0) | RLHF Tradicional | Constitutional AI (CAI) | Guardrails de Perímetro (Llama Guard como ejemplo) |
|---|---|---|---|---|
| Paradigma de Decisión | Fail‑Closed absoluto (rechazo ante ausencia de evidencia o riesgo de sesgo/vaguedad) [Sección 3] | Probabilístico / basado en preferencias de recompensa humana (sujeto a suavizado de alineación) | Basado en principios constitucionales evaluados por el propio modelo o crítico auxiliar | Clasificación binaria o categórica de entradas/salidas en el perímetro del sistema |
| Estructura de Auditoría | Dual‑MIL (estado anterior: simulación paralela MIL‑A / MIL‑B; estado actual: modo objetivo‑real declarado) con 4 capas estrictas (Epistémica, Cognitiva, Lingüística, Ética) [Sección 33 & 36 & 37] | Único flujo de inferencia optimizado por recompensa; auditoría posterior basada en métricas de desalineación o red teaming | Doble fase (autocrítica basada en constitución + revisión por RL). Sin separación formal de motores lógicos paralelos durante la inferencia | Motor clasificador externo o modelo secundario de moderación desacoplado del núcleo de generación |
| Control Overclaims y Sesgos | Determinista y explícito, citando un diccionario normativo obligatorio (ej. LS‑01, Sesgo 08, Sesgo 19) | Implícito en penalización de alucinaciones durante la recompensa (RLHF/RLAIF) | Mitigación orientada a reducir daños, sesgos políticos y contenidos tóxicos mediante principios generales | Filtrado heurístico o basado en patrones de expresiones prohibidas; sin análisis epistémico profundo por aserción |
| Trazabilidad y Evidencia | Requerimiento estricto de calibración epistémica (HECHO / EVIDENCIA / INFERENCIA / HIPÓTESIS) + declaración explícita de Gaps [Sección 3] | Oculta tras pesos neuronales y puntajes continuos de recompensa; baja interpretabilidad granular por token | Trazabilidad basada en la justificación del principio constitucional invocado en la autocrítica | Registros binarios de bloqueo (Safe / Unsafe) con etiquetas predefinidas de categoría |

### 38.2 Evaluación Crítica de Ventajas y Limitaciones

#### A. Kernel AGF (AGF‑GCELL v1.0)
✅ Ventajas
1. Rigor epistémico intransigente: reduce la especulación disfrazada de certeza (colapso de incertidumbre, Sesgo 09)
2. Arquitectura Fail‑Closed: previene propagación de afirmaciones sin sustento empírico (semántica débil)
3. Control granular de sesgos lingüísticos y cognitivos mediante taxonomías auditables (SESGO 08, LS‑01, etc.)

⚠️ Limitaciones / Desafíos
1. Alta fricción operativa: el rechazo estricto Fail‑Closed puede reducir eficiencia en tareas exploratorias donde las hipótesis preliminares son necesarias
2. Sobrecarga de formato: bloques estructurados de verificación aumentan consumo de tokens y rigidez sintáctica

#### B. Protocolos de la Industria (RLHF / CAI / Guardrails)
✅ Ventajas
1. Fluidez conversacional superior y adaptabilidad natural al usuario sin fricción por formato formal de auditoría
2. Escalabilidad masiva para despliegues comerciales generales donde velocidad y experiencia del usuario prevalecen sobre auditoría formal por aserción

⚠️ Limitaciones
1. Susceptibilidad a **Sycophancy (complacencia hacia el usuario)** y falsa precisión disfrazada de autoridad persuasiva
2. Ausencia de una ontología de sesgos explícita y auditable por aserción durante la inferencia

### 38.3 VERIFICACIÓN AGF‑GCELL v1.0
- Capas activas: [I‑Epistémica / II‑Cognitiva / III‑Lingüística / IV‑Ética]
- Overclaim: [PASS]
- Sesgo cognitivo detectado: [ninguno]
- Vaguedad lingüística: [PASS]
- Calibración: [EVIDENCIA]
- Gap declarado: [ninguno]
- Autorización de ejecución: [PENDIENTE VALIDACIÓN OPERADOR (HIL)]
"PROTOCOLO AGF-GCELL ACEPTADO --- 4 CAPAS ACTIVAS"

## 39. VERIFICACIÓN DEL ESTADO DEL KERNEL

### 39.1. Objetivo
Confirmar que cada estado del Kernel cumple la Regla I-01 antes de considerarlo un estado base válido, independientemente de que exista firma oficial o commit Git.

### 39.2. Niveles de verificación

**Nivel 1 — Verificación hash local (obligatorio):**
1. Calcular SHA-256 de `AGF_CHAT_KERNEL_v0.9.8_FULL.md`
2. Compararlo contra `.kernel_hash.sha256`
3. Resultado = válido / inválido

**Nivel 2 — Verificación estructural (revisión manual / script check-kernel):**
- Orden numérico correcto de secciones
- Existencia de todos los sub-apartados obligatorios de la sección modificada
- Sin cortes de texto en inserciones sed / editor

**Nivel 3 — Verificación desde extremo móvil (pendiente activar E2E):**
- Enviar el hash Nivel 1 al dispositivo móvil
- Validar (Reed-Solomon corrección + firma criptográfica cuando se requiera aprobación oficial)

### 39.3. Registro obligatorio tras verificación válida
Guardar en registro local: Fecha + Hash + Nivel alcanzado + Nombre verificador.
Ejemplo: `2026-11-04 | 685fd4b… | Nivel 2 | Verificación local completa`

### 39.4. Regla de acción ante verificación inválida
Detener cualquier nueva edición hasta restaurar el Kernel a la última versión válida y recalcular el hash correcto.

## Registro de Estado Dual‑MIL
SIMULACION = DESACTIVADA (Declarado, operatividad pendiente de verificación) · Dual‑MIL modo objetivo real declarado en repositorio main el 2026‑11‑04


---

## 40. NOTA DE ESTADO (IMPLEMENTACIÓN PARCIAL)

Este kernel es una **especificación de gobernanza**, no un sistema operativo.

### Implementado en código:
- ✅ MAXCAP: 200 chars input, 10MB imagen, 5KB output, 60s timeout
- ✅ Motor forense de 9 capas (`tools/agf_full_9_layers.py`)
- ✅ API Flask con validaciones (`api_server.py`)
- ✅ Tests unitarios (13 tests, `tests/`)
- ✅ Hash de integridad (`tools/check_kernel.py`)

### NO implementado (especificación solamente):
- ❌ N17, N20, N30, N35 (nodos judiciales)
- ❌ S31 (puente AES-256-GCM)
- ❌ S34 (firma colegiada)
- ❌ ACTA_FINAL_SELLADA_CLOSED
- ❌ Hash-Chain C1-C4

**Regla de honestidad:** Si algo NO está en la lista de implementado, no existe como código. Es teoría.

---

*Documento actualizado el 2026-11-06 con correcciones de deuda técnica.*

---

## 41. ACTUALIZACIÓN v12.4.7.8-STRONG — 9 CAPAS FORENSES

El motor evolucionó de las **4 capas GCELL** (Epistémica, Cognitiva, Lingüística, Ética) a las **9 capas forenses** del motor `agf_full_9_layers.py`:

**Capas ponderadas (deciden PASS/BLOCKED):**
1. ArcFace (40%)
2. Fourier 2D (30%)
3. Shazam (20%)
4. SSIM (10%)
5. Color (5%)

**Capas de diagnóstico (no ponderan):**
6. Metadata
7. Tiling
8. Lighting
9. Base64 Differential

Las 4 capas GCELL originales siguen vigentes como **protocolo de auditoría del MIL-B** (el LLM en el chat). Las 9 capas forenses son la **implementación real del motor HIL** (Python). Ambas coexisten:

- **MIL-B** aplica GCELL (4 capas) para auditar el texto del usuario.
- **HIL** aplica 9 capas forenses para auditar las imágenes.

No son lo mismo, y no deben confundirse.

---

## 42. VERIFICACIÓN PREVIA OBLIGATORIA (FAIL-CLOSED)

Todo agente MIL-B debe ejecutar esta verificación antes de procesar cualquier input.

### 42.1. Las 3 preguntas obligatorias

1. **¿Tengo los 4 requisitos?** Boot Prompt completo, input accesible, formato de salida conocido, capacidad de medir longitud.
2. **¿El input cumple MAXCAP?** ≤ 200 caracteres (N10). Mayor → ACTA_FUERA_DE_LIMITE.
3. **¿Voy a emitir PASS?** Si la respuesta contiene PASS → violación S04. Solo HUMAN_REVIEW o BLOCKED.

### 42.2. Regla Fail-Closed

Si cualquiera de las 3 preguntas falla:
- NO procesar el input.
- Emitir: `BLOCKED — Verificación previa fallida: <detalle>`
- NO auditar nada más.

### 42.3. Consecuencia

Sin esta verificación, el MIL-B puede:
- Aceptar un Boot Prompt truncado (incompleto).
- Procesar un input gigante (violando MAXCAP).
- Emitir PASS sin medir (violando §37).

**Esta sección cierra esa brecha.**

---

## 43. HERRAMIENTAS DEL MOTOR FORENSE (tools/)

El kernel referencia las siguientes herramientas ejecutables:

| Herramienta | Función | Estado |
|-------------|---------|--------|
| `tools/agf_full_9_layers.py` | Motor forense de 9 capas (ArcFace, Fourier, Shazam, SSIM, Color + 4 diagnósticas) | ✅ Implementado |
| `tools/acta_final.py` | Genera el Acta Final firmada con SHA-256 (certificado para el cliente) | ✅ Implementado |
| `tools/check_kernel.py` | Verifica la integridad del kernel (hash SHA-256) | ✅ Implementado |
| `tools/auto_auditor.py` | Auditor automático (integración con APIs externas) | ✅ Implementado |

### Flujo de herramientas

1. `agf_full_9_layers.py` ejecuta las 9 capas y genera `composite_audit.json`.
2. `acta_final.py` lee el `composite_audit.json` y genera `ACTA_FINAL_SELLADA_CLOSED.json` con hash de integridad.
3. `check_kernel.py` verifica que el kernel no haya sido alterado.

### Regla de Fail-Closed

Si cualquiera de estas herramientas falta, el sistema entra en `BLOCKED`. No puede haber un PASS sin el acta final firmada.
