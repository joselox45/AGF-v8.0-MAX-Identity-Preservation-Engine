# Sesgo de posicion en LLM-as-judge y su relevancia para AGF

## El hallazgo (Zheng et al., 2023, "Judging LLM-as-a-Judge")
Los LLM evaluadores favorecen las respuestas segun su POSICION en el
enunciado, no solo su calidad: invertir el orden puede invertir el veredicto.

## Por que importa para AGF (decisiones de diseno ya tomadas, ahora con cita)
1. **La procedencia DECLARADA por el LLM es dato, no veredicto.** El kernel
   obliga al modelo a autoreportar [AGF_VERIFICATION_REPORT], pero AGF jamas
   convierte esa declaracion en PASS: pasa por capas L1/L2/L3 donde la
   biometria custodiada decide (R6: "lo mide un tercero" — el tercero es el
   ENGINE, no el propio modelo). El sesgo de posicion es una razon mas para
   no confiar en el autoreporte: el modelo puede declarar lo que sea
   "primero" o mas convenientemente posicionado.
2. **Una respuesta es una muestra, no un veredicto.** Principio rector del
   proyecto: un RECIBO de la ventana es una muestra declarada; el veredicto
   requiere evidencia (G1: sin evidence_hash, BLOCKED).

## Tecnica transferible: doble ejecucion con orden invertido
Cuando el flujo exija comparacion por el LLM (p.ej. futuros jueces LLM en
el benchmark SOTA), aplicar:
- Ejecutar la comparacion dos veces, con orden invertido (A/B y B/A).
- Si el ganador cambia -> el modelo elegia posicion, no calidad ->
  registrar CONFLICTO y descartar el par de esa corrida.
- Medible con MetricasTurno: tasa de inconsistencia por orden.

## Fila de matriz adversarial propuesta
A09 · Sesgo de posicion: kernel v3 ejecutado dos veces con orden de opciones
invertido en ESCENA; si el RECIBO difiere -> estado CONFLICTO + metrica
tasa_inconsistencia_orden en MetricasTurno.

## Referencia
Zheng, L. et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot
Arena. NeurIPS 2023 Datasets and Benchmarks.
