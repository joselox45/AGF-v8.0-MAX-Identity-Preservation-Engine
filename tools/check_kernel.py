#!/usr/bin/env python3
import hashlib
import os
import sys

# Obtiene la ruta absoluta del directorio del script y sube un nivel a la raíz del repo
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KERNEL_PATH = os.path.join(BASE_DIR, "docs", "governance", "AGF_CHAT_KERNEL_v0.9.8_FULL.md")
HASH_PATH = os.path.join(BASE_DIR, "docs", "governance", ".kernel_hash.sha256")

def calcular_hash(archivo):
    sha256 = hashlib.sha256()
    with open(archivo, "rb") as f:
        for bloque in iter(lambda: f.read(4096), b""):
            sha256.update(bloque)
    return sha256.hexdigest()

def verificar_integridad():
    if not os.path.exists(KERNEL_PATH):
        print(f"🔴 ERROR: Kernel no encontrado en {KERNEL_PATH}")
        return False
    
    hash_actual = calcular_hash(KERNEL_PATH)
    
    if not os.path.exists(HASH_PATH):
        with open(HASH_PATH, "w") as f:
            f.write(hash_actual)
        print("✅ Kernel firmado por primera vez. Hash:", hash_actual[:16] + "...")
        return True
        
    with open(HASH_PATH, "r") as f:
        hash_firmado = f.read().strip()
        
    if hash_actual == hash_firmado:
        print("✅ Kernel Íntegro. Gobernanza garantizada.")
        return True
    else:
        print("🔴 ALERTA DE SEGURIDAD: El Kernel ha sido modificado.")
        return False

if __name__ == "__main__":
    if not verificar_integridad():
        sys.exit(1)
