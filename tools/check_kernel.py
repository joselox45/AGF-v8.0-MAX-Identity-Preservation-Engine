#!/usr/bin/env python3
"""
AGF Kernel Integrity Validator (Nivel 5)
Este script se ejecuta antes de cualquier operación. Calcula el hash del Kernel
y lo compara con el hash firmado en el archivo .sha256.
Si alguien lo modifica, el sistema se detiene (Fail-Closed).
"""
import hashlib
import os
import sys

KERNEL_PATH = "../docs/governance/AGF_CHAT_KERNEL_v0.9.8_FULL.md"
HASH_PATH = "../docs/governance/.kernel_hash.sha256"

def calcular_hash(archivo):
    sha256 = hashlib.sha256()
    with open(archivo, "rb") as f:
        for bloque in iter(lambda: f.read(4096), b""):
            sha256.update(bloque)
    return sha256.hexdigest()

def verificar_integridad():
    if not os.path.exists(KERNEL_PATH):
        print("🔴 ERROR: Kernel no encontrado.")
        return False
    
    hash_actual = calcular_hash(KERNEL_PATH)
    
    if not os.path.exists(HASH_PATH):
        # Primera vez: Guardamos el hash original
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
        print("🔴 ALERTA DE SEGURIDAD: El Kernel ha sido modificado sin autorización.")
        print(f"   Hash esperado: {hash_firmado[:16]}...")
        print(f"   Hash actual:   {hash_actual[:16]}...")
        print("   ACCIÓN: Fail-Closed activado.")
        return False

if __name__ == "__main__":
    if not verificar_integridad():
        sys.exit(1)
