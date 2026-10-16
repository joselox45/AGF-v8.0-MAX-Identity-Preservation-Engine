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
