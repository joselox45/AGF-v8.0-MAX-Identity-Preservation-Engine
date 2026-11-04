#!/usr/bin/env python3
import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("LLM_API_KEY")
MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

def auditar_codigo(ruta_archivo):
    if not os.path.exists(ruta_archivo):
        print("🔴 ERROR: Archivo no encontrado.")
        return False
    
    with open(ruta_archivo, "r") as f:
        codigo = f.read()
        
    print("🛡️ [AGF Nivel 5] Enviando código a MIL-B para auditoría automática...")
    
    prompt_sistema = ("Eres el MIL-B del Kernel AGF. Actúas como un auditor adversarial Fail-Closed. "
                      "Analiza el siguiente código. Si tiene vulnerabilidades, fallos de seguridad o "
                      "lógica Fail-Open, responde ESTRICTAMENTE con la palabra RECHAZADO. "
                      "Si es completamente seguro, responde ACEPTADO.")
                      
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": f"Audita este código:\n\n{codigo}"}
        ],
        "temperature": 0.0
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        resultado = response.json()["choices"][0]["message"]["content"].strip().upper()
        
        print(f"📡 Veredicto de MIL-B: {resultado}")
        
        if "RECHAZADO" in resultado:
            print("❌ CÓDIGO BLOQUEADO: MIL-B detectó un riesgo de seguridad.")
            return False
        elif "ACEPTADO" in resultado:
            print("✅ CÓDIGO APROBADO: MIL-B no encontró vulnerabilidades.")
            return True
        else:
            print(f"🟡 RESPUESTA AMBIGUA: {resultado}. Bloqueando por seguridad (Fail-Closed).")
            return False
            
    except Exception as e:
        print(f"🔴 ERROR DE CONEXIÓN: {e}")
        print("❌ Bloqueando ejecución (Fail-Closed por falta de auditoría).")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python auto_auditor.py <ruta_al_archivo.py>")
        sys.exit(1)
    
    es_seguro = auditar_codigo(sys.argv[1])
    if not es_seguro:
        sys.exit(1)
    sys.exit(0)
