# AGF v8 MAX — QUICKSTART PARA TERCEROS
### Ejecución estricta en ventana de chat, sin API, LLM opaco

No necesitas entender la arquitectura completa. Necesitas 3 cosas:
un teléfono/PC con Python, este repositorio, y acceso a cualquier
chatbot multimodal (ChatGPT, Gemini, Grok, Meta AI, afines).

---

## PASO 0 — Obtener el código (2 minutos)

```bash
git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine
python examples/agf_chat_runtime_v0.2_single.py
```

Si no tienes Python: https://python.org (PC) o `pkg install python` (Termux/Android).

## PASO 1 — Generar la orden (30 segundos)

El comando anterior imprime un bloque `[AGF_OPERATION]`. Cópialo completo.
Ese bloque es la única interfaz con el LLM opaco.

## PASO 2 — Ejecutar en el chatbot (1 minuto)

1. Abre tu chatbot (ChatGPT / Gemini / Grok / Meta AI)
2. Adjunta 2 imágenes: **referencia** (cómo debe verse el sujeto) y
   **objetivo** (la que está dañada)
3. Pega el bloque `[AGF_OPERATION]`
4. Recibirás la imagen editada + un reporte `[AGF_VERIFICATION_REPORT]`

El chatbot nunca ejecuta código AGF. Solo lee texto y edita imágenes.

## PASO 3 — Verificar y registrar (2 minutos)

```bash
# Hash de evidencia de cada imagen (custodia)
sha512sum referencia.jpg objetivo.jpg editada.jpg

# Ejecutar la suite de verificación
python -m unittest discover -s tests -v
```

Sube tus hashes como evidencia (issue o PR contra `data/traceability_v9.csv`).

---

## QUÉ ESTÁ GARANTIZADO (y qué no)

| Garantizado | No garantizado (fail-closed) |
|---|---|
| El bloque prohibe cambiar identidad/anatomía/expresión | Verificación biométrica sin pesos ArcFace/FaceNet → estado `BLOCKED` |
| Procedencia forzada: RECOVERED ≠ RECONSTRUCTED ≠ GENERATED | El chatbot puede ignorar instrucciones; por eso el reporte de verificación es obligatorio |
| Cadena de evidencia SHA-512 íntegra por corrida | `PASS` jamás se fabrica: sin evidencia → `BLOCKED` |
| Mínima intervención ante la duda | |
| Todo veredicto pasa por el gobernador APCE (G1–G6) | |

## REGLA DE ORO

> AGF no controla el modelo interno del chatbot. Controla y verifica
> la interacción con él a través de su ventana de chat. Sin API, sin
> pesos, sin backend.

## Estructura relevante para operadores

```
examples/agf_chat_runtime_v0.2_single.py   ← único archivo que necesitas correr
src/prompt_kernel.py                       ← el bloque [AGF_OPERATION] (v0.2)
data/traceability_v9.csv                   ← matriz de evidencia (T21–T28)
docs/CHAT_RUNTIME_ARCHITECTURE.md          ← arquitectura completa
docs/AGF_EVALUATOR_UNDER_APCE.md           ← gobernanza (APCE canónico)
tests/                                     ← 42+ pruebas unitarias
```
