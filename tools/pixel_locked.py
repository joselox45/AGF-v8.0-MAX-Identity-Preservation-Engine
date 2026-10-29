import hashlib
import numpy as np
from PIL import Image, ImageFilter

def _ssim_tile_pillow(ref_tile, gen_tile):
    """
    SSIM real sin OpenCV. Usa Pillow (GaussianBlur) + numpy.
    """
    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2
    
    # Convertir a arrays float
    ref = np.array(ref_tile, dtype=np.float64)
    gen = np.array(gen_tile, dtype=np.float64)
    
    # Usar Pillow para el desenfoque Gaussiano
    ref_img = Image.fromarray(ref.astype(np.uint8))
    gen_img = Image.fromarray(gen.astype(np.uint8))
    
    mu_x = np.array(ref_img.filter(ImageFilter.GaussianBlur(radius=1.5)), dtype=np.float64)
    mu_y = np.array(gen_img.filter(ImageFilter.GaussianBlur(radius=1.5)), dtype=np.float64)
    
    mu_x_sq = mu_x ** 2
    mu_y_sq = mu_y ** 2
    mu_xy = mu_x * mu_y
    
    sigma_x_sq = np.array(Image.fromarray((ref * ref).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=1.5)), dtype=np.float64) - mu_x_sq
    sigma_y_sq = np.array(Image.fromarray((gen * gen).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=1.5)), dtype=np.float64) - mu_y_sq
    sigma_xy = np.array(Image.fromarray((ref * gen).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=1.5)), dtype=np.float64) - mu_xy
    
    numerator = (2 * mu_xy + C1) * (2 * sigma_xy + C2)
    denominator = (mu_x_sq + mu_y_sq + C1) * (sigma_x_sq + sigma_y_sq + C2)
    
    ssim_map = numerator / denominator
    return float(ssim_map.mean())

def _merkle_root(hashes):
    """Calcula Merkle Root de lista ordenada de SHA-256 hex"""
    if not hashes:
        return None
    level = hashes
    while len(level) > 1:
        next_level = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i+1] if i+1 < len(level) else left
            combined = hashlib.sha256((left + right).encode('utf-8')).hexdigest()
            next_level.append(combined)
        level = next_level
    return level[0]

def pixel_locked_ssim_tiles(ref_path: str, gen_path: str, tile_size: int = 32, ssim_threshold: float = 0.92, face_bbox=None):
    """
    AGF v11.0 PIXEL_LOCKED - SSIM por tile 32x32 + SHA-256 + Merkle Root
    (Versión compatible con Pillow, sin OpenCV)
    """
    try:
        ref_img = Image.open(ref_path).convert('L')
        gen_img = Image.open(gen_path).convert('L')
    except Exception as e:
        return {"status": "FAIL-CLOSED", "reason": f"No se pudo leer imagen: {e}", "passed": False, "merkle_root": None}

    if ref_img.size != gen_img.size:
        gen_img = gen_img.resize(ref_img.size, Image.Resampling.LANCZOS)

    w, h = ref_img.size
    tiles_info = []
    failed_tiles = []

    for y in range(0, h, tile_size):
        for x in range(0, w, tile_size):
            if face_bbox:
                fx, fy, fw, fh = face_bbox
                if not (fx <= x < fx+fw and fy <= y < fy+fh):
                    continue

            ref_tile = ref_img.crop((x, y, x+tile_size, y+tile_size))
            gen_tile = gen_img.crop((x, y, x+tile_size, y+tile_size))

            if ref_tile.size[0] < tile_size or ref_tile.size[1] < tile_size:
                continue

            score = _ssim_tile_pillow(ref_tile, gen_tile)
            
            # SHA-256 del tile (usamos numpy para el hash)
            tile_bytes = np.array(gen_tile).tobytes()
            tile_hash = hashlib.sha256(tile_bytes).hexdigest()

            info = {
                "x": x, "y": y,
                "ssim": round(score, 4),
                "sha256": tile_hash,
                "passed": score >= ssim_threshold
            }
            tiles_info.append(info)
            if not info["passed"]:
                failed_tiles.append(info)

    tiles_info_sorted = sorted(tiles_info, key=lambda t: (t["y"], t["x"]))
    hashes_sorted = [t["sha256"] for t in tiles_info_sorted]

    merkle_root = _merkle_root(hashes_sorted)
    mean_ssim = float(np.mean([t["ssim"] for t in tiles_info])) if tiles_info else 0.0
    passed = len(failed_tiles) == 0 and len(tiles_info) > 0

    return {
        "engine": "AGF v11.0 PIXEL_LOCKED (Pillow Compatible)",
        "tile_size": tile_size,
        "threshold": ssim_threshold,
        "total_tiles": len(tiles_info),
        "failed_tiles": len(failed_tiles),
        "mean_ssim": round(mean_ssim, 4),
        "merkle_root": merkle_root,
        "tiles": tiles_info_sorted,
        "failed_details": failed_tiles,
        "passed": passed,
        "status": "PASSED" if passed else "FAIL-CLOSED"
    }
