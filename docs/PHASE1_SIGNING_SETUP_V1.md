# Fase 1 — Setup de firma por plataforma (Economy Toolkit)

Fecha: 2026-04-12

## Objetivo

Activar firma de artefactos/binarios por plataforma en el release pipeline.

## Secrets esperados en GitHub Actions

- `WINDOWS_SIGN_PFX_BASE64`
- `WINDOWS_SIGN_PFX_PASSWORD`
- `MACOS_SIGN_IDENTITY`
- `ECONOMY_GPG_KEY_ID`
- `ECONOMY_GPG_PRIVATE_KEY` (opcional, Linux detached signatures)

## Comportamiento implementado

- **Windows**: si hay PFX + password + `signtool`, firma Authenticode del binario.
- **macOS**: si hay identidad + `codesign`, firma del binario.
- **Linux**: firma detached GPG opcional del binario y checksum.
- Si faltan secretos/herramientas: el pipeline continúa con warning informativo.

## Verificación recomendada

1. Lanzar release con tag semántico.
2. Verificar en logs del job mensajes `[ok] firmado ...`.
3. Confirmar archivos `.asc` en artifacts cuando aplica.

## Nota

La notarización macOS y validaciones adicionales de confianza de certificados pueden añadirse en una iteración posterior.
