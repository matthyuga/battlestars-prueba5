# Phase 9 — Public contract adapter report

## Scope
Implement T9 by introducing an explicit adapter layer from public labels to mode router internals, while preserving public API stability.

## Changes applied

1. Added adapter module:
   - `game/4/core/battle_public_contract_adapter.rpy`
   - new adapter labels:
     - `battle_public_offensive_adapter`
     - `battle_public_enemy_adapter`
     - `battle_public_defensive_adapter`

2. Updated public labels guard:
   - `game/zz_battle_label_guard.rpy`
   - public labels now jump to adapter labels instead of jumping directly to router entries.

## Why
- Keeps public labels as stable facade while making delegation explicit and easier to evolve.
- Reduces coupling between public contract surface and router internals.
- Defensive preflight (`bs_ui_gateway_ensure`) is centralized in defensive adapter path.

## Compatibility
- External callers continue using unchanged public labels:
  - `battle_offensive_turn`
  - `battle_enemy_turn`
  - `battle_defensive_turn`
- Internal routing remains mode-based through existing router entries.
