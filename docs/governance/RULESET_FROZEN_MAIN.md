# Ruleset Frozen-Main-v12.2

## Objetivo
Proteger la rama `main` en `joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine`.

## Cambio aplicado (v12.4.6)

Se desactiva `require_extra_approval_for_unattributed_changes`.

### Motivo
En un repositorio solo-owner:
1. No existe segundo revisor que apruebe PRs.
2. La ancestria de `main` contiene commits con email placeholder (`tu@email`),
   no reescribible sin force-push al main protegido.
3. Resultado: todo PR quedaba BLOCKED requiriendo `--admin` en cada merge,
   convirtiendo el ruleset en "teatro de gobernanza".

### Compensacion
- Bypass `RepositoryRole:Admin (always)` sigue activo para emergencias.
- `required_approving_review_count: 0` se mantiene.
- Checks `doctor` y `Python Syntax Check` deben pasar antes del merge.
- Regla `non_fast_forward` y `deletion` siguen bloqueando push destructivo.

## Reproducibilidad

Script: `tools/apply_ruleset.sh`

Uso:
- `bash tools/apply_ruleset.sh --dry-run` (solo muestra payload)
- `bash tools/apply_ruleset.sh` (aplica, pide confirmacion)

## Referencias
- Snapshot previo: `.github/rulesets/frozen-main-v12.2.current.json`
- Propuesta:      `.github/rulesets/frozen-main-v12.2.proposed.json`
