from pathlib import Path
import csv

import numpy as np
from PIL import Image, ImageDraw

import face_detector as fdmod
from blazeface_decoder import decode

ROOT = Path(".")
MODEL = ROOT / "blaze_face_short_range.tflite"
CORPUS = ROOT / "data/corpus_v1"
OUT = ROOT / "evidence/face_debug"
INPUT_SIZE = 128


def main():
    if OUT.exists() and any(OUT.iterdir()):
        raise RuntimeError(f"El directorio no está vacío; no se sobrescribe: {OUT}")
    OUT.mkdir(parents=True, exist_ok=True)

    images = sorted(CORPUS.glob("id_*/base.png"))
    if not images:
        raise RuntimeError(f"No se encontraron imágenes en {CORPUS}")

    detector = fdmod.TFLiteFaceDetector(
        model_bytes=MODEL.read_bytes(), select="score"
    )
    if detector._interp is None:
        raise RuntimeError("No se pudo inicializar TFLite")

    rows = []

    for path in images:
        original = Image.open(path).convert("RGB")
        arr = np.asarray(original, dtype=np.uint8)
        h, w = arr.shape[:2]

        scale = INPUT_SIZE / float(max(w, h))
        nw = max(1, int(round(w * scale)))
        nh = max(1, int(round(h * scale)))

        resized = np.asarray(
            Image.fromarray(arr).resize((nw, nh), Image.BILINEAR),
            dtype=np.float32,
        )

        px = (INPUT_SIZE - nw) // 2
        py = (INPUT_SIZE - nh) // 2
        canvas = np.zeros((INPUT_SIZE, INPUT_SIZE, 3), dtype=np.float32)
        canvas[py:py + nh, px:px + nw] = resized
        inp = canvas / 127.5 - 1.0

        interpreter = detector._interp
        interpreter.set_tensor(detector._in_idx, inp[None, ...])
        interpreter.invoke()

        reg = interpreter.get_tensor(detector._reg_idx)[0]
        cls = interpreter.get_tensor(detector._cls_idx)[0]

        # Umbral 0 para inspeccionar el candidato con mayor score,
        # no para establecer un umbral recomendado de producción.
        detections = decode(
            reg, cls, detector.anchors, INPUT_SIZE, score_thresh=0.0
        )
        detections.sort(key=lambda d: d.score, reverse=True)

        if not detections:
            rows.append([path.parent.name, "", "", "", "", "", "sin candidato"])
            print(f"{path.parent.name}: sin candidato")
            continue

        d = detections[0]
        y1, x1, y2, x2 = d.box

        # Proyectar del canvas normalizado a píxeles de la imagen original.
        x1 = (x1 * INPUT_SIZE - px) / scale
        x2 = (x2 * INPUT_SIZE - px) / scale
        y1 = (y1 * INPUT_SIZE - py) / scale
        y2 = (y2 * INPUT_SIZE - py) / scale

        # Recortar al marco de la imagen para dibujar.
        x1c = max(0, min(w - 1, int(round(x1))))
        x2c = max(0, min(w - 1, int(round(x2))))
        y1c = max(0, min(h - 1, int(round(y1))))
        y2c = max(0, min(h - 1, int(round(y2))))

        annotated = original.copy()
        draw = ImageDraw.Draw(annotated)
        draw.rectangle((x1c, y1c, x2c, y2c), outline="red", width=3)
        label = f"score={d.score:.3f}"
        draw.rectangle((x1c, max(0, y1c - 18), x1c + 105, y1c), fill="red")
        draw.text((x1c + 3, max(0, y1c - 17)), label, fill="white")

        dest = OUT / f"{path.parent.name}_debug.png"
        annotated.save(dest)

        rows.append([
            path.parent.name,
            f"{d.score:.6f}",
            f"{x1:.2f}", f"{y1:.2f}", f"{x2:.2f}", f"{y2:.2f}",
            str(dest),
        ])
        print(
            f"{path.parent.name}: score={d.score:.4f}, "
            f"caja=({x1c},{y1c})-({x2c},{y2c}), archivo={dest}"
        )

    csv_path = OUT / "detections.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "image_id", "score", "x1", "y1", "x2", "y2", "result"
        ])
        writer.writerows(rows)

    print(f"\nImágenes procesadas: {len(images)}")
    print(f"CSV: {csv_path}")
    print(f"Resultados: {OUT.resolve()}")


if __name__ == "__main__":
    main()
