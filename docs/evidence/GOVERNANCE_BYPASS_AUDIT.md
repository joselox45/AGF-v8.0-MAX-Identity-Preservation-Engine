# Auditoría de Gobernanza - Push Directo a Main

**Fecha:** 2026-10-31
**Tag afectado:** v12.4.7.5-STRONG
**Incidente:** Push directo a `main` sin Pull Request.
**Causa:** Script de automatización en Python ejecutó `git push origin main` directamente en lugar de abrir un PR.
**Resolución:** Se documenta el incidente (Zero-Trust) y se restaura el flujo normal haciendo un PR de limpieza para los esquemas duplicados.
**Lección:** Los scripts automáticos siempre deben hacer checkout a una rama `feature/` o `docs/` y usar `gh pr merge`.
