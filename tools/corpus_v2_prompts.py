#!/usr/bin/env python3
"""AGF corpus_v2 — generador de fichas-semilla y prompts de generacion.
Determinista: las 20 fichas estan fijadas en este archivo (no aleatorias),
cada una con rasgos estables + marca distintiva + color de ojos explicito
(requisito de la futura capa L4 de anillo limbal).
Salida: data/corpus_v2/prompts.md (listo para copiar al chatbot, uno por imagen)
"""
import os, json

REPO = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(REPO, "data", "corpus_v2")

# 20 fichas-semilla: (edad, genero, etnia, ojos, cabello, marca_distintiva)
CARDS = [
    (34, "mujer", "latina",      "marron oscuro",  "negro ondulado largo",   "lunar debajo del ojo izquierdo"),
    (52, "hombre", "caucasico",  "azul grisaceo",  "gris corto con entradas", "cicatriz pequena en el menton"),
    (27, "mujer", "asiatica",    "marron claro",   "negro liso con flequillo", "pecas en el puente de la nariz"),
    (61, "hombre", "afro",       "marron muy oscuro", "canoso corto rizado",   "barba entrecana bien cuidada"),
    (41, "mujer", "caucasica",   "verde",          "rubio cobrizo media melena", "gafas de montura fina (solo variante oclusion)"),
    (45, "hombre", "latino",     "marron",         "castano corto peinado lateral", "lunar prominente en la mejilla derecha"),
    (29, "mujer", "afro",        "marron dorado",  "trenzas medianas",        "pendiente dorado pequeno en la oreja izquierda"),
    (55, "mujer", "caucasica",   "azul",           "plata corto pixie",       "arruga de expresion marcada entre cejas"),
    (38, "hombre", "asiatico",   "marron oscuro",  "negro corto con raya",    "pequena cicatriz en la ceja derecha"),
    (33, "mujer", "latina",      "avellana",       "castano largo con mechas", "hoyuelo en la mejilla izquierda"),
    (47, "hombre", "caucasico",  "verde grisaceo", "pelirrojo corto con barba", "pecas densas en mejillas y nariz"),
    (25, "hombre", "latino",     "marron claro",   "negro rizado medio",      "tattoo pequeno visible en el cuello"),
    (58, "mujer", "asiatica",    "marron oscuro",  "negro corto con volumen", "gafas (solo variante oclusion)"),
    (43, "hombre", "afro",       "marron",         "calvo con barba negra",   "lunar en la sien izquierda"),
    (31, "mujer", "caucasica",   "gris azulado",   "rubio platino largo",     "pequena perforacion en la nariz (nostril)"),
    (49, "hombre", "asiatico",   "marron",         "entrecano corto",         "arrugas marcadas en patas de gallo"),
    (36, "mujer", "afro",        "marron",         "castano rizado afro",     "lunar sobre el labio superior"),
    (63, "hombre", "caucasico",  "azul",           "blanco corto",            "gafas de lectura (solo variante oclusion)"),
    (26, "mujer", "latina",      "marron miel",    "negro largo lacio",       "cejas densas y definidas"),
    (44, "hombre", "latino",     "marron oscuro",  "castano medio con canas", "cicatriz quirurgica discreta en el cuello"),
]

VARIANTS = {
    "base":     "retrato fotorealista de busto, fondo neutro gris plano, luz frontal suave y uniforme, mirada a camara, expresion neutral, iris y textura del ojo claramente visibles",
    "luz":      "retrato fotorealista de busto, fondo neutro gris plano, luz calida lateral desde la izquierda (sombra suave), misma expresion neutral, iris y textura del ojo claramente visibles",
    "oclusion": "retrato fotorealista de busto, fondo neutro gris plano, luz frontal suave, la persona lleva gafas de sol oscuras (ojos parcialmente ocultos), misma expresion neutral",
    "pose":     "retrato fotorealista de busto, fondo neutro gris plano, luz frontal suave, cabeza girada 30 grados hacia la derecha, expresion neutral, iris del ojo visible claramente",
}

HEADER = """# corpus_v2 — prompts de generacion (AGF)
Reglas de oro para cada imagen:
1. PEGA UN PROMPT POR MENSAJE. Espera la imagen, guardala con el nombre indicado.
2. Todas las imagenes de un mismo ID son LA MISMA PERSONA. Si el chatbot
   cambia rasgos entre generaciones, descarta y repite el prompt.
3. Guarda como: data/corpus_v2/{ID}/{variante}.png
4. Nada de filtros, texto ni marcas de agua en la imagen final.
"""

def card_text(i, c):
    edad, genero, etnia, ojos, cabello, marca = c
    return (f"{edad} anos, {genero} {etnia}, ojos {ojos}, "
            f"cabello {cabello}, marca distintiva: {marca}")

def main():
    os.makedirs(OUT, exist_ok=True)
    lines, manifest_cards = [HEADER], {}
    for i, c in enumerate(CARDS, 1):
        fid = f"Fv2-{i:02d}"
        lines.append(f"\n---\n## {fid} — {card_text(i, c)}\n")
        manifest_cards[fid] = {"seed_card": card_text(i, c), "variantes": {}}
        for var, desc in VARIANTS.items():
            prompt = (f"Genera una foto fotorealista de {card_text(i, c)}: "
                      f"{desc}. Alta resolucion, sin texto ni marcas de agua.")
            lines.append(f"**{fid}/{var}.png**\n```\n{prompt}\n```\n")
            manifest_cards[fid]["variantes"][var] = {"prompt": prompt}
    with open(os.path.join(OUT, "prompts.md"), "w", encoding="utf-8") as f:
        f.write("".join(lines))
    # plantilla de manifest (sha256 se llenan en intake)
    man = {"corpus": "agf-corpus-v2", "tipo": "fotorealista-generado-via-CANAL",
           "generador": "COMPLETAR (chatbot usado)", "operador_fecha": "COMPLETAR",
           "n_ids": len(CARDS), "claims_habilitados": "calibracion de umbral + base de ataque L4",
           "limitacion": "rostros generados por LLM; etiquetado de sujeto es ground truth por construccion",
           "ids": manifest_cards}
    with open(os.path.join(OUT, "manifest_plantilla.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=2)
    print(f"OK -> {OUT}/prompts.md ({len(CARDS)} ids x {len(VARIANTS)} = {len(CARDS)*len(VARIANTS)} prompts)")
    print(f"OK -> {OUT}/manifest_plantilla.json")

if __name__ == "__main__":
    main()
