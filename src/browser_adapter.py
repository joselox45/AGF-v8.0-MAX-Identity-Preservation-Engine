"""
AGF Chat Runtime v0.1 — CHAT ADAPTER (BROWSER / MANUAL)
=======================================================
Contrato de transporte hacia la ventana de chat del LLM opaco.
PRINCIPIO ARQUITECTÓNICO (Execution Boundary):

    AGF SHALL NOT CONTROL THE INTERNAL LLM.
    AGF SHALL CONTROL AND VERIFY THE INTERACTION WITH THE LLM
    THROUGH ITS CHAT INTERFACE.

provider = UNKNOWN | interface = CHAT_WINDOW | api = NONE
model_access = BLACK_BOX

INTERACCIÓN PERMITIDA (único canal):
    upload_image | send_prompt | receive_output |
    inspect_output | send_correction

ManualChatAdapter: el operador humano es el transporte (pega el bloque
del kernel en la ventana del chatbot y devuelve el resultado). Es la
única vía estrictamente compatible con "solo ventana de chat" sin
automatización del navegador. BrowserChatAdapter queda como contrato
para futuros adaptadores (Playwright/Appium) sin incluir dependencias.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

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
