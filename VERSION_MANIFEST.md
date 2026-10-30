# AGF Version Manifest - Single Source of Truth

**Last Update:** 2026-10-30
**Status:** AUDITED / PATCHED / PHASE-CERTIFIED

## Current Version Stack

| Component | Version | File |
| :--- | :--- | :--- |
| **Engine Core** | v12.3.5 | `agf.py`, `tools/agf_composite_scorer.py` |
| **Chat Kernel** | v0.9.0-DISRUPTIVE | `docs/governance/AGF_CHAT_KERNEL_v0.9.0_DISRUPTIVE.md` |
| **Frontend UI** | v12.3.5-PHASE-CERTIFIED | `agf_ui.html` |
| **Backend API** | v12.3.4-TRANSPARENT | `api_server.py` |
| **Tiling Detector** | Capa 0 | `tools/agf_tiling_detector.py` |
| **Repository Name** | v8.0-MAX (legacy) | github.com/joselox45/... |

## Naming Convention (Resolution)

The repository name `AGF-v8.0-MAX` is **LEGACY** and should be ignored. The current production version is **v12.3.5-PHASE-CERTIFIED**.

**If you read "v8.0-MAX" anywhere, mentally translate it to "v12.3.5".**

## Model Dependencies (External)

| Model | Size | Status |
| :--- | :--- | :--- |
| `arcface.onnx` | 167 MB | User-supplied (not in repo) |
| `blaze_face_short_range.tflite` | 225 KB | Auto-fetched via `tools/fetch_models.sh` |
| `blaze_face_full_range.tflite` | 1.1 MB | Optional (for full-body detection) |

## Known Limitations (Honest Disclosure)

- **No independent FAR/FRR benchmark:** Thresholds (0.7825 PASS / 0.6325 REVIEW) are heuristic, calibrated on the author's own corpus.
- **No adversarial testing:** Robustness against sophisticated face-swap attacks is not publicly demonstrated.
- **No SHA-256 manifest for arcface.onnx:** The 167MB model's integrity is not auto-verified.
- **"Industrial" is aspirational:** The current state is "production-ready for a single operator", not "certified for enterprise deployment".
