#!/usr/bin/env python3
"""
AGF v8.0-MAX - MAIN ORQUESTADOR (CLI)
=====================================
Punto de entrada unificado para operar el motor forense.
"""
import sys
import os
import subprocess

def check_kernel():
    print("[*] Verificando integridad del Kernel...")
    result = subprocess.run(["python3", "tools/check_kernel.py"])
    if result.returncode != 0:
        print("❌ Kernel alterado. Abortando por Fail-Closed.")
        sys.exit(1)

def run_audit(orig, gen):
    check_kernel()
    print(f"[*] Iniciando auditoría forense de 9 capas...")
    print(f"    Original: {orig}")
    print(f"    Generada: {gen}")
    result = subprocess.run(["python3", "tools/agf_full_9_layers.py", orig, gen, "preservation"])
    sys.exit(result.returncode)

def start_api():
    check_kernel()
    print("[*] Iniciando API Server (Flask)...")
    subprocess.run(["python3", "api_server.py"])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 main.py <comando>")
        print("Comandos:")
        print("  check              - Verificar integridad del Kernel")
        print("  audit <orig> <gen> - Ejecutar motor de 9 capas")
        print("  api                - Levantar API Flask (MAXCAP + Ledger)")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "check":
        check_kernel()
    elif cmd == "audit" and len(sys.argv) == 4:
        run_audit(sys.argv[2], sys.argv[3])
    elif cmd == "api":
        start_api()
    else:
        print("Comando no reconocido o argumentos insuficientes.")
        sys.exit(1)
