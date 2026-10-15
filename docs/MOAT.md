# El Foso (Moat) de AGF — docs/MOAT.md

## Por que el codigo NO es el foso
AGF es MIT: cualquiera puede copiar src/, tools/ y los tests en una tarde.
El codigo es un commodity.

## El foso real: el Evidence Vault
`evidence/vault.jsonl` — cadena append-only con **encadenamiento cruzado
entre corridas** (cada evidencia anclada al hash de la anterior). Un
competidor puede copiar el codigo pero **no puede replicar retroactivamente**:
- El historial de verificaciones reales ejecutadas (t21/t22/verify_*/benchmarks)
- Las corridas con pesos custodiados y SHA-256 fijados
- El primer L3 SUPPORTED (0.931) y los REFUTED aprendidos
- Las mediciones IC 95% del corpus

Cada nuevo usuario que verifica, ENGRUESA el foso: su evidencia se ancla a la
cadena y solo es valida dentro de ella.

## Foso #2: datos de calibracion
El corpus etiquetado + los TAR/FAR medidos son insumos que nadie mas tiene.
El umbral calibrado derivado sera publico, pero los datos no.

## Foso #3: la red de attestation
Cada tercero que firma evidencia con clave registrada fuera del repo anade
confianza acumulativa. La primera attestation independiente real vale mas
que mil lineas de codigo nuevo.

## Como medir el foso
python tools/vault.py metrics  ->  MOAT_METRICS (chain_length, SUPPORTED,
REFUTED, cross-tested, attested). Publicar estos numeros en cada release.

## Defensa activa
- El vault se verifica con `vault.py verify` en CI (recomputo desde disco).
- genesis se hizo con las evidencias reales del 14-oct-2026 (no con datos de
  relleno): la cadena nace de trabajo real.
