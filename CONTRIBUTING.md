# Contributing to AGF v8.0 MAX

## Reglas de Gobernanza

1. **Nunca** hagas merge si MTE falla. FAIL-CLOSED también en CI.
2. Todo nuevo REQ debe tener Txx asociado en `data/test_cases.yaml` y trazabilidad en `data/traceability.csv`.
3. Todo PASS requiere `evidence_ref` + `reason`.

## Workflow

```bash
git checkout -b feat/nueva-regla
# edita data/test_cases.yaml y src/mte_runner.py si aplica
python -m unittest discover -s tests -v
python src/mte_runner.py data/test_cases.yaml
git add .
git commit -m "feat: ..."
git push
```

## Estructura de test case

```yaml
T21:
  description: "Mi nueva regla"
  input: {has_reference: true, similarity: 0.88, fabrication: 0, evidence_ref: "ref.jpg", reason: "explicación"}
  expected: PASS
```
