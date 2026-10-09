#!/usr/bin/env python3
"""
AGF v8 MAX — CLI maestra (chat-window framework)
================================================
Punto unico de operacion. Todo corre del lado del operador;
los LLMs opacos solo reciben texto por su ventana de chat.

  python agf.py doctor     # autodiagnostico de componentes
  python agf.py kernel OP  # emitir bloque [AGF_OPERATION]
  python agf.py go         # kernel -> portapapeles (operador solo pega)
  python agf.py run        # ciclo demo del Chat Runtime
  python agf.py closure A.jpg B.jpg M.tflite [arcface|facenet] [norm|raw|div255]
  python agf.py benchmark --spec pares.json --embedder M.tflite
  python agf.py attest evidence/x.json [--seed HEX]
  python agf.py demo-ventana

PRINCIPIO: AGF no controla el LLM interno; controla y verifica la
interaccion a traves de su ventana de chat. Sin API, sin pesos, sin backend.
"""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))


def cmd_doctor(_):
    from evidence_taxonomy import EvidenceClassifier
    checks = []

    def check(name, fn):
        try:
            ok, detail = fn()
        except Exception as e:
            ok, detail = False, str(e)
        checks.append({"componente": name, "ok": ok, "detail": detail})

    check("python", lambda: (sys.version_info >= (3, 9),
                             f"{sys.version_info.major}.{sys.version_info.minor}"))
    check("numpy", lambda: (True, __import__("numpy").__version__))
    check("PIL", lambda: (True, __import__("PIL").__version__))
    def _tflite():
        from tflite_runtime.interpreter import Interpreter  # noqa
        return True, "tflite_runtime OK"
    check("tflite_runtime", _tflite)
    def _crypto():
        import cryptography
        return True, cryptography.__version__
    check("cryptography", _crypto)
    def _kernel():
        from prompt_kernel import PromptKernel
        b = PromptKernel().build("REPAIR", "ref", "tgt").prompt_block
        return "[AGF_OPERATION]" in b and "IDENTITY_PRESERVATION = MAX" in b, "kernel v0.2 OK"
    check("prompt_kernel", _kernel)
    def _fsm():
        from chat_runtime import ChatRuntime, RuntimeEvent, State
        rt = ChatRuntime(max_retries=0)
        rt.start("REPAIR", b"r", b"t")
        step = rt.feed(RuntimeEvent("OUTPUT_RECEIVED", b"o", "GENERATED"))
        return step.state == State.BLOCKED, "FSM fail-closed OK"
    check("chat_runtime_fsm", _fsm)
    def _governor():
        from apce_governor import APCEGovernor, AGFVerdict
        d = APCEGovernor().review(AGFVerdict("MTE", "PASS", None))
        return d.final_state == "BLOCKED", "G1 no-fabrication OK"
    check("apce_governor", _governor)
    def _embedder():
        from tflite_embedder import TFLiteFaceEmbedder, EmbeddingStatus
        r = TFLiteFaceEmbedder("arcface").embed(None)
        return r.status == EmbeddingStatus.BLOCKED, "embedder fail-closed OK"
    check("tflite_embedder", _embedder)

    n_ok = sum(1 for x in checks if x["ok"])
    estado = "OPERATIVO" if n_ok == len(checks) else \
             "PARCIAL (componentes en False degradan a BLOCKED; nada se fabrica)"
    print(json.dumps({"estado": estado, "ok": f"{n_ok}/{len(checks)}",
                      "checks": checks}, indent=2, ensure_ascii=False))


def cmd_kernel(args):
    from prompt_kernel import PromptKernel, KernelError
    op = args[0] if args else "REPAIR"
    try:
        kr = PromptKernel().build(op, "<SHA512_IMAGEN_REFERENCIA>",
                                  "<SHA512_IMAGEN_OBJETIVO>")
    except KernelError as e:
        print(json.dumps({"status": "BLOCKED", "reason": str(e)})); sys.exit(2)
    print(kr.prompt_block)
    print("\n# OPERADOR: adjunta referencia + objetivo en la ventana del LLM.")


def cmd_go(args):
    from prompt_kernel import PromptKernel, KernelError
    op = args[0] if args else "REPAIR"
    try:
        kr = PromptKernel().build(op, "<referencia>", "<objetivo>")
    except KernelError as e:
        print(json.dumps({"status": "BLOCKED", "reason": str(e)})); sys.exit(2)
    copied = False
    try:
        import shutil, subprocess as sp
        if shutil.which("termux-clipboard-set"):
            sp.run(["termux-clipboard-set"], input=kr.prompt_block.encode(), check=True)
            copied = True
    except Exception:
        copied = False
    if copied:
        print("[OK] Bloque copiado al portapapeles.")
        print("1. Abre tu chatbot y adjunta las 2 imagenes.")
        print("2. Pega (manten pulsado -> Pegar) y envia.")
        print("3. Recibe imagen + [AGF_VERIFICATION_REPORT].")
    else:
        print("[INFO] Sin termux-api: copia el bloque manualmente.")
        print(kr.prompt_block)


def cmd_run(_):
    p = os.path.join(ROOT, "examples", "agf_chat_runtime_v0.2_single.py")
    subprocess.run([sys.executable, p])


def cmd_demo_ventana(_):
    print("""PROTOCOLO OPERADOR — ejecucion estricta en ventana de chat
PASO 1 (este equipo):  python agf.py go
PASO 2 (ventana LLM):  adjunta 2 imagenes + pega
PASO 3 (ventana LLM):  recibe imagen editada + reporte
PASO 4 (este equipo):  sha512sum foto_editada.jpg
PASO 5 (opcional):     python agf.py attest evidence/<archivo>.json
Regla de oro: sin API. La ventana de chat es el unico canal.""")


def _delegate(script, args):
    p = os.path.join(ROOT, "tools", script)
    if not os.path.exists(p):
        print(json.dumps({"status": "BLOCKED", "reason": f"falta {p}"})); sys.exit(2)
    subprocess.run([sys.executable, p] + args)


COMMANDS = {
    "doctor": cmd_doctor,
    "go": cmd_go,
    "kernel": cmd_kernel,
    "run": cmd_run,
    "demo-ventana": cmd_demo_ventana,
    "closure": lambda a: _delegate("closure_t21_tflite.py", a),
    "benchmark": lambda a: _delegate("bio_benchmark.py", a),
    "attest": lambda a: _delegate("attest.py", a),
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        print("comandos:", ", ".join(COMMANDS))
        sys.exit(2)
    COMMANDS[sys.argv[1]](sys.argv[2:])
