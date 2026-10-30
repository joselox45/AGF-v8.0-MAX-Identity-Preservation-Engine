# AGF v12.2 - Identity Preservation Engine (INDUSTRIAL)
**Fail-Closed. Zero-Fabrication. Human-in-the-Loop.**

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
This repository is **frozen and cryptographically signed**. However, forks and open derivations are allowed under the MIT License. See `DERIVATIONS.md` for the full policy.

*Private Repository. Biometric models in .gitignore. Physical schemas in schemas/.*