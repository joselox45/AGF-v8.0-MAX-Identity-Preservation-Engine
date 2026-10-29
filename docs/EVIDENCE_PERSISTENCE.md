# Persistencia de Evidencia — garantias y limites (auditoria 11, H-04)

## Que garantiza la cadena SHA-512 (evidence_writer)
Integridad de la SESION: si un registro de la cadena en memoria se altera,
chain_check() lo detecta (FAIL con seq). Cada herramienta (closure,
verify_image) persiste su JSON en disco al terminar.

## Limites declarados (no ocultos)
1. La cadena es por-sesion; el JSON persistido no esta encadenado ENTRE
   archivos. Un actor con acceso al disco podria editar un JSON y el hash
   interno no lo delataria (no hay anclaje del evidence_hash a disco).
2. No hay sellado temporal confiable (timestamps son declarativos).
3. No hay almacenamiento inmutable (WORM) ni anclaje externo.

## Verificacion post-persistencia (receta)
sha256sum evidence/verify_2026-10-14/*.json  -> comparar contra los
evidence_hash internos publicados en el commit/mensaje. Esto detecta
alteracion posterior a la publicacion, que es la amenaza relevante para
un repo publico con historial git (el historial firmado de git ancla
cada evidencia a un commit).

## Endurecimiento (roadmap)
Encadenar evidence_hash de corrida N contra el JSON de corrida N-1;
publicar el digest de la carpeta de evidencia en el commit; attestation
Ed25519 por tercero con clave registrada fuera del repo.
