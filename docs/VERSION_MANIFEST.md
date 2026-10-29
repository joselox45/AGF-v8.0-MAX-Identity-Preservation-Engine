# Manifiesto de Versiones (auditoria 11, H-08)

| Componente | Version | Estado | Evidencia aplicable |
|---|---|---|---|
| Repositorio / release | v8.0 MAX (linea main) | activo | todo el arbol |
| MTE v1.0 (T01-T20) | v1.0 | especificacion + fixtures 04-oct | ERRATA.md (fixtures, no corrida) |
| v9.0 runtime (T21-T31) | mapping v6 | 8/8 TESTED | data/apce_mapping_t21_t28.csv |
| Chat Runtime (FSM+kernel) | v0.2 (codigo: algunos headers dicen v0.1, heredados) | operativo como puerta de protocolo | INTEGRATION_STATUS.md |
| Verificador biometrico | verify_image + closure | ruta canonica L1/L2/L3 | evidence/verify_2026-10-14/ |
| mte_runner_v2 | 2.2 | evaluador formal canonico | tests/ (73) |
| Protocolo AKADI-O0 | v18.0 | canonico de gobernanza | docs/protocols/ |

## Regla de compatibilidad
Ninguna prueba de un componente demuestra el sistema completo. Cada afirmacion
debe citar componente + version + evidencia. Las versiones de codigo heredadas
(v0.1 en headers) se actualizan al siguiente cambio funcional; no afectan
conducta. APCE G6: nada se auto-promueve a OPERATING_EFFECTIVE.

| Protocolo AKADI-UNIFICADO | v19.0 | canonico UNICO (supersede) | docs/protocols/ |
|   (fuentes: O0 v18.0 + IL v1.6) | | archivados en historical/ con sha256 | |
