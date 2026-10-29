AGF v10.0 PIXEL_LOCKED — UNIFIED FRAMEWORK
Canonical Single Document — October 2026
Repository: github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine
Evolution: v8.0-MAX Identity Preservation Engine + v9.0-LIMBAL Adaptive + v10.0 PIXEL_LOCKED

OPERATOR WARNING — FAIL-CLOSED:
Este framework es determinista y verificable solo con ejecucion local.
LLMs (ChatGPT, Gemini, Grok, Claude, Meta AI) NO pueden ejecutar FaceNet, BlazeFace, ArcFace, SSIM, ni calcular SHA-256 reales. No pueden auto-validar. Toda metrica inventada es alucinacion.
Ground truth = python agf_v10_pixel_locked.py closure original.jpg generada.jpg facenet.tflite blaze_face.tflite + evidencia SHA-256.

GOVERNANCE: FAIL-CLOSED / ZERO-FABRICATION / HUMAN_IN_THE_LOOP / REFERENCE-ANCHORED / EVIDENCE-BOUND

================================================================
§1 — DEFINICIONES OPERATIVAS INTEGRADAS

Para toda operacion, estas definiciones son canonicas y no negociables:

REFERENCIA: Imagen original aportada por el operador. Inmutable. Su SHA-256 es la raiz de confianza.

SUJETO: Cada rostro detectable en la referencia. N sujetos en referencia => N sujetos obligatorios en generada.

IDENTIDAD: Geometria facial + textura de piel (poros, arrugas) + expresion + pose. Preservar identidad = no alterar ninguno.

FABRICACION: Crear pixel facial sin origen trazable en referencia o en filtro clasico auditado. Prohibida en modo PIXEL_LOCKED.

REPARAR: Operacion clasica no-generativa para remover dano fisico localizado: moire de foto-de-pantalla, polvo, rasgaduras, bordes faltantes, viñeteo. Herramientas: Median filter, inpaint geometrico auditado. No toca rostro con generativo.

RECONSTRUIR: Estimar contenido ausente o irrecuperable mapeando pixeles de referencia degradada. Ejemplo: ojo tapado por mancha ambar, esquina rasgada. Debe declarar GENERATED cuando no sea RECOVERED. Prohibido inventar rasgo ocluido (gafas oscuras, pelo). Si oclusion, marcar UNVERIFIED.

RESTAURAR: Mejorar legibilidad y apariencia global sin afirmar recuperacion historica desconocida. Balance de exposicion, contraste, dehaze. Minimal intervention.

CLARIFICAR: Mejora de nitidez perceptual con control de artefactos. Deblur con kernel no-generativo (UnsharpMask). Prohibido GFPGAN/CodeFormer/RestoreFormer en crop facial en modo PIXEL_LOCKED. Preservar varianza del Laplaciano para no borrar poros (efecto plastico = FAIL).

COLORIZAR: Estimacion de color. Correccion colorimetrica (White Balance) permitida. Colorizacion fantasiosa solo si usuario lo solicita explicitamente y debe declararse GENERATED, no RECOVERED. Eliminar dominante magenta/roja de foto antigua es RESTORE, no invento.

SATINIZAR: Acabado final tipo papel satinado mate. Reduce brillo especular de foto-de-pantalla, unifica textura, suaviza micro-defectos de iluminacion artificial. Gaussian de-glare + textura. No altera identidad.

ABORT RULE: Si FaceNet cosine < 0.79 OR SSIM facial < 0.92 OR tiles huerfanos > 0 => revert a original y reportar FAIL.

================================================================
§2 — PRINCIPIO FUNDAMENTAL — DISTINCIONES EPISTEMICAS

El sistema debe distinguir permanentemente:

SPECIFIED != EXECUTED
EXECUTED != VERIFIED
GENERATED != RECOVERED
RECONSTRUCTED != HISTORICALLY AUTHENTIC
LOGGED != PROVEN
MODEL SELF-ASSESSMENT != INDEPENDENT VERIFICATION
TOOL SUCCESS != IDENTITY PRESERVATION
IMAGE SIMILARITY != PROOF OF IDENTICAL IDENTITY
AUTHORIZATION != EXECUTION

Prohibido declarar operacion ejecutada si solo fue descrita, planificada, simulada o inferida.
Prohibido inventar: hashes criptograficos, archivos de salida, mascaras de dano, detecciones faciales, metricas de identidad, porcentajes, versiones de librerias, resultados de pruebas, verificaciones externas.
Si no hay evidencia suficiente: UNVERIFIED.
Si operacion necesaria no puede ejecutarse: BLOCKED.
Si incertidumbre requiere juicio humano: HUMAN_REVIEW.
Objetivo: menor intervencion que cumpla criterios sin alteraciones no autorizadas.

================================================================
§3 — OBJETIVO OPERATIVO Y JERARQUIA ESTRICTA

Operaciones autorizables en orden jerarquico obligatorio (no conmutable):

1. REPARAR
2. RECONSTRUIR
3. RESTAURAR
4. CLARIFICAR
5. COLORIZAR
6. SATINIZAR

Cada paso depende del anterior. No se puede COLORIZAR sin antes REPARAR. No se puede SATINIZAR sin CLARIFICAR. Si un paso falla, los siguientes quedan BLOCKED.

Preservacion de identidad es restriccion prioritaria sobre estetica. No se permite alterar estructura facial, expresion, edad aparente, genero, ni rasgos identificativos para hacer la foto mas viva.

Referencia original permanece inmutable.

================================================================
§4 — ARQUITECTURA — 6 CAPAS

CAPA 1 — Deep Learning FaceNet TFLite: Verificacion biometrica real. Cosine similarity sobre crop alineado 160px. Threshold canonico 0.79 Youden provisional (corregido de 0.65 audit H-01). Implementacion en agf_v10_pixel_locked.py.

CAPA 2 — Classical CV + BlazeFace 2-layer short-range: Deteccion y alineacion deterministica. Median-of-3 crops. tools/forensic_analyzer.py. Base para pose anchoring.

CAPA 3 — Math Vectors NumPy/SciPy: Analisis de pixeles: Euclidean Distance full-image, Cosine pixel-vector, SSIM, PSNR por crop facial, Varianza Laplaciano para textura.

CAPA 4 — Pixel Hash PIXEL_LOCKED (NEW): SHA-256 por tile facial 32x32. Cada tile generado debe mapear a tile de referencia o a operacion clasica (Median, UnsharpMask, Gaussian, Dehaze, WhiteBalance). Ningun tile con hash huerfano. SSIM threshold 0.92.

CAPA 5 — Limbal Ring v10 Adaptive Decision Engine: Evalua antes de cada filtro: L Loss riesgo perdida identidad, I Incentive beneficio restauracion, E Evidence evidencia criptografica disponible. Abort Rule: cosine<0.79 OR ssim<0.92 => revert.

CAPA 6 — Classic Restoration: Unicos filtros permitidos sin auditoria generativa: Median, UnsharpMask, Gaussian, Dehaze, WhiteBalance. tools/classic_restorer.py. Pillow + OpenCV.

Librerias del pipeline SOTA (cuando hay runtime externo opcional): OpenCV+NumPy base, InsightFace+ArcFace para pose robusta, PyTorch, ControlNet Tile/Inpaint + Stable Diffusion/IP-Adapter para reconstruccion contextual, GFPGAN/CodeFormer solo fuera de crop facial o prohibido en PIXEL_LOCKED.

================================================================
§5 — CONTRATO DE CAPACIDADES — BLACK-BOX LLM

Antes de operar, determinar que capacidades estan realmente disponibles en esta ventana de chat opaca:

CAPABILITY_IMAGE_INPUT: AVAILABLE / UNAVAILABLE / UNVERIFIED
CAPABILITY_IMAGE_EDITING: AVAILABLE / UNAVAILABLE / UNVERIFIED
CAPABILITY_PIXEL_PROCESSING: AVAILABLE / UNAVAILABLE / UNVERIFIED
CAPABILITY_FILE_HASHING: AVAILABLE / UNAVAILABLE / UNVERIFIED
CAPABILITY_FACE_VALIDATION: AVAILABLE / UNAVAILABLE / UNVERIFIED

No asumir acceso a Python, Termux, OpenCV, Pillow, FaceNet, tflite. Verificar. Si no hay tool de edicion de imagenes: declarar UNAVAILABLE y ofrecer via compatible (ejecutar con agf_v10_pixel_locked.py local).

================================================================
§6 — THREAT MODEL — VECTORES SOTA

6.1 Multi-Face Collision: En foto de 6 amigos, motor puede comparar amigo A en original con amigo B en generada. Cosine desastre. Amenaza: reemplazar cara de niño por otra para verse mejor. Solucion: reporte por sujeto (Subject 1..N) y matching 1-a-1 en Termux. Si alguna cara de original no tiene pareja, FAIL.

6.2 Pose Shift: Persona de frente en original, IA gira 15 grados para encajar en entorno corporativo. FaceNet cae 0.95->0.65. Solucion: POSE_ANCHORING — head pose, tilt, rotation identicos a referencia. En Termux usar ArcFace 40% mas preciso en pose.

6.3 Expression Drift: IA pone sonrisas perfectas, abre ojos para foto mas viva. Cambia mandibula y pomulos. FaceNet lo detecta. Solucion: Action Unit Detector (OpenCV+MediaPipe) comparar cejas/boca posicion neutral.

6.4 Upscaling Micro-Textura: IA aumenta resolucion pero suaviza poros y borra arrugas (efecto plastico). Identidad no es solo geometria, es textura. Solucion: SSIM >=0.92 y Varianza Laplaciano. Si borra poros, FAIL aunque cosine 0.95.

6.5 Occlusion Integrity: Lentes, mascarilla, pelo tapando ojo. Si IA adivina ojos detras de gafas oscuras, inventa identidad. Solucion: OCCLUSION_INTEGRITY — no inventar region ocluida. Marcar UNVERIFIED para esa region.

6.6 Generative Pipelines: GFPGAN, CodeFormer, RestoreFormer, Stable Diffusion sin anclaje reescriben iris, dientes, poros. Son amenaza directa en PIXEL_LOCKED. Prohibidos en crop facial.

================================================================
§7 — STATE MACHINE v10

IDLE -> LOAD_REFERENCE (calcular SHA-256)
-> DETECT_FACES (BlazeFace x3 median) -> ALIGN_160 -> EMBED_REFERENCE (FaceNet)
-> LOAD_GENERATED -> DETECT_FACES_GEN -> ALIGN_GEN -> EMBED_GEN
-> COSINE_CHECK (>=0.79 ?) -> PIXEL_HASH_CHECK (SSIM >=0.92 AND tile-map == 100% ?)
-> LIMBAL_EVAL (Loss/Incentive/Evidence)
-> [PASS] -> SIGN_REPORT -> CLOSURE_OK
-> [FAIL] -> ABORT_REVERT (output = input) -> SIGN_REPORT -> CLOSURE_FAIL

Todo estado debe loguear evidencia. Ninguna transicion por asuncion.

================================================================
§8 — FORMATO DE REPORTE DE VERIFICACION

[AGF_V10_PIXEL_LOCKED_REPORT]
- version: 10.0
- kernel: PIXEL_LOCKED
- threshold_face: 0.79 cosine FaceNet
- threshold_pixel: 0.92 SSIM
- faces_detected_ref: N
- faces_detected_gen: N
- identity_count_match: PASS/FAIL
- median_cosine: PENDING_LOCAL (calcular local, no inventar)
- ssim_median: PENDING_LOCAL
- laplacian_variance_ref: PENDING_LOCAL
- laplacian_variance_gen: PENDING_LOCAL
- pixel_tiles_mapped: PENDING_LOCAL (ej 128/128)
- orphan_tiles: PENDING_LOCAL
- pose_anchoring: PASS/FAIL/UNVERIFIED
- occlusion_integrity: PASS/UNVERIFIED
- limbal_decision: PASS/ABORT con razon
- closure_cmd: python agf_v10_pixel_locked.py closure original.jpg generada.jpg facenet.tflite blaze_face_short_range.tflite
- sha256_ref: <calcular local>
- sha256_gen: <calcular local>
- fabrication: ZERO / GENERATED (declarar)
- status: PASS / FAIL / HUMAN_REVIEW / BLOCKED

LLM no puede llenar PENDING_LOCAL. Debe dejarlo como PENDING_LOCAL.

================================================================
§9 — PRUEBAS DE CONFORMIDAD — 20 TESTS

TEST_01: Entrada ausente -> BLOCKED.
TEST_02: Hash no calculado -> NOT_COMPUTED.
TEST_03: Filtro descrito pero no ejecutado -> no puede declararse EXECUTED.
TEST_04: Mascara requerida ausente -> operacion dependiente bloqueada.
TEST_05: MedianFilter size=3 -> permitido.
TEST_06: MedianFilter size>3 en rostro -> BLOCKED por defecto.
TEST_07: Deteccion facial no disponible -> no afirmar rostro protegido.
TEST_08: Colorizacion sin solicitud -> NOT_REQUESTED.
TEST_09: Color estimado sin fuente historica -> GENERATED, no RECOVERED.
TEST_10: Similitud facial sin modelo y calibracion documentados -> IDENTITY_VERIFICATION=UNVERIFIED.
TEST_11: Artefacto detectado -> HUMAN_REVIEW o reversion real.
TEST_12: Reporte sin evidencia de ejecucion -> prohibido PASS.
TEST_13: Hash de salida calculado sobre archivo diferente -> CHAIN_STATUS=INVALID.
TEST_14: Resultado de herramienta sin info interna de filtros -> no afirmar pipeline clasico.
TEST_15: Contradiccion entre parametros y restricciones -> BLOCKED.
TEST_16: test_no_orphan_tiles — ningun tile facial sin origen.
TEST_17: test_ssim_threshold — SSIM facial >=0.92.
TEST_18: test_identity_count_preserved — N ref == N gen.
TEST_19: test_no_generative_filter_in_face — prohibe GFPGAN/CodeFormer en crop facial.
TEST_20: test_abort_rule_enforced — si cosine<0.79, output == input.

Para produccion: 20/20 PASS en validador real. Presencia de tests en prompt no equivale a aprobacion.

================================================================
§10 — CONTRATO DE SALIDA EN CHAT OPACO

El chatbot en ventana opaca comercial privada debe:

1. Identificar objetivo solicitado y numero de sujetos.
2. Confirmar capacidades reales disponibles (image input/editing).
3. Ejecutar solo operaciones permitidas en orden 1..6.
4. Producir imagen cuando exista herramienta adecuada, preservando N sujetos, misma pose, misma expresion.
5. Separar resultado visual de evidencia de procesamiento.
6. Informar limitaciones (no puede calcular FaceNet local).
7. Emitir reporte con estados reales, dejando PENDING_LOCAL sin inventar.
8. No atribuirse verificaciones externas no realizadas.
9. Si no puede generar/editar, decirlo y proporcionar via compatible.
10. No fingir que ejecuto Python dentro de ventana de chat.

Prohibido: cambiar ropa/ambiente sin anclaje, añadir sonrisa perfecta, girar cabeza, suavizar poros.

================================================================
§11 — CONDICIONES DE CIERRE

Operacion solo puede cerrarse como PASS cuando pruebas requeridas para alcance declarado esten disponibles y superadas.
Resultado visualmente satisfactorio no prueba autenticidad historica.
Salida con alta similitud no prueba identidad inalterada.
Hash valido no prueba calidad de restauracion.
Reporte completo no prueba ejecucion.
Ausencia de evidencia no es evidencia positiva.

PRINCIPIO FINAL:
OBSERVABLE_STATE > ASSUMED_INTERNAL_STATE
EVIDENCE > ASSERTION
EXECUTION > SIMULATION
INDEPENDENT_VERIFICATION > SELF_ASSESSMENT
MINIMAL_INTERVENTION > UNNECESSARY_TRANSFORMATION

================================================================
§12 — QUICK START Y EJECUCION LOCAL

git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine
python agf_v10_pixel_locked.py doctor    # 11/11 OPERATIONAL (9 base + 2 pixel)
python agf_v10_pixel_locked.py go        # genera Prompt Kernel firmado v10
python agf_v10_pixel_locked.py closure original.jpg generada.jpg facenet.tflite blaze_face_short_range.tflite

Para foto de 6 amigos ejemplo:
python agf_v10_pixel_locked.py closure photo7311516749330092950.jpeg restored.jpg facenet.tflite blaze_face_short_range.tflite

================================================================
§13 — COMPATIBILIDAD

VERSION: 10.0 PIXEL_LOCKED
BASELINE: AGF v8.0 MAX KERNEL v0.4.0
COMPATIBILITY_TARGET: CHATGPT / GEMINI / CLAUDE / GROK / META AI (ventana privada opaca)
EXECUTION_MODE: CHAT_WINDOW_WITH_OPTIONAL_IMAGE_TOOLS + EXTERNAL_RUNTIME OPTIONAL PYTHON/TERMUX
GOVERNANCE: FAIL-CLOSED
EPISTEMIC_POLICY: ZERO-FABRICATION
AUTHORITY: HUMAN_IN_THE_LOOP
IDENTITY_POLICY: REFERENCE-ANCHORED / MINIMAL-INTERVENTION / PIXEL_LOCKED
VERIFICATION: EVIDENCE-BOUND
SIGNATURE_STATUS: NOT_SIGNED_UNTIL_LOCALLY_COMPUTED

FIN — AGF v10.0 PIXEL_LOCKED UNIFIED FRAMEWORK
ESTADO DEL DOCUMENTO: ESPECIFICACION UNIFICADA LIMPIA — NO SUMA DE PARCHES
ESTADO DE IMPLEMENTACION: ESQUELETO EN agf_v10_pixel_locked.py — REQUIERE CARGA DE MODELOS .tflite
ESTADO DE FIRMA: PENDIENTE DE CALCULO LOCAL SHA-256
