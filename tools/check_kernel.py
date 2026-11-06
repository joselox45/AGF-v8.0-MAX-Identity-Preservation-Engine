#!/usr/bin/env python3
import hashlib
import os
import sys

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

    # FAIL-CLOSED: si NO existe el hash, NO firmamos automáticamente.
    if not os.path.exists(HASH_PATH):
        print(f"🔴 FAIL-CLOSED: Archivo de hash no encontrado en {HASH_PATH}.")
        print("   No se firma automáticamente. Requiere firma manual del operador.")
        print("   Acción: sha256sum AGF_CHAT_KERNEL_v0.9.8_FULL.md > .kernel_hash.sha256")
        return False

    hash_actual = calcular_hash(KERNEL_PATH)

    with open(HASH_PATH, "r") as f:
        hash_firmado = f.read().strip()

    if hash_actual == hash_firmado:
        print("✅ Integridad de archivo verificada (No implica gobernanza operativa).")
        return True
    else:
        print("🔴 ALERTA DE SEGURIDAD: El Kernel ha sido modificado sin actualizar la firma.")
        print(f"   Esperado: {hash_firmado[:16]}...")
        print(f"   Real:     {hash_actual[:16]}...")
        return False


if __name__ == "__main__":
    if not verificar_integridad():
        sys.exit(1)
