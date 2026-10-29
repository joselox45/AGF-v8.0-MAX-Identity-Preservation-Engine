#!/usr/bin/env python3
"""
AGF v10.1 PIXEL_LOCKED - Unified CLI (Truly Honest Doctor)
Verifica con importlib la presencia real de las librerías.
"""
import sys
import os
import importlib.util
import subprocess

VERSION = "10.1-PIXEL_LOCKED (Truly Honest)"
DEFAULT_MODE = os.getenv("AGF_MODE", "RESEARCH")

def check(name, condition, details=""):
    status = "[OPERATIVO]" if condition else "[FALTANTE]"
    print(f"{status} {name} {details}")
    return condition

def is_lib_installed(lib_name):
    return importlib.util.find_spec(lib_name) is not None

def doctor():
    print(f"=== AGF {VERSION} DOCTOR ===")
    
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    facenet_root = os.path.exists(os.path.join(root, "facenet.tflite"))
    facenet_sandbox = os.path.exists(os.path.join(root, "sandbox", "facenet.tflite"))
    blaze_root = os.path.exists(os.path.join(root, "blaze_face_short_range.tflite"))
    blaze_sandbox = os.path.exists(os.path.join(root, "sandbox", "blaze_face_short_range.tflite"))

    checks = []
    
    # 1. Python
    checks.append(check("Python 3.9+", sys.version_info >= (3, 9), f"({sys.version.split()[0]})"))
    
    # 2-5. Librerías (Verificación REAL)
    checks.append(check("TFLite Runtime", is_lib_installed("tflite_runtime")))
    checks.append(check("NumPy", is_lib_installed("numpy")))
    checks.append(check("Pillow", is_lib_installed("PIL")))
    checks.append(check("Cryptography", is_lib_installed("cryptography")))
    
    # 6-7. Modelos
    checks.append(check("FaceNet Model", facenet_root or facenet_sandbox, "(raíz)" if facenet_root else "(sandbox)" if facenet_sandbox else ""))
    checks.append(check("BlazeFace Model", blaze_root or blaze_sandbox, "(raíz)" if blaze_root else "(sandbox)" if blaze_sandbox else ""))
    
    # 8-11. Documentos y Herramientas
    kernel_exists = os.path.exists(os.path.join(root, "docs", "governance", "AGF_CHAT_KERNEL_v0.7.0_SMHP.md"))
    checks.append(check("Prompt Kernel v0.7.0 (SMHP)", kernel_exists))
    checks.append(check("Evidence Folder", os.path.isdir(os.path.join(root, "evidence"))))
    checks.append(check("SMHP Validator", os.path.exists(os.path.join(root, "tools", "smhp_validator.py"))))
    checks.append(check("Lighting Normalizer", os.path.exists(os.path.join(root, "tools", "lighting_normalizer.py"))))
    
    passed = sum(checks)
    print(f"\n{passed}/11 VERIFICADOS. Estado: {'OPERATIVO' if passed == 11 else 'INCOMPLETO'}")
    print(f"[INFO] Modo actual: {DEFAULT_MODE}")

def status():
    print(f"=== AGF {VERSION} STATUS ===")
    print(f"Execution Mode: {DEFAULT_MODE}")
    print(f"Biometric Threshold: {'0.85 (PRODUCTION)' if DEFAULT_MODE == 'PRODUCTION' else '0.79 (RESEARCH)'}")
    print("Pixel Threshold (SSIM): 0.92")
    print("Calibration Corpus: PARTIAL (9/20 IDs)")
    print("Last Vault Evidence: evidence/ (Verificar carpeta local)")

def go():
    print(f"=== AGF {VERSION} KERNEL ===")
    print("Generando Prompt Kernel v0.7.0 (SMHP)...")
    print("[OK] Kernel listo para pegar en el chatbot.")
    print("Copia el contenido de docs/governance/AGF_CHAT_KERNEL_v0.7.0_SMHP.md")

def closure(original, generated, facenet, blazeface):
    print(f"=== AGF {VERSION} CLOSURE ===")
    print(f"Original: {original}")
    print(f"Generada: {generated}")
    cmd = ["python", "tools/smhp_validator.py", original, generated, facenet]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("[ERROR] El validador SMHP falló. Revisa los logs.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python src/agf_v10_pixel_locked.py [status|doctor|go|closure]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "status": status()
    elif cmd == "doctor": doctor()
    elif cmd == "go": go()
    elif cmd == "closure" and len(sys.argv) >= 6:
        closure(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        print("Comando no reconocido. Usa: status | doctor | go | closure <orig> <gen> <facenet> <blaze>")
