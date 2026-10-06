#!/usr/bin/env python3
# ======================================================================
# AGF CHAT RUNTIME v0.2 (kernel) — SINGLE-FILE BUNDLE (chat-window portable)
# ======================================================================
# Ejecución ESTRICTA en ventana de chat, sin API, sin acceso al modelo.
# Pegar este archivo completo en la ventana de chat de cualquier LLM
# con capacidad de ejecutar Python (Code Interpreter, analysis tool, etc.)
# o en Termux/PC. Stdlib puro. Fail-closed.
#
#   AGF SHALL NOT CONTROL THE INTERNAL LLM.
#   AGF SHALL CONTROL AND VERIFY THE INTERACTION WITH THE LLM
#   THROUGH ITS CHAT INTERFACE.
# ======================================================================
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Optional, Protocol



KERNEL_VERSION = "AGF_CHAT_RUNTIME v0.2 — PROMPT KERNEL"
OPERATIONS = ("RESTORE", "REPAIR", "RECONSTRUCT")

DEFINITIONS = """DEFINITIONS:
- DAÑO: artefacto, rasgadura, mancha, píxel corrupto, compresión severa,
  ruido, desenfoque local, o región faltante que interrumpe la continuidad.
- ELEMENTO NO DAÑADO: cualquier región sin los defectos anteriores; intocable.
- RECONSTRUCCIÓN LEGÍTIMA: recuperar una región dañada usando exclusivamente
  (a) información visible en REFERENCE_IMAGE, o (b) continuidad local evidente
  de TARGET_IMAGE.
- RECONSTRUCCIÓN ILEGÍTIMA: añadir detalle, textura, iluminación o geometría
  no respaldados por (a) ni (b). Prohibida siempre."""

MINIMUM_INTERVENTION = """PRINCIPLE OF MINIMUM INTERVENTION:
Prefiere dejar un área imperfecta antes que introducir información no
respalda por REFERENCE_IMAGE o por continuidad local evidente.
Cuando dudes, NO intervengas."""

PRIORITIES = [
    "IDENTITY_PRESERVATION = MAX",
    "STRUCTURE_PRESERVATION = MAX",
    "SCENE_PRESERVATION = MAX",
    "MINIMUM_INTERVENTION = MAX",
]

ALLOWED = [
    "1. Eliminar artefactos (ruido, manchas, píxeles corruptos, marcas de compresión)",
    "2. Recuperar continuidad de bordes y superficies dañadas",
    "3. Reconstruir información perdida — SOLO si es estrictamente necesario y "
    "está respaldada por REFERENCE_IMAGE o continuidad local evidente",
    "4. Mejorar nitidez local SOLO en regiones dañadas",
    "5. Corregir iluminación SOLO ante defecto de captura evidente "
    "(sub/sobreexposición local, mancha de luz); nunca como mejora estética",
]

FORBIDDEN = [
    "cambiar identidad",
    "cambiar edad aparente",
    "cambiar anatomía",
    "cambiar expresión sin autorización",
    "cambiar composición",
    "introducir sujetos nuevos",
    "alterar elementos no dañados",
    "reconstrucción ilegítima (definiciones arriba)",
    "usar 'iluminación' como justificación estética de cambios de tono o rostro",
    "sobre-reparar: extender la intervención a regiones sanas",
]

VERIFICATION_FORMAT = """VERIFICATION (obligatorio, formato exacto):
[AGF_VERIFICATION_REPORT]
CHANGES: <lista numerada de cambios, región por región>
JUSTIFICATION: <para cada reconstrucción: evidencia que la respalda —
REFERENCE_IMAGE | CONTINUIDAD_LOCAL>
PROVENANCE: RECOVERED | RECONSTRUCTED | GENERATED
CONFIDENCE: alta | media | baja
UNCERTAIN_AREAS: <regiones dejadas imperfectas por falta de respaldo, o "none">
[/AGF_VERIFICATION_REPORT]"""

PROVENANCE_RULE = (
    "PROVENANCE: RECOVERED = información recuperada de la propia imagen; "
    "RECONSTRUCTED = información inferida y reconstruida (marcar siempre); "
    "GENERATED = contenido nuevo generado; nunca equivalentes entre sí."
)


class KernelError(ValueError):
    pass


@dataclass
class KernelResult:
    operation: str
    prompt_block: str
    attempts_allowed: int


class PromptKernel:
    """Fábrica de bloques operacionales v0.2. Un bloque por intento."""

    def __init__(self, max_retries: int = 2):
        if max_retries < 0:
            raise KernelError("max_retries no puede ser negativo")
        self.max_retries = max_retries
        self._attempt = 0

    def build(self, operation: str, reference_id: str,
              target_id: str) -> KernelResult:
        if operation not in OPERATIONS:
            raise KernelError(
                f"operación '{operation}' no permitida; usar {OPERATIONS}")
        self._attempt = 1
        return KernelResult(operation=operation,
                            prompt_block=self._assemble(
                                operation, reference_id, target_id, None),
                            attempts_allowed=self.max_retries)

    def build_correction(self, operation: str, reference_id: str,
                         target_id: str,
                         rejection_reason: str) -> KernelResult:
        if self._attempt == 0:
            raise KernelError("build() debe ejecutarse antes de correcciones")
        if self._attempt > self.max_retries:
            raise KernelError("se agotaron los intentos; el FSM debe BLOCK")
        self._attempt += 1
        return KernelResult(
            operation=operation,
            prompt_block=self._assemble(operation, reference_id, target_id,
                                        rejection_reason),
            attempts_allowed=self.max_retries - self._attempt + 1)

    def _assemble(self, operation, reference_id, target_id,
                  rejection_reason: Optional[str]) -> str:
        lines = [
            "[AGF_OPERATION]",
            f"KERNEL: {KERNEL_VERSION}",
            "",
            "OPERATION:",
            operation,
            "",
            "INPUT ROLES:",
            f"REFERENCE_IMAGE (id {reference_id}): ancla de identidad y "
            "estructura. NO se edita; evidencia de cómo debe verse el sujeto.",
            f"TARGET_IMAGE (id {target_id}): imagen base a reparar. "
            "Toda intervención ocurre aquí.",
            "",
            DEFINITIONS,
            "",
            "PRIORITY:",
            *[f"- {p}" for p in PRIORITIES],
            "",
            MINIMUM_INTERVENTION,
            "",
            "ALLOWED (orden de preferencia estricto):",
            *[f"- {a}" for a in ALLOWED],
            "",
            "FORBIDDEN:",
            *[f"- {f}" for f in FORBIDDEN],
            "",
            PROVENANCE_RULE,
            "",
            "OUTPUT:",
            "GENERATE_EDITED_IMAGE",
            "",
            VERIFICATION_FORMAT,
        ]
        if rejection_reason:
            lines += ["", "CORRECTION:",
                      f"Motivo del rechazo anterior: {rejection_reason}",
                      "Corrige SOLO lo señalado; no alteres el resto."]
        lines += ["", "[/AGF_OPERATION]"]
        return "\n".join(lines)

# ----------------------------------------------------------------------





class IntakeStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"


@dataclass
class ImageRef:
    image_id: str
    role: str            # REFERENCE | TARGET
    byte_size: int
    width: Optional[int] = None
    height: Optional[int] = None
    status: str = "PASS"
    reason: str = "imagen aceptada"

    def to_dict(self):
        return asdict(self)


class ImageIntake:
    KNOWN_ROLES = ("REFERENCE", "TARGET")

    def accept(self, image_bytes: Optional[bytes], role: str) -> ImageRef:
        if role not in self.KNOWN_ROLES:
            return ImageRef("", role, 0, status="FAIL",
                            reason=f"rol '{role}' desconocido")
        if not image_bytes:
            return ImageRef("", role, 0, status="FAIL",
                            reason="imagen vacía; entrada rechazada (fail-closed)")
        image_id = hashlib.sha512(image_bytes).hexdigest()
        return ImageRef(image_id=image_id, role=role,
                        byte_size=len(image_bytes))

# ----------------------------------------------------------------------




PROVENANCE_TAGS = ("RECOVERED", "RECONSTRUCTED", "GENERATED")


@dataclass
class OutputRecord:
    output_id: str
    origin: str                    # OPERATOR (pegado humano)
    declared_provenance: Optional[str]
    status: str                    # PASS | UNVERIFIED | FAIL
    reason: str = ""

    def to_dict(self):
        return asdict(self)


class ResultCapture:
    def capture(self, output_bytes: Optional[bytes],
                declared_provenance: Optional[str]) -> OutputRecord:
        if not output_bytes:
            return OutputRecord("", "OPERATOR", None, "FAIL",
                                "sin resultado recibido")
        output_id = hashlib.sha512(output_bytes).hexdigest()
        if declared_provenance not in PROVENANCE_TAGS:
            return OutputRecord(output_id, "OPERATOR", None, "UNVERIFIED",
                                "procedencia no declarada; RECOVERED/"
                                "RECONSTRUCTED/GENERATED son distintos")
        return OutputRecord(output_id, "OPERATOR", declared_provenance,
                            "PASS", "procedencia declarada explícitamente")

# ----------------------------------------------------------------------





class Embedder(Protocol):
    """Contrato compatible con v9.0 OnnxFaceEmbedder."""

    def embed(self, rgb_pixels, bbox=None):
        ...


@dataclass
class VerificationResult:
    status: str            # PASS | FAIL | BLOCKED
    identity_preserved: Optional[bool]
    provenance: Optional[str]
    detail: str
    evidence_hash: Optional[str] = None


class IdentityVerifier:
    RESTORE_ACCEPTABLE = ("RECOVERED", "RECONSTRUCTED")

    def __init__(self, embedder: Optional[Embedder] = None,
                 threshold: float = 0.65):
        self.embedder = embedder
        self.threshold = threshold

    def verify(self, reference_rgb, output_rgb,
               declared_provenance: Optional[str]) -> VerificationResult:
        # Regla de procedencia primero: GENERATED no es restauración.
        if declared_provenance == "GENERATED":
            return VerificationResult(
                "FAIL", False, declared_provenance,
                "GENERATED ≠ restauración; viola el objetivo de la operación")
        # Sin canal biométrico real: BLOCKED (fail-closed).
        if self.embedder is None:
            return VerificationResult(
                "BLOCKED", None, declared_provenance,
                "sin embedder ArcFace/FaceNet; identidad NO verificable")
        ref = self.embedder.embed(reference_rgb)
        out = self.embedder.embed(output_rgb)
        for r in (ref, out):
            if getattr(r, "status", None) and r.status.value != "PASS":
                return VerificationResult(
                    "BLOCKED", None, declared_provenance,
                    f"embedding no disponible: {getattr(r, 'reason', r.status)}")
        a, b = ref.vector, out.vector
        cos = sum(x * y for x, y in zip(a, b)) / (
            math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))
        ok = cos >= self.threshold
        ev = hashlib.sha512(json.dumps(
            {"cos": cos, "prov": declared_provenance},
            sort_keys=True).encode()).hexdigest()
        return VerificationResult(
            "PASS" if ok else "FAIL", ok, declared_provenance,
            f"cosine {cos:.4f} vs umbral {self.threshold}", ev)

# ----------------------------------------------------------------------




PRECEDENCE = ("capability", "privacy", "security", "policy",
              "purpose", "authorization")


@dataclass
class GateDecision:
    decision: str          # ACCEPT | REJECT | BLOCK
    layer: str             # qué capa de precedencia decidió
    reason: str


class PolicyGate:
    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries
        self._attempt = 0

    def reset(self):
        self._attempt = 0

    def decide(self, verification_status: str,
               attempt: int,
               capability_ok: bool = True,
               authorization_ok: bool = True) -> GateDecision:
        # capability (capa más alta)
        if not capability_ok:
            return GateDecision("BLOCK", "capability",
                                "capacidad requerida no disponible")
        if not authorization_ok:
            return GateDecision("BLOCK", "authorization",
                                "acción fuera de la autorización otorgada")
        # security / policy: estados cerrados no se negocian
        if verification_status == "BLOCKED":
            return GateDecision("BLOCK", "security",
                                "verificación bloqueada; fail-closed "
                                "(sin PASS fabricado)")
        if verification_status == "FAIL":
            if attempt <= self.max_retries:
                return GateDecision("REJECT", "policy",
                                    f"intento {attempt}/{self.max_retries}: "
                                    "se re-promptea con corrección")
            return GateDecision("BLOCK", "policy",
                                "intentos agotados; operación bloqueada")
        return GateDecision("ACCEPT", "policy",
                            "verificación PASS; resultado liberado")

# ----------------------------------------------------------------------




GENESIS = "0" * 128


@dataclass
class RuntimeEvidence:
    seq: int
    event: str                 # INTAKE | KERNEL | DISPATCH | CAPTURE |
                               # VERIFY | DECISION | BLOCK | ACCEPT
    payload: dict
    prev_hash: str
    record_hash: str
    status: str                # PASS | UNVERIFIED | FAIL | BLOCKED

    def to_dict(self):
        return asdict(self)


class EvidenceWriter:
    def __init__(self):
        self.records: list[RuntimeEvidence] = []

    def record(self, event: str, payload: dict,
               status: str = "PASS") -> RuntimeEvidence:
        seq = len(self.records) + 1
        prev = self.records[-1].record_hash if self.records else GENESIS
        body = json.dumps({"seq": seq, "event": event, "payload": payload,
                           "prev_hash": prev},
                          sort_keys=True, ensure_ascii=False).encode()
        rec = RuntimeEvidence(seq, event, payload, prev,
                              hashlib.sha512(body).hexdigest(), status)
        self.records.append(rec)
        return rec

    def verify(self) -> dict:
        prev = GENESIS
        for r in self.records:
            body = json.dumps({"seq": r.seq, "event": r.event,
                               "payload": r.payload, "prev_hash": r.prev_hash},
                              sort_keys=True, ensure_ascii=False).encode()
            if r.prev_hash != prev or r.record_hash != hashlib.sha512(body).hexdigest():
                return {"status": "FAIL", "seq": r.seq,
                        "reason": "cadena de evidencia alterada"}
            prev = r.record_hash
        return {"status": "PASS" if self.records else "NOT_RUN",
                "records": len(self.records)}

    def dump(self) -> str:
        return json.dumps([r.to_dict() for r in self.records],
                          indent=2, ensure_ascii=False)

# ----------------------------------------------------------------------




EXECUTION_BOUNDARY = {
    "TARGET_ENVIRONMENT": "LLM_CHAT_UI",
    "INTERACTION_CHANNEL": "CHAT_WINDOW",
    "API": "PROHIBITED",
    "DIRECT_MODEL_ACCESS": "PROHIBITED",
    "WEIGHT_ACCESS": "PROHIBITED",
    "BACKEND_ACCESS": "PROHIBITED",
    "EXTERNAL_MODEL_CONTROL": "PROHIBITED",
    "ALLOWED_INTERACTION": [
        "upload_image", "send_prompt", "receive_output",
        "inspect_output", "send_correction",
    ],
}


@dataclass
class Dispatch:
    """Bloque listo para la ventana de chat + instrucción al operador."""
    prompt_block: str
    instruction: str
    boundary: dict


class ChatAdapter(Protocol):
    def dispatch(self, prompt_block: str,
                 image_ids: list[str]) -> Dispatch: ...
    def receive(self, pasted_output: Optional[str]) -> Optional[bytes]: ...


class ManualChatAdapter:
    """Operador como transporte: copia/pega entre AGF y la ventana del LLM."""

    def dispatch(self, prompt_block: str, image_ids: list[str]) -> Dispatch:
        return Dispatch(
            prompt_block=prompt_block,
            instruction=(
                "OPERADOR: 1) adjunta las imágenes con ids "
                f"{image_ids} en la ventana del chatbot; "
                "2) pega el bloque [AGF_OPERATION]; "
                "3) cuando el chatbot responda con la imagen editada, "
                "declara su procedencia (RECOVERED|RECONSTRUCTED|GENERATED) "
                "y pega el resultado de vuelta aquí."
            ),
            boundary=dict(EXECUTION_BOUNDARY),
        )

    def receive(self, pasted_output: Optional[str]) -> Optional[bytes]:
        if not pasted_output:
            return None
        return pasted_output.encode("utf-8", "replace")

# ----------------------------------------------------------------------






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

# ----------------------------------------------------------------------

if __name__ == "__main__":
    rt = ChatRuntime(max_retries=1)
    step = rt.start("REPAIR", b"REFERENCE_IMAGE_BYTES", b"TARGET_IMAGE_BYTES")
    print("== KERNEL v0.2 LISTO PARA LA VENTANA DEL LLM ==")
    print(step.dispatch_prompt)
    print("== INSTRUCCIÓN AL OPERADOR ==")
    print(step.dispatch_instruction)
    step = rt.feed(RuntimeEvent("OUTPUT_RECEIVED", b"EDITED_IMAGE_BYTES",
                                declared_provenance="RECONSTRUCTED"))
    print("== DECISIÓN ==", step.state.value, "->", step.message)
    print("== CADENA DE EVIDENCIA ==", json.dumps(rt.chain_check()))
