# Phase 5 — Cleanup execution report (routing/UI compat)

## Scope
This cleanup pass focuses on reducing transitional compatibility branches introduced during T1–T4 while preserving runtime stability.

## Changes applied

1. **Router defensive entry cleanup**
   - Simplified defensive preflight in `game/4/00_BATTLE_MODE_ROUTER.rpy`.
   - Removed fallback branch to `ensure_renpy_ui_apis` and kept single canonical gateway call:
     - `bs_ui_gateway_ensure()`

2. **Public label guard cleanup**
   - Simplified defensive preflight in `game/zz_battle_label_guard.rpy`.
   - Removed fallback branch to `ensure_renpy_ui_apis` and kept canonical gateway call:
     - `bs_ui_gateway_ensure()`

## Rationale
- T4 already introduced `game/4/shared/battle_runtime_ui_gateway.rpy` as the canonical UI runtime-safe API.
- Keeping both gateway + legacy preflight branches in hot routing paths adds accidental complexity without practical benefit.
- This cleanup narrows defensive routing to a single preflight path while preserving backward compatibility at API level (the alias `ensure_renpy_ui_apis` still exists in the gateway module for non-router call sites if needed).

## Residual technical debt intentionally kept
- Legacy turn implementations `*_legacy_entry` remain active by design (migration in progress).
- 2v2 paths are still stubs delegating to legacy entries until dedicated 2v2 orchestration is completed.
- Additional non-critical `renpy.*` direct usages outside critical turn-flow files remain for later cleanup waves.
