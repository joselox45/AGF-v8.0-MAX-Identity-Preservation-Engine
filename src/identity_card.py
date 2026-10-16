"""
AGF Prompt Kernel v3.0 — Arquitectura IDENTITY_CARD (evolucion incremental;
no desecha v0.2). Implementa la especificacion de tarea:
  - R1-R8 (invariantes desde base 0, NO_VISIBLE, prioridad R7, expresion)
  - Fase 0/1 (IDENTITY_CARD como contrato estricto)
  - Modalidades A/B/C con C=NOT_RUN fail-closed
  - Control de formato F (card identica caracter a caracter)
  - RECIBO con claves exactas + metricas por turno
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# R3: invariantes observables en base 0 (orden = prioridad R7 de grupos)
INVARIANTS = [
    "forma de rostro y mandibula", "tercios faciales",
    "ojos (forma, separacion, color)", "cejas", "nariz", "labios",
    "tono y subtono de piel", "textura visible",
    "marcas (lunares, pecas, cicatrices)", "vello facial", "asimetrias",
    "edad aparente", "expresion base",
]
# R7: prioridad entre invariantes en conflicto (mayor primero)
R7_PRIORITY = ["estructura y proporciones", "marcas distintivas",
               "forma de ojos, cejas, nariz y labios", "tono y textura",
               "expresion"]
R7_GROUP = {  # invariante -> grupo de prioridad R7
    "forma de rostro y mandibula": "estructura y proporciones",
    "tercios faciales": "estructura y proporciones",
    "marcas (lunares, pecas, cicatrices)": "marcas distintivas",
    "ojos (forma, separacion, color)": "forma de ojos, cejas, nariz y labios",
    "cejas": "forma de ojos, cejas, nariz y labios",
    "nariz": "forma de ojos, cejas, nariz y labios",
    "labios": "forma de ojos, cejas, nariz y labios",
    "tono y subtono de piel": "tono y textura",
    "textura visible": "tono y textura",
    "expresion base": "expresion",
}

EXPRESSION_AXES = {
    "boca": ("cerrada", "entreabierta", "sonrisa cerrada", "sonrisa con dientes"),
    "cejas": ("neutras", "elevadas", "fruncidas"),
    "mirada": ("directa", "desviada"),
}

RECIBO_KEYS = ["sujeto_id", "turn", "base0_sha256", "modalidad", "estado",
               "motivo", "lectura_base0", "NO_VISIBLE", "EXTRAPOLADO",
               "CONFLICTO_R7", "cambios_aplicados"]
VALID_STATES = ("EJECUTADO", "CONFLICTO", "NOT_RUN", "FAIL_FORMATO")


class CardError(ValueError):
    pass


@dataclass
class IdentityCard:
    """Fase 0: card en texto, un rasgo por linea, sin numeros."""
    observables: dict          # invariante -> descripcion | "NO_VISIBLE"
    expression: dict         # los 3 ejes obligatorios
    no_visible: list = field(default_factory=list)

    def __post_init__(self):
        for inv in self.observables:
            if inv not in INVARIANTS:
                raise CardError(f"invariante no reconocido: {inv!r}")
        for eje, permitidos in EXPRESSION_AXES.items():
            v = self.expression.get(eje)
            if v is None:
                raise CardError(f"eje de expresion obligatorio ausente: {eje}")
            if v not in permitidos:
                raise CardError(f"valor invalido en {eje}: {v!r}")

    def to_text(self) -> str:
        lines = [f"{inv}: {desc}" for inv, desc in self.observables.items()]
        for eje in EXPRESSION_AXES:                       # orden fijo de ejes
            lines.append(f"expresion {eje}: {self.expression[eje]}")
        return "\n".join(lines)

    @staticmethod
    def parse(text: str) -> "IdentityCard":
        obs, exp = {}, {}
        for line in text.strip().splitlines():
            eje = next((e for e in EXPRESSION_AXES
                        if line.startswith(f"expresion {e}: ")), None)
            if eje:
                exp[eje] = line.split(": ", 1)[1]
            elif ": " in line:
                k, v = line.split(": ", 1)
                obs[k] = v
        return IdentityCard(obs, exp)

    def r7_resolve(self, inv_a: str, inv_b: str) -> str:
        """R7: devuelve el invariante que CEDE (menor prioridad)."""
        ga = R7_PRIORITY.index(R7_GROUP.get(inv_a, "expresion"))
        gb = R7_PRIORITY.index(R7_GROUP.get(inv_b, "expresion"))
        return inv_b if ga < gb else inv_a


# ------------------------------------------------------------------
# Control de formato F (modalidad B)
# ------------------------------------------------------------------
def check_formato(prompt_text: str, card_text: str) -> str:
    """La IDENTITY_CARD del prompt debe ser identica caracter a caracter."""
    return "PASS" if card_text in prompt_text else "FAIL_FORMATO"


# ------------------------------------------------------------------
# RECIBO
# ------------------------------------------------------------------
def parse_recibo(text: str) -> dict:
    out = {}
    in_recibo = False
    for line in text.splitlines():
        if line.strip() == "RECIBO":
            in_recibo = True
            continue
        if in_recibo:
            for piece in line.split(" | "):      # formato pipe del spec
                if ":" in piece:
                    k, v = piece.split(":", 1)
                    out[k.strip()] = v.strip()
    return out


def validate_recibo(d: dict) -> str:
    faltan = [k for k in RECIBO_KEYS if k not in d]
    if faltan:
        return f"FAIL_FORMATO: claves ausentes {faltan}"
    if d["estado"] not in VALID_STATES:
        return f"FAIL_FORMATO: estado invalido {d['estado']!r}"
    return "PASS"


# ------------------------------------------------------------------
# Metricas por turno
# ------------------------------------------------------------------
class MetricasTurno:
    def __init__(self):
        self.n = 0
        self.f_ok = 0
        self.conflicto = 0
        self.extrapolado = 0
        self.not_run = 0

    def feed(self, recibo: dict, formato: str):
        self.n += 1
        if formato == "PASS":
            self.f_ok += 1
        if recibo.get("estado") == "CONFLICTO":
            self.conflicto += 1
        if recibo.get("EXTRAPOLADO", "ninguno") not in ("ninguno", ""):
            self.extrapolado += 1
        if recibo.get("estado") == "NOT_RUN":
            self.not_run += 1

    def rates(self) -> dict:
        n = max(1, self.n)
        return {"turnos": self.n,
                "F_cumplimiento": round(self.f_ok / n, 4),
                "tasa_CONFLICTO": round(self.conflicto / n, 4),
                "tasa_EXTRAPOLADO": round(self.extrapolado / n, 4),
                "tasa_NOT_RUN": round(self.not_run / n, 4)}


# ------------------------------------------------------------------
# Emision del kernel v3 (modalidad B)
# ------------------------------------------------------------------
def kernel_v3(escena: str, card: IdentityCard, turn: int,
              base0_sha256: str, modalidad: str = "B") -> str:
    card_text = card.to_text()
    return f"""[AGF_TASK v3.0]
external_state: {{"turn": {turn}, "sujeto_id": "base_0", "base0_sha256": "{base0_sha256}", "preservar": ["rostro", "edad aparente", "rasgos", "expresion base"]}}
ESCENA: {escena}

IDENTITY_CARD
{card_text}

REGLAS: R1 identidad solo desde base 0 (cada turno vs base 0) ·
R2 lo NO_VISIBLE no se deduce · R3 invariantes solo observables ·
R4 solo fondo/ropa/luz · R5 R1-R3,R7 > ESCENA (conflicto -> CONFLICTO) ·
R6 la identidad la mide un tercero · R7 prioridad: {' > '.join(R7_PRIORITY)} ·
R8 dentadura NO_VISIBLE -> sonrisa cerrada salvo conflicto declarado.

GENERA segun ESCENA con la IDENTITY_CARD como contrato estricto.
La IDENTITY_CARD debe aparecer literal e identica en la salida (control F).
Cierra con el RECIBO (claves exactas: {' | '.join(RECIBO_KEYS)}).
[/AGF_TASK]"""
