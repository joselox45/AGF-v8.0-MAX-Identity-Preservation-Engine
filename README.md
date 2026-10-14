# AGF v8 MAX — Identity Preservation Engine

Motor de preservación de identidad con **ejecución estricta en la ventana de chat**
de LLMs comerciales opacos (ChatGPT, Gemini, Grok, Meta AI). Sin API, sin plugins,
sin acceso al modelo.

**Precisión de enforcement (auditoría 2026-10-14):** AGF no puede imponer
comportamiento al LLM (nadie puede, en caja negra). Lo que hace: (a) instruir
con un kernel de mínima intervención, (b) exigir reporte de procedencia, y
(c) **verificar biométricamente la salida del lado del operador y bloquear
(BLOCKED) lo que no evidencia identidad**. Es observabilidad + decisión
post-hoc fail-closed, no prevención en el modelo. Ver docs/GLOSSARY.md.

## Uso en 30 segundos (operador)

```bash
git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine
python agf.py doctor    # autodiagnóstico (9/9 OPERATIVO en Termux)
python agf.py go        # kernel como artefacto firmado (out/ + sha256)
                        # opcional: --clipboard (no recomendado: clipboard managers)
```

1. Abre tu chatbot → adjunta imagen de referencia + objetivo → pega → envía.
2. Recibes la imagen editada + `[AGF_VERIFICATION_REPORT]` (procedencia forzada).
3. Verificación biométrica opcional en tu equipo: `python agf.py closure A.jpg B.jpg modelo.tflite facenet raw`

El tercero **no necesita leer el prompt**: `agf.py go` lo entrega listo para pegar.

## Qué garantiza el sistema

- **Fail-closed en el veredicto**: sin evidencia → BLOCKED. Nunca se fabrica
  un *veredicto* (demostrado en vivo: un PASS dudoso detectado y rechazado —
  evidence/t21.json). La generación en el LLM sí fabrica píxeles (toda
  generación lo hace): por eso la fabricación se **acota** (mínima
  intervención) y se **verifica** post-hoc. No afirmamos zero-fabrication
  de píxeles; afirmamos zero-fabrication de *aseguramientos*.
- **Verificación biométrica real**: FaceNet TFLite en Android, cosine 0.9675
  reproducible byte-a-byte (evidence/t22.json), pesos con SHA-256 verificado.
- **Procedencia epistemológica**: RECOVERED ≠ RECONSTRUCTED ≠ GENERATED, forzada en código.
- **Gobernanza APCE v8.1.0 canónica**: governor G1–G6; nada se auto-promueve
  a OPERATING_EFFECTIVE. Protocolo AKADI-OMEGA-LITE-O0 v18.0 en docs/protocols/.
- **Evidencia verificable**: cadenas SHA-512, attestation Ed25519 por terceros
  independientes (tools/attest.py).

## Arquitectura

```
APCE v8.1.0 CANÓNICO (control plane, G1–G6)
   └── AGF evaluation plane
        ├── MTE v1.0 (T01–T20)           docs/MTE.md
        ├── v9.0 runtime (T21–T31)       embeddings TFLite, evidencia, SPIFFE/DID
        ├── Chat Runtime v0.2            FSM black-box + Prompt Kernel (auditoría 7.5→9)
        └── agf.py                       CLI maestra: doctor/kernel/go/closure/benchmark/attest
   └── BLACK-BOX LLM CHAT WINDOW        (único canal: texto + imágenes)
```

## Posicionamiento (síntesis de 7 auditorías externas, oct 2026 (9 auditorías))

Este repositorio es un **marco de verificación fail-closed y trazabilidad
ejecutable sobre LLMs opacos** — no una herramienta plug-and-play de edición
de imágenes. Para preservación de identidad en producción masiva existen
caminos más directos (IP-Adapter, InstantID). Para gobernar lo que un LLM
black-box devuelve, con evidencia firmable y cero veredictos fabricados,
este es uno de los enfoques más rigurosos publicados. La pila de
gobernanza (APCE/O0/G1-G6) es deliberada: está diseñada para un nivel de
aseguramiento que el caso de uso actual aún no exige, y se declara como tal.

## Estado de aseguramiento (mapping v6)

**PRIMER L3 SUPPORTED (2026-10-14):** identidad preservada certificada
sobre la salida de un LLM comercial opaco — cosine 0.931, FaceNet custodiado,
tres capas L1/L2/L3 completas (evidence/verify_2026-10-14/). n=1 declarado.

**8/8 controles TESTED** con evidencia real en Termux: T21 ArcFace
cerrado (cosine 0.8901 con alineación BlazeFace; root cause corregido:
box coder SSD /128) y T22 FaceNet determinista (0.9675 byte-a-byte).
Benchmark T30 ejecutado con muestra mínima declarada (TAR n=1, cos 0.9743).
Nada declarado OPERATING_EFFECTIVE por diseño. Comparación SOTA completa
y matriz adversarial 8x4: protocolos publicados, ejecución roadmap.
Detalle: `data/apce_mapping_t21_t28.csv` (mapping v6).

## Licencias

- **Código**: MIT (`LICENSE-CODE`).
- **Pesos de modelos**: NO distribuidos; términos por modelo en `LICENSE-WEIGHTS.md`.
- Garantía: ninguna. Ver `NOTICE.md`.

## Documentos clave

Empieza por docs/GLOSSARY.md: todo el proyecto son 3 conceptos
(GOVERNOR / ENGINE / CANAL), no 8 siglas.

| Doc | Contenido |
|---|---|
| `docs/GLOSSARY.md` | 3 conceptos que explican todo |
| `docs/BENCHMARK_COMPARISON.md` | Protocolo comparativo vs SOTA |
| `docs/QUICKSTART_TERCEROS.md` | Uso para terceros (2 comandos) |
| `docs/FRAMEWORK_CHAT_WINDOW.md` | Marco de ejecución en ventana de chat |
| `docs/AGF_T21_T28_APCE_MAPPING.md` | Mapping con evidencia y gaps |
| `docs/protocols/` | AKADI-OMEGA-LITE-O0 v18.0 (md/pdf/docx) |
| `docs/GUION_VIDEO_60s.md` | Guion demo para redes |
