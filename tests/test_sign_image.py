import unittest
import os
import tempfile
import json
from PIL import Image
import sys
sys.path.insert(0, 'tools')
from agf_sign_image import sign_and_embed

class TestSignImage(unittest.TestCase):
    def test_firma_e_incrustacion(self):
        d = tempfile.mkdtemp()
        img_path = os.path.join(d, "dummy.jpg")
        json_path = os.path.join(d, "trace.json")
        out_path = os.path.join(d, "signed.jpg")
        
        # Crear imagen de prueba y JSON
        Image.new('RGB', (100, 100), color='red').save(img_path)
        with open(json_path, 'w') as f:
            json.dump({"verdict": "HUMAN_REVIEW"}, f)
            
        # Ejecutar la firma
        sign_and_embed(img_path, json_path, out_path)
        
        # Verificar que el tag EXIF se incrusto (usando context manager)
        with Image.open(out_path) as img:
            exif = img.getexif()
            agf_meta = exif.get(0x9286)
        
        self.assertIsNotNone(agf_meta)
        self.assertIn("AGF_SHA256:", agf_meta)
        self.assertIn("AGF_SIG:", agf_meta)

if __name__ == "__main__":
    unittest.main()
