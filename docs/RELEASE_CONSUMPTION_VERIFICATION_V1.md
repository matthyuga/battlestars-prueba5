# Release Consumption Verification — Economy Toolkit (v1)

Fecha: 2026-04-12

## Objetivo

Validar que el paquete descargado no fue alterado antes de usarlo internamente.

## Requisitos

- Archivo release `.zip`
- Archivo checksum `.zip.sha256`

## Verificación recomendada (script oficial)

```bash
python tools/verify_release_checksum.py \
  --package dist/release/<archivo>.zip \
  --checksum-file dist/release/<archivo>.zip.sha256
```

Resultado esperado:
- `[ok] checksum válido ...`

## Verificación con Make (atajo)

```bash
make economy-verify-checksum \
  PACKAGE=dist/release/<archivo>.zip \
  CHECKSUM=dist/release/<archivo>.zip.sha256
```

## Política sugerida de consumo interno

1. No ejecutar binarios cuyo checksum no coincida.
2. Registrar hash validado en ticket/release notes internas.
3. (Opcional) Validar también attestation/provenance del artifact CI.
