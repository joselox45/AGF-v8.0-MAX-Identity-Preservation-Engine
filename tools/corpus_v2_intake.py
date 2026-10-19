#!/usr/bin/env python3
"""AGF corpus_v2 — intake con custodia desde el nacimiento.
Verifica cada imagen recibida (existencia, RGB, tamano >= 512, sin canal
alpha) y emite data/corpus_v2/manifest.json con sha256 por archivo.
Sin esto, el corpus v2 no existe: la leccion de corpus_v1 (7 colores)
se corrige auditando DESDE EL NACIMIENTO.
Uso: python tools/corpus_v2_intake.py --generador "Meta AI" --fecha 2026-10-18
"""
import argparse, hashlib, json, os, sys
from datetime import datetime, timezone

ap = argparse.ArgumentParser()
ap.add_argument("--generador", required=True, help="chatbot usado (ChatGPT/Grok/Meta AI)")
ap.add_argument("--fecha", default=None, help="fecha de generacion YYYY-MM-DD")
ap.add_argument("--min-size", type=int, default=512)
a = ap.parse_args()

REPO = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(REPO, "data", "corpus_v2")
VARIANTS = ["base", "luz", "oclusion", "pose"]

def sha256_file(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def main():
    from PIL import Image
    tpl_path = os.path.join(OUT, "manifest_plantilla.json")
    if not os.path.exists(tpl_path):
        sys.exit("FALTA manifest_plantilla.json -> corre primero tools/corpus_v2_prompts.py")
    man = json.load(open(tpl_path))
    gen_path = os.path.join(OUT, "generadores.json")
    gen_map = json.load(open(gen_path)) if os.path.exists(gen_path) else {}
    files, errores = {}, []
    for fid in man["ids"]:
        for var in VARIANTS:
            rel = f"{fid}/{var}.png"
            p = os.path.join(OUT, rel)
            if not os.path.exists(p):
                errores.append(f"FALTA: {rel}"); continue
            try:
                im = Image.open(p); im.load()
                if im.mode != "RGB":
                    errores.append(f"MODO {im.mode} (exijo RGB): {rel}"); continue
                if min(im.size) < a.min_size:
                    errores.append(f"TAMANO {im.size} < {a.min_size}: {rel}"); continue
            except Exception as e:
                errores.append(f"ILEGIBLE: {rel} ({e})"); continue
            files[rel] = {"sha256": sha256_file(p), "size": list(Image.open(p).size),
                          "prompt": man["ids"][fid].get("variantes", {}).get(var, {}).get("prompt"),
                          "generador": gen_map.get(fid, a.generador)}
    gen_path = os.path.join(OUT, "generadores.json")
    gen_map = json.load(open(gen_path)) if os.path.exists(gen_path) else {}
    man["files"] = files
    man["operador_fecha"] = a.fecha or datetime.now(timezone.utc).date().isoformat()
    man["created_utc"] = datetime.now(timezone.utc).isoformat()
    esperados = len(man["ids"]) * len(VARIANTS)
    if errores or len(files) != esperados:
        print(json.dumps({"status": "INCOMPLETO", "recibidos": len(files),
                          "esperados": esperados, "errores": errores}, ensure_ascii=False, indent=2))
        sys.exit(3)
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=2)
    print(json.dumps({"status": "PASS", "corpus": "agf-corpus-v2",
                      "imagenes": len(files), "generador": a.generador,
                      "manifest": "data/corpus_v2/manifest.json"}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
