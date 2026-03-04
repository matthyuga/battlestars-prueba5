# Phase 10 — Route cleanup report (legacy duplicates)

## Scope
Execute T10 by removing redundant legacy-compatible route labels that no longer participate in active routing.

## Changes applied

1. **Removed redundant 1v1 entry labels**
   - File: `game/4/00_BATTLE_MODE_1V1_ENTRY.rpy`
   - Removed:
     - `battle_offensive_turn_1v1_entry`
     - `battle_enemy_turn_1v1_entry`
     - `battle_defensive_turn_1v1_entry`
   - Kept:
     - `bs_prepare_1v1_turn_entry()` helper used by `*_1v1_impl` in `modes/1v1`.

2. **Removed redundant 2v2 entry labels**
   - File: `game/4/00_BATTLE_MODE_ROUTER.rpy`
   - Removed wrappers:
     - `battle_offensive_turn_2v2_entry`
     - `battle_enemy_turn_2v2_entry`
     - `battle_defensive_turn_2v2_entry`

3. **Router header adjusted**
   - Updated routing objective comment to reflect current state:
     - router delegates to 1v1/2v2 `*_impl` labels directly.

## Outcome
- Public labels remain stable through the public adapter.
- Router resolves directly to one implementation path per phase/mode.
- Duplicate compatibility labels that could create route ambiguity were removed.
