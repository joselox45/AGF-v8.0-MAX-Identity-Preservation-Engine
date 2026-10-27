import math
from types import SimpleNamespace

from tflite_embedder import EmbeddingStatus, VectorComparator
from verification_acceptance import comparison_evidence_valid


def embedding(vector, model_id="test-model:v1"):
    return SimpleNamespace(
        status=EmbeddingStatus.PASS,
        vector=vector,
        model_id=model_id,
        reason="integration-test",
    )


def test_real_comparator_output_passes_hash_validation():
    comparator = VectorComparator(threshold=0.90)
    candidate = [0.95, math.sqrt(1.0 - 0.95**2)]

    result = comparator.verify(
        embedding([1.0, 0.0]),
        embedding(candidate),
    )

    assert result["status"] == "PASS"
    assert "evidence_hash" in result
    assert comparison_evidence_valid(result)


def test_real_comparator_fail_with_hash_passes_formal_validation():
    comparator = VectorComparator(threshold=0.90)

    result = comparator.verify(
        embedding([1.0, 0.0]),
        embedding([0.30, math.sqrt(1.0 - 0.30**2)]),
    )

    assert result["status"] == "FAIL"
    assert "evidence_hash" in result
    # L1 puede validar la integridad de un resultado cuyo L2 sea FAIL.
    assert comparison_evidence_valid(result)


def test_real_comparator_review_required_is_not_formally_accepted():
    comparator = VectorComparator(threshold=0.90)

    result = comparator.verify(
        embedding([1.0, 0.0]),
        embedding([1.0, 0.0]),
    )

    assert result["status"] == "FAIL"
    assert "REQUIRES_REVIEW" in result["reason"]
    assert "evidence_hash" not in result
    assert not comparison_evidence_valid(result)


def test_real_comparator_hash_detects_result_tampering():
    comparator = VectorComparator(threshold=0.90)
    candidate = [0.95, math.sqrt(1.0 - 0.95**2)]

    result = comparator.verify(
        embedding([1.0, 0.0]),
        embedding(candidate),
    )
    assert comparison_evidence_valid(result)

    tampered = dict(result)
    tampered["cosine"] = 0.10
    assert not comparison_evidence_valid(tampered)
