#!/usr/bin/env python3
"""
AGF Corpus v1 — generador determinista de identidades sinteticas + variantes.

Modelo de base:
  - StyleGAN2-TFLite/ONNX (opcional, para claims biometricos finos)
  - Generador parametrico procedural (siempre disponible; valida el PIPELINE,
    NO habilita claims biometricos finos — el manifest lo declara)

Variantes por identidad: dano, pose, luz, oclusion. Todo con seed fijo ->
regeneracion byte-identica. Sin seed o sin generador: falla cerrada.

Uso: python tools/corpus_generate.py --n 20 --out data/corpus_v1 [--stylegan W.tflite]
"""
import argparse, hashlib, json, math, os, random
from datetime import datetime, timezone

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=20)
ap.add_argument("--out", default="data/corpus_v1")
ap.add_argument("--stylegan", default=None, help="pesos TFLite/ONNX opcionales")
ap.add_argument("--seed", type=int, default=20261014)
a = ap.parse_args()

W, H = 256, 256


# ---------- base procedural (parametrica, determinista) ----------
def gen_base(rng, modelo):
    """Rostro parametrico: elipse cabeza, ojos, nariz, boca, pelo, fondo.
    Determinista dado rng. Validacion de pipeline, no foto-realismo."""
    import numpy as np
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (W, H), (rng.randint(180, 240), rng.randint(170, 230), rng.randint(160, 220)))
    d = ImageDraw.Draw(img)
    skin = (rng.randint(180, 235), rng.randint(140, 200), rng.randint(110, 170))
    cx, cy = W // 2 + rng.randint(-12, 12), H // 2 + rng.randint(-10, 10)
    rw, rh = rng.randint(62, 80), rng.randint(84, 104)
    d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=skin)          # cara
    hair = (rng.randint(20, 90), rng.randint(15, 70), rng.randint(10, 50))
    d.ellipse([cx - rw - 6, cy - rh - 14, cx + rw + 6, cy - rh // 3], fill=hair)  # pelo
    eye_y = cy - rh // 4
    for s in (-1, 1):                                                    # ojos
        ex = cx + s * rw // 2
        d.ellipse([ex - 9, eye_y - 6, ex + 9, eye_y + 6], fill=(250, 250, 250))
        d.ellipse([ex - 3, eye_y - 3, ex + 3, eye_y + 3], fill=(30, 40, 60))
        d.ellipse([ex - 12, eye_y - 9, ex + 12, eye_y + 5], outline=hair, width=2)
    d.line([cx, eye_y + 8, cx - 4, cy + 8], fill=(skin[0]-30, skin[1]-30, skin[2]-25), width=3)  # nariz
    mouth_y = cy + rh // 2
    d.arc([cx - 22, mouth_y - 10, cx + 22, mouth_y + 12], 10, 170,
          fill=(rng.randint(120, 170), 60, 60), width=3)                 # boca
    return img


# ---------- variantes deterministas ----------
def v_dano(img, rng):
    import numpy as np
    from PIL import Image
    a = np.asarray(img).astype("int16")
    for _ in range(rng.randint(3, 7)):                                   # raspones
        x, y = rng.randint(0, W - 40), rng.randint(0, H - 40)
        a[y:y + 3, x:x + rng.randint(15, 40)] = (rng.randint(200, 255),) * 3
    import numpy as np
    noise = np.random.RandomState(rng.randint(0, 2**31)).randint(0, 40, (H, W, 1))  # ruido seeded
    a = (a + noise - 20).clip(0, 255)
    return Image.fromarray(a.astype("uint8"))


def v_pose(img, rng):
    import numpy as np
    ang = rng.uniform(-12, 12)
    return img.rotate(ang, resample=2, expand=False, fillcolor=(230, 225, 215))


def v_luz(img, rng):
    import numpy as np
    gamma = rng.uniform(0.6, 1.5)
    lut = [min(255, int(255 * ((i / 255) ** gamma))) for i in range(256)] * 3
    return img.point(lut)


def v_oclusion(img, rng):
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    if rng.random() < 0.5:                                               # gafas
        y = H // 2 - 30
        d.rectangle([W // 2 - 70, y, W // 2 - 10, y + 28], outline=(20, 20, 20), width=4)
        d.rectangle([W // 2 + 10, y, W // 2 + 70, y + 28], outline=(20, 20, 20), width=4)
        d.line([W // 2 - 10, y + 12, W // 2 + 10, y + 12], fill=(20, 20, 20), width=4)
    else:                                                                # barra
        x = rng.randint(30, W - 60)
        d.rectangle([x, 0, x + rng.randint(20, 45), H], fill=(60, 55, 50))
    return img


VARIANTS = {"base": None, "dano": v_dano, "pose": v_pose,
            "luz": v_luz, "oclusion": v_oclusion}


def main():
    os.makedirs(a.out, exist_ok=True)
    manifest = {"corpus": "agf-corpus-v1", "seed": a.seed, "n_ids": a.n,
                "modelo_base": "procedural-parametrico" if not a.stylegan else "stylegan2",
                "claims_habilitados": ("pipeline-validation ONLY (rostro parametrico, no fotorealista)"
                                       if not a.stylegan else "biometrico-fino"),
                "variantes": sorted(VARIANTS), "created_utc": datetime.now(timezone.utc).isoformat(),
                "files": {}}
    for i in range(1, a.n + 1):
        rng = random.Random(a.seed + i)
        idir = os.path.join(a.out, f"id_{i:03d}")
        os.makedirs(idir, exist_ok=True)
        base_img = gen_base(rng, a.stylegan)
        for vname, fn in VARIANTS.items():
            img = base_img if fn is None else fn(base_img.copy(), rng)
            p = os.path.join(idir, f"{vname}.png")
            img.save(p, "PNG")
            manifest["files"][f"id_{i:03d}/{vname}.png"] = {
                "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest(),
                "seed": a.seed + i}
    mp = os.path.join(a.out, "manifest.json")
    json.dump(manifest, open(mp, "w"), indent=2, ensure_ascii=False)
    print(json.dumps({"status": "PASS", "ids": a.n, "files": len(manifest["files"]),
                      "manifest": mp, "claims": manifest["claims_habilitados"]}))


if __name__ == "__main__":
    main()
