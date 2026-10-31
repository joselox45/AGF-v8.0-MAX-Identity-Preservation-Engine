# Firma Criptográfica Vinculante (Pseudo-C2PA)

## 1. El Problema
Hasta ahora, el JSON de trazabilidad viaja como un archivo "sidecar" separado de la imagen. Un atacante podría generar una imagen, robar un JSON válido de otra imagen, y presentarlos juntos. El validador no notaría que no pertenecen al mismo evento.

## 2. La Solución (C2PA Simplificado)
Vincular binariamente la imagen y el JSON mediante criptografía:
1. Se calcula el hash SHA-256 del JSON.
2. Se firma ese hash con una llave privada Ed25519.
3. Se incrusta el hash y la firma en los metadatos EXIF de la imagen generada.

## 3. Implicaciones Forenses
- Si la imagen se modifica (se altera un solo píxel), el hash EXIF ya no coincidirá con el JSON original.
- Si el JSON se altera, el hash no coincidirá con el de la firma.
- **Foso competitivo:** La imagen y su contrato de gobernanza son inseparables.
