"""Middleware de Gobernanza AGF.
Actúa como aduana entre el LLM (texto) y el motor (imágenes).
Verifica estrictamente las reglas del Kernel antes de permitir el paso.
"""
import json
import re

class GovernanceMiddleware:
    def __init__(self, maxcap_chars=200):
        self.maxcap_chars = maxcap_chars

    def validate_input(self, payload):
        """Valida el input del usuario antes de pasarlo al motor."""
        # Regla 1: MAXCAP
        if len(str(payload)) > self.maxcap_chars:
            return False, {
                "error": "ACTA_FUERA_DE_LIMITE",
                "reason": f"Input de {len(str(payload))} chars excede MAXCAP de {self.maxcap_chars}."
            }
        return True, None

    def validate_llm_output(self, llm_response):
        """Valida que el LLM no haya alucinado (PASS falso o falta de JSON)."""
        # Regla 2: Prohibido PASS
        if re.search(r'\bPASS\b', str(llm_response), re.IGNORECASE):
            return False, {
                "error": "VIOLACION_S37",
                "reason": "El LLM intentó emitir un PASS. Prohibido por el Kernel."
            }
        
        # Regla 3: Formato GCELL (debe tener el bloque de verificación)
        if "VERIFICACIÓN AGF-GCELL" not in str(llm_response):
            return False, {
                "error": "VIOLACION_S36",
                "reason": "Falta el bloque GCELL de 4 capas."
            }

        return True, None
