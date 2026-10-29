# Benchmark Report: AI Restoration & Identity Preservation (October 2026)

## Overview
This document records the results of auditing 4 different commercial AIs (Meta AI, Grok, Gemini, Dola) using the AGF SMHP Protocol (v0.7.0). The goal was to evaluate how these AIs handle identity preservation and texture integrity when changing the background.

## Methodology
- **Original Input:** A selfie with specific wardrobe lighting (dark background).
- **Prompt:** "Change the background to a bright corporate office. Do not alter the subject's lighting, facial features, or skin texture."
- **Validation:** `tools/smhp_validator.py` (SSIM for texture + FaceNet for identity).

## Results Matrix

| AI Engine | Identity (FaceNet) | Texture (SSIM) | Lighting Shift | SMHP Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Gemini (Google)** | 0.8453 (PASS) | 0.6417 (FAIL) | 49.69% (FAIL) | ⚠️ HUMAN_REVIEW |
| **Meta AI** | 0.8035 (PASS) | 0.0955 (FAIL) | 49.44% (FAIL) | ⚠️ HUMAN_REVIEW |
| **Grok (xAI)** | 0.7533 (FAIL) | 0.2087 (FAIL) | 50.11% (FAIL) | ❌ BLOCKED |
| **Dola AI** | 0.7493 (FAIL) | 0.5696 (FAIL) | 68.06% (FAIL) | ❌ BLOCKED |

## The "Generative Smoothing" Problem
All tested AIs failed to preserve micro-texture (SSIM < 0.90). Meta AI was the most aggressive, destroying 90% of the original texture (SSIM 0.0955), resulting in a "plastic skin" effect.

## The Lighting Normalization Paradox
When we applied `lighting_normalizer.py` to the generated images, the FaceNet Cosine Similarity actually *decreased* for Gemini and Meta AI. 
- **Conclusion:** Normalization fixes color distribution, but if the AI has already destroyed the facial geometry/texture, the image cannot be recovered. Generative Smoothing is an irreversible damage.

## Final Verdict
None of the commercial AIs tested are safe for forensic identity preservation without strict operator oversight. Gemini is the closest to a "cosmetic" pass, but still requires HUMAN_REVIEW due to texture loss.
