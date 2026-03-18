# Índice rápido — Bitácora y documentación de pre-combate (2026-03-17)

## Documentos clave de la sesión

1. **Bitácora principal de la sesión**
   - Archivo: `docs/BITACORA_SESION_PRECOMBATE_ESPECIALES_2026-03-17.md`
   - Contiene decisiones cerradas sobre:
     - apartado de pre-combate,
     - 4 técnicas especiales nuevas,
     - reglas de bloqueo para técnicas "Ladrón ...",
     - reglas de "Salvaguarda principiante",
     - slots (`atk`, `def`, `spc`) y doble consumo para especiales.

2. **Plan por fases de implementación**
   - Archivo: `docs/PLAN_FASES_PRECOMBATE_TECNICAS_ESPECIALES.md`
   - Define el roadmap incremental desde contrato funcional, UI de pre-combate, integración de especiales, lógica runtime, escalado 2v2 y QA por hitos.


3. **Checklist firmable de Fase 0 (gate de salida)**
   - Archivo: `docs/CHECKLIST_FASE0_SSOT_FIRMABLE.md`
   - Plantilla de aprobación formal para cerrar SSOT funcional antes de pasar a implementación.

4. **Acta de decisiones Fase 0 (actualización de sesión)**
   - Archivo: `docs/FASE0_SSOT_DECISIONES_2026-03-18.md`
   - Consolida reglas cerradas de catálogo, modo libre/slots, perk base de especiales y prioridad de Salvaguarda.

5. **Arranque de Fase 1 (pre-combate)**
   - Archivo: `docs/FASE1_ARRANQUE_PRECOMBATE_2026-03-18.md`
   - Define objetivo, alcance, criterios de aceptación y checklist de implementación inmediata.

6. **Fase 2 — Escalabilidad visual (corte v1)**
   - Archivo: `docs/FASE2_UI_ESCALABILIDAD_2026-03-18.md`
   - Registra compactación de UI, paginación horizontal y vista íconos/fallback simple.

7. **Fase 4 — IA y compatibilidad 1v1/2v2 (corte inicial)**
   - Archivo: `docs/FASE4_IA_COMPAT_1V1_2V2_2026-03-18.md`
   - Registra bloqueo por `unit_key`, reglas forzado/normal y ejecución IA con omisión de técnica bloqueada.

## Resumen funcional consolidado

- Técnicas especiales de la iteración:
  - `Ladrón ofensivo` (ofensiva especial)
  - `Ladrón defensivo` (ofensiva especial)
  - `Ladrón de concentrar` (ofensiva especial)
  - `Salvaguarda principiante` (defensiva especial)
- Reglas de slots acordadas:
  - categorías `atk`, `def`, `spc`;
  - especiales ofensivas consumen `1 atk + 1 spc`;
  - especiales defensivas consumen `1 def + 1 spc`.

## Nota de continuidad

Este índice existe para retomar rápido el contexto sin tener que buscar manualmente entre múltiples notas de sesión.
