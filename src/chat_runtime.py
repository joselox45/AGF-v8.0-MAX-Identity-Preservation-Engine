"""
AGF Chat Runtime v0.1 — FSM (FINITE STATE MACHINE)
==================================================
Bucle de control cerrado sobre la ventana de chat del LLM opaco:

IDLE → INTAKE → KERNEL → DISPATCH → AWAIT_OUTPUT → CAPTURE → VERIFY
                                                          │
                              ┌───────────┬───────────────┤
                              ▼           ▼               ▼
                          ACCEPT    REJECT(re-prompt)   BLOCK

Transporte: ChatAdapter (por defecto ManualChatAdapter: el operador
copia/pega). Sin API. Sin acceso al modelo. Fail-closed en todo estado
material: evidencia ausente => BLOCKED, nunca PASS.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from prompt_kernel import PromptKernel, KernelError
from image_intake import ImageIntake, ImageRef
from result_capture import ResultCapture
from identity_verifier import IdentityVerifier, VerificationResult
from policy_gate import PolicyGate, GateDecision
from evidence_writer import EvidenceWriter
from browser_adapter import ChatAdapter, ManualChatAdapter


class State(str, Enum):
    IDLE = "IDLE"
    INTAKE = "INTAKE"
    KERNEL = "KERNEL"
    DISPATCH = "DISPATCH"
    AWAIT_OUTPUT = "AWAIT_OUTPUT"
    CAPTURE = "CAPTURE"
    VERIFY = "VERIFY"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"      # transitorio: se re-promptea
    BLOCKED = "BLOCKED"


@dataclass
class RuntimeEvent:
    """Evento alimentado por el operador/runtime externo."""
    kind: str                  # OUTPUT_RECEIVED | PROVENANCE_DECLARED
    output: Optional[bytes] = None
    declared_provenance: Optional[str] = None


@dataclass
class Step:
    state: State
    message: str
    dispatch_prompt: Optional[str] = None
    dispatch_instruction: Optional[str] = None
    decision: Optional[GateDecision] = None
    verification: Optional[VerificationResult] = None


class ChatRuntime:
    def __init__(self, adapter: Optional[ChatAdapter] = None,
                 max_retries: int = 2):
        self.adapter = adapter or ManualChatAdapter()
        self.intake = ImageIntake()
        self.kernel = PromptKernel(max_retries=max_retries)
        self.capture = ResultCapture()
        self.verifier = IdentityVerifier()
        self.gate = PolicyGate(max_retries=max_retries)
        self.evidence = EvidenceWriter()
        self.state = State.IDLE
        self.reference: Optional[ImageRef] = None
        self.target: Optional[ImageRef] = None
        self.operation: Optional[str] = None
        self.attempt = 0
        self.last_rejection: Optional[str] = None
        self._awaiting = False

    # -- ciclo principal ------------------------------------------------
    def start(self, operation: str, reference_bytes: bytes,
              target_bytes: bytes) -> Step:
        self.state = State.INTAKE
        self.reference = self.intake.accept(reference_bytes, "REFERENCE")
        self.target = self.intake.accept(target_bytes, "TARGET")
        for img in (self.reference, self.target):
            self.evidence.record("INTAKE", img.to_dict(), img.status)
            if img.status != "PASS":
                return self._block(f"intake rechazado: {img.reason}")
        self.operation = operation
        return self._to_kernel()

    def _to_kernel(self) -> Step:
        self.state = State.KERNEL
        try:
            if self.attempt == 0:
                kr = self.kernel.build(self.operation,
                                       self.reference.image_id,
                                       self.target.image_id)
            else:
                kr = self.kernel.build_correction(
                    self.operation, self.reference.image_id,
                    self.target.image_id, self.last_rejection or "sin motivo")
        except KernelError as e:
            return self._block(str(e))
        self.evidence.record("KERNEL", {"attempt": self.attempt + 1,
                                        "operation": self.operation})
        self.state = State.DISPATCH
        d = self.adapter.dispatch(kr.prompt_block,
                                  [self.reference.image_id,
                                   self.target.image_id])
        self.evidence.record("DISPATCH", {"instruction": d.instruction})
        self.attempt += 1
        self.state = State.AWAIT_OUTPUT
        self._awaiting = True
        return Step(State.AWAIT_OUTPUT, "esperando resultado del chatbot",
                    dispatch_prompt=kr.prompt_block,
                    dispatch_instruction=d.instruction)

    def feed(self, event: RuntimeEvent) -> Step:
        """Operador devuelve el resultado de la ventana de chat."""
        if self.state != State.AWAIT_OUTPUT:
            return Step(self.state, "evento ignorado: no se espera salida")
        self._awaiting = False
        self.state = State.CAPTURE
        out = self.capture.capture(event.output, event.declared_provenance)
        self.evidence.record("CAPTURE", out.to_dict(), out.status)
        if out.status == "FAIL":
            return self._block("sin resultado; operación abortada")
        self.state = State.VERIFY
        v = self.verifier.verify(None, None, out.declared_provenance)
        self.evidence.record(
            "VERIFY",
            {"status": v.status, "detail": v.detail,
             "provenance": v.provenance,
             "evidence_hash": v.evidence_hash}, v.status)
        dec = self.gate.decide(v.status, self.attempt)
        self.evidence.record("DECISION", {"decision": dec.decision,
                                          "layer": dec.layer,
                                          "reason": dec.reason})
        if dec.decision == "ACCEPT":
            self.state = State.ACCEPTED
            return Step(State.ACCEPTED, f"ACCEPT: {dec.reason}",
                        decision=dec, verification=v)
        if dec.decision == "REJECT":
            self.state = State.REJECTED
            self.last_rejection = v.detail or dec.reason
            step = Step(State.REJECTED,
                        f"REJECT: {dec.reason}; regenerando kernel")
            next_step = self._to_kernel()
            next_step.decision = dec
            next_step.verification = v
            return next_step
        return self._block(dec.reason, dec, v)

    def _block(self, reason: str, dec: Optional[GateDecision] = None,
               v: Optional[VerificationResult] = None) -> Step:
        self.state = State.BLOCKED
        self.evidence.record("BLOCK", {"reason": reason}, "BLOCKED")
        return Step(State.BLOCKED, f"BLOCKED: {reason}", decision=dec,
                    verification=v)

    def chain_check(self) -> dict:
        return self.evidence.verify()
