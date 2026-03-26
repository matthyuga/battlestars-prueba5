# Phase 8 — Incoming context isolation for 2v2

## Scope
Implement T8 by isolating incoming-damage context handling for 2v2 and wiring critical producers/entrypoints to a dedicated SSOT module.

## Changes applied

1. **New SSOT module for incoming context (2v2)**
   - Added `game/4/modes/2v2/battle_incoming_ctx_2v2.rpy`.
   - Provides:
     - `bs_get_incoming_ctx_2v2()`
     - `bs_set_incoming_ctx_2v2(...)`
     - `bs_clear_incoming_ctx_2v2(...)`
     - `bs_clear_incoming_ctx(...)` (compat alias)
   - Keeps legacy mirrors (`incoming_damage_target_key`, `incoming_damage_source_key`, `incoming_damage_sources`) in sync.

2. **2v2 router preflight update**
   - Updated `game/4/modes/2v2/battle_router_2v2.rpy` to use phase-aware prep:
     - clears incoming ctx at attack-entry phases (`off`, `enemy`),
     - preserves context on defensive entry (`def`).

3. **Critical incoming producers migrated to SSOT setter**
   - Updated assignments in:
     - `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy`
     - `game/4/j/04C_OFFENSIVE_COREV3.rpy`
     - `game/4/j/04C_OFFENSIVE_RESOLVEV1.rpy`
   - New behavior prefers `bs_set_incoming_ctx_2v2(...)` with fallback to direct legacy assignments.

## Expected impact
- Reduce risk of stale `incoming_damage_target_key` leaking between consecutive 2v2 turns.
- Keep current combat core compatible while moving context ownership into one module.

## Residual debt
- Some non-critical producers may still write legacy incoming fields directly and can be migrated in later cleanup waves.
