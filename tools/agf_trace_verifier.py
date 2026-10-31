#!/usr/bin/env python3
"""AGF Trace Verifier — Valida trazabilidad de Entrada (Input) y Salida (Output)."""
import json, sys

def calculate_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0]); yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2]); yB = min(boxA[3], boxB[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    if interArea == 0: return 0.0
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    return interArea / float(boxAArea + boxBArea - interArea)

def verify_trace(json_path):
    with open(json_path) as f: trace = json.load(f)
    
    in_claimed = trace.get("input_audit", {}).get("original_claimed_llm", {}).get("face_bbox", [0,0,0,0])
    in_real = trace.get("input_audit", {}).get("original_real_python", {}).get("face_bbox", [0,0,0,0])
    iou_in = calculate_iou(in_claimed, in_real)
    if iou_in < 0.85:
        print(f"FALLO: Alucinacion de entrada. IoU {iou_in:.2f} < 0.85"); return False
        
    out_claimed = trace.get("output_audit", {}).get("generated_claimed_llm", {}).get("face_bbox", [0,0,0,0])
    out_real = trace.get("output_audit", {}).get("generated_real_python", {}).get("face_bbox", [0,0,0,0])
    iou_out = calculate_iou(out_claimed, out_real)
    if iou_out < 0.85:
        print(f"FALLO: Alucinacion de salida. IoU {iou_out:.2f} < 0.85"); return False
        
    print(f"OK: Trazabilidad validada. IoU Input {iou_in:.2f}, IoU Output {iou_out:.2f}.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2: print("Uso: python tools/agf_trace_verifier.py trace.json"); sys.exit(1)
    verify_trace(sys.argv[1])
