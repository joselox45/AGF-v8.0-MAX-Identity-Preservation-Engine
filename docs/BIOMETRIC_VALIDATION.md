# Validacion Biometrica — estado y limites (auditoria 11, H-03)

## Umbral 0.65: PROVISIONAL, no derivado empiricamente
El umbral comun a ArcFace/FaceNet es un punto de partida de ingenieria, NO
una constante validada. La derivacion exige: corpus etiquetado (mismo/distinto
sujeto), TAR/FAR con IC 95% por modelo y por condicion (retrato vs escena
compleja), y tabla de decision documentada. ROADMAP: data/corpus_v1 +
tools/corpus_benchmark.py ya existen; falta ejecutar con etiquetas.

## Hallazgo de estabilidad (2026-10-14, inedito)
Las escenas callejeras multirrostro producen varianza entre corridas (mismo
par: 0.476 vs 0.098) porque el detector selecciona por score y el entorno
XNNPACK no garantiza reproducibilidad en escenas complejas. Consecuencia:
los REFUTED de escenas callejeras (verify_2026-10-14/) son MEDICIONES
INESTABLES, no veredictos. El L3 SUPPORTED (0.931) es de retrato de medio
cuerpo — condicion estable.

## Parche de estabilidad (proximo)
Seleccion de cara por MAYOR AREA (no score), num_threads=1, y mediana de
N=3 corridas por par. Hasta aplicarse, los veredictos biometricos solo son
vinculantes en condiciones de retrato (cara dominante en cuadro).

## Lo que un PASS L2 significa hoy
"Similitud coseno >= umbral provisional en condiciones de medicion estables,
con pesos custodiados y pipeline alineado". NO es garantia biometrica
concluyente (H-03 del auditor, aceptado).
