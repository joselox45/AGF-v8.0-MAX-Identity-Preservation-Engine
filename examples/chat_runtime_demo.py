"""Demo AGF Chat Runtime v0.1 — ciclo completo simulado en ventana de chat."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from chat_runtime import ChatRuntime, RuntimeEvent

rt = ChatRuntime(max_retries=1)

# 1) Intake de imágenes (bytes pegados por el operador)
step = rt.start("REPAIR", b"REFERENCE_IMAGE_BYTES", b"TARGET_IMAGE_BYTES")
print("[DISPATCH]", step.dispatch_instruction[:120], "...")
print("[KERNEL BLOCK]\n", step.dispatch_prompt)

# 2) El operador pega el bloque en ChatGPT/Gemini/Grok y devuelve el resultado
step = rt.feed(RuntimeEvent("OUTPUT_RECEIVED", b"EDITED_IMAGE_BYTES",
                            declared_provenance="RECONSTRUCTED"))
print("[RESULT]", step.state.value, "->", step.message)
print("[CHAIN]", json.dumps(rt.chain_check()))
