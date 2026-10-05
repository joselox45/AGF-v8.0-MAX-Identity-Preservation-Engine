"""AGF Chat Runtime v0.1 — unitarias (stdlib puro)."""
import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from prompt_kernel import PromptKernel, KernelError
from image_intake import ImageIntake
from result_capture import ResultCapture
from identity_verifier import IdentityVerifier
from policy_gate import PolicyGate
from evidence_writer import EvidenceWriter
from chat_runtime import ChatRuntime, RuntimeEvent, State
from browser_adapter import ManualChatAdapter, EXECUTION_BOUNDARY


class TestKernel(unittest.TestCase):
    def test_kernel_builds_controlled_block(self):
        k = PromptKernel()
        r = k.build("REPAIR", "ref123", "tgt456")
        for token in ("IDENTITY_PRESERVATION = MAX", "FORBIDDEN",
                      "VERIFICATION:", "REQUIRED", "REPAIR"):
            self.assertIn(token, r.prompt_block)

    def test_kernel_rejects_unknown_operation(self):
        with self.assertRaises(KernelError):
            PromptKernel().build("FACE_SWAP", "a", "b")

    def test_kernel_correction_and_retry_cap(self):
        k = PromptKernel(max_retries=1)
        k.build("RESTORE", "a", "b")
        r = k.build_correction("RESTORE", "a", "b", "cambió la expresión")
        self.assertIn("CORRECTION", r.prompt_block)
        with self.assertRaises(KernelError):
            k.build_correction("RESTORE", "a", "b", "otro")


class TestIntakeCapture(unittest.TestCase):
    def test_intake_hash_deterministic(self):
        i = ImageIntake()
        a = i.accept(b"fake-image-bytes", "REFERENCE")
        b = i.accept(b"fake-image-bytes", "REFERENCE")
        self.assertEqual(a.image_id, b.image_id)
        self.assertEqual(a.status, "PASS")

    def test_intake_empty_fail_closed(self):
        r = ImageIntake().accept(b"", "TARGET")
        self.assertEqual(r.status, "FAIL")
        self.assertIn("fail-closed", r.reason)

    def test_capture_requires_provenance(self):
        c = ResultCapture()
        self.assertEqual(c.capture(b"img", None).status, "UNVERIFIED")
        self.assertEqual(c.capture(b"img", "RECONSTRUCTED").status, "PASS")
        self.assertEqual(c.capture(b"", "RECOVERED").status, "FAIL")


class TestVerifierGate(unittest.TestCase):
    def test_verifier_fail_closed_without_embedder(self):
        v = IdentityVerifier().verify(None, None, "RECOVERED")
        self.assertEqual(v.status, "BLOCKED")

    def test_generated_never_accepted_in_restore(self):
        v = IdentityVerifier().verify(None, None, "GENERATED")
        self.assertEqual(v.status, "FAIL")
        self.assertFalse(v.identity_preserved)

    def test_gate_block_on_blocked_verification(self):
        d = PolicyGate(max_retries=1).decide("BLOCKED", attempt=1)
        self.assertEqual((d.decision, d.layer), ("BLOCK", "security"))

    def test_gate_reject_then_block(self):
        g = PolicyGate(max_retries=1)
        self.assertEqual(g.decide("FAIL", attempt=1).decision, "REJECT")
        self.assertEqual(g.decide("FAIL", attempt=2).decision, "BLOCK")

    def test_gate_capability_highest_precedence(self):
        d = PolicyGate().decide("PASS", attempt=1, capability_ok=False)
        self.assertEqual((d.decision, d.layer), ("BLOCK", "capability"))


class TestEvidenceFSM(unittest.TestCase):
    def test_evidence_chain_tamper_detected(self):
        w = EvidenceWriter()
        w.record("INTAKE", {"a": 1})
        w.record("VERIFY", {"b": 2})
        w.records[0].payload["a"] = 999
        self.assertEqual(w.verify()["status"], "FAIL")

    def test_fsm_full_cycle_generated_blocks(self):
        rt = ChatRuntime(max_retries=1)
        step = rt.start("REPAIR", b"ref-img", b"tgt-img")
        self.assertEqual(step.state, State.AWAIT_OUTPUT)
        # GENERATED -> FAIL -> REJECT -> re-prompt (intento 1/1)
        step = rt.feed(RuntimeEvent("OUTPUT_RECEIVED", b"out-img",
                                    declared_provenance="GENERATED"))
        self.assertEqual(step.state, State.AWAIT_OUTPUT)
        # segundo intento: se agotan retries -> BLOCK
        step = rt.feed(RuntimeEvent("OUTPUT_RECEIVED", b"out-img",
                                    declared_provenance="GENERATED"))
        self.assertEqual(step.state, State.BLOCKED)
        self.assertEqual(rt.chain_check()["status"], "PASS")

    def test_fsm_generated_blocks_immediately_with_zero_retries(self):
        rt = ChatRuntime(max_retries=0)
        rt.start("REPAIR", b"r", b"t")
        step = rt.feed(RuntimeEvent("OUTPUT_RECEIVED", b"o",
                                    declared_provenance="GENERATED"))
        self.assertEqual(step.state, State.BLOCKED)

    def test_fsm_unknown_provenance_blocks(self):
        rt = ChatRuntime(max_retries=0)
        rt.start("RESTORE", b"r", b"t")
        step = rt.feed(RuntimeEvent("OUTPUT_RECEIVED", b"out", None))
        self.assertEqual(step.state, State.BLOCKED)

    def test_fsm_intake_failure_blocks(self):
        rt = ChatRuntime()
        step = rt.start("REPAIR", b"", b"t")
        self.assertEqual(step.state, State.BLOCKED)

    def test_boundary_constants(self):
        self.assertEqual(EXECUTION_BOUNDARY["API"], "PROHIBITED")
        self.assertIn("send_prompt",
                      EXECUTION_BOUNDARY["ALLOWED_INTERACTION"])
        self.assertTrue(ManualChatAdapter().dispatch("x", ["i1"]))


if __name__ == "__main__":
    unittest.main()
