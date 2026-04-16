# Bitácora de sesión — 2026-04-16

## Objetivo
- Consolidar continuidad de Fase 5 (A/B/C/D) en lobby/preparación/selector.
- Dejar trazabilidad para retomar en próxima sesión sin perder contexto.
- Preparar base de planilla de costos de técnicas (EP/EC) a partir de los datos compartidos.

## Cambios aplicados
1. **A/B/C de hardcode/data-driven completados técnicamente**:
   - Resolver unificado de roster y consumo desde selector/runtime.
   - Selector legacy migrado a lista dinámica (sin héroes hardcodeados en menús).
   - Catálogos item/técnicas externalizados a JSON versionable.
2. **D de verificación**:
   - QA de staging/precombat (`qa_fase4_lobby_prep_staging_gate.sh`) en PASS.
   - QA de hardcode/data contracts (`qa_fase5_p0_hardcode_guard.sh`) en PASS.
3. **Artefacto de continuidad de datos de costos**:
   - `docs/planilla_costos_tecnicas_ep_ec_v1.csv` (vista horizontal: técnicas en columnas lado a lado)
   - `docs/patron_escala_1_a_10_ec_v1.csv` (patrón 1..10 por técnica)
   - `docs/regla_escalado_tecnicas_v1.md` (regla y umbrales de crecimiento)

## Estado actual
- **Bloque A (roster unificado):** ✅
- **Bloque B (selector sin hardcodes):** ✅
- **Bloque C (catálogos JSON):** ✅
- **Bloque D (guardas/QA):** ✅

## Riesgos / observaciones
- Aún falta validación empírica Win7/Win10 de performance (freeze/latencia), que sigue en itinerario.
- El dataset de costos recibido mezcla “ep_base” y tramos de “ec_costo”; en próxima sesión conviene validar fórmula exacta de EP por escala.

## Próximo paso recomendado (siguiente sesión)
1. Revisar el Excel original fuente (si se comparte archivo) y comparar contra `planilla_costos_tecnicas_ep_ec_v1`.
2. Definir contrato final de costos por técnica:
   - `ep_base`,
   - regla EP por escala (si aplica),
   - `ec_costo` por tramos.
3. Integrar el contrato de costos en runtime (selector/can_afford/pay_costs) bajo flag de migración.
4. Actualizar checklist de docs para reflejar oficialmente A/B/C/D cerrados.

## Evidencia rápida
- `scripts/qa_fase4_lobby_prep_staging_gate.sh` → PASS
- `scripts/qa_fase5_p0_hardcode_guard.sh` → PASS
