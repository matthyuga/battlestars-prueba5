# SLA de validación — Economy Toolkit (v1)

Fecha: 2026-04-12

## Objetivo

Definir tiempos y criterios mínimos antes de aprobar una versión de economía.

## SLA propuesto

1. **Preflight técnico**
   - comando: `make economy-preflight`
   - objetivo: < 10 min en entorno CI estándar.

2. **Gate de economía**
   - comando: `make economy-gate ...`
   - objetivo: sin alertas críticas fuera de umbral.

3. **Revisión funcional (QA/Design/PM)**
   - revisar `dashboard.html` + `diff.md`
   - tiempo máximo recomendado: 1 día hábil desde artifacts listos.

4. **Aprobación release**
   - checklist completo de manual operativo,
   - evidencias adjuntas en ticket/release notes.

## Criterios de bloqueo

- fallas en preflight,
- gate con alertas fuera de política,
- ausencia de artifacts de revisión,
- checksum no verificado para binario distribuido.
