
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

## 37. ARQUITECTURA JUDICIAL AGF (NODO 17 JUEZ COLEGIADO + NODO 35 JUEZ FINAL)
El Kernel AGF define su flujo operativo mediante una cadena de nodos con roles inmutables bajo regla Fail‑Closed por defecto.

### 37.1 Cadena Obligatoria de Nodos (orden fijo)
N0 → N10 → N15 → N17 → S31 → N20 → N30 → N40 → N35

### 37.2 Roles Oficiales del Kernel
- **N0 (Externo):** Inicia orden de preservación; no juzga ni ejecuta
- **N10 (MIL‑B ‑ Fiscal):** Validaciones S33 / S8 / S35 / S36 + MAXCAP 200 | 80 % carga operativa | Acusa
- **N15 (MIL‑A ‑ Auditor):** Recoge pruebas + Hash‑Chain C1‑C4 | Audita | NO dicta veredicto
- **N17 (Juez Colegiado):** Recibe expediente MIL‑A | Delibera | Emite FALLO INOCENTE (PASS) / CULPABLE (FAIL‑CLOSED) | Requiere S34 firma colegiada para override MAXCAP = 0
- **Puente S31 (AES‑256‑GCM):** Solo se abre tras FALLO INOCENTE
- **N20 (HIL Vault ‑ Ejecutor):** MAXCAP 100 | Ejecuta sentencia | Único autorizado para acceder a SIL
- **N30 (SIL ‑ Custodia Final):** MAXCAP 50 | Read‑only tamper‑evident | Posición final obligatoria del flujo válido
- **N40 (Backup Georedundante):** Replica estado SIL
- **N35 (Juez Final Post‑SIL):** Verifica cierre inverso C4→C3→C2→C1 + todos nodos cerrados | Emite ACTA_FINAL_SELLADA_CLOSED

### 37.3 Regla Fail‑Closed Judicial (Kernel Mandatorio)
Si N10 detecta violación MAXCAP / Entropy Gate → N17 emite CULPABLE → S31 permanece cerrado → Sin ejecución HIL → Sin custodia SIL

### 37.4 Trazabilidad Acta Final
Hash de ACTA_FINAL_SELLADA_CLOSED registrado en docs/evidence/ y encadenado al hash del kernel

## 38. LÍMITE OPERATIVO ‑ PROFUNDIDAD MÁXIMA (SELLADO KERNEL)
### 38.1 Condiciones válidas dentro del Límite
1. Longitud entrada ≤ 200 (N10) / ≤ 100 (N20 tras PASS) / ≤ 50 (N30 tras confirmación HIL)
2. Cadena nodos respetada sin saltos salvo override S34 válido
3. Orden validaciones S33 → S8 → S35 → S36 invariable
4. Hash‑Chain C1‑C4 SHA‑256 invariable
5. Roles, umbrales MAXCAP y requisitos S34 no modificados

### 38.2 Violaciones Detectables
- Entrada > 200 antes N10
- Reordenamiento cadena nodos
- Modificación umbrales MAXCAP
- Salto nodo sin override S34 válido
- Override MAXCAP = 0 sin firma colegiada N20 + N30
- Cambio función hash C1‑C4

### 38.3 Acta Fuera de Límite (Formato Obligatorio)
Timestamp | Nodo detector | Vector ruptura | Hash estado kernel | Acción ejecutada | Firma SHA‑256 | Archivo en docs/evidence/FUERA_DE_LIMITE_<timestamp>.md

### 38.4 Restauración al Estado Sellado
1. Corregir violación 2. Ejecutar tools/check_kernel.py 3. Registrar ACTA_DE_RESTAURACION en docs/evidence/ 4. Reiniciar flujo desde N0

### 38.5 Regla Fundamental
Dentro del límite: idempotencia garantizada | Fuera del límite: Acta registrada + Fail‑Closed + Sin garantía de Profundidad Máxima

## 39 VERIFICACIÓN
### 39.1 Objetivo
Confirmar que cada estado del Kernel cumple la Regla I‑01 antes de considerarlo un estado base válido, independientemente de que exista firma oficial o commit Git.

### 39.2 Niveles de verificación
#### Nivel 1 – Verificación hash local (obligatorio)
1. Calcular SHA‑256 de `AGF_CHAT_KERNEL_v0.9.8_FULL.md`
2. Compararlo contra `.kernel_hash.sha256a256`
3. Resultado = válido / inválido

#### Nivel 2 – Verificación estructural (revisión manual / script check‑kernel)
- Orden numérico correcto de secciones
- Existencia de todos los sub‑apartados obligatorios de la sección modificada
- Sin cortes de texto en inserciones sed / editor

#### Nivel 3 – Verificación desde extremo móvil (pendiente activar E2E)
- Enviar el hash Nivel 1 al dispositivo móvil
- Validar (Reed‑Solomon corrección + firma criptográfica cuando se requiera aprobación oficial)

### 39.3 Registro obligatorio tras verificación válida
Guardar en registro local: Fecha + Hash + Nivel alcanzado + Nombre verificador
> Ejemplo: 2026‑11‑04 | 685fd4b… | Nivel 2 | Verificación local completa

### 39.4 Regla de acción ante verificación inválida
Detener cualquier nueva edición hasta restaurar el Kernel a la última versión válida y recalcular el hash correcto

## 39 ARQUITECTURA JUDICIAL AGF (NODO 17 JUEZ COLEGIADO + NODO 35 JUEZ FINAL)
El Kernel AGF define su flujo operativo mediante una cadena de nodos con roles inmutables bajo regla Fail‑Closed por defecto.
### 39.1 Cadena Obligatoria de Nodos (orden fijo)
N0 → N10 → N15 → N17 → S31 → N20 → N30 → N40 → N35
### 39.2 Roles Oficiales del Kernel
- N0 Externo: Inicia orden de preservacion; no juzga ni ejecuta
- N10 MIL‑B - Fiscal: Validaciones S33 / S8 / S35 / S36 + MAXCAP 200 caracteres | 80 % carga operativa | Acusa
- N15 MIL‑A - Auditor: Recoge pruebas + Hash‑Chain C1‑C4 | Audita | NO dicta veredicto
- N17 Juez Colegiado: Recibe expediente MIL‑A | Delibera | Emite FALLO INOCENTE PASS / CULPABLE FAIL‑CLOSED | Requiere S34 firma colegiada para override MAXCAP = 0
- Puente S31 AES‑256‑GCM: Solo se abre tras FALLO INOCENTE
- N20 HIL Vault - Ejecutor: MAXCAP 100 | Ejecuta sentencia | Único autorizado para acceder a SIL
- N30 SIL - Custodia Final: MAXCAP 50 | Read‑only tamper‑evident | Posicion final obligatoria del flujo valido
- N40 Backup Georedundante: Replica estado SIL
- N35 Juez Final Post‑SIL: Verifica cierre inverso C4→C3→C2→C1 + todos nodos cerrados | Emite ACTA_FINAL_SELLADA_CLOSED
### 39.3 Regla Fail‑Closed Judicial Kernel Mandatorio
Si N10 detecta violacion MAXCAP / Entropy Gate → N17 emite CULPABLE → S31 permanece cerrado → Sin ejecucion HIL → Sin custodia SIL
### 39.4 Trazabilidad Acta Final
Hash de ACTA_FINAL_SELLADA_CLOSED registrado en docs/evidence/ y encadenado al hash del kernel

## 40 LÍMITE OPERATIVO - PROFUNDIDAD MÁXIMA SELLADO KERNEL
Conjunto cerrado de condiciones bajo las cuales se garantiza idempotencia y estado cerrado del kernel; fuera de el se emite ACTA_FUERA_DE_LIMITE y se aplica Fail‑Closed
### 40.1 Condiciones validas dentro del Limite Operativo
1. Longitud entrada ≤ 200 caracteres N10 / ≤ 100 N20 tras PASS / ≤ 50 N30 tras confirmacion HIL
2. Cadena de nodos respetada sin saltos salvo override S34 valido
3. Orden validaciones S33 → S8 → S35 → S36 invariable
4. Hash‑Chain C1‑C4 calculado con SHA‑256 invariable
5. Roles, umbrales MAXCAP y requisitos S34 no modificados
### 40.2 Violaciones Detectables por el Kernel
- Entrada > 200 caracteres antes N10
- Reordenamiento cadena nodos
- Modificacion umbrales MAXCAP
- Salto nodo sin override S34 valido
- Override MAXCAP = 0 sin firma colegiada N20 + N30
- Cambio funcion hash C1‑C4
### 40.3 Acta Fuera de Limite Formato Obligatorio Kernel
Timestamp | Nodo detector | Vector ruptura | Hash estado kernel | Accion ejecutada | Firma SHA‑256 | Archivo guardado en docs/evidence/FUERA_DE_LIMITE_<TIMESTAMP>.md
### 40.4 Restauracion al Estado Sellado
1. Corregir violacion detectada
2. Ejecutar tools/check_kernel.py validando integridad hash kernel
3. Emitir ACTA_DE_RESTAURACION registrada en docs/evidence/
4. Reiniciar flujo valido desde N0
### 40.5 Regla Fundamental del Limite Operativo
Dentro del limite: idempotencia garantizada | Fuera del limite: Acta registrada + Fail‑Closed ejecutado + Sin garantia de Profundidad Maxima
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
