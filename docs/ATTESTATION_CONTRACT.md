# Contrato de Attestation (auditoria 11, H-02)

## Que tools/attest.py DEMUESTRA (y no demuestra)
DEMUESTRA: integridad (el artefacto no cambio desde la firma) respecto de la
clave Ed25519 indicada, mas checks estructurales (cosine presente, status,
hashes). El campo --signer queda DENTRO del cuerpo firmado.

NO DEMUESTRA por si solo: independencia del firmante, competencia, autoridad,
ni veracidad de los resultados firmados. Una firma no es attestation
independiente (APCE G5 lo distingue).

## Attestation INDEPENDIENTE (requiere, ademas del codigo)
1. Tercero distinto del productor del artefacto.
2. Clave publica cuya identidad se verifique FUERA del artefacto
   (registro publico, perfil verificable, o encuentro presencial).
3. Alcance declarado: que atesto (integridad? reproduccion? ambas?).
4. Conservacion de la clave publica por el verificador, no solo en el JSON.
5. Opcional y recomendado: reproducir la medicion antes de firmar.

## Verificacion sin confianza en el firmante
python tools/attest.py solo valida criptografia. Para validar INDEPENDENCIA:
comprobar la identidad del attestor por un canal distinto al repositorio.
Ver docs/ATTESTATION_INVITATION.md para el protocolo operativo.
