# AKADI AGF v8.0 MAX — Matriz de Trazabilidad Ejecutable (MTE) v1.0

Paquete de publicación para GitHub.

**Estado:** especificación de pruebas / ejecución pendiente. Este paquete no certifica el repositorio ni la preservación biométrica.

## Contenido
- `docs/MTE.md`: matriz maestra, reglas de cierre y métricas.
- `data/traceability.csv`: requisitos, fuentes, pruebas y criterios.
- `data/test_cases.yaml`: contratos T01–T20.
- `schemas/test-result.schema.json`: esquema JSON de resultados.
- `src/mte_runner.py`: evaluador local de estados.
- `tests/test_mte_runner.py`: pruebas unitarias del evaluador.

## Uso
Requiere Python 3.10+.

```bash
python -m unittest discover -s tests -v
python src/mte_runner.py examples/sample-results.json
```

El runner evalúa registros proporcionados; no ejecuta generación de imágenes, validación biométrica, ni pruebas del host LLM.

## Estados
`PASS`, `FAIL`, `BLOCKED`, `UNVERIFIED`, `NOT_RUN`, `NOT_APPLICABLE`.

Un `PASS` requiere referencia de evidencia y razón no vacía. `NOT_RUN`, `BLOCKED` y `UNVERIFIED` nunca se convierten en conformidad.

## Publicación
Sube el contenido del ZIP a un repositorio GitHub. Revisa y adapta los apartados marcados como propuestas antes de declarar conformidad.
