"""Validación estricta de embeddings repetidos para verificación facial."""
import math
from statistics import median


def stable_median(embed_fn, pixels, runs=3, expected_dim=None):
    """Devuelve la mediana solo si las tres ejecuciones son válidas."""
    if runs != 3:
        return None

    vectors = []
    for _ in range(3):
        try:
            result = embed_fn(pixels)
            status = getattr(getattr(result, "status", None), "value", None)
            raw = getattr(result, "vector", None)
            if status != "PASS" or raw is None or len(raw) == 0:
                return None
            vector = [float(value) for value in raw]
        except Exception:
            return None

        if expected_dim is not None and len(vector) != expected_dim:
            return None
        if not vector or not all(math.isfinite(value) for value in vector):
            return None
        if not any(value != 0.0 for value in vector):
            return None
        vectors.append(vector)

    if len({len(vector) for vector in vectors}) != 1:
        return None

    result = [median(column) for column in zip(*vectors)]
    if not all(math.isfinite(value) for value in result):
        return None
    if not any(value != 0.0 for value in result):
        return None
    return result


def comparison_evidence_valid(result):
    """L1 PASS requiere que el SHA-512 coincida con el contenido comparado."""
    import hashlib
    import hmac
    import json
    import math

    if not isinstance(result, dict):
        return False
    if result.get("status") not in ("PASS", "FAIL"):
        return False

    cosine = result.get("cosine")
    if (not isinstance(cosine, (int, float))
            or isinstance(cosine, bool)
            or not math.isfinite(cosine)):
        return False

    digest = result.get("evidence_hash")
    if not isinstance(digest, str) or len(digest) != 128:
        return False
    if any(c not in "0123456789abcdef" for c in digest.lower()):
        return False

    # VectorComparator calcula el hash ANTES de añadir evidence_hash.
    payload = dict(result)
    payload.pop("evidence_hash", None)
    expected = hashlib.sha512(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()

    return hmac.compare_digest(digest.lower(), expected)
