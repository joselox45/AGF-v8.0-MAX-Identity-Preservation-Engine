#!/usr/bin/env python3
"""Calibrador de umbral ArcFace.
Simula el cálculo de FAR/FRR para justificar el umbral de 0.65.
"""
import numpy as np

# Simulación de distribuciones (en un caso real, se extraen de ArcFace)
# Personas distintas (impostores)
impostores = np.random.normal(loc=0.20, scale=0.10, size=1000)
# Misma persona (genuinos)
genuinos = np.random.normal(loc=0.80, scale=0.10, size=1000)

def calcular_metricas(umbral):
    # FAR: Falsos Aceptados (impostores que superan el umbral)
    far = np.sum(impostores >= umbral) / len(impostores)
    # FRR: Falsos Rechazados (genuinos que no superan el umbral)
    frr = np.sum(genuinos < umbral) / len(genuinos)
    return far, frr

print("Umbral | FAR (%) | FRR (%) | EER (Equal Error Rate)")
print("-" * 55)

mejor_eer = 1.0
mejor_umbral = 0.0

for u in np.arange(0.3, 0.9, 0.05):
    far, frr = calcular_metricas(u)
    eer = (far + frr) / 2
    if eer < mejor_eer:
        mejor_eer = eer
        mejor_umbral = u
    print(f"{u:.2f}   | {far*100:6.2f}  | {frr*100:6.2f}  | {eer*100:.2f}%")

print("\n[!] El umbral óptimo (menor EER) es aproximadamente:", round(mejor_umbral, 2))
print("[!] Nota: Los datos son simulados. En producción, se extraen del modelo real.")
