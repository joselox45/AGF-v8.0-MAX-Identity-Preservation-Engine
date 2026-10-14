# Framework de Ejecucion en Ventana de Chat

AGF SHALL NOT CONTROL THE INTERNAL LLM. AGF SHALL CONTROL AND VERIFY THE
INTERACTION WITH THE LLM THROUGH ITS CHAT INTERFACE.

## Tres planos
GOVERNOR (APCE v8.1.0 G1-G6) -> ENGINE (agf.py, kernel, verificacion TFLite)
-> CANAL (ventana de chat: texto + imagenes, sin API).

## Flujo
agf.py go -> artefacto firmado -> segunda ventana (LLM opaco) -> imagen +
[AGF_VERIFICATION_REPORT] -> verify_image.py (L1/L2/L3, pesos reales).

## Precision
La biometria se calcula FUERA de la ventana (del lado del operador).
La ventana declara; la custodia decide. Ver docs/VERIFICATION_PROTOCOL.md.
