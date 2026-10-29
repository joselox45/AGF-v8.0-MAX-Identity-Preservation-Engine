# Glosario AGF — 3 conceptos, no 8 siglas

Todo el proyecto se explica con tres piezas:

| Concepto | Qué es | Antiguas siglas que absorbe |
|---|---|---|
| **GOVERNOR** | Autoridad de gobernanza: decide qué cuenta como evidencia, precedencia y estados de aseguramiento. Nada se auto-promueve. | APCE v8.1.0, G1–G6, AKADI-O0 v18.0 |
| **ENGINE** | Código que ejecuta el operador: kernel de prompts, FSM, verificación biométrica TFLite, evidencia SHA-512, attestation. | AGF, MTE v1.0, v9.0 runtime, Chat Runtime, T01–T32 |
| **CANAL** | Única vía con el LLM opaco: su ventana de chat (texto + imágenes). Sin API. El LLM nunca ejecuta código AGF. | black-box chat window |

Lectura rápida de cualquier doc: *el GOVERNOR exige, el ENGINE verifica,
el CANAL transmite*. Todo lo demás es implementación.

## Estados de aseguramiento (del GOVERNOR)
SPECIFIED → IMPLEMENTED → TESTED → OPERATING_EFFECTIVE → INDEPENDENTLY_ATTESTED
Ningún peldaño implica el siguiente. **OPERATIONAL_DEGRADED**: componente
operativo con función reducida declarada (ver mapping).

## Frase rectora (de la investigacion de sesgos de juez LLM)

> "Una respuesta es una muestra, no un veredicto."

En AGF: todo lo que declara la ventana (RECIBO, provenance, estimaciones
visuales) es MUESTRA. El VEREDICTO exige evidencia encadenada y, para L3,
biometria custodiada + discriminacion cruzada.
