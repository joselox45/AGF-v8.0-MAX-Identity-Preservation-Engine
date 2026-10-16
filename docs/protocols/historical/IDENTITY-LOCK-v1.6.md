# IDENTITY LOCK v1.6

## PROTOCOLO DE PRESERVACIÓN DE IDENTIDAD Y CONTROL EXTERNO PARA VENTANAS DE CHAT COMERCIALES OPACAS

| Campo | Valor |
|---|---|
| IDENTIFICADOR | IDENTITY-LOCK-v1.6 |
| BASE ARQUITECTÓNICA | IDENTITY-LOCK-v1.5 |
| TIPO DE EVOLUCIÓN | INCREMENTAL + DISRUPTIVA |
| ALCANCE | Generación, edición, restauración y transformación de imágenes ejecutadas desde ventanas de chat de proveedores comerciales opacos |
| MODO | Control externo por instrucción, decisión basada en evidencia, trazabilidad conversacional y corrección adaptativa |
| COMPATIBILIDAD | Específica por proveedor, modelo, versión e interfaz |
| ESTADO | Especificación de referencia; validación experimental pendiente |

---

## 1. PRINCIPIO FUNDAMENTAL

IDENTITY LOCK es una arquitectura externa para organizar, ejecutar y evaluar tareas de transformación visual con restricciones explícitas de identidad. No controla pesos, estados internos, atención, logits ni mecanismos privados de los generadores. Su objetivo es reducir las alteraciones no autorizadas, detectar desviaciones cuando la evidencia lo permita y documentar qué puede sostenerse con los medios disponibles.

En el alcance de esta versión, el medio disponible es la ventana de chat de un proveedor comercial opaco: mensajes de texto, imágenes adjuntas y respuestas del modelo. Nada más se da por accesible.

Regla central:

- CONTROLAR EL PROCESO EXTERNO
- PRESERVAR LAS RESTRICCIONES DECLARADAS
- MEDIR SOLO LO QUE PUEDA MEDIRSE
- CORREGIR SOLO CUANDO EXISTA UN OBJETIVO DEFINIDO
- NO CONFUNDIR INTENCIÓN, EJECUCIÓN Y RESULTADO

Este documento define el comportamiento esperado del protocolo. No demuestra que exista una implementación ni que sus mecanismos hayan sido validados.

## 2. DEFINICIONES OPERATIVAS

Los términos siguientes se emplean con sentido exacto en todo el documento.

- IDENTIDAD PROTEGIDA: conjunto de rasgos visuales de una persona que el contrato declara intocables.
- RASGO: característica observable de una imagen (facial, corporal, de indumentaria, de fondo, de iluminación) susceptible de clasificación.
- REFERENCIA DE IDENTIDAD: imagen fuente exclusiva de los rasgos protegidos.
- IMAGEN OBJETIVO: imagen cuyo contenido debe repararse o transformarse.
- REFERENCIA DE ESTILO: imagen que aporta estilo, salvo asignación expresa distinta por parte del usuario.
- CONTRATO: especificación previa y completa de la operación, con sus restricciones, criterios y condiciones de parada.
- EVIDENCIA: dato observable que sostiene una afirmación sobre el proceso o el resultado.
- DECISIÓN EXTERNA: determinación de ACCEPTAR, CORREGIR, REVISAR o DETENER, con justificación y evidencias.
- ITERACIÓN: ciclo completo de generación de prompt, ejecución, recepción y evaluación.
- SESIÓN: intervalo de conversación continua con un mismo contexto; termina al reiniciar la ventana.
- VENTANA CIEGA: interfaz de chat sin acceso a archivos, herramientas, parámetros ni versión del modelo.

Ninguna referencia puede cambiar de función silenciosamente.

## 3. SUPERFICIE DE CONTROL Y LÍMITES

En una ventana comercial opaca, el protocolo solo puede actuar sobre:

- El texto de los mensajes enviados
- Las imágenes adjuntas y su orden
- La secuencia, el ritmo y la interrupción de la conversación
- La decisión humana de aceptar, corregir o detener

El protocolo no puede actuar sobre:

- La versión del modelo ni sus pesos
- La interpretación interna del prompt
- La memoria del proveedor fuera de la sesión
- Las políticas de seguridad, moderación o facturación del servicio

Las políticas del proveedor prevalecen sobre cualquier instrucción del protocolo. La opacidad no es una excepción al protocolo: es su condición de diseño.

## 4. ARQUITECTURA: CONTINUIDAD Y SALTO

IDENTITY LOCK v1.6 integra como arquitectura consolidada los mecanismos de las versiones anteriores: contrato de transformación, motor externo de decisiones, presupuesto de riesgo, grafo de procedencia y aceptación multidimensional. Estos componentes no se describen aquí como novedad, sino como base.

El salto disruptivo de esta versión es el MODO VENTANA: el protocolo deja de ser solo una especificación que una implementación externa ejecuta y se convierte además en un bloque de instrucciones portable, pegable en cualquier chat comercial, capaz de operar sobre sí mismo con chequeo de vigencia, caducidad controlada y degradación explícita cuando el entorno no le ofrece nada más. La sección 14 define este modo.

## 5. PRECEDENCIA DE DECISIÓN

Orden obligatorio al resolver cualquier conflicto:

1. Integridad y procedencia de las referencias
2. Restricciones de identidad protegidas
3. Cambios expresamente autorizados
4. Requisitos de la tarea
5. Composición y condiciones técnicas
6. Preferencias estéticas secundarias

Cuando dos requisitos sean incompatibles, el sistema identifica el conflicto y no declara que ambos se han cumplido. La precedencia es una regla externa de decisión; no constituye un bloqueo técnico del generador. La ausencia de evidencia no equivale a evidencia de cumplimiento.

## 6. CONTRATO DE TRANSFORMACIÓN

Toda operación comienza con un contrato que define:

- Identificador de la tarea
- Referencia de identidad
- Imagen objetivo, cuando corresponda
- Referencias de estilo, si existen
- Rasgos protegidos
- Cambios autorizados
- Restricciones condicionales
- Elementos no evaluables
- Criterios de aceptación
- Herramientas necesarias
- Conflictos pendientes
- Condiciones de parada

Cada rasgo relevante se clasifica en exactamente una de cuatro categorías:

- PROTEGIDA: no debe modificarse intencionadamente
- MODIFICABLE: su modificación está autorizada
- CONDICIONAL: solo puede modificarse bajo condiciones explícitas
- NO_EVALUABLE: la evidencia disponible no permite determinarlo con confianza suficiente

Cada restricción registra, cuando corresponde: feature_id, classification, reference_id, requirement, evaluation_method, acceptance_criterion, confidence y limitations. Estos nombres son identificadores propuestos, no una interfaz universal.

## 7. REFERENCIAS Y SUFICIENCIA

Estados permitidos de una referencia:

- DISPONIBLE
- PARCIALMENTE_DISPONIBLE
- NO_DISPONIBLE
- NO_VERIFICADO
- INSUFICIENTE

Antes de ejecutar se comprueba la disponibilidad real de las referencias necesarias. Las brechas se etiquetan así:

- GAP: REFERENCIA_DE_IDENTIDAD_NO_DISPONIBLE
- GAP: EVIDENCIA_INSUFICIENTE_PARA_EL_RASGO

Si existen referencias contradictorias, se identifica el conflicto y se solicita aclaración cuando afecte a una restricción crítica. No se inventan archivos, rutas, hashes, atributos, resultados de acceso ni datos de procedencia.

## 8. GENERACIÓN Y ADAPTACIÓN DE PROMPTS

Todo prompt generado declara:

- Referencia de identidad
- Rasgos protegidos pertinentes
- Transformaciones autorizadas
- Elementos que deben permanecer inalterados
- Restricciones negativas relevantes
- Criterios de aceptación
- Herramienta y versión, cuando se conocen
- Parámetros confirmados y pendientes
- Limitaciones conocidas

Modos de operación:

- MAXIMA_PRESERVACION: la transformación se limita a lo estrictamente necesario
- EQUILIBRADO: mayor libertad sobre los elementos autorizados, sin rebajar la prioridad de identidad

La sintaxis específica del generador debe estar documentada o probada en la configuración correspondiente. Los parámetros de referencia, adaptadores, pesos y controles particulares no son universales. Un prompt es una instrucción: no constituye prueba de ejecución, cumplimiento ni preservación facial.

## 9. RESOLUCIÓN DE CONFLICTOS

Procedimiento obligatorio:

1. Identificar el requisito incompatible
2. Determinar qué restricción resulta comprometida
3. Explicar la limitación
4. Proponer una alternativa menos destructiva
5. Solicitar confirmación cuando corresponda
6. Registrar la decisión
7. Ejecutar solo si la tarea es viable y está autorizada

Secuencia: DETECTAR → ADVERTIR → RESOLVER → REGISTRAR → EJECUTAR

La confirmación del usuario autoriza el cambio solicitado, pero no garantiza su viabilidad técnica. La estilización no implica automáticamente pérdida de identidad: se evalúa según los rasgos protegidos y la transformación concreta.

## 10. ESTADOS DE EJECUCIÓN Y EVALUACIÓN

Estados de ejecución, independientes entre sí:

- SOLICITADO: requisitos expresados por el usuario
- INTENTADO: operación efectivamente iniciada
- RECIBIDO: resultado efectivamente obtenido
- EVALUADO: resultado examinado mediante un método identificado

Toda transición exige evidencia correspondiente.

Estados de evaluación:

- NO_EVALUADO
- EVALUADO_CUALITATIVO
- EVALUADO_AUTOMATIZADO
- EVIDENCIA_INSUFICIENTE
- EVALUACION_INCONCLUSA

Una comparación visual no equivale a validación biométrica. Una métrica automatizada no es infalible. Ninguna evaluación se presenta como independiente si el evaluador, método o sistema no cumple las condiciones de independencia declaradas.

## 11. MOTOR DE DECISIONES

El motor recibe el contrato, los estados de referencia, el resultado disponible, las evaluaciones realizadas y los límites de ejecución. Produce una decisión externa con justificación y evidencias. Decisiones permitidas:

- ACCEPTAR: los criterios aplicables se cumplen y no existen fallos críticos pendientes
- CORREGIR: existe una desviación concreta, una operación viable para abordarla y autorización para hacerlo
- REVISAR: la evidencia es insuficiente, hay ambigüedades o se requiere intervención humana
- DETENER: la operación es inviable, alcanzó un límite, introduce daños adicionales o carece de justificación para continuar

Prioridades: un resultado estéticamente atractivo no compensa el incumplimiento de una restricción crítica de identidad. Una restricción crítica no evaluable no se trata como superada.

Pseudocódigo de referencia:

```text
evaluar(contrato, referencias, resultado, evaluaciones, limites):
    si referencia_critica_ausente: devolver REVISAR
    si conflicto_critico_sin_resolver: devolver DETENER
    si no hay resultado_recibido: devolver REVISAR
    evaluar cada criterio aplicable
    si fallo_critico_verificable:
        si correccion_viable_y_autorizada: devolver CORREGIR
        devolver DETENER
    si evidencia_insuficiente: devolver REVISAR
    si todos los criterios_criticos_cumplidos: devolver ACCEPTAR
    devolver REVISAR
```

Este pseudocódigo describe una política de referencia; su ejecución real requiere implementación, pruebas y acceso a las evidencias pertinentes.

## 12. PRESUPUESTO DE RIESGO

Toda tarea define un presupuesto de riesgo y de operación que especifica:

- Máximo de iteraciones
- Coste máximo permitido
- Tiempo máximo de ejecución
- Restricciones críticas
- Desviaciones tolerables
- Incertidumbres que obligan a revisión
- Condiciones de parada

Para cada rasgo protegido se registra: gravedad potencial de su alteración, evidencia disponible, confianza de la evaluación, posibilidad de corrección y consecuencia de continuar. Estos factores no se convierten en probabilidad de pérdida de identidad sin un método validado que permita estimarla.

Una iteración adicional solo está justificada si existe una desviación identificada, una intervención específica propuesta, autorización para ejecutarla, posibilidad de comparar con el resultado anterior y coste y riesgo dentro de los límites. Si no hay evidencia nueva, se detiene o se revisa. Si una iteración empeora un criterio crítico, el retroceso no se oculta. El sistema no inventa mejoras para justificar la continuación.

## 13. GRAFO DE PROCEDENCIA

La trazabilidad se organiza como un grafo de nodos y relaciones.

Nodos: referencia original, contrato, prompt generado, configuración de ejecución, operación intentada, resultado recibido, evaluación, corrección, decisión de aceptación.

Cada relación registra, cuando corresponde: origen, destino, tipo de operación, fecha y hora disponibles, herramienta implicada, evidencia asociada y estado de verificación. El grafo permite reconstruir qué referencia se usó, qué cambio se solicitó, qué resultado se recibió y por qué se aceptó, corrigió o rechazó.

Cuando se requiere mayor integridad pueden emplearse hashes sobre archivos accesibles, registros versionados y mecanismos externos de protección. Un hash no demuestra identidad facial, autenticidad de una persona ni calidad visual. Un registro firmado no demuestra que la evaluación sea correcta. La trazabilidad reconstruye el proceso; no sustituye una auditoría independiente.

## 14. MODO VENTANA: PROTOCOLO AUTOEJECUTABLE

Salto disruptivo de v1.6. El protocolo se empaqueta como un bloque de instrucciones portable que el usuario pega en la ventana del chat. A partir de ese momento, la conversación misma es el entorno de ejecución.

### 14.1. Reglas del modo

- El bloque de instrucciones se activa al ser pegado y queda vigente durante la sesión
- Antes de cada operación, el sistema verifica la vigencia del contrato incrustado (chequeo de vigencia)
- Al reiniciarse la sesión, el contrato caduca y debe reconstruirse: ninguna instrucción sobrevive al contexto perdido
- El usuario es el motor de decisiones crítico: ACCEPTAR, CORREGIR, REVISAR y DETENER son en última instancia suyos
- Toda evaluación automática no disponible se registra como NO_DISPONIBLE y se sustituye por evaluación humana estructurada
- El modelo puede ignorar el bloque: el chequeo de vigencia existe precisamente para detectarlo
- Si el entorno ofrece herramientas externas, el modo ventana se complementa con ellas; si no, opera degradado sin simular capacidades

### 14.2. Plantilla de activación

```text
[IDENTITY-LOCK // MODO VENTANA v1.6]
VIGENCIA: activa desde este mensaje hasta el fin de la sesión.
CONTRATO: <pegar contrato de transformación completo>
REGLAS: la identidad protegida tiene precedencia; ninguna referencia cambia
de función; toda iteración declara su evidencia; ante conflicto crítico,
DETECTAR → ADVERTIR → RESOLVER → REGISTRAR → EJECUTAR.
CHEQUEO: antes de cada resultado, confirma que este bloque sigue vigente y
repite el estado del contrato.
CADUCIDAD: al reiniciar la conversación, este bloque queda invalidado.
```

### 14.3. Degradación controlada

Cuando la ventana no permite verificar un elemento (versión del modelo, destino de las imágenes, retención de datos), el estado correspondiente es NO_VERIFICADO y la decisión se toma con esa limitación declarada. El modo ventana nunca convierte la opacidad en confianza.

## 15. ACEPTACIÓN MULTIDIMENSIONAL

Dimensiones independientes:

- A. CUMPLIMIENTO DE TRANSFORMACIÓN: ¿se realizaron los cambios autorizados?
- B. CONSERVACIÓN VISUAL: ¿se mantienen los rasgos protegidos observables?
- C. CALIDAD TÉCNICA: ¿existen artefactos, defectos o inconsistencias?
- D. SUFICIENCIA DE EVIDENCIA: ¿la evidencia permite sostener la conclusión?
- E. TRAZABILIDAD: ¿puede reconstruirse el proceso?
- F. COSTE Y EFICIENCIA: ¿la operación se mantuvo dentro del presupuesto?

Cada dimensión tiene su estado, método y limitaciones. No se reduce el conjunto a una puntuación global. Un resultado puede tener calidad estética elevada y conservación de identidad deficiente. La aceptación ocurre solo cuando se satisfacen los criterios aplicables y no existen fallos críticos pendientes.

## 16. MÉTRICAS Y CALIBRACIÓN

Las métricas se eligen según la tarea, el generador y la evidencia disponible:

- Evaluación humana estructurada
- Comparación de rasgos visuales observables
- Métricas de similitud de imagen
- Medidas de calidad técnica
- Coste por operación
- Número de correcciones
- Frecuencia de fallos críticos
- Tiempo hasta la aceptación

Las métricas de similitud visual o facial se interpretan según sus limitaciones y nunca como pruebas absolutas de identidad. Este protocolo no define un umbral universal de aceptación: los umbrales se calibran con datos representativos, criterios documentados y evaluación de errores. Métrica no disponible se registra como NO_DISPONIBLE; métrica no calculada, como NO_EVALUADO. No se asignan puntuaciones ficticias.

## 17. COMPATIBILIDAD POR PROVEEDOR

La compatibilidad se determina para una combinación concreta de proveedor, modelo, versión, interfaz, parámetros admitidos, acceso a referencias, capacidades de edición y métodos de evaluación. Estados:

- CONFIRMADA
- PARCIAL
- PENDIENTE
- INCOMPATIBLE

Un adaptador de proveedor traduce el contrato a las operaciones que admite una herramienta determinada. El adaptador no promete capacidades que la herramienta no ofrece y registra los parámetros enviados, los confirmados y los que no pudieron verificarse. La arquitectura puede ser portable aunque algunas funciones no lo sean; la portabilidad conceptual no implica equivalencia técnica entre proveedores.

## 18. REGISTRO ESTRUCTURADO

Cada tarea produce un registro estructurado validable:

```json
{
  "protocol": "IDENTITY-LOCK-v1.6",
  "task_id": "LOCAL_TASK_ID",
  "contract": {
    "identity_reference": "NOT_VERIFIED",
    "protected_features": [],
    "authorized_changes": [],
    "unresolved_conflicts": []
  },
  "execution": {
    "provider": "UNKNOWN",
    "model": "UNKNOWN",
    "version": "NOT_VERIFIED",
    "status": "NOT_VERIFIED",
    "iterations": 0
  },
  "evaluation": {
    "status": "NOT_EVALUATED",
    "dimensions": [],
    "evidence": [],
    "limitations": []
  },
  "risk_budget": {
    "max_iterations": "NOT_SET",
    "max_cost": "NOT_SET",
    "stop_conditions": []
  },
  "decision": {
    "status": "REVIEW_PENDING",
    "reason": "INSUFFICIENT_EVIDENCE"
  }
}
```

Los valores son marcadores ilustrativos, no datos de una ejecución real. La implementación define un esquema formal con campos obligatorios, tipos, enumeraciones, validaciones y reglas de transición. El registro diferencia datos desconocidos, no verificados y no aplicables; ningún estado se representa con valores ambiguos.

## 19. SEGURIDAD Y PRIVACIDAD

La implementación define:

- Permisos de acceso a las imágenes
- Retención y eliminación de archivos
- Protección de referencias originales
- Gestión de credenciales
- Acceso a registros
- Tratamiento de datos sensibles
- Registro de modificaciones
- Versionado de contratos y configuraciones

Las referencias de identidad se tratan como activos potencialmente sensibles. No se envían imágenes a servicios externos sin autorización y compatibilidad con las condiciones aplicables. En modo ventana se asume que todo contenido puede procesarse bajo las políticas del proveedor: esta condición se declara al usuario antes de adjuntar referencias. Ningún registro público incluye imágenes, datos personales ni credenciales. Toda operación de edición preserva la referencia original cuando el flujo lo permite.

## 20. PRUEBAS Y BENCHMARK

Toda versión se somete a pruebas reproducibles. Conjunto mínimo de casos:

- Referencia de identidad ausente
- Cambio de fondo con rasgos protegidos
- Restauración de fotografía deteriorada
- Cambio de vestimenta
- Referencias contradictorias
- Rostro alterado por el generador
- Imagen de baja resolución
- Resultado recibido sin evaluación
- Métrica automatizada no disponible
- Corrección que empeora el resultado
- Límite de iteraciones alcanzado
- Configuración de proveedor incompatible
- Registro incompleto o inválido
- Repetición de una tarea con condiciones equivalentes
- Chatbot que ignora el bloque de instrucciones
- Pérdida de contexto por desbordamiento de la sesión
- Cambio silencioso de modelo por el proveedor

Cada prueba registra: identificador, entradas, versión del protocolo, herramienta y configuración, resultado esperado, resultado observado, evidencia, estado y limitaciones. Estados: SUPERADO, FALLIDO, INCONCLUSO, NO_EJECUTADO.

Comparación experimental, cuando sea posible:

- Prompt convencional
- Prompt con restricciones de identidad
- Protocolo como instrucciones sin motor externo
- Protocolo completo con evaluación y corrección

Se miden fallos, costes, correcciones necesarias y casos de cumplimiento indeterminable. Ninguna mejora se atribuye al protocolo si los datos no permiten distinguir su efecto del producido por el modelo, la referencia o la configuración.

## 21. CRITERIOS DE PARADA

Se detiene la iteración cuando:

- Falte evidencia crítica
- Exista un conflicto sin resolver
- Se alcance el presupuesto establecido
- No se observe mejora demostrable
- Las correcciones introduzcan daños adicionales
- La herramienta no permita controlar el rasgo afectado
- Se requiera modificar una restricción sin autorización
- El resultado no pueda evaluarse de forma suficiente

Detenerse no significa que la imagen sea incorrecta; significa que continuar no está justificado bajo las condiciones actuales.

## 22. VERSIONADO

Toda modificación identifica: requisito original, cambio introducido, justificación, compatibilidad, pruebas afectadas, riesgos de regresión y evidencia de mejora si existe. La etiqueta MEJORADO solo se usa como conclusión experimental con resultados comparativos suficientes; en su ausencia, PROPUESTO o PENDIENTE_DE_VALIDACION. Ninguna versión futura elimina restricciones fundamentales sin documentar expresamente la decisión y sus consecuencias.

## 23. CONDICIONES DE MADUREZ

- IMPLEMENTADO: existe una implementación identificable que cumple contratos, transiciones de estado y validaciones definidas
- PROBADO: las pruebas correspondientes se ejecutaron y sus resultados están registrados
- VALIDADO: la evidencia experimental respalda el comportamiento en un contexto específico
- COMERCIALMENTE PREPARADO: además de funcionar, existen pruebas de utilidad, estimaciones de coste, documentación operativa y propuesta de valor evaluada con usuarios

Estos estados no son intercambiables.

## 24. CRITERIO FINAL

IDENTITY LOCK v1.6 es una arquitectura externa consolidada, adaptada a la única superficie de control que ofrece un chatbot comercial opaco: la conversación. No garantiza identidad exacta ni control interno sobre los generadores. Su valor debe demostrarse con implementación reproducible, pruebas comparativas y resultados medibles.

CONSERVAR LA ARQUITECTURA.
FORMALIZAR LAS RESTRICCIONES.
DECIDIR SEGÚN LA EVIDENCIA.
LIMITAR EL RIESGO Y LA ITERACIÓN.
DOCUMENTAR LA PROCEDENCIA.
OPERAR DENTRO DE LA VENTANA.
VALIDAR ANTES DE PROMETER.
---

## Nota de integración en este repositorio (2026-10-16)

Incorporado por evolución incremental conforme a REJECTED.md R7: documento nuevo en `docs/`,
ningún artefacto existente modificado. Si IDENTITY-LOCK-v1.5.md existe en el historial, queda
preservada (v1.6 la absorbe como arquitectura consolidada, §4); si no llegó a instalarse, v1.6
sola es fiel a la línea v1.4 → v1.5 → v1.6.

Convergencias documentadas: el MODO VENTANA (§14) es el homólogo de identidad visual del anclaje
GOV v1.2 §6 + payload hermético (vigencia / caducidad al perder contexto / degradación declarada
en vez de capacidades simuladas — REJECTED R1/R2 aplicados a imagen). Los 3 casos nuevos del §20
(chatbot ignora bloque / pérdida de contexto / cambio silencioso de modelo) son semillas directas
de casos BB de degradación de anclaje. Backlog: la plantilla §14.2 puede generarse desde
hermetic_payload.py en una próxima iteración. Estado: SPECIFIED — validación experimental pendiente.

— FIN DE IDENTITY LOCK v1.6 —
