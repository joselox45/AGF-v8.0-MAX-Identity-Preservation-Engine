# cuadruple_v1.3.py – Gestor Capas Universal v1.3 Foso Marianas
class GestorCapasUniversal:
    def __init__(self):
        self.capas_activas = []
        self.modo_actual = "MINIMO"
        self.ipm = 0
        self.nivel_profundidad = "SUPERFICIE"

    def calcular_ipm(self, p_ruido: float, p_rafaga: float, p_perdida_fragmento: float):
        # Entrada: valores porcentuales (ej: 5 = 5 %)
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

    def evaluar_canal_universal(self, p_ruido: float, p_rafaga: float, p_perdida_fragmento: float, cpu_libre: int):
        self.calcular_ipm(p_ruido, p_rafaga, p_perdida_fragmento)
        capas = ["polar"]
        if p_rafaga > 2:
            capas.append("rs")
        if p_ruido > 2:
            if p_ruido >= 12 and cpu_libre >= 30:
                capas.append("turbo")
            else:
                capas.append("ldpc")
        if p_perdida_fragmento > 3:
            capas.append("raptor")
        self.capas_activas = capas
        self._actualizar_modo()
        return self.capas_activas, self.ipm, self.nivel_profundidad

    def _actualizar_modo(self):
        mapa = {
            ("polar",): "MINIMO",
            ("polar", "rs"): "ESTANDAR",
            ("polar", "rs", "ldpc"): "ROBUSTO",
            ("polar", "rs", "turbo"): "TURBO",
            ("polar", "rs", "ldpc", "raptor"): "MAXIMO",
            ("polar", "rs", "turbo", "raptor"): "MAXIMO"
        }
        self.modo_actual = mapa.get(tuple(sorted(self.capas_activas)), "PERSONALIZADO")


if __name__ == "__main__":
    gestor = GestorCapasUniversal()
    pruebas = [
        ("Prueba 1 ‑ Concat export local", 0, 0, 0, 10),
        ("Prueba 2 ‑ JPEG esteganografía", 5, 4, 2, 20),
        ("Prueba 3 ‑ Chat‑kernel red extrema", 15, 12, 12, 40)
    ]
    for nombre, pr, prf, pf, cpu in pruebas:
        capas, ipm, nivel = gestor.evaluar_canal_universal(pr, prf, pf, cpu)
        print(f"{nombre}")
        print(f"IPM: {ipm} | Nivel: {nivel} | Capas activas: {sorted(capas)} | Modo: {gestor.modo_actual}\n")
