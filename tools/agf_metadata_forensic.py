#!/usr/bin/env python3
"""
AGF v12.2 - Metadata Forensic (Triaje Rápido)
Detecta la firma XMP de IA y el tipo de compresión JPEG.
"""
import sys
import os
from PIL import Image

def analyze_metadata(image_path):
    if not os.path.exists(image_path):
        return {"error": "File not found"}

    img = Image.open(image_path)
    info = img.info
    
    # 1. Detectar Certificado XMP de IA
    xmp_data = str(info.get('xmp', '')) + str(info.get('XML:com.adobe.xmp', ''))
    is_ai_generated = "trainedAlgorithmicMedia" in xmp_data or "digitalSourceType" in xmp_data
    
    # 2. Detectar Compresión Progresiva (típico de IA/Web)
    is_progressive = "progressive" in str(info).lower()
    
    # 3. Detectar Firmas de Meta AI (FBMD)
    is_facebook = "FBMD" in str(info.get('Iptc', ''))
    
    return {
        "is_ai_generated": is_ai_generated,
        "is_progressive": is_progressive,
        "is_facebook_export": is_facebook,
        "xmp_found": bool(xmp_data)
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python tools/agf_metadata_forensic.py <imagen>")
        sys.exit(1)
        
    print(f"=== AGF METADATA FORENSIC: {sys.argv[1]} ===")
    result = analyze_metadata(sys.argv[1])
    
    if "error" in result:
        print(f"❌ {result['error']}")
        sys.exit(1)
        
    print(f" XMP de IA detectado: {'🚨 SÍ' if result['is_ai_generated'] else '✅ NO'}")
    print(f" Compresión Progresiva (Web/IA): {'⚠️ SÍ' if result['is_progressive'] else '✅ NO'}")
    print(f" Rastro de Facebook (FBMD): {'⚠️ SÍ' if result['is_facebook_export'] else '✅ NO'}")
    
    if result['is_ai_generated']:
        print("\n🚨 VEREDICTO: BLOCKED (Certificado XMP de IA detectado)")
        print("La imagen fue generada por IA. Zero-Fabrication activado.")
    else:
        print("\n✅ VEREDICTO: LIMPIO (Sin firmas de IA en metadatos)")
