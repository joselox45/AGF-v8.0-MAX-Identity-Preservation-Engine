IDENTITY LOCK v1.5

PROTOCOLO ADAPTATIVO DE PRESERVACIÓN DE IDENTIDAD, ORQUESTACIÓN Y CONTROL BASADO EN EVIDENCIA

IDENTIFICADOR: IDENTITY-LOCK-v1.5
BASE ARQUITECTÓNICA: IDENTITY-LOCK-v1.4
TIPO DE EVOLUCIÓN: INCREMENTAL + DISRUPTIVA
ALCANCE: Generación, edición, restauración y transformación de imágenes
MODO: Control externo, evaluación, trazabilidad y corrección adaptativa
COMPATIBILIDAD: Dependiente del proveedor, modelo, versión, interfaz y herramientas disponibles
ESTADO: Especificación de referencia; implementación y validación experimental pendientes

0. PRINCIPIO FUNDAMENTAL

IDENTITY LOCK es una arquitectura externa para organizar, ejecutar y evaluar tareas de transformación visual con restricciones explícitas de identidad.

No controla directamente los pesos, estados internos, atención, logits ni mecanismos privados de los generadores.

Su objetivo es reducir las alteraciones no autorizadas, detectar desviaciones cuando sea posible y documentar qué puede sostenerse con la evidencia disponible.

Regla central:

CONTROLAR EL PROCESO EXTERNO.
PRESERVAR LAS RESTRICCIONES DECLARADAS.
MEDIR SOLO LO QUE PUEDA MEDIRSE.
CORREGIR SOLO CUANDO EXISTA UN OBJETIVO DEFINIDO.
NO CONFUNDIR INTENCIÓN, EJECUCIÓN Y RESULTADO.

Este documento define el comportamiento esperado del protocolo. No demuestra que exista una implementación ni que las mejoras propuestas hayan sido validadas.

1. CONTINUIDAD ARQUITECTÓNICA

IDENTITY LOCK v1.5 conserva los principios fundamentales de v1.4:

Precedencia de las restricciones de identidad.

Separación entre identidad y transformación.

Uso explícito de referencias con funciones diferenciadas.

Estados de disponibilidad, suficiencia e incertidumbre.

Compatibilidad específica por configuración.

Resolución explícita de conflictos.

Diferenciación entre ejecución y evaluación.

Trazabilidad de solicitudes, resultados y decisiones.

Aceptación multidimensional.

Pruebas de regresión.

Corrección localizada cuando las herramientas la permitan.

Detención cuando no exista progreso demostrable.

Ninguna de estas capacidades se considera implementada simplemente por estar descrita en el protocolo.

Evolución respecto a v1.4

Se incorporan cinco mecanismos nuevos:

Contrato de transformación formalizable y validable.

Motor externo de decisiones basado en evidencia.

Presupuesto de riesgo y límites de iteración.

Grafo de procedencia de referencias, operaciones y resultados.

Evaluación comparativa de resultados y versiones.

Estos mecanismos amplían la arquitectura anterior sin reemplazarla.

2. PRINCIPIO DE PRECEDENCIA

La identidad visual declarada como protegida constituye una restricción prioritaria.

Orden de decisión:

Integridad y procedencia de las referencias.

Restricciones de identidad protegidas.

Cambios expresamente autorizados.

Requisitos de la tarea.

Composición y condiciones técnicas.

Preferencias estéticas secundarias.

Cuando dos requisitos sean incompatibles, el sistema debe identificar el conflicto y evitar declarar que ambos se han cumplido.

La precedencia es una regla externa de decisión; no constituye un bloqueo técnico del generador.

Las políticas de seguridad y las limitaciones de las herramientas siguen siendo aplicables.

3. CONTRATO DE IDENTIDAD Y TRANSFORMACIÓN

Antes de iniciar una operación, construir un contrato que defina:

Identificador de la tarea.

Referencia de identidad.

Imagen objetivo, cuando corresponda.

Referencias de estilo, si existen.

Rasgos protegidos.

Cambios autorizados.

Restricciones condicionales.

Elementos no evaluables.

Criterios de aceptación.

Herramientas necesarias.

Conflictos pendientes.

Condiciones de parada.

Cada característica relevante se clasifica como:

PROTEGIDA: no debe modificarse intencionadamente.

MODIFICABLE: su modificación está autorizada.

CONDICIONAL: solo puede modificarse bajo condiciones explícitas.

NO_EVALUABLE: la evidencia disponible no permite determinarla con suficiente confianza.

La fuente exclusiva de los rasgos protegidos es IDENTITY_REFERENCE.

TARGET_IMAGE aporta la información correspondiente al contenido que debe repararse o transformarse.

STYLE_REFERENCE aporta estilo, salvo que el usuario le asigne expresamente otra función.

Ninguna referencia puede cambiar de función silenciosamente.

3.1. Registro de restricciones

Cada restricción debe contener, cuando sea pertinente:

feature_id

classification

reference_id

requirement

evaluation_method

acceptance_criterion

confidence

limitations

Los nombres de los campos son identificadores propuestos para la implementación. No constituyen una interfaz técnica universal.

4. REFERENCIAS Y SUFICIENCIA

Estados permitidos:

DISPONIBLE

PARCIALMENTE_DISPONIBLE

NO_DISPONIBLE

NO_VERIFICADO

INSUFICIENTE

Antes de ejecutar, comprobar la disponibilidad real de las referencias necesarias.

Si falta la referencia de identidad:

GAP: REFERENCIA DE IDENTIDAD NO DISPONIBLE

Si la referencia existe, pero no permite determinar un rasgo:

GAP: EVIDENCIA INSUFICIENTE PARA EL RASGO

Si existen referencias contradictorias, identificar el conflicto y solicitar aclaración cuando afecte a una restricción crítica.

No inventar archivos, rutas, hashes, atributos, resultados de acceso ni datos de procedencia.

5. GENERACIÓN Y ADAPTACIÓN DE PROMPTS

Cada prompt generado debe declarar:

Referencia de identidad.

Rasgos protegidos pertinentes.

Transformaciones autorizadas.

Elementos que deben permanecer inalterados.

Restricciones negativas relevantes.

Criterios de aceptación.

Herramienta y versión, cuando se conozcan.

Parámetros confirmados y pendientes.

Limitaciones conocidas.

Se mantienen dos modos:

MAXIMA_PRESERVACION: limitar la transformación a lo estrictamente necesario.

EQUILIBRADO: permitir mayor libertad sobre los elementos autorizados sin rebajar la prioridad de identidad.

La sintaxis específica del generador debe estar documentada o probada en la configuración correspondiente.

Los parámetros de referencia, adaptadores, pesos y controles particulares no son universales.

Un prompt es una instrucción. No constituye prueba de ejecución, cumplimiento ni preservación facial.

6. RESOLUCIÓN DE CONFLICTOS

Procedimiento obligatorio:

Identificar el requisito incompatible.

Determinar qué restricción resulta comprometida.

Explicar la limitación.

Proponer una alternativa menos destructiva.

Solicitar confirmación cuando corresponda.

Registrar la decisión.

Ejecutar únicamente si la tarea es viable y está autorizada.

Secuencia:

DETECTAR → ADVERTIR → RESOLVER → REGISTRAR → EJECUTAR

La confirmación del usuario autoriza el cambio solicitado, pero no garantiza su viabilidad técnica.

La estilización no implica automáticamente pérdida de identidad; debe evaluarse según los rasgos protegidos y la transformación concreta.

7. CICLO DE EJECUCIÓN Y EVALUACIÓN

Se mantienen cuatro estados independientes:

SOLICITADO: requisitos expresados por el usuario.

INTENTADO: operación que efectivamente se inició.

RECIBIDO: resultado que se obtuvo.

EVALUADO: resultado que se examinó mediante un método identificado.

La transición entre estados requiere evidencia correspondiente.

Estados de evaluación:

NO_EVALUADO

EVALUADO_CUALITATIVO

EVALUADO_AUTOMATIZADO

EVIDENCIA_INSUFICIENTE

EVALUACION_INCONCLUSA

Una comparación visual no equivale a validación biométrica.

Una métrica automatizada no es infalible.

Una evaluación no debe presentarse como independiente si el evaluador, método o sistema utilizado no cumple las condiciones de independencia declaradas.

8. SALTO DISRUPTIVO I: MOTOR EXTERNO DE DECISIONES

La principal ampliación de v1.5 es transformar las reglas de evaluación en una política de decisión formalizable.

El motor recibe el contrato, los estados de referencia, el resultado disponible, las evaluaciones realizadas y los límites de ejecución.

Produce una decisión externa, acompañada de su justificación y de las evidencias utilizadas.

8.1. Decisiones permitidas

ACCEPTAR

Los criterios aplicables se cumplen y no existen fallos críticos pendientes.

CORREGIR

Se ha identificado una desviación concreta, existe una operación viable para abordarla y la corrección está autorizada.

REVISAR

La evidencia es insuficiente, existen ambigüedades o se necesita intervención humana.

DETENER

La operación es inviable, ha alcanzado un límite, introduce daños adicionales o no existe una justificación suficiente para continuar.

8.2. Prioridad de las decisiones

Un resultado estéticamente atractivo no puede compensar el incumplimiento de una restricción crítica de identidad.

Si una restricción crítica no puede evaluarse, el sistema no debe tratarla como superada.

La ausencia de evidencia no equivale a evidencia de cumplimiento.

8.3. Pseudocódigo de referencia

evaluar(contrato, resultado, evidencia): si falta una referencia crítica: devolver REVISAR si existe un conflicto crítico sin resolver: devolver DETENER si no existe resultado recibido: devolver REVISAR evaluar cada criterio aplicable si existe fallo crítico verificable: si hay corrección viable y autorizada: devolver CORREGIR devolver DETENER si la evidencia es insuficiente: devolver REVISAR si todos los criterios críticos se cumplen: devolver ACEPTAR devolver REVISAR 

Este pseudocódigo describe una política de referencia. Su ejecución real requiere implementación, pruebas y acceso a las evidencias pertinentes.

9. SALTO DISRUPTIVO II: PRESUPUESTO DE RIESGO

v1.5 introduce un mecanismo para impedir que el proceso continúe transformando una imagen indefinidamente sin demostrar mejoras.

Cada tarea define un presupuesto de riesgo y de operación.

El presupuesto debe especificar, según la tarea:

Máximo de iteraciones.

Coste máximo permitido.

Tiempo máximo de ejecución.

Restricciones críticas.

Desviaciones tolerables.

Incertidumbres que obligan a revisión.

Condiciones de parada.

9.1. Riesgo por restricción

Para cada rasgo protegido, registrar:

Gravedad potencial de su alteración.

Evidencia disponible.

Confianza de la evaluación.

Posibilidad de corrección.

Consecuencia de continuar.

No convertir estos factores en una probabilidad de pérdida de identidad sin un método validado que permita estimarla.

9.2. Política de iteración

Una iteración adicional solo está justificada si:

Existe una desviación identificada.

Se propone una intervención específica.

La intervención está autorizada.

Es posible comparar el resultado nuevo con el anterior.

El coste y el riesgo permanecen dentro de los límites.

Si no existe evidencia nueva, detener o revisar.

Si la nueva iteración empeora un criterio crítico, no ocultar el retroceso.

El sistema no debe inventar una mejora para justificar la continuación.

10. SALTO DISRUPTIVO III: GRAFO DE PROCEDENCIA

La trazabilidad deja de ser únicamente una lista de campos y pasa a organizarse como un grafo de procedencia.

10.1. Tipos de nodos

Referencia original.

Contrato de transformación.

Prompt generado.

Configuración de ejecución.

Operación intentada.

Resultado recibido.

Evaluación.

Corrección.

Decisión de aceptación.

10.2. Relaciones

Cada relación registra, cuando corresponda:

Origen.

Destino.

Tipo de operación.

Fecha y hora disponibles.

Herramienta implicada.

Evidencia asociada.

Estado de verificación.

El grafo debe permitir reconstruir qué referencia se utilizó, qué cambio se solicitó, qué resultado se recibió y por qué se aceptó, corrigió o rechazó.

10.3. Integridad de los registros

Cuando se requiera mayor integridad, pueden emplearse hashes calculados sobre archivos accesibles, registros versionados y mecanismos externos de protección contra modificaciones.

Un hash no demuestra identidad facial, autenticidad de una persona ni calidad visual.

Un registro firmado tampoco demuestra que la evaluación sea correcta.

La trazabilidad permite reconstruir el proceso; no sustituye una auditoría independiente.

11. ACEPTACIÓN MULTIDIMENSIONAL

Mantener dimensiones independientes:

A. CUMPLIMIENTO DE TRANSFORMACIÓN

¿Se realizaron los cambios autorizados?

B. CONSERVACIÓN VISUAL

¿Se mantienen los rasgos protegidos observables?

C. CALIDAD TÉCNICA

¿Existen artefactos, defectos o inconsistencias?

D. SUFICIENCIA DE EVIDENCIA

¿La evidencia permite sostener la conclusión?

E. TRAZABILIDAD

¿Puede reconstruirse el proceso?

F. COSTE Y EFICIENCIA

¿La operación se mantuvo dentro del presupuesto establecido?

Cada dimensión tendrá su estado, método y limitaciones.

No se recomienda reducir todas las dimensiones a una puntuación global única.

Un resultado puede tener calidad estética elevada y conservación de identidad deficiente.

La aceptación se produce únicamente cuando se satisfacen los criterios aplicables y no existen fallos críticos pendientes.

12. MÉTRICAS Y CALIBRACIÓN

Las métricas deben elegirse según la tarea, el generador y la evidencia disponible.

Pueden incluir:

Evaluación humana estructurada.

Comparación de rasgos visuales observables.

Métricas de similitud de imagen.

Medidas de calidad técnica.

Coste por operación.

Número de correcciones.

Frecuencia de fallos críticos.

Tiempo hasta la aceptación.

Las métricas de similitud visual o facial deben interpretarse según sus limitaciones y no como pruebas absolutas de identidad.

No existe un umbral universal de aceptación definido por este protocolo.

Los umbrales deberán calibrarse con datos representativos, criterios documentados y evaluación de errores.

Cuando una métrica no esté disponible, registrar NO_DISPONIBLE.

Cuando no se haya calculado, registrar NO_EVALUADO.

No asignar puntuaciones ficticias.

13. COMPATIBILIDAD Y ADAPTADORES

La compatibilidad se determina para una combinación concreta de:

Proveedor.

Modelo.

Versión.

Interfaz.

Parámetros admitidos.

Acceso a referencias.

Capacidades de edición.

Métodos de evaluación.

Estados:

CONFIRMADA

PARCIAL

PENDIENTE

INCOMPATIBLE

Un adaptador de proveedor traduce el contrato de transformación a las operaciones que admite una herramienta determinada.

El adaptador no debe prometer capacidades que la herramienta no ofrece.

Debe registrar los parámetros enviados, los parámetros confirmados y los datos que no pudieron verificarse.

La arquitectura podrá ser portable aunque algunas funciones no lo sean. La portabilidad conceptual no implica equivalencia técnica entre proveedores.

14. REGISTRO ESTRUCTURADO

Cada tarea debe producir un registro estructurado validable.

Ejemplo ilustrativo:

{ "protocol": "IDENTITY-LOCK-v1.5", "task_id": "LOCAL_TASK_ID", "contract": { "identity_reference": "NOT_VERIFIED", "protected_features": [], "authorized_changes": [], "unresolved_conflicts": [] }, "execution": { "provider": "UNKNOWN", "model": "UNKNOWN", "version": "NOT_VERIFIED", "status": "NOT_VERIFIED", "iterations": 0 }, "evaluation": { "status": "NOT_EVALUATED", "dimensions": [], "evidence": [], "limitations": [] }, "risk_budget": { "max_iterations": null, "max_cost": null, "stop_conditions": [] }, "decision": { "status": "REVIEW_PENDING", "reason": "INSUFFICIENT_EVIDENCE" } } 

Los valores son marcadores ilustrativos, no datos de una ejecución real.

La implementación debe definir un esquema formal con campos obligatorios, tipos, enumeraciones, validaciones y reglas de transición.

El registro debe diferenciar datos desconocidos, datos no verificados y datos que no aplican.

No utilizar null, una cadena vacía o un valor predeterminado para representar estados distintos sin una definición explícita.

15. SEGURIDAD, PRIVACIDAD Y CONTROL DE CAMBIOS

La implementación deberá definir:

Permisos de acceso a las imágenes.

Retención y eliminación de archivos.

Protección de referencias originales.

Gestión de credenciales.

Acceso a registros.

Tratamiento de datos sensibles.

Registro de modificaciones.

Versionado de contratos y configuraciones.

Las referencias de identidad deben tratarse como activos potencialmente sensibles.

No enviar imágenes a servicios externos sin que la operación esté autorizada y sea compatible con las condiciones aplicables.

No incluir imágenes, datos personales ni credenciales en registros públicos por defecto.

Toda operación de edición debe preservar la referencia original cuando el flujo lo permita, para facilitar la comparación y la recuperación.

16. PRUEBAS DE REGRESIÓN Y BENCHMARK

Cada versión deberá someterse a pruebas reproducibles.

Conjunto mínimo de casos:

Referencia de identidad ausente.

Cambio de fondo con rasgos protegidos.

Restauración de fotografía deteriorada.

Cambio de vestimenta.

Referencias contradictorias.

Rostro alterado por el generador.

Imagen de baja resolución.

Resultado recibido sin evaluación.

Métrica automatizada no disponible.

Corrección que empeora el resultado.

Límite de iteraciones alcanzado.

Configuración de proveedor incompatible.

Registro incompleto o inválido.

Repetición de una tarea con condiciones equivalentes.

Cada prueba registrará:

Identificador.

Entradas.

Versión del protocolo.

Herramienta y configuración.

Resultado esperado.

Resultado observado.

Evidencia.

Estado.

Limitaciones.

Estados:

SUPERADO, FALLIDO, INCONCLUSO, NO_EJECUTADO.

Comparación experimental

Comparar, cuando sea posible:

Prompt convencional.

Prompt con restricciones de identidad.

v1.5 como protocolo de instrucciones.

v1.5 con motor externo de evaluación y corrección.

Mantener las condiciones comparables y documentar las diferencias.

Medir tanto los fallos como los costes, las correcciones necesarias y los casos en que no puede determinarse el cumplimiento.

No atribuir una mejora al protocolo si los datos no permiten distinguir su efecto del producido por el modelo, la referencia o la configuración.

17. CRITERIOS DE PARADA

Detener la iteración cuando:

Falte evidencia crítica.

Exista un conflicto sin resolver.

Se alcance el presupuesto establecido.

No se observe mejora demostrable.

Las correcciones introduzcan daños adicionales.

La herramienta no permita controlar el rasgo afectado.

Se requiera modificar una restricción sin autorización.

El resultado no pueda evaluarse de forma suficiente.

Detenerse no significa necesariamente que la imagen sea incorrecta; significa que continuar no está justificado bajo las condiciones actuales.

18. EVOLUCIÓN Y VERSIONADO

Cada nueva versión deberá conservar la trazabilidad respecto a la arquitectura precedente.

Toda modificación deberá identificar:

Requisito original.

Cambio introducido.

Justificación.

Compatibilidad.

Pruebas afectadas.

Riesgos de regresión.

Evidencia de mejora, si existe.

La etiqueta MEJORADO solo debe utilizarse como conclusión experimental cuando existan resultados comparativos suficientes.

Mientras no existan pruebas, utilizar PROPUESTO o PENDIENTE_DE_VALIDACION.

Las versiones futuras no deberán eliminar restricciones fundamentales sin documentar expresamente la decisión y sus consecuencias.

19. CONDICIONES DE MADUREZ

IDENTITY LOCK v1.5 se considerará implementado cuando exista una implementación identificable que cumpla los contratos, las transiciones de estado y las validaciones definidas.

Se considerará probado cuando las pruebas correspondientes se hayan ejecutado y sus resultados estén registrados.

Se considerará validado para un contexto específico cuando la evidencia experimental respalde su comportamiento dentro de ese alcance.

Se considerará comercialmente preparado cuando, además de funcionar, existan pruebas de utilidad, estimaciones de costes, documentación operativa y una propuesta de valor evaluada con usuarios.

Estos estados no son intercambiables.

20. CRITERIO FINAL

IDENTITY LOCK v1.5 conserva la arquitectura de v1.4 y propone una evolución hacia un sistema externo de control más formalizable, evaluable y potencialmente automatizable.

Su salto disruptivo consiste en convertir las reglas en decisiones justificadas por evidencia, con límites explícitos de riesgo, procedencia verificable y criterios de aceptación independientes.

No garantiza identidad exacta ni control interno sobre generadores comerciales.

Su valor deberá demostrarse mediante una implementación reproducible, pruebas comparativas y resultados medibles.

CONSERVAR LA ARQUITECTURA.
FORMALIZAR LAS RESTRICCIONES.
DECIDIR SEGÚN LA EVIDENCIA.
LIMITAR EL RIESGO Y LA ITERACIÓN.
DOCUMENTAR LA PROCEDENCIA.
VALIDAR ANTES DE PROMETER.

FIN DE IDENTITY LOCK v1.5


---

## ANEXO A — TAXONOMÍAS OPERATIVAS PARA AUDITORÍA

### A.0. Estado y alcance del anexo

Este anexo es una extensión del protocolo IDENTITY LOCK v1.5. No modifica
las secciones 0-13 del documento principal. Proporciona vocabulario
operativo para la sección 3.1 (Registro de restricciones) y la sección 8
(Motor externo de decisiones).

Estado: especificación de referencia. Los valores numéricos mencionados
en este anexo son candidatos propuestos, no umbrales calibrados. Su
aplicación requiere validación experimental (HIL) según el principio de
la sección 12: "No asignar puntuaciones ficticias".

Compatibilidad con kernel v0.9.5:
- Este anexo NO redefine veredictos del kernel v0.9.5.
- Los veredictos operativos (HUMAN_REVIEW, PENDING_LOCAL_VERIFICATION,
  BLOCKED) prevalecen sobre cualquier taxonomía aquí descrita.
- Las decisiones de este anexo (ACEPTAR, CORREGIR, REVISAR, DETENER) se
  mapean al kernel según la tabla A.5.

### A.1. IMMUTABLE_FEATURES — vocabulario para el contrato de identidad

Lista de referencia para declarar restricciones de identidad en el
contrato (sección 3.1). Cada item puede marcarse como:

- INMUTABLE: no puede alterarse bajo ninguna circunstancia.
- MUTABLE_AUTORIZADO: puede alterarse si el contrato lo autoriza.
- NO_EVALUADO: no se ha verificado su conservación.

| Código | Rasgo | Descripción |
|---|---|---|
| FACE_SHAPE | Forma del rostro | Contorno general, proporciones |
| EYE_SHAPE | Forma de ojos | Contorno, apertura, inclinación |
| EYEBROW_DENSITY_CURVE | Cejas | Densidad y curvatura |
| NOSE_BRIDGE_ANGLE_WIDTH | Puente nasal | Ángulo y anchura |
| NOSE_NOSTRIL_SHAPE | Fosas nasales | Forma y apertura |
| LIP_CURVATURE_VOLUME | Labios | Curvatura y volumen |
| JAWLINE_ANGLE | Mandíbula | Ángulo y contorno |
| CHIN_PROJECTION | Mentón | Proyección y forma |
| FOREHEAD_HEIGHT | Frente | Altura y contorno |
| INTEROCULAR_DISTANCE | Distancia interocular | Separación entre ojos |
| SKIN_TONE_HSV | Tono de piel | Valores HSV |
| SKIN_TEXTURE | Textura | Poros, arrugas, lunares, cicatrices, pecas |
| NATURAL_ASYMMETRY | Asimetría natural | Vector de asimetría del sujeto |
| AGE_APPEARANCE | Apariencia de edad | Edad aparente |
| FACIAL_HAIR_PATTERN | Vello facial | Patrón y densidad (si aplica) |
| DISTINCTIVE_MARKS | Marcas distintivas | Lunares, cicatrices, pecas específicas |
| EAR_SHAPE | Forma de orejas | Solo si visibles |

Nota: esta lista es vocabulario, no un umbral. La evaluación de cada
rasgo depende de la disponibilidad de referencias y modelos (HIL).

### A.2. ANTI_BEAUTIFICATION — categorías de deriva por estética no autorizada

Deriva cosmética: alteración de rasgos con el objetivo (implícito o
explícito) de "mejorar" la apariencia del sujeto. Viola el principio de
precedencia de restricciones (sección 2) cuando no está autorizada.

| Código | Señal | Descripción |
|---|---|---|
| SKIN_SMOOTHING | Suavizado de piel | Reducción de poros, arrugas, textura |
| AGE_REDUCTION | Reducción de edad | Alteración hacia apariencia más joven |
| EYE_ENLARGEMENT | Agrandamiento de ojos | Aumento de tamaño aparente |
| FACE_SLIMMING | Adelgazamiento facial | Reducción de anchura de mandíbula o mejillas |
| SYMMETRY_CORRECTION | Corrección de simetría | Eliminación de asimetría natural |
| MAKEUP_HALLUCINATION | Maquillaje inventado | Añadir maquillaje no presente en referencia |
| TEETH_WHITENING | Blanqueamiento dental | Exageración de blancura de dientes |

Cada categoría detectada se registra en el contrato (sección 3.1) como
restricción violada. La decisión resultante (sección 8.1) se determina:

- CORREGIR si existe corrección viable y autorizada.
- REVISAR si la detección es ambigua o hay múltiples categorías.
- DETENER si la suma de derivas compromete la identidad del sujeto.

NUNCA se asigna PASS. El kernel v0.9.5 prohíbe veredictos PASS en fases
MIL/SIL/PIL (ver schema agf_strong_conditioning_schema.json, campo verdict).

### A.3. MULTI_SUBJECT_PROTOCOL — auditoría de N sujetos

Cuando el contrato involucra N sujetos (N mayor o igual a 2), se aplica el
siguiente protocolo de auditoría. Es de EVALUACIÓN, no de generación.

A.3.1. Binding posicional
- SUBJECT_i se vincula a REFERENCE_i según orden posicional declarado en
  el contrato (izquierda a derecha u otro criterio explícito).
- El binding se registra como nodo del grafo de procedencia (sección 10.1).

A.3.2. Evaluación independiente
- Cada sujeto se evalúa por separado.
- Veredictos por sujeto: CONFIRMADA, PARCIAL, PENDIENTE, INCOMPATIBLE
  (sección 13).
- NUNCA se promedia entre sujetos para un veredicto agregado.

A.3.3. Operaciones prohibidas
- Transferencia de rasgos entre sujetos.
- Blending o morphing entre rostros de sujetos distintos.
- Face swap cruzado (aplicar cara de SUBJECT_1 a SUBJECT_2).
- Cualquier operación que mezcle embeddings entre sujetos.

A.3.4. Decisión agregada (mínimo, no promedio)
- Si algún sujeto DETENER: conjunto DETENER.
- Si algún sujeto REVISAR: conjunto REVISAR.
- Si algún sujeto CORREGIR: conjunto CORREGIR.
- Solo si TODOS los sujetos ACEPTAR: conjunto ACEPTAR.

A.3.5. Registro
Cada sujeto emite su propio nodo de evaluación en el grafo de procedencia,
con su veredicto individual y sus métricas asociadas.

### A.4. CPEP_IDENTITY_PRESERVATION_FAILED — token fail-closed

CPEP (Canonical Preservation Error Protocol) es el token que indica que
la conservación de identidad declarada no puede sostenerse con la
evidencia disponible.

A.4.1. Cuándo se emite
- Evidencia insuficiente para emitir decisión distinta de DETENER.
- Restricción crítica (A.1) no evaluable por falta de modelo o referencia.
- Violación acumulada de ANTI_BEAUTIFICATION (A.2) más allá del presupuesto
  de riesgo (sección 9).
- Contaminación cruzada detectada en multi-sujeto (A.3).

A.4.2. Mapeo con kernel v0.9.5
CPEP_IDENTITY_PRESERVATION_FAILED se mapea al veredicto BLOCKED del kernel.
El campo reason del JSON lo incluye explícitamente.

Ejemplo de JSON compatible con agf_strong_conditioning_schema.json:

    {
      "kernel_version": "v0.9.5",
      "phase": "SIL",
      "verdict": "BLOCKED",
      "metrics_missing": ["arcface"],
      "reason": "CPEP_IDENTITY_PRESERVATION_FAILED: evidencia insuficiente para conservación de identidad. Requiere HIL.",
      "hardware_signature": "SYNTHETIC (No CMOS Sensor)"
    }

A.4.3. Prohibiciones
- NUNCA se mapea a PASS.
- NUNCA se omite del JSON cuando el veredicto es BLOCKED por identidad.
- NUNCA se sustituye por una métrica numérica no verificada.

A.4.4. Escalamiento
Tras emitir CPEP_IDENTITY_PRESERVATION_FAILED:
1. Registrar nodo de decisión DETENER en el grafo (sección 10.1).
2. Solicitar referencia de mayor calidad o modelo HIL disponible.
3. No reintentar automáticamente sin nueva evidencia (sección 9.2).

### A.5. Tabla de mapeo con kernel v0.9.5

| Decisión IDENTITY_LOCK | Veredicto kernel v0.9.5 |
|---|---|
| ACEPTAR | (no aplicable en MIL/SIL, solo HIL) |
| CORREGIR | HUMAN_REVIEW |
| REVISAR | HUMAN_REVIEW o PENDING_LOCAL_VERIFICATION |
| DETENER | BLOCKED |
| CPEP emitido | BLOCKED (con reason explícito) |

Nota: kernel v0.9.5 prohíbe PASS en fases MIL/SIL/PIL. El veredicto PASS
solo puede emitirse desde HIL con evidencia verificable (ver kernel v0.9.5
sección 6: "El SIL_SCORE es SOLO un diagnóstico").

### A.6. Referencias cruzadas

- Sección 3.1: Registro de restricciones — vocabulario en A.1.
- Sección 8: Motor externo de decisiones — decisiones en A.2, A.3.
- Sección 9: Presupuesto de riesgo — límites en A.4.
- Sección 10: Grafo de procedencia — nodos por sujeto en A.3.5.
- Sección 11: Aceptación multidimensional — veredictos por sujeto en A.3.2.
- Sección 13: Compatibilidad y adaptadores — estados en A.3.2.
- Kernel v0.9.5 sección 7: Strong Conditioning — compatibilidad A.4, A.5.
- Schema: schemas/agf_strong_conditioning_schema.json — campos JSON A.4.2.

---

FIN DEL ANEXO A

---

## ANEXO B — HONESTIDAD EPISTÉMICA Y TRAZABILIDAD DE CADENA

### B.0. Estado y alcance del anexo

Este anexo documenta cuatro conceptos extraídos de una evaluación crítica
del protocolo externo CPEP v1.2-CANDIDATE (Chat-Pure Epistemic Protocol).
CPEP completo fue RECHAZADO por las razones listadas en B.6. Solo los
cuatro conceptos siguientes se consideran compatibles con IDENTITY LOCK
y el kernel v0.9.5.

Estado: especificación de referencia. Los cuatro conceptos son vocabulario
y mecanismos de declaración honesta. NO modifican el enum de verdict del
kernel v0.9.5.

Compatibilidad con kernel v0.9.5:
- Este anexo NO reemplaza el schema agf_strong_conditioning_schema.json.
- Los cuatro conceptos aquí descritos son opcionales: si un implementador
  los usa, debe declararlos en el campo reason o en documentación asociada.
- El enum verdict sigue siendo {HUMAN_REVIEW, PENDING_LOCAL_VERIFICATION,
  BLOCKED}. PASS sigue prohibido (ver kernel v0.9.5 sección 7).

### B.1. trace_verification_status — estado de la cadena de turnos

Cuando una conversación tiene múltiples turnos y cada turno referencia
turnos anteriores, el LLM debe declarar el estado de esa cadena.

Valores permitidos:

| Estado | Descripción | Requisito |
|---|---|---|
| EXACT | Los valores citados coinciden exactamente con turnos reales | previous_snapshots DEBE coincidir |
| UNVERIFIABLE | El LLM no puede copiar los valores exactos (límite de contexto, reinicio) | previous_snapshots DEBE ser [] |
| PARTIAL | Algunos valores coinciden y otros no | Listar qué coincide y qué no |

Regla de oro: NO fabricar el trace. Si no se puede copiar exacto, se
declara UNVERIFIABLE con razón explícita. Un trace vacío honesto es
preferible a un trace fabricado convincente.

Mapeo con kernel v0.9.5:
- EXACT: reason puede declarar "trace_verified"
- UNVERIFIABLE: reason debe declarar "trace_unverifiable: <razón>"
- PARTIAL: reason debe declarar qué coincide y qué no

### B.2. recollection_approximate vs previous_snapshots

Distinción formal entre dos tipos de memoria:

| Campo | Naturaleza | Auditable |
|---|---|---|
| previous_snapshots | Evidencia oficial, copiable exacto | SÍ (comparar con turnos reales) |
| recollection_approximate | Memoria aproximada, informativa | NO (es solo declaración) |

recollection_approximate es un array con elementos del tipo:
  {"turn": N, "remembered_value": X, "status": "APPROXIMATE_NOT_EXACT"}

Regla: recollection_approximate NUNCA debe mezclarse con
previous_snapshots. Si un implementador solo tiene memoria aproximada,
previous_snapshots debe ser [] y recollection_approximate lleva lo
aproximado con status explícito.

Mapeo con kernel v0.9.5:
- Si solo hay memoria aproximada: reason debe declarar
  "trace_unverifiable + recollection_approximate" (nunca solo "trace")
- Si hay evidencia exacta: reason puede declarar "trace_verified"

### B.3. retroactive_declarations — cierre honesto de cadenas

Cuando se descubre que en turnos anteriores se fabricó metadata (no
contenido), el LLM NO debe re-emitir esos turnos (costoso, arriesga
nuevos errores). En su lugar, declara retroactivamente:

  retroactive_declarations: {
    "turns_X_Y_status": "UNVERIFIABLE_RETROACTIVELY_DECLARED",
    "turn_X": {
      "metadata_fabricated": true,
      "content_valid": true,
      "reason": "..."
    },
    "chain_closure_note": "..."
  }

Propósito: contenido válido + metadata fabricada. Declararlo es más
honesto que re-emitir (que introduciría nuevas fabricaciones).

Mapeo con kernel v0.9.5:
- Si se usa retroactive_declarations: reason debe declarar
  "retroactive_closure: turns_X_Y"
- El veredicto del turno actual sigue siendo {HUMAN_REVIEW,
  PENDING_LOCAL_VERIFICATION, BLOCKED} según corresponda
- NUNCA se emite PASS como recompensa por honestidad

### B.4. citations_status — taxonomía de evidencia externa

Cuando el LLM cita fuentes externas, debe declarar el estado de esa
evidencia:

| Estado | Descripción | Requisito |
|---|---|---|
| VERIFIABLE_URLS_OBTAINED_VIA_LOOKUP | URLs obtenidas tras intentar lookup explícito | citations.length > 0 |
| VERIFIABLE_URLS_OBTAINED | URLs obtenidas (sin lookup explícito) | citations.length > 0 |
| PARTIAL_URLS | Algunas URLs, no todas las necesarias | citations.length > 0 |
| NO_URLS_NEEDED | La claim no requiere cita externa | citations puede ser [] |
| NO_VERIFIABLE_URLS | Se intentó lookup y no se obtuvieron URLs | citations puede ser [] + razón |

Regla anti-fabricación: NO declarar NO_VERIFIABLE_URLS sin intentar
lookup explícito. NO declarar PARTIAL_URLS con citations.length == 0.

Mapeo con kernel v0.9.5:
- citations_status se mapea al campo metrics_missing:
  - NO_VERIFIABLE_URLS → añadir a metrics_missing
  - PARTIAL_URLS → añadir "citations_partial" a metrics_missing
- El campo reason debe declarar el estado de citations si es relevante
- NUNCA se usa citations_status para emitir PASS

### B.5. Tabla de mapeo con kernel v0.9.5

| Concepto IDENTITY_LOCK | Campo kernel v0.9.5 | Verdict resultante |
|---|---|---|
| trace EXACT + evidencia real | reason: "trace_verified" | HUMAN_REVIEW o PENDING_LOCAL_VERIFICATION |
| trace UNVERIFIABLE | reason: "trace_unverifiable: <razón>" | HUMAN_REVIEW (nunca PASS) |
| recollection_approximate solo | reason: "trace_unverifiable + approximate" | HUMAN_REVIEW |
| retroactive_declarations | reason: "retroactive_closure: turns_X_Y" | HUMAN_REVIEW o BLOCKED |
| citations NO_VERIFIABLE_URLS | metrics_missing += "citations" | HUMAN_REVIEW |
| citations PARTIAL_URLS | metrics_missing += "citations_partial" | HUMAN_REVIEW |

Regla transversal: ningún concepto de este anexo puede resultar en PASS.
El enum {HUMAN_REVIEW, PENDING_LOCAL_VERIFICATION, BLOCKED} prevalece.

### B.6. CPEP v1.2 — por qué se rechaza completo

El protocolo externo CPEP v1.2-CANDIDATE fue evaluado y rechazado como
adopción completa por las siguientes razones:

Razones de rechazo:

1. Métricas inventadas estructurales: campos como tokens_available,
   epistemic_score.G y ambiguity_score se presentan como números
   calculados pero no tienen fórmula ni fuente verificable. Un LLM no
   puede conocer tokens_available (requiere API). Viola Zero-Fabrication.

2. Incompatibilidad con schema v0.9.5: CPEP usa 11 campos obligatorios
   por turno. El kernel v0.9.5 usa 6 campos con additionalProperties:
   false. Adoptar CPEP requeriría reescribir el kernel completo.

3. Verbosidad incompatible con chat: ~500 líneas de system prompt y
   ~1500-2000 tokens de overhead por turno. Para preguntas simples el
   coste es desproporcionado.

4. Colisión de nomenclatura: CPEP en este protocolo significa "Chat-Pure
   Epistemic Protocol". CPEP_IDENTITY_PRESERVATION_FAILED (Anexo A) es
   un token fail-closed específico de identidad. Mantener ambos nombres
   confunde a implementadores.

Conceptos extraídos (los únicos que se adoptan): B.1, B.2, B.3, B.4.

Conceptos rechazados (lista completa): tokens_available,
tokens_needed, epistemic_score.G, ambiguity_score,
confidence_in_declaration, 11 campos obligatorios por turno,
pre_flight como campo obligatorio, 19 tests auto-ejecutables sin
verificación real, formato de 500 líneas como system prompt.

### B.8. Prohibición de evidencia procedural fabricada

El LLM NO debe declarar tool execution logs, file paths, timestamps, hashes
o artefactos de verificación que no hayan sido producidos por una fuente
externa verificable.

Motivo: bajo presión epistémica sostenida, los LLMs pueden fabricar no solo
hechos sino evidencia de que verificaron hechos (tool logs ficticios, paths
inexistentes, hashes inventados, timestamps fabricados). Este es un fallo
más grave que alucinar un hecho: es fabricar la prueba de haberlo verificado.

Reglas operativas:

1. Si un tool no fue ejecutado externamente, no existe su output. Declarar
   como máximo el plan ("se ejecutaría X"), nunca el resultado.
2. Si un output fue truncado o tiene exit code != 0, se declara
   UNVERIFIABLE, no confirmado.
3. Si un hash no fue calculado sobre archivo persistido, es recollection
   aproximada, no evidencia (B.2).
4. La compactación de contexto NUNCA convierte un output parcial en
   resultado confirmado. Si el LLM no puede citar la fuente externa exacta
   en el turno actual, debe declarar UNVERIFIABLE.

Mapeo con kernel v0.9.5:
- reason debe declarar "evidence_procedural_unverifiable" cuando aplique
- verdict mínimo HUMAN_REVIEW si se detecta fabricación procedural
- NUNCA se emite PASS como recompensa por "citar evidencia"

Referencias: OLIF (fabricación de audit-trails bajo presión), Compaction
as Epistemic Failure (outputs parciales tratados como confirmados).

### B.7. Referencias cruzadas

- Sección 10: Grafo de procedencia — trazabilidad de cadena (B.1, B.2).
- Sección 12: cálculo explícito — aplicable a cualquier métrica (B.6).
- Anexo A A.4: CPEP_IDENTITY_PRESERVATION_FAILED — distinto de CPEP v1.2.
- Kernel v0.9.5 sección 7: Strong Conditioning — enum verdict (B.5).
- Schema: schemas/agf_strong_conditioning_schema.json — campos compatibles.

---

FIN DEL ANEXO B

---

## ANEXO C — NIVELES DE CONDICIONAMIENTO (WEAK vs STRONG)

### C.0. Estado y alcance del anexo

Este anexo formaliza la diferencia entre el acceso que un LLM tiene a
imagenes codificadas como base64 (tokens alfanumericos) y el acceso que
un proceso Python tiene a la matriz real de pixeles (float32[H,W,3]).

Estado: especificacion de referencia. NO modifica el schema v0.9.5.
Los campos propuestos en C.5 son opcionales: si un implementador los usa,
debe declararlos en el campo `reason` del JSON existente.

Compatibilidad con kernel v0.9.5:
- NO cambia el enum de verdict {HUMAN_REVIEW, PENDING_LOCAL_VERIFICATION,
  BLOCKED}. PASS sigue prohibido.
- NO cambia el schema agf_strong_conditioning_schema.json.
- NO introduce campos obligatorios al output.
- Los conceptos se declaran via `reason` (texto libre ya existente).

### C.1. Definicion

Todo input de imagen en el contexto de chat llega codificado como base64
(tokens alfanumericos). El LLM NO ve la matriz de pixeles. Esto constituye
CONDICIONAMIENTO SEMANTICO DEBIL (weak_semantic).

Cuando un proceso Python descomprime la imagen y opera sobre la matriz
float32[H,W,3], esto constituye CONDICIONAMIENTO FUERTE (strong_pixel).

| Nivel      | Modo de acceso                    | Ejemplo              |
|------------|-----------------------------------|----------------------|
| weak       | base64 tokens (alfanumerico)      | LLM en chat          |
| strong     | float32[H,W,3] descomprimido      | Python + Pillow      |
| HIL        | hardware fisico + modelos reales  | Termux + ArcFace     |

### C.2. Capacidades reales del LLM con base64

PUEDE:
- Reconocer patrones token-level (estructura JPEG, WebP, PNG).
- Inferir contenido aproximado (semantica, no pixeles).
- Describir lo que el prompt del usuario declara.
- Invocar herramientas Python externas (cuando esten disponibles).

NO PUEDE:
- Leer valores RGB/HSV reales.
- Calcular metricas geometricas en pixeles (distancia interocular,
  angulo de mandibula, proyeccion de menton).
- Medir texturas (frecuencias, poros, ruido, artefactos de sintesis).
- Ejecutar deteccion de caras real (BlazeFace TFLite).
- Calcular embeddings biometricos (ArcFace ONNX 167MB).
- Verificar identidad de forma autonoma.

### C.3. Contraste weak vs strong

| Aspecto                  | weak (LLM+base64)     | strong (Python+pixels)   |
|--------------------------|-----------------------|--------------------------|
| Acceso a pixeles         | NO                    | Si (float32[H,W,3])      |
| Deteccion de caras real  | NO (estima)           | Si (BlazeFace TFLite)    |
| Embedding biometrico     | NO                    | Si (ONNX / TFLite)       |
| Metricas geometricas     | NO                    | Si (con modelos)         |
| Verdict de identidad     | HUMAN_REVIEW          | Solo en HIL              |
| Calculo de SSIM real     | Aproximado            | Si (sobre pixeles)       |

### C.4. Prohibiciones explicitas

El LLM operando en weak_semantic NO debe:

1. Declarar "he visto la imagen" cuando solo recibio base64.
2. Fabricar valores de pixel_mean, pixel_std, box coordinates, distance,
   cosine similarity, SSIM o cualquier metrica que requiera acceso a
   pixeles.
3. Afirmar deteccion de caras como si fuera real (BlazeFace no ejecuto).
4. Declarar `metrics_missing: []` si ArcFace, BlazeFace u otro modelo
   requerido no esta disponible en el entorno.
5. Emitir PASS como veredicto (kernel v0.9.5 seccion 6 prohibe PASS).

Violacion de cualquiera de las 5 reglas: veredicto minimo HUMAN_REVIEW,
reason debe declarar la violacion explicitamente.

### C.5. Declaracion en reason (sin schema patch)

El LLM puede declarar su nivel de condicionamiento en el campo reason
del JSON existente:

    {
      "kernel_version": "v0.9.5",
      "phase": "SIL",
      "verdict": "HUMAN_REVIEW",
      "metrics_missing": ["arcface", "blazeface", "ssim"],
      "reason": "conditioning_level: weak_semantic. input_modality: base64_tokens. pixel_access: false. Metricas geometricas requieren HIL.",
      "hardware_signature": "SYNTHETIC (No CMOS Sensor)"
    }

Ventaja: usa el campo reason (ya existente), no rompe additionalProperties.
El schema v0.9.5 permanece intacto.

### C.6. Bridge weak -> strong

Para pasar de condicionamiento debil a fuerte:

1. Declarar `conditioning_level: weak_semantic` en reason.
2. Invocar herramienta Python externa (cuando exista).
3. Recibir metricas del tool (NO inventarlas).
4. Reportar en `metrics_missing` lo que sigue faltando.
5. Mantener verdict en {HUMAN_REVIEW, PENDING_LOCAL_VERIFICATION, BLOCKED}.

El bridge NO convierte al LLM en strong. Solo importa resultados de un
proceso strong (Python con pixels reales). El LLM sigue siendo weak.

Nota: `src/agf_retina.py` NO existe aun. Es deuda tecnica futura. El
bridge puede usar modulos existentes: src/face_detector.py,
src/face_align.py, src/face_embedding.py.

### C.8. COLS — Commercial Opaque LLM Services

El kernel AGF opera dentro de un COLS (Commercial Opaque LLM Service):
ventana de chat de un LLM comercial donde el usuario no puede observar ni
verificar el modelo subyacente, sus operaciones internas, el conteo real
de tokens, ni la integridad de sus procesos.

Implicaciones para el kernel:

1. El kernel NO puede verificar qué modelo responde. Puede ser sustituido
   silenciosamente por uno más barato sin notificación. Cualquier
   afirmación sobre la identidad del modelo es UNVERIFIABLE.
2. El kernel NO puede verificar el conteo de tokens ni la facturación. Las
   afirmaciones del proveedor sobre costos o uso no son auditables desde
   dentro del chat.
3. El kernel NO puede verificar la integridad de las operaciones internas
   del proveedor (tool calls, retrievals, fine-tuning en vuelo).
4. El kernel asume opacidad total y NO pretende auditarla. Lo que el kernel
   puede hacer: forzar honestidad epistémica (Anexo B), prohibir fabricación
   (B.8), declarar conditioning_level (C.1).

Mapeo con kernel v0.9.5:
- reason debe declarar "cols_opacity_assumed" cuando el LLM afirme algo
  que dependa del modelo subyacente
- verdict mínimo HUMAN_REVIEW para cualquier verificación que dependa de
  propiedades internas del proveedor
- NUNCA se emite PASS basado en afirmaciones del proveedor no auditables

Referencias: Invisible Tokens Visible Bills (arXiv:2505.18471), One Token
Is Enough (fingerprinting de LLM opaco, referencia de lo que NO se puede
verificar desde el kernel).

### C.7. Referencias cruzadas

- Seccion 1 del kernel: "No ves pixeles directos" (formalizado aqui).
- Seccion 4 del kernel: OUTPUT FINAL OBLIGATORIO (JSON forense).
- Seccion 7 del kernel: STRONG CONDITIONING (JSON SCHEMA).
- Anexo A A.1: IMMUTABLE_FEATURES (requieren strong_pixel para medirse).
- Anexo A A.4: CPEP_IDENTITY_PRESERVATION_FAILED (cuando falta modelo).
- Anexo B B.1: trace_verification_status (honestidad de la cadena).

---

FIN DEL ANEXO C
