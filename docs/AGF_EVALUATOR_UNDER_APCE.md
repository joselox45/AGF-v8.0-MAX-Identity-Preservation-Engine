# AGF como Verification Evaluator bajo gobierno APCE
## AGF-EVALUATOR-APCE-CONTRACT v1.0

## 1. Jerarquía arquitectónica (innegociable)

```
┌─────────────────────────────────────────────┐
│  APCE v8.1.0 — CANONICAL AUTHORITY          │
│  (control plane: policy, precedence,        │
│   assurance state machine, authorization)   │
└──────────────────┬──────────────────────────┘
                   │ gobierna
                   ▼
┌─────────────────────────────────────────────┐
│  AGF v8 MAX / v9.0 / Chat Runtime v0.1      │
│  (evaluation plane: MTE, embedding,         │
│   evidence, identity, chat verification)    │
└──────────────────┬──────────────────────────┘
                   │ evalúa
                   ▼
         BLACK-BOX LLM CHAT WINDOW
```

AGF **nunca** promueve su propio veredicto por encima de APCE.
Un `PASS` de AGF sin evidencia aceptable por APCE sigue siendo `BLOCKED`.

## 2. Separación de roles

| Responsabilidad | Dueño |
|---|---|
| Autoridad, precedencia, política, autorización | **APCE** |
| Decisión de aceptación operativa (ACCEPT/REJECT/BLOCK) | **APCE** (vía Policy Gate gobernado) |
| Medición, comparación, hash, verificación técnica | **AGF** |
| Estados de aseguramiento (SPECIFIED→…→ATTESTED) | **APCE** (AGF alimenta transiciones con evidencia) |
| Evidencia cruda (embeddings, cadenas SHA-512, captures) | **AGF** |
| Cadena de custodia de decisiones | **APCE** (con evidencia de AGF adjunta) |

## 3. Contrato de evaluación

Toda evaluación AGF se somete a `APCEGovernor.review()`:

```
AGF veredicto (PASS/FAIL/BLOCKED/UNVERIFIED/NOT_RUN)
        + evidencia (hash, vector, cadena)
        + contexto (capability, authorization)
                │
                ▼
        APCEGovernor.review()
                │
   ┌────────────┼─────────────┐
   ▼            ▼             ▼
 CONFIRMED   DOWNGRADED    VETOED
 (APCE PASS) (APCE BLOCKED)(APCE CONFLICT→APCE prevails)
```

Reglas:
- **G1 (No fabrication):** AGF PASS sin evidence_hash → `BLOCKED` automático.
- **G2 (Fail-closed):** AGF BLOCKED/UNVERIFIED nunca se promueve; se propaga.
- **G3 (Precedence):** capability > privacy > security > policy > purpose > authorization. Capa bloqueante en APCE anula cualquier veredicto AGF.
- **G4 (Conflict):** veredicto AGF incompatible con control canónico APCE → veta y registra; APCE prevalece.
- **G5 (Traceability):** todo veredicto confirmado queda ligado a evidence_hash + mapping record.
- **G6 (Assurance states):** AGF no transiciona estados de aseguramiento; solo APCE lo hace con evidencia AGF + verificación APCE.

## 4. Alineación de máquinas de estado

```
APCE:  SPECIFIED → IMPLEMENTED → TESTED → OPERATING_EFFECTIVE → INDEPENDENTLY_ATTESTED
                         ▲
                         │ alimenta con evidencia AGF (tests OK, hashes, runs)
AGF:   NOT_RUN → BLOCKED/UNVERIFIED → PASS/FAIL  (nunca salta a OPERATING_EFFECTIVE por sí solo)
```

Bloqueos APCE que congelan a AGF: `EVIDENCE_GAP`, `VERSION_GAP`, `CONFLICT`,
`FAILED`, `EXECUTED_NOT_VERIFIED`, `IMPLEMENTABILITY_GAP`.

## 5. Flujo operativo gobernado

```
1. AGF ejecuta medición (MTE / embedding / captura)
2. AGF emite veredicto técnico + evidencia
3. APCEGovernor.review() aplica G1–G6
4. Si CONFIRMED → la decisión operativa pasa al Policy Gate APCE
5. Policy Gate decide ACCEPT / REJECT / BLOCK con precedencia APCE
6. Evidence Writer registra (cadena APCE, adjuntos AGF)
7. Rollback si: conflicto material, precedencia violada, postcondición no verificable
```

## 6. Estado

- AGF evaluation plane: OPERATIVE (MTE + v9.0 + Chat Runtime, tests OK)
- APCE authority plane: CANONICAL v8.1.0 (por gobernanza de proyecto)
- Integración gobernada: DEFINIDA (este contrato + `src/apce_governor.py`)
- OPERATING_EFFECTIVE del conjunto: pendiente de evidencia operacional independiente
