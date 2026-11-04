# AGF v8.0-MAX — Identity Preservation Engine
**Versión:** v1.4.1-security (Kernel v0.9.8)
**Estado:** CERRADO / IP PROTEGIDA

Este repositorio contiene el Kernel de Gobernanza y el Motor de Preservación de Identidad AGF. El sistema opera bajo un principio de **FAIL-CLOSED** y **ZERO-FABRICACIÓN**.

## 🏛️ Arquitectura de Gobernanza (v0.9.8)
El sistema divide sus operaciones en dos canales estrictos:
*   **MIL (Chatbot):** Motor de Inferencia Lógica. Solo audita y verifica. No ejecuta código.
*   **HIL (Termux):** Motor de Ejecución. Corre Python, audita imágenes y verifica hashes.

### Secciones Clave del Kernel (0 al 23)
*   **Sección 3:** Prohibiciones Duras (Fail-Closed).
*   **Sección 8:** Entropy Gate (Anti-alucinación y WEAK_SEMANTIC).
*   **Sección 23:** Protocolo FLUJO_CONTENEDOR (Encapsulamiento de respuestas).
    *   *23.4:* Regla de limpieza de interfaz (clear obligatorio en scripts).
    *   *23.5:* Prohibición de Heredoc Multilínea (para evitar congelar Termux).

## 🚀 Activación Rápida

### 1. En el Chatbot (MIL)
Copia el contenido de docs/governance/CHATBOT_BOOT_PROMPT.md y pégalo como primer mensaje en cualquier LLM. Activa el rol de Juez Puro.

### 2. En la Terminal (HIL)
El entorno está configurado con el alias agf en .bashrc. Para cargar el Kernel y ejecutar herramientas:
agf tools/hil_test/test_cuadruple_capa_HIL.py

## 🛡️ Protección de Propiedad Intelectual (IP)
*   **Historial purgado:** Se eliminó sonda_marianas.py y scripts de esteganografía/Reed-Solomon del repositorio y de todo el historial de Git.
*   **Verificación:** Prueba de Oro (Clon Fresco) confirma 0 rastros en el árbol principal y tags.
*   **Nota de Soporte:** Pendiente purga de refs/pull/N/head por GitHub Support.

---
---
*Documento actualizado el 2026-11-03 bajo la gobernanza de la Sección 23.*
## 📂 Estructura del Proyecto
*   docs/governance/ — Kernel, reglas y boot prompts.
*   docs/evidence/ — Snapshot de sesión (Input/Output containers).
*   src/ — Gobernanza, políticas y capas de veredicto.
*   tools/ — Auditoría forense y Juez Puro. (Los motores de esteganografía y biometría han sido removidos por seguridad de IP).
*   agf_ui.html — Interfaz visual estática (No ejecutable / Solo referencia de diseño).
