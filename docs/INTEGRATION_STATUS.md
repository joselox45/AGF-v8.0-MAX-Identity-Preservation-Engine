# Estado de Integracion (auditoria 11, H-01)

## DECLARACION EXPLICITA
La ruta FSM de `src/chat_runtime.py` NO realiza biometria. Invoca
`verifier.verify(None, None, provenance)`, que retorna BLOCKED (fail-closed).
Esto es DISEÑO, no bug oculto: la FSM es la PUERTA DE PROTOCOLO
(procedencia + gobernanza), no el verificador biometrico.

## Ruta biometrica canonica (la que certifica)
`tools/verify_image.py` — BlazeFace -> alineacion -> FaceNet/ArcFace TFLite
-> VectorComparator -> VerdictLayers (L1/L2/L3). Es la UNICA ruta que puede
emitir L2 PASS/SUPPORTED. Toda evidencia biometrica del repo (t21, t22,
verify_2026-10-14/) proviene de ella o de tools/closure_t21_tflite.py.

## Prueba de integracion E2E (receta reproducible)
La evidencia E2E ya existe: evidence/verify_2026-10-14/ (20 corridas,
incl. L3 SUPPORTED cosine 0.931). Para reproducir:
  python tools/verify_image.py <ref> <candidata> facenet.tflite facenet raw \
      blaze_face_short_range.tflite --provenance-declared --cross-tested \
      --subject-label same --prompt-sha256 <hash del kernel pegado>
Criterio de aceptacion del auditor: L2=PASS exige cosine>=umbral con pesos
custodiados; L3=SUPPORTED exige ademas cross-tested real etiquetado.

## Hoja de ruta (cuando la FSM deba verificar sola)
Conectar TFLiteFaceEmbedder al ChatRuntime (inyeccion, igual que closure) y
alimentar verify() con los pixeles de intake en vez de None. Hasta entonces,
esta declaracion rige y ninguna afirmacion debe atribuir biometria a la FSM.
