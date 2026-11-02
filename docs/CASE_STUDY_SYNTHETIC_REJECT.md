# Caso de Estudio: Rechazo de Imagen Sintética en Capa 0 (Detección de Rostro)

**Fecha:** 2026-11-02
**Módulo:** Motor Forense (HIL) - Layer 0 (Tiling + BlazeFace)
**Estado:** ✅ PASS (El sistema funcionó como se diseñó: Fail-Closed)

## 1. El Escenario (Curiosidad / Stress Test)
Con el objetivo de probar los límites del motor, se generó una imagen "desde cero" usando Python (PIL). Se dibujó una cara geométrica (círculos para ojos, un arco para la boca) y se guardó como `original_abuela_falsa.jpg`.

Luego, se intentó comparar esta imagen sintética contra la foto real de la abuela (`docs/assets/abuela_original.jpg`) usando el comando `./agf.sh preservation`.

## 2. El Resultado
**Veredicto:** `❌ BLOCKED: No se detectó rostro en una o ambas imágenes.`

## 3. Diagnóstico Técnico
El motor forense no colapsó, ni inventó métricas. El **Layer 0** (el detector de rostros BlazeFace/TFLite) analizó la imagen generada y determinó que no contenía un rostro humano válido. 

Al no haber dos caras para comparar, el sistema abortó inmediatamente (Fail-Closed) antes de llegar a calcular ArcFace o Fourier.

## 4. La Lección (MIL vs HIL)
*   Un LLM (MIL) podría haber alucinado: *"Aquí está mi dibujo de la abuela, se parece mucho, le doy un PASS"*.
*   El motor HIL (Python) fue honesto: *"Esto es un dibujo, no hay rostro humano. No puedo auditar esto"*.

**El sistema prioriza la detección biológica real sobre la conveniencia de dar una respuesta.**
