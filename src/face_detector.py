"""
AGF v9.0 — T30: Detector facial TFLite (BlazeFace u otro detector 128x128).
===========================================================================
Prerequisito del benchmark de robustez biométrica: alinear el recorte facial
antes del embedding. Fail-closed: sin modelo -> BLOCKED.
Salida: lista de bbox (x1, y1, x2, y2, score) ordenadas por score.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass
class Detection:
    x1: int; y1: int; x2: int; y2: int
    score: float


@dataclass
class DetectionResult:
    status: str            # PASS | BLOCKED | FAIL
    detections: Optional[list] = None
    reason: str = ""


class TFLiteFaceDetector:
    INPUT_SIZE = 128       # BlazeFace front

    def __init__(self, model_bytes: Optional[bytes] = None):
        self._interp = None
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
            self._in = self._interp.get_input_details()[0]["index"]
            self._out = self._interp.get_output_details()[0]["index"]
        except Exception:
            self._interp = None

    def detect(self, rgb_pixels: Optional[Sequence] = None,
               score_threshold: float = 0.7) -> DetectionResult:
        if self._interp is None or rgb_pixels is None:
            return DetectionResult("BLOCKED", None,
                                   "sin detector TFLite o sin píxeles; fail-closed")
        import numpy as np  # type: ignore
        try:
            arr = np.asarray(rgb_pixels, dtype=np.float32)
            h = w = self.INPUT_SIZE
            ys = (np.arange(h) * (arr.shape[0] / h)).astype(int).clip(0, arr.shape[0]-1)
            xs = (np.arange(w) * (arr.shape[1] / w)).astype(int).clip(0, arr.shape[1]-1)
            arr = arr[ys][:, xs] / 255.0
            self._interp.set_tensor(self._in, np.expand_dims(arr, 0))
            self._interp.invoke()
            raw = np.asarray(self._interp.get_tensor(self._out)).flatten()
            # Formato BlazeFace-approx: pares (score, cx, cy, w, h) por cara
            dets = []
            for i in range(0, len(raw) - 4, 5):
                s, cx, cy, bw, bh = (float(v) for v in raw[i:i+5])
                if s < score_threshold:
                    continue
                x1 = int((cx - bw/2) * arr.shape[1]); y1 = int((cy - bh/2) * arr.shape[0])
                x2 = int((cx + bw/2) * arr.shape[1]); y2 = int((cy + bh/2) * arr.shape[0])
                dets.append(Detection(max(0,x1), max(0,y1),
                                      min(arr.shape[1],x2), min(arr.shape[0],y2), s))
            dets.sort(key=lambda d: -d.score)
            return DetectionResult("PASS", dets, f"{len(dets)} rostro(s)")
        except Exception as e:
            return DetectionResult("FAIL", None, str(e))
