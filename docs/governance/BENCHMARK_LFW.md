# Benchmark LFW (Labeled Faces in the Wild)

## 1. Propósito
Sustituir los umbrales heurísticos del  (0.7825 / 0.6325) por umbrales calibrados empíricamente mediante curvas ROC y FAR/FRR.

## 2. Metodología
1. Descargar LFW Deep Funneled (aprox. 200MB).
2. Generar pares (misma persona / distinta persona).
3. Extraer embeddings con ArcFace ONNX.
4. Calcular distancias coseno.
5. Evaluar el umbral que minimiza el EER (Equal Error Rate) donde FAR == FRR.

## 3. Métricas a Reportar
- **FAR (False Acceptance Rate):** Porcentaje de impostores aceptados (crítico).
- **FRR (False Rejection Rate):** Porcentaje de usuarios legítimos rechazados.
- **AUC-ROC:** Área bajo la curva (calidad global del modelo).
- **EER (Equal Error Rate):** El punto de equilibrio (umbral óptimo).

## 4. Integración
El resultado de este benchmark se usará para actualizar la constante  en el código de Python, garantizando que la gobernanza del Kernel se base en matemáticas y no en estimaciones.
