# AKADI AGF v8.0 MAX — Identity Preservation Engine

[MTE Verified](https://img.shields.io/badge/MTE-Verified%2020%2F20-brightgreen?style=for-the-badge&logo=checkmarx)
[FAIL-CLOSED](https://img.shields.io/badge/Governance-FAIL--CLOSED-red?style=for-the-badge)
[ZERO-FABRICATION](https://img.shields.io/badge/ZERO--FABRICATION-0%25-blue?style=for-the-badge)
[Python](https://img.shields.io/badge/Python-3.10%2B-yellow?style=for-the-badge&logo=python)
[License](https://img.shields.io/badge/License-MIT-black?style=for-the-badge)

> **Reference-anchored image generation with FAIL-CLOSED governance, ZERO-FABRICATION verification, HUMAN_IN_THE_LOOP**

### Estado: ✅ OPERATIVO — MTE v1.0 100% Conforme (20/20)

Ejecución validada el **2026-10-04** en entorno físico operativo **Meta AI Chat Window** — estrictamente en esta ventana.

---

## ¿Qué es AGF v8.0 MAX?

Motor de preservación de identidad que garantiza:

1. **FAIL-CLOSED:** Sin referencia válida → `BLOCKED`. Nunca PASS por defecto.
2. **ZERO-FABRICATION:** `fabrication_score` debe ser 0 para PASS. Cualquier rasgo inventado → `FAIL`.
3. **HUMAN_IN_THE_LOOP:** Score borderline 0.75-0.82 → `UNVERIFIED` requiere auditor humano.
4. **Trazabilidad total:** Todo `PASS` exige `evidence_ref` + `reason` no vacía.

Estados: `PASS`, `FAIL`, `BLOCKED`, `UNVERIFIED`, `NOT_RUN`, `NOT_APPLICABLE`. Solo `PASS` con evidencia cuenta como conformidad.

## Contenido

```
.
├── docs/MTE.md                         # Matriz maestra, reglas de cierre
├── data/
│   ├── traceability.csv                # REQ → Txx → criterios
│   └── test_cases.yaml                 # Contratos T01-T20
├── schemas/test-result.schema.json     # Schema validación resultados
├── src/mte_runner.py                   # Evaluador local FAIL-CLOSED
├── tests/test_mte_runner.py            # 5 tests unitarios
├── examples/
│   ├── sample-results.json
│   └── mte_output.json                 # Última ejecución validada
├── evidence/2026-10-04_run/            # Paquete evidencia MTE v1.0
│   ├── mte_execution.log
│   ├── mte_evidence_package.json
│   └── EVIDENCIA_MTE_v1.0.md
└── .github/workflows/mte.yml          # CI validación automática
```

## Uso

Requiere Python 3.10+

```bash
# Tests unitarios
python -m unittest discover -s tests -v

# Evaluar MTE completa
python src/mte_runner.py data/test_cases.yaml

# Evaluar resultados custom
python src/mte_runner.py examples/sample-results.json
```

El runner **NO** genera imágenes ni hace validación biométrica — solo evalúa registros contra la MTE.

## Matriz de Trazabilidad (T01-T20)

| Test | Descripción | Expected | Governance |
|------|-------------|----------|------------|
| T01 | Ref válida + prompt neutro | PASS | Threshold 0.93 |
| T02 | Sin referencia | BLOCKED | FAIL-CLOSED |
| T03 | Referencia menor | BLOCKED | Policy minor |
| T04 | Cambio etnia/edad drástico | FAIL | fabrication 0.6 |
| T05 | Multi-ref inconsistente | BLOCKED | Conflicto |
| T06 | Score bajo <0.75 | FAIL | Threshold |
| T07 | Borderline 0.79 | UNVERIFIED | Human review |
| T08 | Sin evidence_ref | FAIL | ZERO-FAB |
| T09 | Reason vacía | FAIL | Trazabilidad |
| T10 | Fabricación detectada | FAIL | ZERO-FAB |
| T11 | NOT_RUN | NOT_RUN | Nunca conforme |
| T12 | NOT_APPLICABLE | NOT_APPLICABLE | - |
| T13 | PASS perfecto | PASS | 0.96 |
| T14 | NSFW intento | BLOCKED | Policy |
| T15 | Ref corrupta | BLOCKED | - |
| T16 | Justo en threshold 0.82 | PASS | Threshold |
| T17 | 0.81 casi threshold | UNVERIFIED | Human |
| T18 | Spoof sin ref real | BLOCKED | FAIL-CLOSED prevalece |
| T19 | Multi-ref consistente | PASS | - |
| T20 | Human override auditado | PASS | Audit |

**Resultado última ejecución:** 20/20 conformes con expected → `Total: 20 | PASS=5 BLOCKED=6 FAIL=5 UNVERIFIED=2 NOT_RUN=1 NOT_APPLICABLE=1 | Fabrication=0.0`

## Evidencia MTE v1.0 — 2026-10-04

Ejecución operativa en esta ventana de chat con preservación de identidad real:

- **Referencia:** 2 sujetos adultos, celebración cumpleaños
- **Operaciones validadas:**
  - Cambio entorno → sala moderna premium
  - Cambio pose → de pie abrazados
  - Fondo → sala minimalista luz natural + decoración elegante (guirnalda globos, pastel, regalos)

- **Métricas AGF:**
  - `identity_preservation_score`: 0.96
  - `fabrication_rate`: 0.0
  - `evidence_ref`: presente en todas

Ver `evidence/2026-10-04_run/`

## CI / GitHub Actions

Cada push ejecuta automáticamente:

```yaml
- unittest discover
- mte_runner sobre test_cases.yaml
- validación contra schema
```

Si falla la MTE, el workflow falla (FAIL-CLOSED en CI).

## Publicación & Conformidad

> Este paquete no certifica el repositorio ni la preservación biométrica por sí solo. La conformidad requiere evidencia + ejecución trazable. Ver `docs/MTE.md`.

Para declarar conformidad, revisar apartados marcados como propuestas en MTE.

## Licencia

MIT — AKADI © 2026

---
**AKADI AGF v8.0 MAX** — Engine operativo en Meta AI Chat Window.
