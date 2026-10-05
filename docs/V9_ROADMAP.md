# AKADI AGF — Mapa de Evolución v8.0 MAX → v9.0

## 1. Qué certifica hoy v8.0 MAX (MTE v1.0)

El repositorio `joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine` publica la
**Matriz de Trazabilidad Ejecutable v1.0**, un paquete de *especificación*:

| Componente | Función | Límite declarado |
|---|---|---|
| `docs/MTE.md` | Matriz maestra, reglas de cierre, métricas | No ejecuta nada |
| `data/traceability.csv` | Requisitos → fuentes → pruebas → criterios | Datos estáticos |
| `data/test_cases.yaml` | Contratos T01–T20 | Contratos, no runtime |
| `src/mte_runner.py` | Evaluador local de estados | Evalúa registros ajenos |
| `tests/test_mte_runner.py` | Unitarias del evaluador | No cubre biometría |

Estados de la MTE: `PASS`, `FAIL`, `BLOCKED`, `UNVERIFIED`, `NOT_RUN`,
`NOT_APPLICABLE`. Regla de oro: `NOT_RUN`, `BLOCKED` y `UNVERIFIED` **nunca**
se convierten en conformidad.

## 2. Brecha detectada (los tres pendientes)

| # | Pendiente | Por qué no cabía en v8.0 | Resolución v9.0 |
|---|---|---|---|
| P1 | Embedding real ArcFace/FaceNet | El host LLM opaco no permite cargar pesos ni ONNX | `src/face_embedding.py` con degradación BLOCKED; comparador coseno puro con anti-replay |
| P2 | Firmas criptográficas de evidencia | Evidencia = texto sin custodia | `src/evidence_signing.py`: cadena SHA-512 encadenada + Ed25519; HMAC degrada a UNVERIFIED |
| P3 | Integración Agent Identity SPIFFE/DID | Sin identidad verificable del agente | `src/agent_identity.py`: SPIFFE ID + did:key Ed25519 + SVID anclado |

## 3. Restricción operativa: ventana de chat de LLM comercial opaco

Diseño completo bajo el **chat-window runtime contract**:

1. **Bloque único copiable** — cada módulo cabe pegado en un mensaje de chat.
2. **stdlib-first** — dependencias opcionales (`numpy`, `onnxruntime`,
   `cryptography`) que, si faltan, degrada el estado a `BLOCKED`/`UNVERIFIED`,
   jamás `PASS` fabricado (fail-closed).
3. **Sin red, sin filesystem, sin secretos persistidos** — el único estado es
   texto (JSON + hashes) que el operador copia de vuelta.
4. **Evidencia portátil** — cada resultado lleva `evidence_hash` SHA-512
   verificable fuera de la ventana.

## 4. Nuevas filas de trazabilidad (T21–T28)

| ID | Requisito | Estado objetivo |
|---|---|---|
| T21 | Embedding ArcFace ONNX real | PASS solo con pesos válidos |
| T22 | Embedding FaceNet ONNX real | PASS solo con pesos válidos |
| T23 | Comparador coseno + umbral | FAIL-CLOSED en vectores ausentes |
| T24 | Anti-replay de embeddings (cos ≥ 0.99999 → FAIL) | FAIL |
| T25 | Cadena de custodia SHA-512 encadenada | PASS |
| T26 | Firma Ed25519 de evidencia | PASS / UNVERIFIED sin crypto |
| T27 | SPIFFE ID + did:key de agente | PASS / BLOCKED sin clave |
| T28 | Verificación estructural SVID pre-firma | FAIL-CLOSED |

## 5. Convención de estados heredada

Se preserva la semántica MTE v1.0: un `PASS` exige evidencia y razón no
vacías; `NOT_RUN`/`BLOCKED`/`UNVERIFIED` nunca computan conformidad.
