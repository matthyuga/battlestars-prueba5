# Playbook de incidentes y rollback — Economy Toolkit (v1)

Fecha: 2026-04-12

## Objetivo

Responder rápido cuando una versión de economía genera alertas críticas o resultados anómalos.

## Severidades

- **SEV-1**: impacto alto en economía (inflación severa, bloqueo de progresión, inconsistencia crítica).
- **SEV-2**: desviaciones relevantes detectadas por gate/dashboard.
- **SEV-3**: issues menores de reporte/operación sin impacto de balance inmediato.

## Procedimiento de respuesta

1. **Contención**
   - detener promoción de versión nueva,
   - mantener versión estable anterior como baseline de referencia.

2. **Diagnóstico**
   - revisar `diff.json`, `diff.md`, `dashboard.html`, `economy_ci_metrics.json`.
   - identificar métrica y escenario con mayor |Δ%|.

3. **Decisión**
   - rollback a baseline anterior si SEV-1/SEV-2 no mitigable rápido,
   - hotfix de fórmula/thresholds y repetir ciclo.

4. **Verificación post-acción**
   - ejecutar `make economy-preflight`,
   - ejecutar compare/gate entre rollback/hotfix y baseline estable,
   - documentar decisión final.

## Evidencias mínimas a adjuntar en incidente

- hash/versión old/new,
- artefactos CI (diff + dashboard + metrics),
- resultado de gate,
- acción tomada (rollback/hotfix).
