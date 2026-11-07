# AGF v8.0-MAX — Identity Preservation Engine

**Versión:** v12.4.7.8-STRONG (Kernel v0.9.8)

**Versionado:** Repo v8.0-MAX es producto. Motor v12.4.7.8-STRONG es motor forense. Kernel v0.9.8 es gobernanza. Tres números, tres capas, sin conflicto.
**Estado:** Open Core · IP Privada Protegida

---

## ¿Qué es AGF?

Motor de auditoría forense de imágenes generadas por IA. Verifica si una imagen generada preserva la identidad de la persona original usando matemáticas locales (ArcFace + Fourier + SSIM), no la palabra de un chatbot.

**Filosofía:** *"Generate in the Chat. Get caught by the Math."*

---

## Arquitectura Dual (MIL/SIL/HIL)

| Rol | Dónde corre | Qué hace |
|-----|-------------|----------|
| **MIL-A** | Chatbot | Genera imágenes y texto |
| **MIL-B** | Chatbot con Boot Prompt | Audita la evidencia JSON |
| **HIL** | Termux / VPS | Procesa píxeles reales con ArcFace |

**Regla de oro:** Un LLM nunca dice `PASS`. Solo el HIL (Python) certifica identidad.

---

## Contenido del Open Core

### Motor Forense
- `tools/agf_full_9_layers.py` — Motor de 5 capas ponderadas + 4 de diagnóstico
- `agf_full.sh` — Orquestador CLI
- `main.py` — Orquestador CLI (audit, check, api)\n- `api_server.py` — API Flask con `/health` y `/audit`

### Infraestructura
- `Dockerfile` — Imagen Python 3.11 + OpenCV
- `docker-compose.yml` — Stack completo (AGF + MinIO + Prometheus + Grafana)
- `prometheus.yml` — Scraping de métricas
- `requirements.txt` — Dependencias Python

### Gobernanza
- `docs/governance/AGF_CHAT_KERNEL_v0.9.8_FULL.md`
- `docs/governance/CHATBOT_BOOT_PROMPT.md`
- `tools/check_kernel.py`

---

## IP Privada (Bóveda Local, NO en GitHub)

- `arcface.onnx` (174 MB) — Modelo de reconocimiento facial
- `blaze_face_full_range.tflite` — Detector de rostros
- `SISTEMA_CUADRUPLE_CAPA_v1.3_FOSO_MARIANAS.txt` — Especificación IPM

Se montan como volúmenes en el VPS.

---

## Instalación

### Local (Termux / Linux)
```bash
git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine
pip install -r requirements.txt
./agf_full.sh original.jpg generada.jpg preservation

### VPS con Docker
```bash
git clone https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine.git
cd AGF-v8.0-MAX-Identity-Preservation-Engine
scp arcface.onnx usuario@IP_VPS:~/
docker compose up -d
```
```

---

## Motor de 9 Capas Forenses

| Capa | Peso | Umbral |
|---|---|---|
| ArcFace (Identidad) | 40% | >= 0.65 (Hard Gate) |
| Fourier 2D | 30% | >= 0.40 |
| Shazam (Bordes) | 15% | >= 0.50 |
| SSIM (Pixeles) | 10% | >= 0.70 |
| Color Fingerprint | 5% | Delta H <= 90 grados |

**Total: 100%**

### Ledger de evidencia
Ledger núcleo en core/evidence_ledger.py (clase EvidenceLedger, hash-chain). Integración en core/agf_ledger.py (registrar_evidencia, verificar_ledger) usada por api_server.py. Ambos complementarios, no duplicados.

### Capas de Diagnóstico (no ponderan)

| Capa | Funcion |
|---|---|
| Metadata (XMP / EXIF) | Detecta firmas XMP/IA |
| Tiling (OpenCV Haar) | Detección de rostros (OpenCV o fallback) |
| Lighting (PIL + NumPy) | Consistencia de iluminación |
| Base64 Differential (hashlib) | Comparación binaria de hashes |

---



---

## Matriz de Correspondencia: Capas, Herramientas y Roles

Para evitar confusión entre el protocolo de chat (MIL-B) y el motor forense (HIL), esta es la correspondencia exacta:

| Rol | Entorno | Capas que aplica | Herramientas |
|-----|---------|------------------|--------------|
| **MIL-B** (Auditor) | Chatbot (ChatGPT/Claude/Meta) | **4 Capas GCELL** (Epistémica, Cognitiva, Lingüística, Ética) | Ninguna. Solo texto. Prohibido ejecutar código. |
| **HIL** (Motor Forense) | Python (Termux/VPS) | **9 Capas Forenses** (ArcFace, Fourier, Shazam, SSIM, Color + 4 diagnósticas) | `tools/agf_full_9_layers.py`, `tools/acta_final.py`, `tools/check_kernel.py` |

### Capas del MIL-B (Protocolo de texto)
El Boot Prompt obliga al LLM a auditar el texto bajo 4 capas GCELL y a declarar `GAP RESIDUAL` si no puede verificar algo (ej. un hash).

### Capas del HIL (Motor de imágenes)
El motor Python ejecuta las 9 capas reales sobre las imágenes y genera:
1. Un `composite_audit.json` con las métricas.
2. Un `acta_final.json` firmado con hash.
3. Un registro en el `ledger.jsonl` (hash-chain).

**Regla de oro:** El MIL-B nunca dice `PASS`. Si el HIL dice `BLOCKED` (porque ArcFace < 0.65), el sistema entero se detiene.

---

## Verificación Previa (Boot Prompt v2)

El Boot Prompt incluye una **verificación previa obligatoria** (sección 0) que el LLM debe ejecutar antes de auditar cualquier input:

1. ¿Tiene los 4 requisitos del MIL-B?
2. ¿El input cumple MAXCAP (≤200 caracteres)?
3. ¿Va a emitir PASS? (prohibido)

Si falla cualquiera, el LLM debe responder `BLOCKED` y NO auditar.

**Sin esta verificación, el Boot Prompt no cumple con el Kernel v0.9.8.**

## API Endpoints

| Endpoint | Metodo | Descripcion |
|---|---|---|
| `/health` | GET | Health check |
| `/audit` | POST | Recibe 2 imagenes, devuelve veredicto |

```bash
curl -X POST http://localhost:8000/audit -F "original=@original.jpg" -F "generated=@generada.jpg"
```

---

## Observabilidad

- **Prometheus:** `http://localhost:9090`
- **Grafana:** `http://localhost:3000` (usuario: `admin` · password: ver variable `GF_SECURITY_ADMIN_PASSWORD`)
- **MinIO:** `http://localhost:9001` (usuario: ver variable `MINIO_ROOT_USER` · password: ver `MINIO_ROOT_PASSWORD`)

---

## Limites Declarados

- **FAR/FRR:** No medidos en datasets estandar.
- **Corpus:** ~30 imagenes (no estadisticamente significativo).
- **Benchmark:** `UNVERIFIED / PENDING EXTERNAL`.

AGF es production-ready para un operador individual. NO certificado para verificacion empresarial.

---

## Licencia

MIT - Open Core, IP privada protegida.

---

*Actualizado el 2026-11-06 bajo gobernanza del Kernel v0.9.8.*

## No Dependency on Private Commercial LLM APIs

AGF-GCELL core runs locally, without any dependency on private commercial LLM chatbot APIs.
The forensic engine, the ledger, and the verification use local math (ArcFace + Fourier + SSIM), not the word of a chatbot.
MIL-A / MIL-B can be any LLM, including a commercial one, but the core does not send biometric data, photos, embeddings, or keys to external APIs.
Your photos, embeddings, and keys stay on your machine / your server.

## Roles in plain words / Roles en palabras simples

English: Think of a kitchen. SIL is the oven, it only cooks, it does not think. MIL is the assistant cook, it prepares and checks. HIL is YOU, the chef owner, you taste and say YES or NO. No dish goes out without YOU.

Espanol: Piensa en una cocina. SIL es el horno, solo cocina, no piensa. MIL es el ayudante de cocina, prepara y revisa. HIL eres TU, el chef dueno, tu pruebas y dices SI o NO. Ningun plato sale sin TI.

English: SIL = Software, the code. It executes tests, calculates, generates reports. It does not decide.
Espanol: SIL = Software, el codigo. Ejecuta tests, calcula, genera actas. No decide.

English: MIL-A = AI Operator. It prepares commands, cleans, generates. It does the work.
Espanol: MIL-A = IA Operadora. Prepara comandos, limpia, genera. Hace el trabajo.

English: MIL-B = AI Auditor. It checks the work of MIL-A, asks for evidence, says HUMAN_REVIEW or BLOCKED. It does not execute changes.
Espanol: MIL-B = IA Auditora. Revisa el trabajo de MIL-A, pide evidencia, dice HUMAN_REVIEW o BLOCKED. No ejecuta cambios.

English: MIL-C = AI Keeper. It saves backup and compares before/after. It alerts if something is lost.
Espanol: MIL-C = IA Guardiana. Guarda copia y compara antes/después. Alerta si algo se pierde.

**COPIAR EL BOOT (PASOS PARA DESCARGAR, SI RECIEN ENTRAS A GITHUB:**
**1. CREA UNA CUENTA EN GITHUB.COM SI NO TIENES, CON TU CORREO Y CONTRASENA. SI YA TIENES, ENTRA CON TU CUENTA.**
**2. EN EL BUSCADOR DE GITHUB, ESCRIBE: JOSELOX45/AGF-V8.0-MAX-IDENTITY-PRESERVATION-ENGINE Y PULSA ENTER.**
**3. ENTRA A LA CARPETA docs/governance/ PULSANDO SOBRE ELLA.**
**4. ABRE EL ARCHIVO CHATBOT_BOOT_PROMPT.md PULSANDO SOBRE EL.**
**5. PULSA RAW ARRIBA A LA DERECHA. AHORA VES SOLO EL TEXTO DEL BOOT, SIN BOTONES.**
**PARA COPIARLO: EN EL MOVIL, MANTEN PULSADO EL TEXTO HASTA QUE SALGA SELECCIONAR TODO, PULSA SELECCIONAR TODO, LUEGO PULSA COPIAR. EN LA COMPUTADORA, PULSA CTRL + A PARA SELECCIONAR TODO, LUEGO CTRL + C PARA COPIAR.**
**PARA DESCARGARLO: PULSA LOS 3 PUNTOS ... ARRIBA A LA DERECHA, PULSA DOWNLOAD O DESCARGAR. EL ARCHIVO BAJA A TU CARPETA DOWNLOADS / DESCARGAS.**
**SUBELO O PEGALO AL CHATBOT DE TU PREFERENCIA: ABRE EL CHATBOT, ABRE UN CHAT NUEVO, PULSA EN EL CUADRO DE TEXTO DONDE ESCRIBES. EN EL MOVIL, MANTEN PULSADO Y PULSA PEGAR. EN LA COMPUTADORA, PULSA CTRL + V PARA PEGAR. SI QUIERES SUBIRLO COMO ARCHIVO, PULSA EL CLIP O + Y ELIGE EL ARCHIVO CHATBOT_BOOT_PROMPT.md QUE DESCARGASTE. LUEGO PULSA ENVIAR.**
**SOLO NECESITAS EL BOOT. NO NECESITAS SUBIR NI PEGAR NINGUN OTRO ARCHIVO.**
**PROBADO EN: CLAUDE, CHATGPT, META AI, CUENTA FREE. AUN NO EN CUENTAS PLUS / PREMIUM.**
**AUN NO SE REALIZARON PRUEBAS EN OTROS CHATBOTS COMO GROK, DEEPSEEK, KIMI 3, DOLA, NI EN NINGUN OTRO ASISTENTE DE IA. PUEDES CREAR UNA CUENTA O USAR TU CUENTA Y PROBARLO.**
**EL BOOT EN .TXT TAMBIEN EXISTE, PERO AUN NO SE REALIZARON PRUEBAS CON EL BOOT EN .TXT.**
