#!/usr/bin/env python3
import argparse
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import os

def process_image(input_path, output_path, filter_type):
    if not os.path.exists(input_path):
        print(f"[ERROR] Imagen no encontrada: {input_path}")
        return

    img = Image.open(input_path).convert("RGB")
    print(f"Procesando: {input_path} | Filtro: {filter_type}")

    if filter_type == "median":
        img = img.filter(ImageFilter.MedianFilter(size=3))
    elif filter_type == "gaussian":
        img = img.filter(ImageFilter.GaussianBlur(radius=1.0))
    elif filter_type == "unsharp":
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
    elif filter_type == "contrast":
        img = ImageOps.autocontrast(img, cutoff=1)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
    elif filter_type == "color":
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.1)

    img.save(output_path, quality=95)
    print(f"[OK] Imagen guardada en: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--filter", default="median", choices=["median", "gaussian", "unsharp", "contrast", "color"])
    args = parser.parse_args()
    process_image(args.input, args.output, args.filter)
