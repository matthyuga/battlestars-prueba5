# T6 — Protocolo de higiene de build y validación QA

## Objetivo
Garantizar que el runtime ejecuta exactamente el código fuente vigente y evitar falsos positivos por artefactos stale (`.rpyc`, cachés Python, build viejo).

## Rutina estándar (antes de smoke/regresión)

1. Ejecutar limpieza de artefactos:

```bash
scripts/qa_clean_build.sh
```

2. (Opcional) Vista previa sin borrar:

```bash
scripts/qa_clean_build.sh --dry-run
```

3. Arrancar juego en build/sesión limpia.
4. Ejecutar smoke mínimo:
   - 1v1: `off -> enemy -> def`
   - 2v2: target slot 0 y slot 1
5. Si hay traceback, registrar:
   - hash commit probado,
   - último log `ROUTE ...`,
   - archivo/línea reportado.

## Criterio de aceptación T6
- No quedan `.rpyc/.rpymc` stale luego de la limpieza.
- El traceback (si aparece) mapea a líneas existentes en fuente actual.
- El smoke base es reproducible por otro dev con los mismos pasos.

## Notas
- Este protocolo no reemplaza QA funcional; evita desalineación fuente/runtime.
- Mantener esta rutina como paso obligatorio previo a validar regresiones críticas de turno defensivo.
