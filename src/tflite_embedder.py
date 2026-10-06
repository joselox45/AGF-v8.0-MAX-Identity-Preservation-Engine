"""
AGF v9.0 — TFLiteFaceEmbedder (cierre T21/T22 en Termux)
=========================================================
Backend TFLite para embedding facial real. Mismo contrato que
OnnxFaceEmbedder (EmbeddingResult + VectorComparator), mismo
fail-closed: sin interprete o sin modelo -> BLOCKED, nunca PASS
fabricado. Compatibe con tflite-runtime y tensorflow-lite.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence


class EmbeddingStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    NOT_RUN = "NOT_RUN"


@dataclass
class EmbeddingResult:
    status: EmbeddingStatus
    model_id: str
    vector: Optional[list] = None
    norm: Optional[float] = None
    evidence_hash: Optional[str] = None
    reason: str = ""


class TFLiteFaceEmbedder:
    """ArcFace (512-d) / FaceNet (128-d) via TFLite."""

    MODEL_SPECS = {
        "arcface": {"input_size": (112, 112), "output_dim": 512},
        "facenet": {"input_size": (160, 160), "output_dim": 128},
    }

    def __init__(self, model_kind: str, model_bytes: Optional[bytes] = None,
                 normalize: str = "arcface"):
        """normalize=True: entrada (x-127.5)/128 (ArcFace ONNX estandar).
        normalize=False: el modelo incluye su propia capa de escalado
        (p.ej. facenet.tflite derivado de deepface) -> NO normalizar."""
        if isinstance(normalize, bool):
            normalize = "arcface" if normalize else "raw"
        if normalize not in ("arcface", "raw", "div255"):
            raise ValueError("normalize debe ser arcface|raw|div255")
        if model_kind not in self.MODEL_SPECS:
            raise ValueError(f"model_kind debe ser uno de {list(self.MODEL_SPECS)}")
        self.model_kind = model_kind
        self.spec = self.MODEL_SPECS[model_kind]
        self.normalize = normalize
        self.model_id = f"{model_kind}:tflite:unknown-weights"
        self._interp = None
        self._in_idx = self._out_idx = None
        if model_bytes:
            self._load(model_bytes)

    # -- carga ----------------------------------------------------------
    def _get_interpreter_class(self):
        try:
            from tflite_runtime.interpreter import Interpreter  # type: ignore
            return Interpreter
        except ImportError:
            pass
        try:
            from tensorflow.lite.python.interpreter import Interpreter  # type: ignore
            return Interpreter
        except ImportError:
            return None

    def _load(self, model_bytes: bytes) -> None:
        Interpreter = self._get_interpreter_class()
        if Interpreter is None:
            self._interp = None
            self.reason = "sin tflite_runtime ni tensorflow.lite"
            return
        import tempfile, os
        try:
            with tempfile.NamedTemporaryFile(suffix=".tflite", delete=False) as f:
                f.write(model_bytes)
                path = f.name
            self._interp = Interpreter(model_path=path)
            os.unlink(path)
            self._interp.allocate_tensors()
            self._in_idx = self._interp.get_input_details()[0]["index"]
            self._out_idx = self._interp.get_output_details()[0]["index"]
            self.model_id = (f"{self.model_kind}:tflite:"
                             + hashlib.sha256(model_bytes).hexdigest()[:16])
        except Exception:
            self._interp = None  # modelo invalido -> fail-closed

    # -- inferencia ------------------------------------------------------
    def embed(self, rgb_pixels: Optional[Sequence] = None,
              bbox: Optional[tuple] = None) -> EmbeddingResult:
        if self._interp is None or rgb_pixels is None:
            return EmbeddingResult(
                EmbeddingStatus.BLOCKED, self.model_id,
                reason="sin interprete TFLite o sin píxeles; fail-closed")
        try:
            import numpy as np  # type: ignore
            arr = np.asarray(rgb_pixels, dtype=np.float32)
            if bbox:
                x1, y1, x2, y2 = bbox
                arr = arr[y1:y2, x1:x2]
            h, w = self.spec["input_size"]
            arr = self._resize_np(arr, (h, w))
            if self.normalize == "arcface":
                arr = (arr - 127.5) / 128.0
            elif self.normalize == "div255":
                arr = arr / 255.0
            arr = np.expand_dims(arr, axis=0)  # NHWC
            self._interp.set_tensor(self._in_idx, arr)
            self._interp.invoke()
            vec = self._interp.get_tensor(self._out_idx).flatten()
            n = float(np.linalg.norm(vec))
            if n == 0.0:
                raise ValueError("embedding de norma cero")
            vec = (vec / n).tolist()
            ev = hashlib.sha512(json.dumps(vec).encode()).hexdigest()
            return EmbeddingResult(EmbeddingStatus.PASS, self.model_id,
                                   vector=vec, norm=1.0, evidence_hash=ev,
                                   reason="embedding real TFLite")
        except ImportError:
            return EmbeddingResult(EmbeddingStatus.BLOCKED, self.model_id,
                                   reason="numpy no disponible")
        except Exception as e:
            return EmbeddingResult(EmbeddingStatus.FAIL, self.model_id,
                                   reason=str(e))

    @staticmethod
    def _resize_np(arr, size_hw):
        import numpy as np  # type: ignore
        h, w = size_hw
        ys = (np.arange(h) * (arr.shape[0] / h)).astype(int).clip(0, arr.shape[0] - 1)
        xs = (np.arange(w) * (arr.shape[1] / w)).astype(int).clip(0, arr.shape[1] - 1)
        return arr[ys][:, xs]


# -- comparador (mismo contrato que v9.0) ---------------------------------
class VectorComparator:
    COSINE_IDENTICAL_TOLERANCE = 0.99999

    def __init__(self, threshold: float = 0.65,
                 identical_tolerance: float = COSINE_IDENTICAL_TOLERANCE):
        self.threshold = threshold
        self.identical_tolerance = identical_tolerance

    def verify(self, reference: EmbeddingResult,
               candidate: EmbeddingResult) -> dict:
        out = {"rule": "FACE_VERIFY_TFLITE"}
        for r in (reference, candidate):
            if r.status is not EmbeddingStatus.PASS or not r.vector:
                return {**out, "status": "BLOCKED",
                        "reason": f"embedding sin PASS: {r.reason or r.status.value}"}
        if reference.model_id.split(":")[0] != candidate.model_id.split(":")[0]:
            return {**out, "status": "BLOCKED",
                    "reason": "modelos distintos; comparacion cruzada no permitida"}
        cos = self.cosine(reference.vector, candidate.vector)
        out["cosine"] = round(cos, 6)
        if cos >= self.identical_tolerance:
            return {**out, "status": "FAIL", "reason": "replay/fabricacion"}
        out["status"] = "PASS" if cos >= self.threshold else "FAIL"
        out["reason"] = f"cosine {cos:.4f} vs umbral {self.threshold}"
        out["evidence_hash"] = hashlib.sha512(
            json.dumps(out, sort_keys=True).encode()).hexdigest()
        return out

    @staticmethod
    def cosine(a, b):
        if len(a) != len(b) or not a:
            raise ValueError("vectores incompatibles")
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(x * x for x in b))
        if na == 0 or nb == 0:
            raise ValueError("norma cero")
        return sum(x * y for x, y in zip(a, b)) / (na * nb)
