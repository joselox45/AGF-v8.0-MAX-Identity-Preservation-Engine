# Politica de Derivacion - AGF v12.2
**Estado:** Congelada y Firmada
**Autor:** joselox45
**Licencia:** MIT

## Permitido
- Fork bajo MIT.
- Ramas experimentales y PRs.

## Prohibido
- Falsos AGF Oficiales sin SHA-256.
- Modificar el Kernel sin firma.

## Verificar
sha256sum -c AGF_v12.2_FIRMA_SHA256.txt

## Advertencia de GPG
El autor original no ha firmado los commits con GPG. Esto significa que un atacante podria reescribir la historia de Git. Se recomienda usar el hash SHA-256 de los archivos como verificacion alternativa.

## Verificacion de Autenticidad
Para verificar que estas ante el AGF Oficial:
sha256sum -c AGF_v12.2_FIRMA_SHA256.txt
git verify-tag v12.4.2-REPO-SYNC
