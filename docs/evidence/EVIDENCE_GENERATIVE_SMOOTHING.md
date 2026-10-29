# Evidence Report: Generative Smoothing Detection (AGF v11.0)

## Context
This document records the empirical proof that commercial AI models (e.g., Gemini) destroy skin texture (Generative Smoothing) during restoration, even when facial geometry is preserved.

## Methodology
- Original Image: `sandbox/base0_test.png`
- Generated Image: `sandbox/gemini_norm.png`
- Validator: `tools/verif_local.py` (Pillow + NumPy, No OpenCV)

## Results
- **Laplacian Variance (Original):** 157.95
- **Laplacian Variance (Generated):** 43.17
- **Texture Loss:** 72.67% (Threshold: < 10%)
- **SSIM Global:** 0.6443 (Threshold: > 0.90)
- **Verdict:** ❌ HUMAN_REVIEW (Generative Smoothing detected)

## Conclusion
While FaceNet (geometry) gave a PASS (0.8453), the Local Verifier (texture) detected a 72.67% loss of skin detail. This proves that identity preservation requires not only facial geometry checks but also texture integrity checks (SSIM / Laplacian). 
