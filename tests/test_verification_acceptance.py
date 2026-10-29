import unittest
from types import SimpleNamespace

from verification_acceptance import stable_median


def result(status="PASS", vector=None):
    return SimpleNamespace(
        status=SimpleNamespace(value=status),
        vector=[1.0, 2.0, 3.0] if vector is None else vector,
    )


class TestStableMedian(unittest.TestCase):
    def test_tres_vectores_validos_devuelven_mediana(self):
        values = iter([
            result(vector=[1, 2, 3]),
            result(vector=[2, 4, 6]),
            result(vector=[3, 6, 9]),
        ])
        self.assertEqual(
            stable_median(lambda _: next(values), None, expected_dim=3),
            [2.0, 4.0, 6.0],
        )

    def test_bloquea_si_falla_primera_ejecucion(self):
        values = iter([result("FAIL"), result(), result()])
        self.assertIsNone(stable_median(lambda _: next(values), None))

    def test_bloquea_si_falla_segunda_ejecucion(self):
        values = iter([result(), result("FAIL"), result()])
        self.assertIsNone(stable_median(lambda _: next(values), None))

    def test_bloquea_si_falla_tercera_ejecucion(self):
        values = iter([result(), result(), result("FAIL")])
        self.assertIsNone(stable_median(lambda _: next(values), None))

    def test_bloquea_vector_vacio(self):
        values = iter([result(vector=[]), result(), result()])
        self.assertIsNone(stable_median(lambda _: next(values), None))

    def test_bloquea_dimension_incorrecta(self):
        values = iter([result(vector=[1, 2]), result(), result()])
        self.assertIsNone(
            stable_median(lambda _: next(values), None, expected_dim=3)
        )

    def test_bloquea_nan_e_inf(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            values = iter([
                result(vector=[bad, 2, 3]), result(), result()
            ])
            self.assertIsNone(stable_median(lambda _: next(values), None))

    def test_bloquea_vector_de_ceros(self):
        values = iter([
            result(vector=[0, 0, 0]),
            result(vector=[0, 0, 0]),
            result(vector=[0, 0, 0]),
        ])
        self.assertIsNone(stable_median(lambda _: next(values), None))

    def test_bloquea_numero_de_ejecuciones_distinto_de_tres(self):
        self.assertIsNone(stable_median(lambda _: result(), None, runs=2))


if __name__ == "__main__":
    unittest.main()


import hashlib
import json


def _comparison_with_valid_hash(status="PASS", cosine=0.95):
    result = {
        "rule": "FACE_VERIFY_TFLITE",
        "cosine": round(cosine, 6),
        "status": status,
        "reason": f"cosine {cosine:.4f} vs umbral 0.90",
    }
    result["evidence_hash"] = hashlib.sha512(
        json.dumps(
            {k: v for k, v in result.items()},
            sort_keys=True
        ).encode()
    ).hexdigest()
    return result


def test_comparison_evidence_accepts_authentic_hash():
    from verification_acceptance import comparison_evidence_valid
    assert comparison_evidence_valid(_comparison_with_valid_hash())


def test_comparison_evidence_accepts_fail_with_authentic_hash():
    from verification_acceptance import comparison_evidence_valid
    assert comparison_evidence_valid(
        _comparison_with_valid_hash(status="FAIL", cosine=0.30)
    )


def test_comparison_evidence_rejects_missing_hash():
    from verification_acceptance import comparison_evidence_valid
    assert not comparison_evidence_valid({
        "status": "FAIL", "cosine": 0.30
    })


def test_comparison_evidence_rejects_review_without_hash():
    from verification_acceptance import comparison_evidence_valid
    assert not comparison_evidence_valid({
        "status": "FAIL",
        "cosine": 1.0,
        "reason": (
            "REQUIRES_REVIEW: vectores indistinguibles; "
            "no acredita capturas independientes"
        ),
    })


def test_comparison_evidence_rejects_malformed_hash():
    from verification_acceptance import comparison_evidence_valid
    result = _comparison_with_valid_hash()
    result["evidence_hash"] = "not-a-sha512"
    assert not comparison_evidence_valid(result)


def test_comparison_evidence_rejects_tampered_cosine():
    from verification_acceptance import comparison_evidence_valid
    result = _comparison_with_valid_hash()
    result["cosine"] = 0.10
    assert not comparison_evidence_valid(result)


def test_comparison_evidence_rejects_tampered_reason():
    from verification_acceptance import comparison_evidence_valid
    result = _comparison_with_valid_hash()
    result["reason"] = "texto alterado después de calcular el hash"
    assert not comparison_evidence_valid(result)


def test_comparison_evidence_rejects_nonfinite_cosine():
    from verification_acceptance import comparison_evidence_valid
    result = _comparison_with_valid_hash()
    result["cosine"] = float("nan")
    assert not comparison_evidence_valid(result)


def test_comparison_evidence_rejects_wrong_status():
    from verification_acceptance import comparison_evidence_valid
    result = _comparison_with_valid_hash()
    result["status"] = "BLOCKED"
    assert not comparison_evidence_valid(result)
