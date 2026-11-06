# AGF v8.0-MAX — Identity Preservation Engine

**Versión:** v12.4.7.8-STRONG (Kernel v0.9.8)
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
Ledger en core/evidence_ledger.py. Archivo core/agf_ledger.py existe en repo. Archivo autoritativo pendiente de decision HIL.

### Capas de Diagnóstico (no ponderan)

| Capa | Funcion |
|---|---|
| Metadata (XMP / EXIF) | Revisar metadatos |
| Tiling (OpenCV Haar) | Detectar rostros / mosaico |
| Lighting (PIL + NumPy) | Consistencia de luz |
| Base64 Differential (hashlib) | Diferencia entre originales |

| # | Capa | Función |
|---|------|---------|
| 1 | Metadata | Detecta firmas XMP/IA |
| 2 | Tiling | Detección de rostros (OpenCV o fallback) |
| 3 | Lighting | Consistencia de iluminación |
| 4 | Base64 Differential | Comparación binaria de hashes |

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
