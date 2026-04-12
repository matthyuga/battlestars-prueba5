# Manual de operación — Economy Toolkit (QA / Design / PM)

Fecha: 2026-04-12

## Objetivo

Ejecutar el ciclo principal de economía sin tocar código, usando el ejecutable.

## 1) Preparación

1. Descargar artefacto release correspondiente al sistema operativo.
2. Verificar checksum antes de ejecutar.
3. Descomprimir el `.zip`.

## 2) Verificación de integridad

Con script oficial:

```bash
python tools/verify_release_checksum.py \
  --package dist/release/<archivo>.zip \
  --checksum-file dist/release/<archivo>.zip.sha256
```

Debe mostrar: `[ok] checksum válido ...`

## 3) Flujo recomendado no técnico (wizard)

Ejecutar:

- Linux/macOS: `./economy-toolkit wizard`
- Windows: `economy-toolkit.exe wizard`

El wizard guía:
1. versión nueva,
2. versión previa,
3. thresholds,
4. nombre de bundle,
5. salida dashboard/report.

## 4) Salidas que deben revisarse

En el bundle generado (`artifacts/economy_reports/<bundle>/`):
- `diff.json`
- `diff.md`
- `dashboard.html`
- `manifest.json`

## 5) Decisión operativa

- Si no hay alertas críticas: aprobar avance.
- Si hay alertas: devolver a balance para ajuste y repetir ciclo.

## 6) Checklist rápido para QA/Design/PM

- [ ] checksum validado
- [ ] wizard ejecutado sin errores
- [ ] dashboard abierto y revisado
- [ ] diff revisado (p50/p95)
- [ ] decisión documentada (aprobar/ajustar)
