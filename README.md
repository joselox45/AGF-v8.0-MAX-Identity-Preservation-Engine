# AGF v12.2 - Identity Preservation Engine (INDUSTRIAL)
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

## Usage with Chatbots (Kernel v0.8.4)
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
The API () now extracts the exact reason from the scorer's . If the engine blocks an image (e.g., no face detected), the API returns HTTP 200 with . This provides full transparency without crashing.

## Transparent Fail-Closed API
The API () now extracts the exact reason from the scorer's . If the engine blocks an image (e.g., no face detected), the API returns HTTP 200 with . This provides full transparency without crashing.


## Transparent Fail-Closed API
The API (`api_server.py`) now extracts the exact reason from the scorer's `stdout`. If the engine blocks an image (e.g., no face detected), the API returns HTTP 200 with a `BLOCKED` verdict and the exact `reason`. This provides full transparency without crashing.

## AGF Validation Pyramid (X-in-the-Loop)
The AGF architecture follows the industry-standard X-in-the-Loop validation methodology:

1. **MIL (Model-in-the-Loop):** The Chat Kernel (v0.8.8). The LLM simulates compliance but does not calculate metrics.
2. **SIL (Software-in-the-Loop):** The Web UI (). Simulates the dashboard for user experience.
3. **PIL (Processor-in-the-Loop):** The Flask API + ONNX runtime executing on the Android processor.
4. **HIL (Hardware-in-the-Loop):** The full forensic engine () running with real models (ArcFace, Fourier) on physical hardware.
5. **Digital Twin:** The immutable evidence stored in  with SHA-256 hashes.

Only HIL and Digital Twin results are considered valid for identity preservation. MIL and SIL are for development and visualization.

## Phase Certification Protocol (Kernel v0.9.0)
The Kernel now forces the LLM to self-classify its validation phase (MIL, SIL, PIL, HIL). This prevents the LLM from claiming it verified the identity when it only generated the image. The API and Termux engine operate in the HIL (Hardware-in-the-Loop) phase.
