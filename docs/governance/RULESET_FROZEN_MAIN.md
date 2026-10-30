# Ruleset Frozen-Main — Historia y estado actual

## Objetivo
Proteger la rama `main` en `joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine`.

## Cronologia

### v12.2 (2026-10-29) — version inicial
Ruleset original con 5 reglas:
- `deletion`, `non_fast_forward`, `creation`, `update`, `pull_request`

El parametro `require_extra_approval_for_unattributed_changes` estaba en `true`,
lo que bloqueaba todo PR en repositorio solo-owner (no hay segundo revisor).

### v12.2 patched (2026-10-30, PR #4) — intento de fix fallido
Se cambio `require_extra_approval_for_unattributed_changes: true -> false`.

**Resultado: NO funciono.** Los PRs #5 y #6 seguian `BLOCKED` a pesar de:
- Todos los checks en `success`
- Sin reviews pendientes
- Sin threads sin resolver
- Flag `require_extra_approval` confirmado en `false` via API

### Diagnostico del bug
El culpable no era `require_extra_approval` sino la combinacion:

    { "type": "update", "parameters": null }
    +
    "require_extra_approval_for_unattributed_changes": false

GitHub interpreta `update: null` como "bloquear toda actualizacion de la rama",
incluyendo merges via PR. El flag `require_extra_approval: false` no override esa
restriccion. Es un bug conocido de GitHub con rulesets que combinan reglas `update`
con parametros permisivos.

### v12.3-minimal (2026-10-30, post-PR #5) — fix real
Se elimino el ruleset viejo (id 26185862) y se creo uno minimalista (id 26237246)
sin `update` ni `creation`. Conserva las reglas que importan:

- `deletion` — bloquea borrar main
- `non_fast_forward` — bloquea force-push destructivo
- `pull_request` — requiere PR + checks verdes

**Resultado: FUNCIONO.** PR #5 fue el primer merge sin `--admin` en la historia del repo.

## Compensacion
- Bypass `RepositoryRole:Admin (always)` activo para emergencias manuales.
- `required_approving_review_count: 0` (no requiere review, repo solo-owner).
- Checks `doctor` y `Python Syntax Check` obligatorios via branch protection.

## Reproducibilidad
Script: `tools/apply_ruleset.sh`

Uso:
- `bash tools/apply_ruleset.sh --dry-run` — muestra payload sin aplicar
- `bash tools/apply_ruleset.sh` — aplica, pide confirmacion

## Referencias
- Snapshot pre-nuclear:   `.github/rulesets/frozen-main-v12.2.pre-nuclear.json`
- Snapshot v12.2 original: `.github/rulesets/frozen-main-v12.2.current.json`
- Propuesta v12.2 (buggeada): `.github/rulesets/frozen-main-v12.2.proposed.json`
- Ruleset vigente:        `.github/rulesets/frozen-main-v12.3-minimal.proposed.json`
