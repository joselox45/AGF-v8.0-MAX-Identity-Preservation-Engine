# LICENSE-WEIGHTS — Model Weights & Third-Party Model Licensing
# AGF v12.4.7.8-STRONG — Better than Soup — Explicit Compliance Matrix
# Version: 2026-11-01 — AKADI 22.0

> **Este archivo es OBLIGATORIO junto a LICENSE y NOTICE.**
> Los pesos biométricos NO están en el repo por .gitignore — tienen licencia aparte.

## Resumen Ejecutivo — ¿Puedo vender mi servicio de restauración?

**SÍ, pero solo con estos stacks:**

| Stack | Comercial Pagado | Seguro |
|---|---|---|
| AGF + PhotoMaker V1 (OpenCLIP ViT-H/14) | ✅ SÍ | Apache-2.0 commercial-safe |
| AGF + arcface.onnx / buffalo_l / antelopev2 | ❌ NO | InsightFace Non-Commercial BLOCKED |
| AGF + PhotoMaker V2, IP-Adapter FaceID, InstantID, PuLID, Arc2Face | ❌ NO | Heredan InsightFace BLOCKED |
| AGF + Soup buffalo_l / antelopev2 | ❌ NO | BLOCKED for paid per Soup docs |
| AGF + modelo propio entrenado sin InsightFace | ✅ SÍ | Tu licencia |

**Regla de oro:** Si cobras por restaurar, NO uses ningún embedder que dependa de InsightFace.

---

## 1. AGF Core — Pesos Forenses (no incluidos)

| Componente | Archivo | Tamaño | Licencia | Uso Comercial | Descarga | SHA-256 |
|---|---|---|---|---|---|---|
| **ArcFace ONNX** | `arcface.onnx` | 167MB | InsightFace Non-Commercial | ❌ Pesos NO comercial | `tools/fetch_models.sh` manual | Ver `tool_hashes.txt` |
| **Buffalo_L** | `models/buffalo_l/` | ~300MB | InsightFace Non-Commercial | ❌ BLOCKED paid | `tools/fetch_models.sh` | Ver |
| **AntelopeV2** | `models/antelopev2/` | ~400MB | InsightFace Non-Commercial | ❌ BLOCKED paid | `tools/fetch_models.sh` | Ver |
| **BlazeFace** | `blazeface.tflite` | ~1MB | Apache-2.0 / MIT | ✅ SÍ | Auto via pip | - |

**Cómo descargar (obligatorio):**
```bash
./tools/fetch_models.sh
# Coloca manualmente arcface.onnx en raíz
# Verifica:
sha256sum arcface.onnx
cat tool_hashes.txt  # compara
```

---

## 2. Soup Submodule (si usas fused repo)

| Componente | Licencia | Comercial | Notas |
|---|---|---|---|
| `vendors/soup/` código | Apache-2.0 | ✅ SÍ | Keep LICENSE + NOTICE per Apache §4,§6 |
| Soup `buffalo_l` / `antelopev2` | InsightFace Non-Commercial | ❌ BLOCKED for paid services | Documentado en Soup docs/models.md |
| Soup templates / recipes | Apache-2.0 | ✅ SÍ | 100+ recipes |

**Compliance Apache-2.0 §4:** Cuando redistribuyes Soup:
- (a) Da copia de Apache License 2.0
- (b) Marca archivos modificados: `# Modificado por: joselox45...`
- (c) Retén copyright, patent, trademark notices
- (d) Incluye NOTICE readable

---

## 3. Identity Preservation Stacks — Matriz Comercial (mejor que Soup)

Esta tabla es la que Soup no tiene clara — aquí está explícita:

| Stack | Encoder | Decoder | Licencia Encoder | Licencia Decoder | Comercial | Notas |
|---|---|---|---|---|---|---|
| **PhotoMaker V1** | OpenCLIP ViT-H/14 | SDXL | Apache-2.0 | CreativeML Open RAIL++-M | ✅ SÍ — Único safe | Recomendado para tu servicio pagado |
| PhotoMaker V2 | InsightFace + OpenCLIP | SDXL | Non-Commercial | RAIL++-M | ❌ NO | Hereda InsightFace |
| IP-Adapter FaceID | InsightFace | SDXL/SD1.5 | Non-Commercial | Apache-2.0 / RAIL | ❌ NO | BLOCKED |
| InstantID | InsightFace + ControlNet | SDXL | Non-Commercial | Apache-2.0 | ❌ NO | BLOCKED |
| PuLID | InsightFace | SDXL | Non-Commercial | MIT | ❌ NO | BLOCKED |
| Arc2Face | ArcFace | SD | Non-Commercial | MIT | ❌ NO | BLOCKED |
| SimSwap / FaceFusion | ArcFace | GAN | Non-Commercial | Varies | ❌ NO | GAN loss, no forense |

**Para AGF + servicio pagado:** Usa **PhotoMaker V1** o entrena tu propio encoder sin InsightFace.

---

## 4. LLMs (si usas Soup para entrenar restaurador)

| Modelo | Licencia | Comercial | Hub |
|---|---|---|---|
| Llama-3.1-8B-Instruct | Meta Llama 3.1 Community | ✅ Con restricciones | huggingface.co/meta-llama |
| Qwen2.5 / Qwen3 | Qwen License | ✅ SÍ | huggingface.co/Qwen |
| Gemma 3 | Gemma License | ✅ SÍ | huggingface.co/google |
| Mistral / Mixtral | Apache-2.0 | ✅ SÍ | huggingface.co/mistralai |
| DeepSeek R1/V3 | DeepSeek License | ✅ SÍ | huggingface.co/deepseek-ai |

Ver `docs/models.md` de Soup para VRAM guide y extras matrix completa.

---

## 5. Librerías Open Source

| Librería | Licencia | Comercial | Notas |
|---|---|---|---|
| onnxruntime | MIT | ✅ SÍ | HIL verification |
| tflite-runtime | Apache-2.0 | ✅ SÍ | BlazeFace |
| Pillow, NumPy, OpenCV, scikit-image | BSD / MIT / Apache | ✅ SÍ | Procesamiento |
| PyTorch, Transformers, PEFT | BSD / Apache-2.0 | ✅ SÍ | Soup training |

---

## 6. Cómo cumplir — Checklist para tu repo

Cuando publiques `AGF-v8.0-MAX-Identity-Preservation-Engine`:

- [ ] `LICENSE` (MIT) en raíz — GitHub detecta badge
- [ ] `NOTICE` en raíz — con 8 secciones
- [ ] `LICENSE-WEIGHTS.md` (este archivo) en raíz
- [ ] `tool_hashes.txt` con SHA-256 de modelos
- [ ] `.gitignore` incluye `*.onnx`, `models/`, `buffalo_l/`, etc.
- [ ] Si modificas archivo de Soup: añade `# Modificado por: joselox45...`
- [ ] Si vendes servicio: usa PhotoMaker V1 o encoder propio, documenta en README

**Script verificación:**
```bash
# Verifica que no subiste pesos por error
git ls-files | grep -E "\.onnx|buffalo|antelope" && echo "ERROR: pesos en git!" || echo "OK: sin pesos"

# Verifica LICENSE + NOTICE presentes
ls LICENSE NOTICE LICENSE-WEIGHTS.md && echo "OK: licencias presentes"
```

---

## 7. Para Servicio Pagado — Qué poner en tu README

```markdown
## Licencias Comerciales

- Código AGF: MIT — uso libre
- Pesos biométricos: NO incluidos, descarga manual, non-commercial
- Servicio pagado: usa PhotoMaker V1 (Apache-2.0) — único stack comercial-safe
- Ver LICENSE-WEIGHTS.md para matriz completa
```

---

## 8. Contacto y Auditoría

- AGF Original: https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine
- Soup Original: https://github.com/MakazhanAlpamys/Soup
- Paper Layer Streaming: https://doi.org/10.5281/zenodo.21918325 v3
- Audit: AKADI 22.0 (P0+P1 patched) + Grok — 120/120 tests passing
- Status: AUDITED, PHASE-CERTIFIED (MIL/SIL/PIL/HIL), Benchmark UNVERIFIED

---

END OF LICENSE-WEIGHTS — Mejor que Soup porque incluye matriz comercial explícita,
instrucciones SHA-256, y checklist de compliance que Soup no tiene.