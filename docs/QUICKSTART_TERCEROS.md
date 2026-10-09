# AGF — Uso para terceros (link + 2 comandos, sin leer el prompt)

## Qué recibes
Solo el link del repositorio. No necesitas leer ni entender ningun prompt.

## Pasos

```bash
# 1. Una sola vez
pkg install -y git python
git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine

# 2. Opcion A (recomendada): kernel en el portapapeles, solo pegas
pkg install -y termux-api
python agf.py go          # -> bloque copiado; solo Ctrl+V en el chatbot

# 2. Opcion B (sin termux-api): te lo muestra para copiar a mano
python agf.py kernel REPAIR
```

1. Abre ChatGPT / Gemini / Grok / Meta AI
2. Adjunta referencia + objetivo
3. Pega y envia
4. Recibe imagen editada + reporte [AGF_VERIFICATION_REPORT]

## Nota tecnica honesta
Los LLM opacos solo aceptan texto por su ventana: el prompt viaja como un
mensaje mas. Pero es solo una orden de trabajo (sin claves ni datos); tu no
tienes que leerlo, editarlo ni entenderlo. El sistema de verificacion y
evidencia queda en tu equipo (agf.py), no en el chatbot.

## Verificacion (opcional, cuando tengas modelos TFLite)
python agf.py closure fotoA.jpg fotoB.jpg modelo.tflite facenet raw
