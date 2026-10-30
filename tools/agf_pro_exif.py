#!/usr/bin/env python3
"""
AGF v12.2 - Pro EXIF Forensic (Metadata de Camara)
Extrae parametros avanzados de camara para detectar fotos reales vs IA.
"""
import sys
import os
from PIL import Image
from PIL.ExifTags import TAGS

def analyze_exif(image_path):
    if not os.path.exists(image_path):
        return None

    img = Image.open(image_path)
    exif = img.getexif()
    
    if not exif:
        return {"has_exif": False, "reason": "No hay datos EXIF (posible IA)"}
    
    # Extraer todos los tags EXIF
    exif_data = {}
    for tag_id, value in exif.items():
        tag_name = TAGS.get(tag_id, tag_id)
        exif_data[tag_name] = value
    
    # Detectar parametros clave de camara profesional
    pro_params = {
        "Camera_Make": exif_data.get("Make", "N/A"),
        "Camera_Model": exif_data.get("Model", "N/A"),
        "WhiteBalance_Kelvin": exif_data.get("ColorTemperature", "N/A"),
        "Tint_GM": exif_data.get("WhiteBalance", "N/A"),
        "SNR": exif_data.get("PhotographicSensitivity", "N/A"),  # ISO
        "Black_Level": exif_data.get("BlackLevel", "N/A"),
        "Exposure_Time": exif_data.get("ExposureTime", "N/A"),
        "F_Number": exif_data.get("FNumber", "N/A"),
        "Focal_Length": exif_data.get("FocalLength", "N/A"),
        "Software": exif_data.get("Software", "N/A"),
    }

    # Detección de etiquetas de hardware avanzado (Focal Length, Distorsión, etc.)
    advanced_params = {
        "FocalLength_35mm": exif_data.get("FocalLengthIn35mmFilm", "N/A"),
        "Lens_Model": exif_data.get("LensModel", "N/A"),
        "Light_Source": exif_data.get("LightSource", "N/A"),
        "WhiteBalance_Tint": exif_data.get("WhiteBalance", "N/A"),
        "Exposure_Bias": exif_data.get("ExposureBiasValue", "N/A"),
        "Shutter_Speed": exif_data.get("ShutterSpeedValue", "N/A"),
        "Metering_Mode": exif_data.get("MeteringMode", "N/A"),
        "Flash": exif_data.get("Flash", "N/A"),
    }
    pro_params.update(advanced_params)

    
    return {
        "has_exif": True,
        "is_camera": pro_params["Camera_Make"] != "N/A",
        "params": pro_params
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python tools/agf_pro_exif.py <imagen>")
        sys.exit(1)

    result = analyze_exif(sys.argv[1])
    
    print(f"=== AGF PRO EXIF: {sys.argv[1]} ===")
    
    if not result["has_exif"]:
        print(f"\n⚠️ {result['reason']}")
        print("🚨 ALERTA: Sin EXIF profesional. Posible generacion por IA.")
        sys.exit(0)
    
    print(f"\n📷 Camara: {result['params']['Camera_Make']} {result['params']['Camera_Model']}")
    print(f"Software: {result['params']['Software']}")
    print(f"\n--- Parametros Profesionales ---")
    print(f"Kelvin (Temp): {result['params']['WhiteBalance_Kelvin']}")
    print(f"Tint (G/M): {result['params']['Tint_GM']}")
    print(f"ISO (SNR): {result['params']['SNR']}")
    print(f"Black Level: {result['params']['Black_Level']}")
    print(f"Exposure: {result['params']['Exposure_Time']}s")
    print(f"Aperture: f/{result['params']['F_Number']}")
    print(f"Focal Length: {result['params']['Focal_Length']}mm")
    
    if result["is_camera"]:
        print("\n✅ PASS: Metadatos de camara profesional detectados.")
    else:
        print("\n⚠️ HUMAN_REVIEW: EXIF incompleto. Posible IA o export web.")
