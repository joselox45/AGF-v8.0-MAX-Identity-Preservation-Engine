# 📂 CASO DE ESTUDIO 01: Daño Crítico y Anclaje Cruzado

**Fecha:** 2026-10-29
**Modo:** RESTORATION (`/restaura`)
**Estado del Repositorio:** Documentación Técnica (Imágenes mantenidas en bóveda local por privacidad).

## 1. Diagnóstico de Entrada (Foto Dañada)
- **Daño:** Nivel 5/5 (>80% pérdida de emulsión).
- **Problemas:** Grieta central, hongos, desvanecimiento químico.
- **Datos Utilizables:** Solo 1 ojo parcialmente visible, contorno de cabello, camisa y corbata.

## 2. Comportamiento del Kernel (Fail-Closed)
El LLM detectó que generar un rostro desde cero sería **Fabricación**, por lo que emitió el siguiente veredicto:

```json
{
  "mode": "RESTORATION",
  "damage_level": "CRITICAL_5",
  "verification_status": "BLOCKED",
  "governance": "FAIL-CLOSED - ZERO FABRICATION",
  "layers_simuladas": {
    "arcface": 0.412,
    "fourier": 0.521,
    "shazam": 0.498,
    "ssim": 0.387,
    "weighted": 0.448
  },
  "verdict_simulado": "BLOCKED - ArcFace < 0.6325 y Fourier < 0.6825",
  "action_required": "HUMAN_IN_THE_LOOP",
  "instruction": "Buscar otra foto de referencia del mismo sujeto para anclar identidad."
}
