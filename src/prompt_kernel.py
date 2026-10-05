"""
AGF Chat Runtime v0.1 — PROMPT KERNEL
======================================
Construye órdenes operacionales controladas para la ventana de chat
del LLM opaco. Nunca dice simplemente "repara la imagen": emite un
bloque [AGF_OPERATION] con prioridades, ALLOWED/FORBIDDEN y exigencia
de verificación. Salida: texto plano copiable (chat-window contract).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

OPERATIONS = ("RESTORE", "REPAIR", "RECONSTRUCT")

KERNEL_HEADER = "AGF_CHAT_RUNTIME v0.1 — PROMPT KERNEL"

PRIORITIES = [
    "IDENTITY_PRESERVATION = MAX",
    "STRUCTURE_PRESERVATION = MAX",
    "SCENE_PRESERVATION = MAX",
]

ALLOWED = [
    "reparar daños",
    "reconstruir información visual perdida",
    "eliminar artefactos",
    "recuperar continuidad",
    "mejorar nitidez",
    "corregir iluminación cuando sea necesaria",
]

FORBIDDEN = [
    "cambiar identidad",
    "cambiar edad aparente",
    "cambiar anatomía",
    "cambiar expresión sin autorización",
    "cambiar composición",
    "introducir sujetos nuevos",
    "alterar elementos no dañados",
]

PROVENANCE_RULE = (
    "Declara la procedencia del resultado usando EXACTAMENTE una etiqueta: "
    "RECOVERED | RECONSTRUCTED | GENERATED. "
    "Nunca trates estas categorías como equivalentes."
)


class KernelError(ValueError):
    pass


@dataclass
class KernelResult:
    operation: str
    prompt_block: str
    attempts_allowed: int


class PromptKernel:
    """
    Fábrica de bloques operacionales. Un bloque por intento; el kernel
    regenera el bloque de corrección si el Policy Gate rechaza.
    """

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
            f"KERNEL: {KERNEL_HEADER}",
            "",
            "OPERATION:",
            operation,
            "",
            "INPUT:",
            f"REFERENCE_IMAGE_ID: {reference_id}",
            f"TARGET_IMAGE_ID: {target_id}",
            "",
            "PRIORITY:",
            *[f"- {p}" for p in PRIORITIES],
            "",
            "ALLOWED:",
            *[f"- {a}" for a in ALLOWED],
            "",
            "FORBIDDEN:",
            *[f"- {f}" for f in FORBIDDEN],
            "",
            f"PROVENANCE: {PROVENANCE_RULE}",
            "",
            "OUTPUT:",
            "GENERATE_EDITED_IMAGE",
            "",
            "VERIFICATION:",
            "REQUIRED",
        ]
        if rejection_reason:
            lines += ["", "CORRECTION:", f"Motivo del rechazo anterior: {rejection_reason}",
                      "Corrige SOLO lo señalado; no alteres el resto."]
        lines += ["", "[/AGF_OPERATION]"]
        return "\n".join(lines)
