"""
AGF v9.0 — Embedding biométrico real (ArcFace / FaceNet)
========================================================
Contrato de ejecución en ventana de chat (chat-window runtime contract):
  - stdlib-first: funciona pegado como bloque único en cualquier chatbot
    comercial opaco. numpy y onnxruntime son OPCIONALES y degradan con
    estado BLOCKED (fail-closed), nunca PASS fabricado.
  - Sin red, sin filesystem obligatorio, sin secretos persistidos.
  - Salida: JSON plano + hash de evidencia (SHA-512).

Regla ZERO-FABRICATION: si no hay modelo real cargado, el estado es
BLOCKED / NOT_RUN. Nunca se sintetiza un embedding.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field, asdict
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

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


# ------------------------------------------------------------------
# Comparador de vectores — núcleo puro (sin dependencias)
# ------------------------------------------------------------------
class VectorComparator:
    """
    Similitud coseno + verificación umbral con doble cierre:

    1. FAIL-CLOSED  : si el embedding de referencia o candidato no existe
                      o su norma es 0 → BLOCKED.
    2. ANTI-REPLAY  : coseno >= 0.99999 se trata como replay/fabricación
                      (vectores idénticos bit a bit no ocurren entre dos
                      capturas reales del mismo rostro).
    """

    COSINE_IDENTICAL_TOLERANCE = 0.99999

    def __init__(self, threshold: float = 0.65,
                 identical_tolerance: float = COSINE_IDENTICAL_TOLERANCE):
        if not 0.0 < threshold < 1.0:
            raise ValueError("threshold debe estar en (0,1)")
        self.threshold = threshold
        self.identical_tolerance = identical_tolerance

    @staticmethod
    def _l2(v: Sequence[float]) -> float:
        return math.sqrt(sum(float(x) * float(x) for x in v))

    def cosine(self, a: Sequence[float], b: Sequence[float]) -> float:
        if len(a) != len(b) or len(a) == 0:
            raise ValueError("vectores de dimensión incompatible")
        na, nb = self._l2(a), self._l2(b)
        if na == 0.0 or nb == 0.0:
            raise ValueError("vector de norma cero")
        dot = sum(float(x) * float(y) for x, y in zip(a, b))
        return dot / (na * nb)

    def verify(self, reference: EmbeddingResult,
               candidate: EmbeddingResult) -> dict:
        evid = {
            "rule": "FACE_VERIFY",
            "model_ref": reference.model_id,
            "model_cand": candidate.model_id,
        }
        for r in (reference, candidate):
            if r.status is not EmbeddingStatus.PASS or not r.vector:
                return {**evid, "status": EmbeddingStatus.BLOCKED.value,
                        "reason": f"embedding {r.model_id} sin PASS: {r.reason or r.status.value}"}
        if reference.model_id.split(":", 1)[0] != candidate.model_id.split(":", 1)[0]:
            return {**evid, "status": EmbeddingStatus.BLOCKED.value,
                    "reason": "modelos distintos; comparación cruzada no permitida"}
        try:
            cos = self.cosine(reference.vector, candidate.vector)
        except ValueError as e:
            return {**evid, "status": EmbeddingStatus.BLOCKED.value, "reason": str(e)}
        evid["cosine"] = round(cos, 6)
        if cos >= self.identical_tolerance:
            return {**evid, "status": "FAIL",
                    "reason": "replay/fabricación: vectores estadísticamente idénticos"}
        if cos >= self.threshold:
            evid["status"] = EmbeddingStatus.PASS.value
            evid["reason"] = f"cosine {cos:.4f} >= umbral {self.threshold}"
        else:
            evid["status"] = EmbeddingStatus.FAIL.value
            evid["reason"] = f"cosine {cos:.4f} < umbral {self.threshold}"
        evid["evidence_hash"] = hashlib.sha512(
            json.dumps(evid, sort_keys=True).encode()).hexdigest()
        return evid


# ------------------------------------------------------------------
# Embedder real (ArcFace / FaceNet vía ONNX) — opcional, fail-closed
# ------------------------------------------------------------------
class OnnxFaceEmbedder:
    """
    Carga pesos ONNX reales (ArcFace r100 / FaceNet NN4).
    En ventana de chat sin onnxruntime ni pesos → BLOCKED, no excepción.
    """

    MODEL_SPECS = {
        "arcface": {"input_size": (112, 112), "output_dim": 512},
        "facenet": {"input_size": (160, 160), "output_dim": 128},
    }

    def __init__(self, model_kind: str, onnx_bytes: Optional[bytes] = None):
        if model_kind not in self.MODEL_SPECS:
            raise ValueError(f"model_kind debe ser uno de {list(self.MODEL_SPECS)}")
        self.model_kind = model_kind
        self.spec = self.MODEL_SPECS[model_kind]
        self.model_id = f"{model_kind}:onnx:unknown-weights"
        self._session = None
        if onnx_bytes:
            self._load(onnx_bytes)

    def _load(self, onnx_bytes: bytes) -> None:
        try:
            import onnxruntime as ort  # type: ignore
        except ImportError:
            self._session = None
            return
        try:
            self._session = ort.InferenceSession(onnx_bytes)
            self.model_id = (f"{self.model_kind}:onnx:"
                             + hashlib.sha256(onnx_bytes).hexdigest()[:16])
        except Exception:
            self._session = None  # pesos inválidos → fail-closed

    def embed(self, rgb_pixels: Optional[Sequence] = None,
              bbox: Optional[tuple] = None) -> EmbeddingResult:
        """rgb_pixels: lista anidada [H][W][3] entera 0-255 (pego vía chat)."""
        if self._session is None or rgb_pixels is None:
            return EmbeddingResult(
                status=EmbeddingStatus.BLOCKED, model_id=self.model_id,
                reason="sin onnxruntime/pesos válidos o sin píxeles; "
                       "estado BLOCKED (fail-closed)")
        try:
            import numpy as np  # type: ignore
            arr = np.asarray(rgb_pixels, dtype=np.float32)
            if bbox:  # recorte alineado
                x1, y1, x2, y2 = bbox
                arr = arr[y1:y2, x1:x2]
            h, w = self.spec["input_size"]
            # resize bilineal simple (interpolación pura, sin cv2)
            arr = self._resize_np(arr, (h, w))
            arr = (arr - 127.5) / 128.0                      # normalización [-1,1]
            arr = np.transpose(arr, (2, 0, 1))[np.newaxis, ...]
            inp = self._session.get_inputs()[0].name
            vec = self._session.run(None, {inp: arr})[0].flatten()
            n = float(np.linalg.norm(vec))
            if n == 0.0:
                raise ValueError("embedding de norma cero")
            vec = (vec / n).tolist()
            ev = hashlib.sha512(json.dumps(vec).encode()).hexdigest()
            return EmbeddingResult(status=EmbeddingStatus.PASS,
                                   model_id=self.model_id, vector=vec, norm=1.0,
                                   evidence_hash=ev, reason="embedding real ONNX")
        except ImportError:
            return EmbeddingResult(status=EmbeddingStatus.BLOCKED,
                                   model_id=self.model_id,
                                   reason="numpy no disponible en la ventana de chat")
        except Exception as e:
            return EmbeddingResult(status=EmbeddingStatus.FAIL,
                                   model_id=self.model_id, reason=str(e))

    @staticmethod
    def _resize_np(arr, size_hw):
        import numpy as np  # type: ignore
        h, w = size_hw
        ys = (np.arange(h) * (arr.shape[0] / h)).astype(int).clip(0, arr.shape[0] - 1)
        xs = (np.arange(w) * (arr.shape[1] / w)).astype(int).clip(0, arr.shape[1] - 1)
        return arr[ys][:, xs]
