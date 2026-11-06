# cuadruple_v1.3.py v1.3 ampliado: IPM + Verificación Hash Kernel + Export CSV
import hashlib
import csv
from pathlib import Path

# Rutas relativas al repositorio
RUTA_KERNEL = Path("docs/governance/AGF_CHAT_KERNEL_v0.9.8_FULL.md")
RUTA_HASH = Path("docs/governance/.kernel_hash.sha256")
RUTA_CSV = Path("registro_pruebas_ipm.csv")

class GestorIPM:
    def __init__(self):
        self.capas_activas = []
        self.modo_actual = "MINIMO"
        self.ipm = 0
        self.nivel_profundidad = "SUPERFICIE"

    def calcular_ipm(self, p_ruido: float, p_rafaga: float, p_perdida_fragmento: float):
        self.ipm = int((p_ruido * 150) + (p_rafaga * 300) + (p_perdida_fragmento * 400))
        if self.ipm < 200:
            self.nivel_profundidad = "SUPERFICIE"
        elif 200 <= self.ipm < 4000:
            self.nivel_profundidad = "BATIAL"
        elif 4000 <= self.ipm < 6000:
            self.nivel_profundidad = "ABISAL"
        else:
            self.nivel_profundidad = "CHALLENGER_DEEP"
        return self.ipm, self.nivel_profundidad

    def evaluar_capas(self, p_ruido: float, p_rafaga: float, p_perdida_fragmento: float, cpu_libre: float):
        self.capas_activas = ["polar"]
        if p_rafaga > 2:
            self.capas_activas.append("rs")
        if p_ruido > 2:
            if p_ruido >= 12 and cpu_libre >= 30:
                self.capas_activas.append("turbo")
            else:
                self.capas_activas.append("ldpc")
        if p_perdida_fragmento > 3:
            self.capas_activas.append("raptor")
        capas_ordenadas = tuple(sorted(self.capas_activas))
        mapa_modos = {
            ("polar",): "MINIMO",
            ("polar", "rs"): "ESTANDAR",
            ("ldpc", "polar", "rs"): "ROBUSTO",
            ("polar", "rs", "turbo"): "TURBO",
            ("ldpc", "polar", "raptor", "rs"): "MAXIMO",
            ("polar", "raptor", "rs", "turbo"): "MAXIMO"
        }
        self.modo_actual = mapa_modos.get(capas_ordenadas, "PERSONALIZADO")
        return sorted(self.capas_activas), self.modo_actual

    def verificar_hash_kernel(self):
        if not RUTA_KERNEL.exists() or not RUTA_HASH.exists():
            return False, "❌ Archivo Kernel o archivo hash no encontrado"
        hash_calculado = hashlib.sha256(RUTA_KERNEL.read_bytes()).hexdigest()
        hash_guardado = RUTA_HASH.read_text().strip()
        coinciden = hash_calculado == hash_guardado
        mensaje = f"Calculado: {hash_calculado}\nGuardado: {hash_guardado}"
        return coinciden, mensaje

    def exportar_csv(self, lista_resultados):
        with open(RUTA_CSV, "w", newline="", encoding="utf‑8") as f:
            escritor = csv.writer(f)
            escritor.writerow(["Nombre_Prueba", "Ruido_%", "Rafaga_%", "Perdida_%", "CPU_Libre_%", "IPM", "Nivel_Profundidad", "Capas_Ordenadas", "Modo"])
            for fila in lista_resultados:
                escritor.writerow(fila)

if __name__ == "__main__":
    gestor = GestorIPM()
    resultados = []
    pruebas = [
        ("Prueba 1 ‑ Concat export local", 0, 0, 0, 10),
        ("Prueba 2 ‑ JPEG esteganografía", 5, 4, 2, 20),
        ("Prueba 3 ‑ Chat‑kernel red extrema", 15, 12, 12, 40)
    ]
    for nombre, ruido, rafaga, perdida, cpu in pruebas:
        ipm, nivel = gestor.calcular_ipm(ruido, rafaga, perdida)
        capas, modo = gestor.evaluar_capas(ruido, rafaga, perdida, cpu)
        print(f"{nombre}")
        print(f"IPM: {ipm} | Nivel: {nivel} | Capas ordenadas: {capas} | Modo: {modo}\n")
        resultados.append([nombre, ruido, rafaga, perdida, cpu, ipm, nivel, str(capas), modo])
    gestor.exportar_csv(resultados)
    print("✅ Resultados pruebas exportados a registro_pruebas_ipm.csv")
    valido, texto_hash = gestor.verificar_hash_kernel()
    print("\n=== Verificación Hash Kernel ===")
    print(f"Estado: {'✅ VÁLIDO (I‑01 cumplido)' if valido else '❌ INVÁLIDO (I‑01 roto)'}")
    print(texto_hash)
