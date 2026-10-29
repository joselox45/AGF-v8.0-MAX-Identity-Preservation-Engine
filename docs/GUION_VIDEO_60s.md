# GUIÓN VIDEO DEMO — AGF v8 MAX (60 segundos)
Formato: vertical 9:16 (TikTok/Reels/Shorts). Grabación real en el teléfono.
Locución: tú, voz en off, tono seco y técnico. Sin música hype.

## ESCENA 1 (0-8s) — EL PROBLEMA
VISUAL: Split screen. Izquierda: foto familiar dañada (rayón/mancha).
        Derecha: la misma foto "restaurada" por IA genérica con la cara CAMBIADA.
TEXTO EN PANTALLA: "La IA 'restaura' tu foto... y te cambia la cara"
LOCUCIÓN: "Pediste que una IA repare una foto. ¿Y si te cambia la identidad?"

## ESCENA 2 (8-20s) — LA SOLUCIÓN
VISUAL: Termux real. Escribes: python agf.py go
        → "[OK] Bloque copiado al portapapeles."
TEXTO: "AGF: Identity Lock + mínima intervención"
LOCUCIÓN: "AGF genera una orden de trabajo quirúrgica: qué se puede tocar,
qué está prohibido cambiar, y qué se hace ante la duda: no tocar."

## ESCENA 3 (20-35s) — EJECUCIÓN EN EL CHATBOT
VISUAL: Grabación de pantalla del chatbot (ChatGPT/Gemini/Grok).
        Adjuntas 2 fotos. Pegas. Envías. Recibes imagen editada + reporte.
TEXTO: "Sin API. Sin plugins. Solo la ventana de chat."
LOCUCIÓN: "Sin API, sin instalar nada en el modelo. Solo su ventana de chat.
El chatbot nunca ejecuta nuestro código."

## ESCENA 4 (35-50s) — LA VERIFICACIÓN (el diferencial)
VISUAL: Termux: python agf.py closure fotoA fotoB facenet.tflite facenet raw
        → JSON con cosine 0.9675, status PASS, weights_sha256.
TEXTO: "Verificación biométrica real: cosine 0.9675 · reproducible"
LOCUCIÓN: "Y aquí está la diferencia: no confiamos en el chatbot.
Verificamos con FaceNet en tu teléfono. Mismo rostro: 0.9675.
Reproducible, byte a byte, con evidencia firmable."

## ESCENA 5 (50-60s) — CIERRE
VISUAL: Logo/texto: github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine
        + badges: "Fail-closed · Zero fabrication · APCE governed"
TEXTO: "Código abierto. Gobernanza APCE. Sin PASS fabricados."
LOCUCIÓN: "Código abierto. Si no hay evidencia, el sistema se niega a afirmar.
Eso es AGF."

## NOTAS DE PRODUCCIÓN
- Usa TUS fotos reales del closure (ya tienes evidencia verificada)
- La escena 4 es la que ningún competidor puede filmar: verificación en device
- Versión EN: duplicar guion con locución en inglés (mismo material)
- Hashtags: #IA #restauracionfotos #identidad #failclosed #opensource
