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
