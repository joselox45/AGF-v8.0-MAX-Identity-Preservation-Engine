#!/usr/bin/env python3
"""
AGF v9.0-LIMBAL - Motor de Decisión Adaptativo
Arquitectura: Anillo 1 (Identidad) -> Anillo 2 (Calidad) -> Anillo 3 (Decisión Limbal)
"""
from PIL import Image, ImageFilter, ImageStat, ImageEnhance
import numpy as np

class AGFv9LimbalEngine:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path).convert("RGB")
        self.original_image = self.image.copy()
        self.metrics = {}
        self.plan = []

    def observar_y_medir(self):
        """
        Anillo de Calidad: Calcula métricas iniciales (Ruido y Contraste).
        Usa la desviación estándar y varianza de la imagen en escala de grises.
        """
        gray = self.image.convert("L")
        stat = ImageStat.Stat(gray)
        
        # Q-01 Ruido residual (aproximado por varianza)
        self.metrics['ruido'] = stat.var[0]
        # Q-03 Contraste local (aproximado por desviación estándar)
        self.metrics['contraste'] = stat.stddev[0]
        
        print(f"[OBSERVAR] Métricas Base -> Ruido (Var): {self.metrics['ruido']:.2f} | Contraste (StdDev): {self.metrics['contraste']:.2f}")

    def diagnosticar_limbal(self):
        """
        Anillo Limbal: Toma decisiones basadas en la evidencia (métricas).
        No aplica filtros por defecto.
        """
        # PÉRDIDA: Si no filtramos, la imagen se ve mal.
        # INCENTIVO: Si aplicamos de más, perdemos identidad.
        # EVIDENCIA: Los umbrales numéricos.
        
        # MÓDULO M: Median Adaptativo (Eliminar ruido/speckles)
        if self.metrics['ruido'] > 400:  
            self.plan.append("median")
            
        # MÓDULO U1: Unsharp Principal (Recuperar bordes/nitidez)
        if self.metrics['contraste'] < 45: 
            self.plan.append("unsharp")
            
        if not self.plan:
            print("[DIAGNÓSTICO] Imagen estable. No se requieren transformaciones (Regla de Mínima Intervención).")
        else:
            print(f"[DIAGNÓSTICO] Transformaciones justificadas por evidencia: {self.plan}")

    def aplicar_transformacion(self):
        """Aplica únicamente los filtros diagnosticados."""
        for filtro in self.plan:
            if filtro == "median":
                # Módulo M
                self.image = self.image.filter(ImageFilter.MedianFilter(size=3))
                print("  -> Módulo M aplicado: MedianFilter")
            elif filtro == "unsharp":
                # Módulo U1
                self.image = self.image.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=3))
                print("  -> Módulo U1 aplicado: UnsharpMask")

    def validar_y_abortar(self, cosine_facenet):
        """
        Capa 4: Validación de Regresión / Regla de Aborto.
        Se usa el resultado de FaceNet en Termux.
        """
        print(f"[VALIDACIÓN] Recibido Cosine de FaceNet: {cosine_facenet}")
        
        if cosine_facenet < 0.79:
            print("  [!] REGLA DE ABORTO ACTIVADA: Identidad degradada por debajo del umbral 0.79.")
            print("  [!] Revirtiendo imagen al estado original (Fail-Closed).")
            self.image = self.original_image
            return "FAIL"
        
        print("  [✓] Identidad preservada. Transformaciones aceptadas.")
        return "PASS"

    def guardar(self, output_path):
        """Guarda la imagen resultante."""
        self.image.save(output_path, quality=95)
        print(f"[OUTPUT] Imagen final guardada en: {output_path}")

# --- Flujo de Ejecución Principal ---
if __name__ == "__main__":
    # 1. Iniciar el motor con la imagen original
    engine = AGFv9LimbalEngine("base0_bebe_chef.jpg")
    
    # 2. Ejecutar el bucle de decisión
    engine.observar_y_medir()
    engine.diagnosticar_limbal()
    engine.aplicar_transformacion()
    
    # 3. Simulación de validación con FaceNet
    # (En producción, aquí se leería el resultado real de agf.py closure)
    estado_final = engine.validar_y_abortar(cosine_facenet=0.85) # Simulamos un PASS
    
    if estado_final == "PASS":
        engine.guardar("resultado_v9_final.jpg")
    else:
        print("[!] Proceso finalizado con FAIL. No se genera nueva imagen.")
