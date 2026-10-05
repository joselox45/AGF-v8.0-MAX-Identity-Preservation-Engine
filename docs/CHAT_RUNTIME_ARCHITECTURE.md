# AGF Chat Runtime v0.1 — Arquitectura

## Principio arquitectónico (Execution Boundary)

```
AGF SHALL NOT CONTROL THE INTERNAL LLM.
AGF SHALL CONTROL AND VERIFY THE INTERACTION WITH THE LLM
THROUGH ITS CHAT INTERFACE.
```

- `provider = UNKNOWN` | `interface = CHAT_WINDOW` | `api = NONE`
- `model_access = BLACK_BOX`
- Interacción permitida (único canal): `upload_image`, `send_prompt`,
  `receive_output`, `inspect_output`, `send_correction`.

## Planes

| Plano | Componentes |
|---|---|
| CONTROL | `prompt_kernel.py`, `policy_gate.py`, `chat_runtime.py` (FSM), MTE |
| RUNTIME | `browser_adapter.py` (Manual por defecto), `image_intake.py`, `result_capture.py` |
| EVIDENCE | `evidence_writer.py` (cadena SHA-512, append-only) |
| VERIFICATION | `identity_verifier.py` (integra v9.0 embedding; fail-closed) |

## FSM

```
IDLE → INTAKE → KERNEL → DISPATCH → AWAIT_OUTPUT → CAPTURE → VERIFY
        │                                             │
        └──────────────► BLOCKED ◄──┬─────────┬───────┘
                                  ACCEPT   REJECT → KERNEL (re-prompt, ≤ max_retries)
```

## Distinción epistemológica (nunca equivalentes)

- **RECOVERED** — información recuperada de la propia imagen.
- **RECONSTRUCTED** — inferida y reconstruida; siempre declarada.
- **GENERATED** — contenido nuevo; **nunca equivale a restauración** (FAIL en la ruta de restauración).

## Fail-closed

Evidencia ausente, verificación bloqueada o procedencia no declarada ⇒
`BLOCKED`. Nunca se fabrica un `PASS` (coherente con MTE v1.0 y APCE).

## Uso

```bash
python -m unittest discover -s tests -v
python examples/chat_runtime_demo.py
```
