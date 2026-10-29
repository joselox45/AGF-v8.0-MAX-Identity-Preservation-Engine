# ERRATA y Notas de Reconciliacion (auditoria 10, 2026-10-14)

## 1. Paquete "20/20" del 04-oct-2026 = FIXTURES HISTORICOS
`evidence/2026-10-04_run/` contiene registros con campos `expected`/`conforms`
propios y `evidence_ref` a archivos inexistentes (`ref_001.jpg`). NO constituye
una corrida del runner actual:
- Su namespace T01-T20 difiere de `docs/MTE.md` (especificacion, no registros).
- `mte_runner_v2` (canonico) lo evalua como NON_CONFORMANT — comportamiento correcto.
- `RELEASE_NOTES_v8.0.0.md` y el tag `v8.0.0-MTE-VERIFIED` son HISTORICOS
  (el tag apunta a un commit sin evidence/). El estado actual lo define
  `data/apce_mapping_t21_t28.csv` (mapping v6) y este documento.

## 2. Afirmaciones corregidas
- README "oct 2024->2026": ERRATA — el repo se creo el 2026-10-02. Son
  9 auditorias procesadas en octubre 2026.
- "Uno de los enfoques mas rigurosos publicados": valoracion del autor,
  no hecho verificado (APCE G1: no es garantia).

## 3. Estado L3 SUPPORTED (n=1, declarado)
Unico veredicto completo: cosine 0.931, evidence/verify_2026-10-14/.
Los booleanos provenance_declared/cross_person_tested son afirmaciones del
operador; los JSON no etiquetan sujeto mismo/distinto (mejora en v2.2 del
verificador). FAR no medida; umbral 0.65 comun a ArcFace/FaceNet sin
derivacion empirica documentada (roadmap).

## 4. Fusión de protocolos (2026-10-16)
AKADI-OMEGA-LITE-O0 v18.0 + IDENTITY-LOCK v1.6 → PROTOCOLO AKADI UNIFICADO
v19.0 (canonico unico). Fuentes archivados en docs/protocols/historical/ con
hashes en LINEAGE.txt. Conflictos de precedencia resueltos: jerarquia de
autoridad (Parte I) > precedencia operativa de tarea (Parte II §7).

## 5. Fork del vault (2026-10-16, secuela del incidente de retrocompat)
El registro seq 27 (snapshot kernel_v3_demo, 2026-10-15) fue escrito con el
_body de la version transicional del bug de retrocompat. Su hash no recomputa
con la semantica v1.1 fijada. Medida: los registros 1-26 permanecen como
GENESIS VERIFICADA (head 64ff9500...); los registros 27+ se marcan como
SEGMENTO DE TRANSICION no garantizado; la cadena productiva continua desde el
registro 30 (primer verify con pipeline estable). El FAIL del vault fue
CORRECTO: detecto la inconsistencia introducida por nuestra propia
herramienta — mismo patron que el anti-replay con los recortes negros.
Actualizacion: creado evidence/vault_v2.jsonl — genesis = veredicto 0.944837
(kernel v3 Meta AI, pipeline estable, 2026-10-16). v1 archivado como
vault_v1_historical.jsonl (registros 1-26 genesis verificada; 27-31 transicion).
La cadena productiva es v2. tools/vault.py usa AGF_VAULT o v2 por defecto.

## 6. FAR medida por primera vez (2026-10-17, herramienta propia tools/calibrate_threshold.py)

Corridas (ambas ancladas al vault):
- facenet.tflite raw -> evidence/calibration_corpus_v1_20261017T233305Z.json (vault seq 2)
- arcface_digidow.tflite div255 -> evidence/calibration_corpus_v1_20261017T233814Z.json (vault seq 3)

Resultados corpus_v1 (n_genuine=80, n_impostor=190):
- FaceNet @0.65 (umbral operativo): TAR=1.00 [0.954-1.0], FAR=1.00 [0.980-1.0]
- FaceNet mejor umbral (Youden J=0.244, th=0.95): TAR=0.71, FAR=0.47
- ArcFace @0.65: TAR=0.625 [0.516-0.723], FAR=0.558 [0.487-0.627]
- ArcFace mejor umbral (Youden J=0.311, th=0.95): TAR=0.40, FAR=0.089 [0.057-0.139]

Diagnostico de causa raiz: imagenes base = 7 colores unicos (dibujo
parametrico plano, no fotografia). El embedding colapsa en AMBOS modelos:
variaciones de pose/luz desplazan el vector mas que el cambio de identidad
(FaceNet: genuine min 0.7569 < impostor min 0.846). EER insalvable en
ambos espacios de embedding -> el corpus no contiene senal discriminativa.

Estados corregidos:
- Umbral 0.65: pasa de "sin derivacion empirica" a "NO VALIDADO —
  FAR medida 0.558-1.00 segun modelo en el unico corpus disponible".
- corpus_v1: pierde aptitud para calibracion; queda solo como smoke-test
  de pipeline (deteccion + embedding + cosine no crashean).
- Criterio GOVERNOR: ningun umbral nuevo se adopta hasta corpus
  fotorealista con impostores medidos (roadmap #5, ahora bloqueante
  demostrado con evidencia convergente de dos modelos).

## 9. Primera calibracion real (2026-10-19, corpus_v2 parcial 9 IDs x 4 = 36)

Corpus: 9 identidades fotorealistas via CANAL (Meta AI, Gemini, Grok, ChatGPT,
Arena x2, Copilot, Dola), custodia SHA-256 desde intake, 8 generadores distintos.
Pares: 27 genuinos (base vs luz/oclusion/pose) + 36 impostores (base vs base).
Ambas corridas ancladas al vault (seq 28: align 112, seq 29: align 160).

RESULTADOS (IC 95% Wilson):
- AGF_ALIGN=112: Youden th=0.70, J=0.417, TAR 0.778, FAR 0.361
- AGF_ALIGN=160: Youden th=0.79, J=0.500, TAR 0.556, FAR 0.056 [0.015-0.18]
- Umbral legado 0.65: FAR 0.36-0.56 segun alineacion -> INVALIDADO DEFINITIVAMENTE.

DECISIONES:
a) Configuracion canonica v3: BlazeFace 2L + FaceNet norm + ALIGN 160
   (template escalado, ver fix en face_align.py) + mediana N=3 + threads=1.
b) Umbral de trabajo PROVISIONAL: 0.79 (Youden, corpus_v2 parcial). No adoptar
   como umbral de produccion: recalibrar al completar los 20 IDs (faltan 11
   por regenerar) y reportar curva DET completa.
c) EER ~0.31 en ambas alineaciones: separacion real pero no de grado
   produccion. Lecciones: corpus pequeno, 3 IDs de procedencia dificil
   (Fv2-06 upscaled, Fv2-05 gafas en las 4, Fv2-09 divergencia de prompt).
d) La eleccion 112-vs-160 se tomo CON DATOS (63 pares), no con intuicion:
   el control de 3 pares de anoche era ambiguo; la calibracion no.
