# Caso de Estudio: Bloqueo por Alucinación de Textura (Fourier 0.000)

**Fecha:** 2026-11-02
**Módulo:** Motor Forense (HIL) + Juez Puro (SIL)
**Estado:** ✅ PASS (El sistema funcionó como se diseñó: Fail-Closed)

## 1. El Escenario
Se sometió a auditoría una restauración de una fotografía familiar (la abuela) generada por un modelo de IA generativa. El objetivo era verificar si la IA preservó la identidad y la textura real, o si simplemente "redibujó" la imagen.

## 2. Los Resultados del Motor Forense (HIL)
Al ejecutar `./agf.sh preservation`, el motor arrojó las siguientes métricas:

*   **[1] Identidad (ArcFace): 0.7714** (Alta similitud, la IA intentó mantener el rostro).
*   **[2] Firma de Frecuencia (Fourier): 0.0000** 🚨 (Fallo crítico).
*   **[3] Estructura (Shazam): 0.0000**
*   **[4] Píxeles (SSIM): 0.9007** (La estructura general se mantuvo).
*   **[5] Huella Cromática: 0.9021**

**Veredicto:** `🚨 BLOCKED (Hard Gate Extremo: Fourier 0.000 < 0.40 (Alucinación total))`

## 3. Diagnóstico Técnico (¿Por qué bloqueó?)
El `Fourier 0.000` significa que la textura y el ruido de la imagen generada son **matemáticamente incompatibles** con la original. La IA no "reparó" los píxeles existentes; **inventó una textura nueva desde cero**. Aunque el rostro (ArcFace) y la estructura (SSIM) parezcan similares a simple vista, la firma de frecuencia delata que la imagen es una fabricación sintética.

## 4. Las Pruebas Unitarias (SIL)
En paralelo, se ejecutaron los tests del repositorio:
*   `Ran 137 tests in 2.804s`
*   `OK` (137 PASS, 0 FAIL).

**Conclusión:** La lógica interna del código (Kernel, Vault, SSIM, NMS, etc.) está perfectamente sana. El bloqueo no fue un error del software, fue una **decisión correcta de gobernanza**.

## 5. Valor Forense del Caso
Este caso demuestra la diferencia entre un LLM comercial y el AGF Engine:
*   Un humano (o un LLM) habría visto la foto y dicho: *"Qué buena restauración"*.
*   El AGF Engine midió los píxeles y dijo: *"La textura es falsa, la identidad está en riesgo. BLOCKED"*.

**El sistema prioriza la verdad matemática sobre la apariencia estética.**
