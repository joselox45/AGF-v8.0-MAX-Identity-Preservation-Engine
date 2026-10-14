# AGF v8 MAX — Identity Preservation Engine

Motor de preservación de identidad con **ejecución estricta en la ventana de chat**
de LLMs comerciales opacos (ChatGPT, Gemini, Grok, Meta AI). Sin API, sin plugins,
sin acceso al modelo. AGF no controla el LLM interno: controla y verifica la
interacción a través de su interfaz conversacional.

## Uso en 30 segundos (operador)

```bash
git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine
python agf.py doctor    # autodiagnóstico (9/9 OPERATIVO en Termux)
python agf.py go        # kernel copiado al portapapeles -> pega en tu chatbot
```

1. Abre tu chatbot → adjunta imagen de referencia + objetivo → pega → envía.
2. Recibes la imagen editada + `[AGF_VERIFICATION_REPORT]` (procedencia forzada).
3. Verificación biométrica opcional en tu equipo: `python agf.py closure A.jpg B.jpg modelo.tflite facenet raw`

El tercero **no necesita leer el prompt**: `agf.py go` lo entrega listo para pegar.

## Qué garantiza el sistema

- **Fail-closed**: sin evidencia → BLOCKED. Nunca se fabrica un PASS
  (demostrado en vivo: un PASS dudoso fue detectado y rechazado — evidence/t21.json).
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

## Estado de aseguramiento (mapping v4)

7/8 controles TESTED con evidencia real en Termux; T21 (ArcFace) con gap medido
y ruta de cierre (T21-ALIGN: BlazeFace + alineación). Nada declarado
OPERATING_EFFECTIVE por diseño. Detalle: `data/apce_mapping_t21_t28.csv`.

## Licencias

- **Código**: MIT (`LICENSE-CODE`).
- **Pesos de modelos**: NO distribuidos; términos por modelo en `LICENSE-WEIGHTS.md`.
- Garantía: ninguna. Ver `NOTICE.md`.

## Documentos clave

| Doc | Contenido |
|---|---|
| `docs/QUICKSTART_TERCEROS.md` | Uso para terceros (2 comandos) |
| `docs/FRAMEWORK_CHAT_WINDOW.md` | Marco de ejecución en ventana de chat |
| `docs/AGF_T21_T28_APCE_MAPPING.md` | Mapping con evidencia y gaps |
| `docs/protocols/` | AKADI-OMEGA-LITE-O0 v18.0 (md/pdf/docx) |
| `docs/GUION_VIDEO_60s.md` | Guion demo para redes |
