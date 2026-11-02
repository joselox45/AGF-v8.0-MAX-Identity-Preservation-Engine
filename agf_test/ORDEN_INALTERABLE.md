# ORDEN INALTERABLE — AGF v12.3.8

## 1. Primer test obligatorio inalterable
tools/agf_token_forensic.py
- CAPA 4.5 Puente SIL-HIL
- HIL mide tokens SIL (Base64 294 bloques, entropía, ratio)
- Correlación Overlay 6.27% pixel
- PASS doblemente sellado 0.9489 + 6.12% token
- Regla: DECLARO → EJECUTO → VERIFICO

## 2. Segundo test inalterable
Capa 5-9 Composite
- [1] 40% ArcFace
- [2] 30% Fourier (veto <0.40)
- [3] 20% Shazam
- [4] 10% SSIM
- [5] 5% Color
- Threshold 0.7825, veto ArcFace <0.30

## 3. Extras
Metadata, Tiling, Lighting, Base64, Overlay visual
