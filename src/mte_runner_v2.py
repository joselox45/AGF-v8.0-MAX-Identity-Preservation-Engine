"""
AGF — mte_runner v2 (T32). Cierra los 3 P0 de la auditoria externa:
  P0-1: cobertura obligatoria (rechaza ausentes/duplicados/desconocidos)
  P0-2: evidence_ref validado (formato sha256:<64hex> + verificacion en disco)
  P0-3: resultado identificado (version del runner + commit + cobertura)
Compatibilidad: mte_runner v1 queda intacto; v2 es el evaluador canónico.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from dataclasses import dataclass, asdict

RUNNER_VERSION = "2.0"
EVIDENCE_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

REQUIRED_TESTS = tuple(
    [f"T{n:02d}" for n in range(1, 21)] +      # T01..T20 (MTE v1.0)
    [f"T{n}" for n in range(21, 32)]           # T21..T31 (v9.0 + T29-T31)
)
REQUIRED_SET = frozenset(REQUIRED_TESTS)

# Auditoria 10 (critico 2): mapa test_id -> archivo real de evidencia en disco.
# Sin esto, v2.1 buscaba evidence/T21.json cuando el archivo es t21.json
# (Linux es case-sensitive) y rechazaba la evidencia real del propio repo.
EVIDENCE_MAP = {
    "T21": "t21.json", "T22": "t22.json",
    "T26": "closure_t21_t26.json", "T27": "closure_t21_t26.json",
    "T30": "benchmark_t30.json",
}

TERMINAL_BAD = ("FAIL", "BLOCKED", "UNVERIFIED", "NOT_RUN")
VALID_STATES = ("PASS", "FAIL", "BLOCKED", "UNVERIFIED",
                "NOT_RUN", "NOT_APPLICABLE")


@dataclass
class RunnerVerdict:
    status: str            # CONFORMANT_WITHIN_TESTED_SCOPE | NON_CONFORMANT
    reasons: list
    runner_version: str
    commit_sha: str
    tests_covered: int
    tests_required: int
    metrics: dict = None   # C_req / C_exec / C_evidence / C_pass (auditoria 10)

    def to_dict(self):
        return asdict(self)


class MTERunnerV2:
    def __init__(self, repo_root: str = "."):
        self.repo_root = repo_root

    # -- P0-3: identidad del evaluador ---------------------------------
    def _commit_sha(self) -> str:
        try:
            out = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True,
                text=True, cwd=self.repo_root, timeout=5)
            return out.stdout.strip() if out.returncode == 0 else "UNKNOWN"
        except Exception:
            return "UNKNOWN"

    # -- P0-2: evidencia -----------------------------------------------
    def _check_evidence(self, rec: dict) -> str | None:
        """Devuelve razon de rechazo o None si es aceptable."""
        if rec.get("status") != "PASS":
            return None                      # solo PASS exige evidencia
        ev = rec.get("evidence_ref") or ""
        if not EVIDENCE_RE.match(ev):
            return f"evidence_ref invalido (debe ser sha256:<64hex>): {ev!r}"
        digest = ev.split(":", 1)[1]
        fname = EVIDENCE_MAP.get(rec["test_id"],
                                 f"{rec['test_id']}.json")
        path = os.path.join(self.repo_root, "evidence", fname)
        if os.path.exists(path):
            real = hashlib.sha256(open(path, "rb").read()).hexdigest()
            if real != digest:
                return (f"hash de evidencia no coincide con {path} "
                        f"(declarado {digest[:12]}… vs real {real[:12]}…)")
        return None                          # archivo ausente: NO DETERMINADO
                                               # pero no invalida por si solo

    # -- P0-1: cobertura --------------------------------------------------
    def evaluate(self, records: list) -> RunnerVerdict:
        reasons = []
        # duplicados
        ids = [r.get("test_id", "") for r in records]
        seen, dups = set(), set()
        for i in ids:
            if i in seen:
                dups.add(i)
            seen.add(i)
        if dups:
            reasons.append(f"test_id duplicados: {sorted(dups)}")
        # desconocidos
        unknown = [i for i in ids if i and i not in REQUIRED_SET]
        if unknown:
            reasons.append(f"test_id desconocidos: {sorted(set(unknown))}")
        # ausentes
        missing = sorted(REQUIRED_SET - set(ids))
        if missing:
            reasons.append(f"pruebas obligatorias ausentes: {missing}")
        # estados invalidos + evidencia + exclusiones gobernadas (G-04)
        for r in records:
            if r.get("status") not in VALID_STATES:
                reasons.append(
                    f"{r.get('test_id')}: estado invalido {r.get('status')!r}")
            if r.get("status") == "NOT_APPLICABLE":
                if not (r.get("na_justification") or "").strip():
                    reasons.append(
                        f"{r.get('test_id')}: NOT_APPLICABLE sin justificacion")
                if not (r.get("na_authority") or "").strip():
                    reasons.append(
                        f"{r.get('test_id')}: NOT_APPLICABLE sin autoridad que aprueba la exclusion")
            bad_ev = self._check_evidence(r)
            if bad_ev:
                reasons.append(bad_ev)
        # agregacion (semantica v1)
        statuses = {r.get("status") for r in records}
        if not reasons and not (statuses & set(TERMINAL_BAD)):
            status = "CONFORMANT_WITHIN_TESTED_SCOPE"
        else:
            status = "NON_CONFORMANT"
        covered = set(ids) & REQUIRED_SET
        exec_ids = {r.get("test_id") for r in records
                    if r.get("status") in ("PASS", "FAIL")}
        ev_ok = {r.get("test_id") for r in records
                 if r.get("status") == "PASS" and not self._check_evidence(r)}
        return RunnerVerdict(
            status, reasons, RUNNER_VERSION, self._commit_sha(),
            len(covered), len(REQUIRED_SET),
            metrics={"C_req": round(len(covered) / len(REQUIRED_SET), 4),
                     "C_exec": round(len(exec_ids) / len(REQUIRED_SET), 4),
                     "C_evidence": (round(len(ev_ok) / len(exec_ids), 4)
                                    if exec_ids else None),
                     "C_pass": round(len(ev_ok) / len(REQUIRED_SET), 4)})


def load_records(path: str) -> list:
    return json.load(open(path))
