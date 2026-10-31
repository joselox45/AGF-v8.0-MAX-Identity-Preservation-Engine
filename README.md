# AGF v12.4.5.10 - Identity Preservation Engine (STRONG)
**Fail-Closed. Zero-Fabrication. Human-in-the-Loop.**

> `LEGACY: The repo name says v8.0-MAX. Current version is v12.4.5.10-STRONG. See VERSION_MANIFEST.md.`

> **Status:** AUDITED (AKADI 22.0 + Grok) · PATCHED (P0+P1) · PHASE-CERTIFIED (MIL/SIL/PIL/HIL)
> **Independent Benchmark:** UNVERIFIED (honest disclosure)

**Fail-Closed. Zero-Fabrication. Human-in-the-Loop.**

> *Audit AKADI 22.0: P0 patches applied. See `docs/evidence/AUDIT_AKADI_RESPONSE.md`.*

AGF is a forensic-grade identity verification engine designed to audit AI-generated images (Meta AI, Grok, ChatGPT, Stable Diffusion). It does not trust what the LLM claims; it verifies identity, texture, structure, and metadata locally.

## The Technical Difference: Semantics vs. Pixels
- **The Chatbot (LNM):** A blind generator. It "sees" latent tokens, not pixels. It cannot compute mathematical metrics. Its only job is to apply the Trigger (`/repara` or `/preserva`) and declare that it has no physical hardware.
- **The Human (Termux):** The forensic judge. It decompresses the file, reads the real pixel matrix, and applies the mathematical layers to verify historical truth.

## Quick Installation (Clone & Run)
```bash
git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine
pip install numpy pillow onnxruntime tflite-runtime
./tools/fetch_models.sh
```
*(Note: You must place `arcface.onnx` in the root manually).*

## Canonical Path in Termux
The LLM only generates. Termux audits with forensic layers. The system seals everything in `termux_sealed/`.

```bash
# Preservation Mode (Modern photos)
./agf.sh preservation original_photo.jpg generated_photo.jpg

# Restoration Mode (Old damaged photos)
./agf.sh restoration old_photo.jpg restored_photo.jpg
```

## Forensic Architecture (Sovereign Weighted Score)
The core engine computes a weighted score over 5 mathematical layers:

1. **ArcFace (40%):** 3D facial identity. *(Extreme Veto: < 0.30)*
2. **Fourier 2D (30%):** Frequency signature / anti-hallucination. *(Extreme Veto: < 0.40)*
3. **Edge Shazam (20%):** Facial edge constellation.
4. **SSIM (10%):** Structural pixel similarity.
5. **Color Fingerprint (5%):** HSV chromatic hue.

Plus 2 complementary diagnostic layers:
- **Metadata (XMP):** Warns if the image has an AI signature (does not block).
- **Overlay Diff:** Generates a visual heatmap for human review (does not add to score).

## Web Interface (Visual Dashboard)
```bash
python -m http.server 8080
# Open in Chrome: http://localhost:8080/agf_ui.html
```

## Usage with Chatbots (Kernel v0.9.5)
To prevent LLMs from ignoring the rules, use Slash Triggers. The LLM must return a JSON declaring it has no physical sensor.

- `/repara` → Activates RESTORATION MODE.
- `/preserva` → Activates PRESERVATION MODE.

## Governance Rules
# 1. **LLMs lie:** Never trust a PASS that a chatbot gives itself.
# 2. **Local Verification:** All metrics must be computed in Termux.
# 3. **Human-in-the-Loop:** If the system says `HUMAN_REVIEW`, you decide.

## Derivation Policy
This repository uses **Git tags for versioning**. Cryptographic signing (GPG) is not currently implemented. Forks and open derivations are allowed under the MIT License. See `DERIVATIONS.md` for the full policy.

*Private Repository. Biometric models in .gitignore. Physical schemas in schemas/.*
## Scale Normalization
For AI-generated images, always normalize the scale before auditing to avoid false negatives.
```bash
python tools/agf_scale_normalizer.py original_photo.jpg generated_photo.jpg
./agf.sh preservation sandbox/normalized_orig.jpg sandbox/normalized_gen.jpg
```

## Full-Stack Architecture (Web + API)
AGF is not just a CLI. You can run a local Flask API to consume the forensic engine from any web or mobile app.
1. Start the API: `python api_server.py` (runs on http://0.0.0.0:8000)
2. Start the Web UI: `python -m http.server 8080`
3. Open Chrome at: `http://localhost:8080/agf_ui.html`
The Web UI now uses `fetch()` to send cropped images to the Flask backend and displays the REAL ONNX metrics (no more simulation).


## Advanced Diagnostics (Termux)
Beyond the 5 weighted layers, the repository includes secondary forensic tools:
- `tools/agf_base64_diff.py`: Binary flow analysis (Base64 Differential).
- `tools/agf_lighting_forensic.py`: Light physics and shadow consistency.
- `tools/agf_overlay_diff.py`: Visual heatmap of alterations.

## Audit Status (AKADI 22.0)
The repository has been audited and patched:
- P0 (Critical): Fixed API Fail-Closed, Crash handling, Identity Floor (0.65/0.55), and Weights sum (1.0).
- P1 (Technical Debt): Fourier 2D now aligns faces with BlazeFace before FFT. API URL in the Web UI is dynamic. Dependencies updated.

### Running Tests
python -m unittest discover tests

## Layer 0: Tiling Detection (P1 Patch)
For full-body or group photos where faces are small, AGF uses a Tiling Detector. It divides the image into a 3x3 grid, detects faces in each tile, applies Non-Maximum Suppression (NMS) to remove duplicates, and filters out low-variance (blurry/fake) detections. If no valid faces are found, it returns BLOCKED (Fail-Closed).

## Transparent Fail-Closed API
The API (`api_server.py`) now extracts the exact reason from the scorer's `stdout`. If the engine blocks an image (e.g., no face detected), the API returns HTTP 200 with a `BLOCKED` verdict and the exact `reason`. This provides full transparency without crashing.

## AGF Validation Pyramid (X-in-the-Loop)
The AGF architecture follows the industry-standard X-in-the-Loop validation methodology:

1. **MIL (Model-in-the-Loop):** The Chat Kernel (v0.9.5). The LLM simulates compliance but does not calculate metrics.
2. **SIL (Software-in-the-Loop):** The Web UI (). Simulates the dashboard for user experience.
3. **PIL (Processor-in-the-Loop):** The Flask API + ONNX runtime executing on the Android processor.
4. **HIL (Hardware-in-the-Loop):** The full forensic engine () running with real models (ArcFace, Fourier) on physical hardware.
5. **Digital Twin:** The immutable evidence stored in  with SHA-256 hashes.

Only HIL and Digital Twin results are considered valid for identity preservation. MIL and SIL are for development and visualization.

## Phase Certification Protocol (Kernel v0.9.0)
The Kernel now forces the LLM to self-classify its validation phase (MIL, SIL, PIL, HIL). This prevents the LLM from claiming it verified the identity when it only generated the image. The API and Termux engine operate in the HIL (Hardware-in-the-Loop) phase.

## Independent Benchmark Status
**Status:** UNVERIFIED / PENDING EXTERNAL

- **FAR/FRR (Face Recognition):** Not measured on standard datasets (LFW, CFP, AgeDB). Thresholds 0.7825 (PASS) and 0.6325 (REVIEW) are heuristic, calibrated on the author's local corpus.
- **Adversarial Robustness:** Not tested against sophisticated face-swap (FaceSwap, DeepFaceLab) or adversarial embeddings.
- **Corpus Size:** ~30 images (wedding, family, damaged photos). Not statistically significant.

**What this means:** AGF is production-ready for a single-operator workflow (family photo restoration), but **NOT certified for enterprise identity verification** until independent benchmarks are published.


## Repository Privacy Status
The repository is **PRIVATE**. Anonymous HTTP requests to raw.githubusercontent.com return 404. This is **intentional privacy behavior**, not a technical failure. Auditors must be invited as collaborators to access the full source.
## Full 9-Layer Audit (Hierarchical)
For deep forensic analysis, use `./agf_full.sh <orig> <gen> <mode>`. This runs all 9 layers but respects the hierarchy:
- **Filters (No Block):** Metadata (only on generated image), Tiling.
- **Diagnostics (No Score):** Lighting, Base64 Differential.
- **Final Judge (Score):** ArcFace, Fourier, Shazam, SSIM, Color, Overlay.

**Important:** Metadata from the original is ignored (social media adds FBMD). The final verdict (PASS/BLOCKED) depends ONLY on the weighted score.


## SIL Weighted Score (Kernel v0.9.4)
The Kernel now allows the LLM to compute a `SIL_SCORE` (Software-in-the-Loop) using its Python Sandbox and Latent Vectors (SSIM, Semantic Similarity, Color, Fourier).

**Important:** The SIL_SCORE is a diagnostic metric only. It does NOT replace the HIL (Hardware-in-the-Loop) truth computed by Termux with the real ArcFace model. The LLM MUST declare `metrics_missing: ["arcface"]` if it cannot access the 167MB model. Zero-Fabrication remains enforced.

## Case Study 11: SIL (Chatbot) vs HIL (Termux) Contradiction
This case demonstrates why the Kernel prohibits LLMs from self-validating identity.

- **Chatbot (MIL/SIL phase):** Declared `HUMAN_REVIEW` because it could not access the ArcFace model. Its `SIL_SCORE` (simulated) was 0.895.
- **Termux (HIL phase):** Computed the real `HIL_SCORE` with ArcFace (167MB). Result: **0.8045 (PASS)**.

**Conclusion:** The SIL_SCORE is a diagnostic estimate. The HIL_SCORE is the mathematical truth. Only Termux can certify identity preservation. See `docs/evidence/CASE_11_SIL_VS_HIL.md`.

---

## Current Status
- **Engine:** v12.4.5.10 (Audited, Phase-Certified, Strong Conditioning)
- **Kernel:** v0.9.5 (Strong Conditioning)
- **Tests:** 120/120 passing
- **Audits:** AKADI 22.0 (P0+P1 patched) + Grok (versioning + benchmark disclosure)
- **Repository:** Public for external AI auditing (no biometric data in tree)


## Kernel v0.9.5 (Strong Conditioning)
The Kernel now enforces a strict JSON schema for LLM outputs (Hard Conditioning). The LLM MUST return the exact schema or the local API will reject the response. This prevents the LLM from hallucinating fields or bypassing the Fail-Closed governance.

### Cloud-Native Architecture
A `Dockerfile` and `docker-compose.yml` are included for VPS deployment (AWS, Hetzner, DigitalOcean) with MinIO for evidence storage and Prometheus for monitoring.

### Anexo A — Contratos de identidad complejos

Para contratos de identidad que incluyan:
- Multi-sujeto (varias personas en la misma imagen)
- Restricciones por rasgo facial específico
- Anti-beautification (deriva cosmética)
- Token CPEP_IDENTITY_PRESERVATION_FAILED

Ver `docs/governance/IDENTITY_LOCK_v1.5.md` **Anexo A**. Ese anexo NO redefine veredictos: el enum `verdict` sigue siendo `{HUMAN_REVIEW, PENDING_LOCAL_VERIFICATION, BLOCKED}`. `PASS` sigue prohibido.

### Anexo B — Honestidad epistémica y trazabilidad de cadena

Para honestidad epistémica de cadenas multi-turno:
- `trace_verification_status`: EXACT / UNVERIFIABLE / PARTIAL
- `recollection_approximate`: separado de `previous_snapshots`
- `retroactive_declarations`: cierre honesto de cadenas fabricadas
- `citations_status`: 5 estados de evidencia externa

Ver `docs/governance/IDENTITY_LOCK_v1.5.md` **Anexo B**. Ese anexo NO modifica veredictos: el enum `verdict` sigue siendo `{HUMAN_REVIEW, PENDING_LOCAL_VERIFICATION, BLOCKED}`. `PASS` sigue prohibido.

### Anexo C — Niveles de condicionamiento (weak vs strong)

Contrato de entrada formalizado:
- **weak_semantic**: el LLM recibe base64 (tokens alfanuméricos). Puede inferir semántica aproximada, NO leer píxeles.
- **strong_pixel**: proceso Python descomprime a `float32[H,W,3]`. Puede medir geometría, texturas, embeddings.
- **HIL**: hardware + modelos reales (Termux + ArcFace). Único que certifica identidad.

5 prohibiciones explícitas para el LLM en `weak_semantic`:
1. NO declarar "he visto la imagen" cuando solo recibió base64.
2. NO fabricar métricas que requieran píxeles (pixel_mean, box, cosine, SSIM).
3. NO afirmar detección de caras como si fuera real.
4. NO declarar `metrics_missing: []` si los modelos no están disponibles.
5. NO emitir `PASS` (kernel v0.9.5 sección 6).

Ver `docs/governance/IDENTITY_LOCK_v1.5.md` **Anexo C**. `PASS` sigue prohibido.

### Docs adicionales de gobernanza

- `docs/governance/MIL_VS_HIL_VERDICT_SCOPE.md`: aclaracion del alcance de PASS en MIL (prohibido) vs HIL (valido con umbrales + humano).
- `docs/governance/PRUNE_AUDIT_2026-10-31.md`: auditoria de poda (repo correctamente dimensionado, sin poda de corpus/evidence justificada).
