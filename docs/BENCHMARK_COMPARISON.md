# Benchmark comparativo de preservación de identidad — protocolo v1

## Por qué este documento existe
La auditoría externa (2026-10-14) señaló: "sin tabla comparativa, el claim
de identidad no se sostiene fuera de tu repo". Correcto. Este es el protocolo
para producirla con rigor.

## Regla metodológica central (no negociable)
Los cosine de métodos distintos **no son comparables entre sí** (cada
pipeline usa su propio espacio de embedding). La comparación válida exige
**un verificador común**: nuestro FaceNet TFLite (custodiado,
weights_sha256 54660297… verificado) aplicado a las SALIDAS de cada método.

## Diseño
| Parámetro | Valor |
|---|---|
| Identidades | 20 (autorizadas, con consentimiento documentado) |
| LLMs opacos | 3 (ChatGPT, Gemini, Grok) — vía AGF CANAL |
| Métodos base | AGF kernel / IP-Adapter / InstantID / PhotoMaker / PuLID |
| Variantes por identidad | referencia nítida + objetivo dañado + 2 generadas |
| Métricas | cosine(mismo) TAR, cosine(distinto) FAR, tasa BLOCKED real @ 0.65 |

## Tabla (a completar con corridas reales)
| Método | cosine mismo (media) | cosine distinto (max) | TAR@0.65 | FAR@0.65 | BLOCKED real |
|---|---|---|---|---|---|
| AGF kernel + FaceNet-verify | 0.9675 (n=1, evidence/t22.json) | pendiente | pendiente | pendiente | pendiente |
| IP-Adapter + FaceNet-verify | — | — | — | — | — |
| InstantID + FaceNet-verify | — | — | — | — | — |
| PhotoMaker + FaceNet-verify | — | — | — | — | — |
| PuLID + FaceNet-verify | — | — | — | — | — |

## Estado
PROTOCOLO SPECIFIED. Ejecución pendiente (requiere 20 identidades
consentidas + GPUs para los métodos base). Hasta entonces, el claim
comparativo del proyecto es **NO DETERMINED** por diseño.
