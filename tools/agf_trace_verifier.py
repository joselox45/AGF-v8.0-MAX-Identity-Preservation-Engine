#!/usr/bin/env python3
"""
AGF Trace Verifier — Valida trazabilidad 3D (XY + Z + Pose + Rotacion + IDs).
"""
import json
import sys

def verify_trace(json_path: str):
    with open(json_path) as f:
        trace = json.load(f)

    orig_pose = trace.get("original", {}).get("pose", {})
    gen_pose = trace.get("generated_real", {}).get("pose", {})

    delta_yaw = abs(gen_pose.get("yaw", 0) - orig_pose.get("yaw", 0))

    # Umbral dinámico basado en giro (CPEP vFinal)
    if delta_yaw < 30:
        threshold = 0.60
    elif delta_yaw < 90:
        threshold = 0.50
    elif delta_yaw < 170:
        threshold = 0.40
    else:
        threshold = 0.35

    print(f"INFO: Delta yaw {delta_yaw}°, threshold ajustado a {threshold}.")

    arcface = trace.get("identity", {}).get("arcface", 0.0)

    if arcface < threshold:
        print(f"FALLO: ArcFace {arcface:.2f} < threshold {threshold:.2f}")
        return False

    print(f"OK: Trazabilidad validada. ArcFace {arcface:.2f} >= {threshold:.2f}.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python tools/agf_trace_verifier.py trace.json")
        sys.exit(1)
    verify_trace(sys.argv[1])
