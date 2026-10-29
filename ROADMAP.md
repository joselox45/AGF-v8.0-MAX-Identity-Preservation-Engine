# AGF Roadmap

## v10.0 - The Future (Help Wanted)
- [ ] **ONNX Migration:** Replace `tflite-runtime` with `onnxruntime` to support **ArcFace** or **AdaFace** (99.8% accuracy vs. FaceNet's 97.5%).
- [ ] **Web GUI:** Create a simple `Streamlit` or `Gradio` interface so users don't need to use the terminal.
- [ ] **Batch Processing:** Add support for auditing folders of images instead of one by one.
- [ ] **Classical Fallback:** Fully integrate OpenCV Haar Cascade as a fallback when BlazeFace fails on vintage photos.

## v9.x - Current Stable
- [x] Adaptive Decision Engine (Limbal Ring).
- [x] Kernel v0.3 (Fail-Closed).
- [x] Classical Restorer (Pillow).
## Reference Documents
*   `docs/reference/SOTA_RESTORATION_PIPELINE_GEMINI.md`: A detailed breakdown of the exact generative AI pipeline (GFPGAN, ControlNet) that causes Identity Drift. We use this as our Threat Model to test the AGF engine's auditing capabilities.
