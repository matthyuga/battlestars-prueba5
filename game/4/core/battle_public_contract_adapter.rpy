# ============================================================
# battle_public_contract_adapter.rpy — Adapter contrato público
# ============================================================
# T9: mantiene labels públicas estables y delega explícitamente
# al router por modo (sin cambiar callers externos).
# ============================================================

label battle_public_offensive_adapter:
    jump battle_offensive_turn_router_entry


label battle_public_enemy_adapter:
    jump battle_enemy_turn_router_entry


label battle_public_defensive_adapter:
    python:
        import renpy.store as S
        try:
            fn_ensure = getattr(S, "bs_ui_gateway_ensure", None)
            if callable(fn_ensure):
                fn_ensure()
        except Exception:
            pass
    jump battle_defensive_turn_router_entry
