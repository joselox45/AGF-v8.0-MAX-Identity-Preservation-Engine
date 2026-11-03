# Caso de Estudio: El Bug de Longitud en Reed-Solomon (Chien Search)

**Fecha:** 2026-11-03
**Módulo:** Reed-Solomon / Motor HIL
**Estado:** ✅ RESUELTO (Fail-Closed detectó el fallo)

## 1. El Error
Al ejecutar el pipeline de Cuádruple Capa con la librería `reedsolo`, el motor arrojó:
> `Too many (or few) errors found by Chien Search for the errata locator polynomial!`

## 2. La Causa Raíz (No era un bug de reedsolo)
El script del Chatbot intentaba decodificar el flujo de datos sin saber su longitud exacta. Leía los bits del mensaje + millones de bits de los píxeles vacíos de la imagen. `reedsolo` intentaba corregir el ruido de los píxeles, superaba su capacidad de corrección (t=16) y colapsaba.

## 3. La Solución (Header AKAD)
Se implementó una cabecera de 40 bytes antes de los datos:
- `AKAD` (4 bytes mágicos).
- Longitud del mensaje (4 bytes).
- SHA-256 (32 bytes).

Ahora, el extractor lee la cabecera, sabe exactamente cuántos bytes pedirle a `reedsolo`, y la decodificación es exitosa (PASS).

## 4. Lección de Gobernanza
Reed-Solomon es una herramienta matemática perfecta, pero requiere saber **dónde empieza y dónde termina** el mensaje. Sin un contrato de longitud (AKAD), el motor no puede distinguir entre datos y ruido. El Fail-Closed del Kernel fue lo que detectó este fallo antes de dar un falso PASS.
