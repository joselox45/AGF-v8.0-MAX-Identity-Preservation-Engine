"""
AGF T21-ALIGN — TFLiteFaceDetector con decodificador BlazeFace real.
Requiere face_detection_short_range.tflite (MediaPipe, 128x128).
Fail-closed: sin modelo -> BLOCKED.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

from blazeface_decoder import generate_anchors, decode, nms


@dataclass
class DetectionResult:
    status: str                    # PASS | BLOCKED | FAIL
    detections: Optional[list] = None
    reason: str = ""


class TFLiteFaceDetector:
    INPUT_SIZE = 128

    def __init__(self, model_bytes: Optional[bytes] = None):
        self._interp = None
        self.anchors = generate_anchors()
        if model_bytes:
            self._load(model_bytes)

    def _load(self, model_bytes: bytes) -> None:
        try:
            from tflite_runtime.interpreter import Interpreter  # type: ignore
        except ImportError:
            try:
                from tensorflow.lite.python.interpreter import Interpreter  # type: ignore
            except ImportError:
                self._interp = None
                return
        import tempfile, os
        try:
            with tempfile.NamedTemporaryFile(suffix=".tflite", delete=False) as f:
                f.write(model_bytes)
                path = f.name
            self._interp = Interpreter(model_path=path)
            os.unlink(path)
            self._interp.allocate_tensors()
            outs = sorted(self._interp.get_output_details(),
                          key=lambda d: d["shape"][-1])
            self._reg_idx = outs[-1]["index"]      # (1,896,16)
            self._cls_idx = outs[0]["index"]       # (1,896,1)
            self._in_idx = self._interp.get_input_details()[0]["index"]
        except Exception:
            self._interp = None

    def detect(self, rgb_pixels: Optional[Sequence] = None,
               score_threshold: float = 0.7) -> DetectionResult:
        if self._interp is None or rgb_pixels is None:
            return DetectionResult("BLOCKED", None,
                                   "sin detector TFLite o sin pixeles; fail-closed")
        try:
            import numpy as np  # type: ignore
            arr = np.asarray(rgb_pixels, dtype=np.float32)
            orig_h, orig_w = arr.shape[:2]
            h = w = self.INPUT_SIZE
            ys = (np.arange(h) * (orig_h / h)).astype(int).clip(0, orig_h - 1)
            xs = (np.arange(w) * (orig_w / w)).astype(int).clip(0, orig_w - 1)
            inp = arr[ys][:, xs] / 255.0
            self._interp.set_tensor(self._in_idx, np.expand_dims(inp, 0))
            self._interp.invoke()
            reg = self._interp.get_tensor(self._reg_idx).reshape(896, 16)
            cls = self._interp.get_tensor(self._cls_idx).reshape(896, 1)
            dets = decode(reg, cls, self.anchors,
                          input_size=self.INPUT_SIZE,
                          score_thresh=score_threshold)
            dets = nms(dets)
            sx = orig_w / self.INPUT_SIZE
            sy = orig_h / self.INPUT_SIZE
            for d in dets:
                x1, y1, x2, y2 = d.box
                d.box = (x1 * sx, y1 * sy, x2 * sx, y2 * sy)
                d.keypoints = [(kx * sx, ky * sy) for kx, ky in d.keypoints]
            return DetectionResult("PASS", dets, f"{len(dets)} rostro(s)")
        except Exception as e:
            return DetectionResult("FAIL", None, str(e))
