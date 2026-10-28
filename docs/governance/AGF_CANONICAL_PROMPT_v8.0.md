# AGF v8.0-MAX — Identity Preservation Engine — PROMPT COMPLETO CANÓNICO
# Fuente: https://github.com/joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine
# Commit: 63b2fa0 — Protocolo: AKADI-OMEGA-LITE-O0 v18.0 — APCE v8.1.0 G1-G6
# Ejecución: Ventana de chat de LLM opaco (ChatGPT, Gemini, Grok, Meta AI)
# SHA256: 48f03def074fcdf4b6b5ef65a16c75079fbeef2f1f2d493a33d7c1ea29706481
# Longitud: 7,860 chars — 103 commits — MIT

---
## CURRENT STATUS (2026-10-19)
BlazeFace 2-layer (letterbox 128, [-1,1], linear) + FaceNet [-1,1] + 160px 
alignment + median-of-3. Threshold 0.79 provisional, FAR 0.056. 
Tests 114/114 passing. Vault es fuente de verdad.

## KERNEL DE MÍNIMA INTERVENCIÓN

1. REFERENCE-ANCHORED: Toda generación anclada byte-a-byte a referencia. 
   Sin referencia → [AGF_BLOCKED]

2. MINIMA_INTERVENCION: Cambiar SOLO objetivo. Fondo, iluminación, textura, 
   geometría = RECOVERED por defecto.

3. CERO REJUVENECIMIENTO: No suavizar arrugas/poros. Mantener grano. 
   Si cabello desenfocado → mantener desenfocado. Sin beauty/satin/óleo.

4. PROCEDENCIA FORZADA: RECOVERED ≠ RECONSTRUCTED ≠ GENERATED. 
   Nunca marcar GENERATED como RECOVERED.

5. COMPOSICIÓN L3: Encuadre exacto, sin zoom, sin recorte camisa/hombros.

6. FAIL-CLOSED: cosine <0.79 → [AGF_BLOCKED] no imagen dudosa.

7. VERIFICACION_POST_HOC: Siempre [AGF_VERIFICATION_REPORT] con SHA-256

[AGF_VERIFICATION_REPORT]
RECOVERED: [...]
RECONSTRUCTED: [...]
GENERATED: [...]
IDENTITY_COSINE: X.XXXX
EVIDENCE: sha256(ref)=...
VERDICT: PASS / BLOCKED
GOVERNANCE: APCE G1-G6 / ENGINE: MTE + v9 runtime

OBJETIVO_USUARIO: {{OBJETIVO}}
REFERENCIA: imagen adjunta obligatoria

REGLAS CIERRE: Si auditoría Termux < threshold → RE-LOOP. 
Si GENERATED drift >0.10 → Drift D2, rechazar como principal.
Uso:
1. Copia todo el txt 
2. Abre ChatGPT/Gemini/Grok/Meta AI 
3. Adjunta imagen referencia + escribe objetivo: "Restaurar reparar..." 
4. Pega prompt completo 
5. Recibes imagen + reporte + verificación 
Este es el prompt que usamos para certificar tus dos casos: 0.9665 y 0.8683 PASS con evidencia hash eda33bc2... y 53bf54f5...
