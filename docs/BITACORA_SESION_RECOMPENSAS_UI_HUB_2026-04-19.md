# Bitácora de sesión — Recompensas + UI Hub (2026-04-19)

## Objetivo de la sesión

Dejar documentado el estado real del trabajo para retomar en otra sesión sin perder contexto, con foco en:

- economía EXP/Oro configurable,
- perfiles de condiciones de recompensa,
- bridge de recompensas hacia cuenta,
- y refactor de navegación/UI en el hub.

## Estado consolidado (qué ya quedó integrado)

### 1) Runtime post-combate -> simulador (payload ampliado)

En el armado de request del runtime se están enviando parámetros de condición y de base/step de recompensas:

- `reward_condition_exp_mult`
- `reward_condition_oro_mult`
- `reward_condition_probability_mult`
- `reward_condition_tags`
- `base_exp_real`
- `base_oro_real`
- `step_exp_real`
- `step_oro_real`

Referencia: `game/04e_battle_end_result.rpy`.

### 2) Contrato/simulador con parámetros configurables y condiciones

En el contrato/simulación se validan y clapean multiplicadores/inputs de condiciones de recompensa, y se consumen los parámetros `base_*`/`step_*` configurables.

Además, el cálculo de recompensa integra multiplicadores por condición:

- `reward_condition_exp_mult`
- `reward_condition_oro_mult`
- `reward_condition_probability_mult`

y se propaga metadata/tags en el resultado.

Referencia: `game/10C_PROGRESSION_SIM_CONTRACT_V1.rpy`.

### 3) Bridge idempotente simulación -> cuenta

La aplicación de recompensas post-simulación contempla puente a cuenta y control anti-duplicado con registro:

- `sim_account_reward_bridge_registry_v1`

para evitar re-aplicar recompensas ya bridged.

Referencia: `game/10C_PROGRESSION_SIM_CONTRACT_V1.rpy`.

### 4) APIs de economía y utilidades DEV en hub

Se consolidaron funciones utilitarias para cuenta/economía:

- `bs_saga_gain_account_rewards`
- `bs_saga_exp_required_for_level`
- `bs_saga_dev_set_gain_profile`
- `bs_saga_dev_apply_semirandom_gain`
- `bs_saga_estimate_duels_to_targets`

Referencia: `game/ui_hub/ui_hub_audit_economy.rpy`.

### 5) UI Hub: helper seguro + navegación por retorno

Se usa wrapper seguro de acciones UI:

- `bs_saga_ui_call(...)`

y navegación basada en códigos `Return("nav:...")`, con helpers:

- `bs_saga_nav_matches(...)`
- `bs_saga_lobby_nav_target(...)`

Esto evita side-effects de `Jump(...)` directo dentro de screens llamadas con `call_screen`.

Referencias:

- `game/12_BATTLESTARS_SAGA_UI_HUB_V1.rpy`
- `game/ui_hub/ui_hub_screens_lobby.rpy`
- `game/ui_hub/ui_hub_screens_prep.rpy`

### 6) Gestión de condiciones de recompensa en preparación

Se añadieron defaults/getters/toggles y armado de perfil:

- `bs_saga_reward_conditions_defaults`
- `bs_saga_get_prep_reward_conditions`
- `bs_saga_set_prep_reward_condition`
- `bs_saga_toggle_prep_reward_condition`
- `bs_saga_build_reward_condition_profile`

y controles UI para modificar flags y base/step de recompensa.

Referencias:

- `game/12_BATTLESTARS_SAGA_UI_HUB_V1.rpy`
- `game/ui_hub/ui_hub_screens_prep.rpy`
- `game/ui_hub/ui_hub_state.rpy`

## Decisiones de arquitectura tomadas

1. **Mantener compatibilidad dual de tokens nav** (`to_*` + `nav:*`) en labels/ruteo para no romper rutas legacy.
2. **No cerrar screens por side-effect**: preferencia por `Function(bs_saga_ui_call, ...)` y `Return("nav:...")`.
3. **Bridge de recompensas idempotente**: priorizado para evitar duplicados entre reintentos o replays.
4. **Parámetros de economía tunables**: base/step y multiplicadores expuestos para balance iterativo.

## Riesgos conocidos / puntos a vigilar al retomar

- Verificar in-game que cada ruta `Return("nav:...")` tenga manejo explícito en label padre.
- Revisar consistencia entre “Tienda” y “Catálogo de ítems” (comparten screen/catalog flow) para evitar ambigüedades de UX.
- Corroborar que no existan rutas legacy que todavía dependan de `return` implícito hacia menú principal.
- Confirmar en QA manual que el bridge idempotente no bloquee aplicaciones válidas en escenarios de multi-battle.

## Checklist recomendado para próxima sesión

1. Smoke test navegacional completo:
   - Lobby -> Preparación -> Staging/Config/Room -> Lobby.
   - Lobby -> Perfil/Héroes/Tienda/Inventario/Catálogos/Torre -> Lobby.
2. Smoke test economía:
   - Ajustar `base/step` y flags de condición en prep.
   - Ejecutar combate/simulación.
   - Validar EXP/Oro en cuenta + registro idempotente.
3. Capturar evidencia mínima en docs:
   - tabla de casos probados (entrada, resultado esperado, resultado real).

## Referencia rápida de archivos críticos

- `game/04e_battle_end_result.rpy`
- `game/10C_PROGRESSION_SIM_CONTRACT_V1.rpy`
- `game/12_BATTLESTARS_SAGA_UI_HUB_V1.rpy`
- `game/ui_hub/ui_hub_audit_economy.rpy`
- `game/ui_hub/ui_hub_screens_lobby.rpy`
- `game/ui_hub/ui_hub_screens_prep.rpy`
- `game/ui_hub/ui_hub_state.rpy`

