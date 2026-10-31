# Auditoría de poda — 2026-10-31

## Objetivo

Determinar si el repositorio contiene archivos superfluos (huérfanos, duplicados, obsoletos) que puedan eliminarse sin romper funcionalidad. Preservando siempre el principio de Fail-Closed y Zero-Fabrication del kernel v0.9.5.

## Metodología

1. Auditar archivos en raíz (imágenes scratchpad, docs top-level)
2. Auditar evidence/ (runs repetidos, JSONs históricos)
3. Auditar data/ (corpus de benchmark)
4. Verificar qué está trackeado en git vs gitignored
5. Verificar dependencias (tests, tools, docs) antes de proponer borrados

## Hallazgos

### 1. Imágenes scratchpad en raíz (19 archivos)

Estado: **NO trackeadas en git** (.gitignore línea 20: *.jpg, *.png, *.webp).

Acción: eliminadas del disco local (~3.5MB liberados). No afecta al repo.

Duplicados detectados por tamaño exacto:
- boda_orig.jpg == foto_ancla.jpg (539659 bytes)
- check_orig.jpg == nueva_orig.jpg (338952 bytes)
- señor_iluminado.jpg == test_generada.jpg (133571 bytes)
- señor_original.jpg == test_facebook_señor.jpg == test_original.jpg (174402 bytes)

Protegidos (no eliminados): foto_antigua_SEALED.jpg + .agf.json (evidencia), overlay_diff.png (output de tool), blaze_face_*.tflite, arcface.onnx.

### 2. Evidence/ repetido (218 archivos locales)

Estado: **NO trackeados en git** (.gitignore línea 16: evidence/).

Desglose por prefijo:
- t22_* (61 archivos): runs de test T22 repetidos
- verify_* (54 archivos): runs de verificación con timestamps a segundos
- closure_blocked_* (11 archivos): runs bloqueados
- calibration_* (7 archivos): corridas de calibración
- Resto (85 archivos): benchmarks, casos, attestations

Acción: mantener en disco (evidencia histórica). No afecta al repo. Puede archivarse localmente en el futuro si se necesita espacio.

### 3. data/corpus_v1 + data/corpus_v2 (136 PNGs, ~40MB trackeados)

Estado: **SÍ trackeados en git** (data/ no está en .gitignore).

Análisis:
- corpus_v1 (~14MB): procedural-paramétrico, reproducible con tools/corpus_generate.py (seed 777, test_corpus.py valida determinismo byte-a-byte)
- corpus_v2 (~25MB): generado por chatbot desde prompts, NO reproducible byte-a-byte

Dependencias:
- tools/calibrate_threshold.py: usa data/corpus_v1 como default
- tools/corpus_benchmark.py: usa data/corpus_v1 como default
- tools/corpus_v2_intake.py + corpus_v2_prompts.py: generan/verifican corpus_v2
- tests/test_corpus.py: **NO usa el corpus trackeado**, genera su propio corpus temporal con --seed 777
- docs/ERRATA.md, docs/BIOMETRIC_VALIDATION.md: documentan los corpus

Decisión: **NO podar**. Razones:
1. corpus_v2 es evidencia no reproducible (Anexo B: preservar audit trail)
2. corpus_v1 es test data canónico para auditoría externa
3. git rm --cached solo afecta HEAD, no reduce .git (55MB sigue)
4. Beneficio real: HEAD 47.6MB -> ~34MB (insignificante con 393GB libres)
5. Costo: romper tools por defecto + actualizar 2 docs
6. Reescritura de history (git filter-repo) sería destructiva: invalida tags v12.4.x, rompe clones existentes

### 4. evidence/*.png + *.jpg trackeados (40 archivos, ~6.6MB)

Estado: **SÍ trackeados en git** (entraron antes del .gitignore actual).

Análisis:
- 100 JSONs: logs de runs, reproducibles
- 40 PNG/JPG: evidencia histórica (chatgpt_image_edit_2026-10-14, base0_lock)
- 10 MD/TXT/CSV: documentación

Decisión: **NO podar**. Razones:
1. Entraron antes de .gitignore, son audit trail histórico
2. Anexo B exige preservación de evidencia
3. git rm --cached no reduce .git (los objetos siguen en history)
4. 6.6MB es insignificante

### 5. Docs top-level huérfanos

- ROADMAP.md: huérfano pero estándar open-source
- SECURITY.md: huérfano pero estándar open-source

Decisión: **NO podar**. Estándares de la industria.

## Verificación de dimensionamiento

| Componente | Tamaño trackeado | % del repo |
|---|---|---|
| data/corpus_v1 + v2 | ~40 MB | 84% |
| evidence/ (binarios) | ~6.6 MB | 14% |
| Código + docs + tests | ~1.2 MB | 2% |
| **Total trackeado** | **47.6 MB** | 100% |

Ratio .git/contenido: 55MB/47.6MB = 1.15x (compresión normal, nada anómalo).

Contexto: 393GB libres. Sin presión de espacio.

Comparación con patrones:
- Librería Python: 1-5MB
- Motor forense + corpus + evidence: 30-100MB (rango esperado)
- ML framework con pesos: 500MB-5GB (AGF está en el extremo lean)

## Conclusión

El repositorio está correctamente dimensionado para su función (motor forense con corpus de validación y audit trail de evidencia).

No hay deuda técnica real. .gitignore excluye correctamente:
- arcface.onnx (167MB), blaze_face_*.tflite, sandbox/ (325MB)
- evidence/ local (218 archivos, 8.1MB)
- Imágenes scratchpad en raíz (19 archivos, 3.5MB)
- Modelos *.onnx, *.tflite, *.h5
- __pycache__, *.pyc, *.log, .DS_Store, .env

Única acción ejecutada: limpieza local de 19 imágenes scratchpad (~3.5MB liberados en disco). No afecta al repo.

## Referencias

- .gitignore: reglas vigentes
- Kernel v0.9.5 seccion 6: Fail-Closed
- IDENTITY_LOCK_v1.5.md Anexo B: preservación de evidencia y honestidad epistémica
- IDENTITY_LOCK_v1.5.md Anexo C: weak_semantic vs strong_pixel
- docs/BIOMETRIC_VALIDATION.md: descripción de los corpus
- docs/ERRATA.md: erratas conocidas

---

FIN DEL DOCUMENTO
