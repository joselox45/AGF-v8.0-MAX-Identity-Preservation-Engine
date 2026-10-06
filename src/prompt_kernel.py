"""
AGF Chat Runtime — PROMPT KERNEL v0.2
=====================================
Mejoras sobre v0.1 (auditoría externa, 7.5/10 → objetivo 9+):
  M1  Definiciones operativas: DAÑO / ELEMENTO NO DAÑADO / RECONSTRUCCIÓN
      LEGÍTIMA vs ILEGÍTIMA (elimina la zona gris de "reconstruir").
  M2  Roles explícitos de imagen: REFERENCE = ancla de identidad (no se
      edita); TARGET = base a reparar (única que se interviene).
  M3  Principio de MÍNIMA INTERVENCIÓN: ante la duda, no intervenir.
  M4  ALLOWED jerarquizada en orden estricto de preferencia.
  M5  Iluminación: solo corrige defecto de captura evidente, nunca
      mejora estética (cierra el "cuando sea necesaria" vago).
  M6  VERIFICATION con formato exacto: cambios, justificación por
      reconstrucción, provenance, confianza, áreas inciertas.
Salida: texto plano copiable (chat-window contract).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

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
