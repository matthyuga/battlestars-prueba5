# ============================================================
# battle_router_1v1.rpy — Implementación dedicada de entradas 1v1
# ============================================================
# T3 (separación por modo): centraliza la orquestación 1v1 sin
# romper compatibilidad con labels históricas *_1v1_entry.
# ============================================================

label battle_offensive_turn_1v1_impl:
    python:
        import renpy.store as S
        bs_prepare_1v1_turn_entry(owner="player")
        try:
            fn_route_log = getattr(S, "bs_log_turn_contract", None)
            if callable(fn_route_log):
                fn_route_log("battle_offensive_turn_legacy_entry", "1v1", owner="player", target="auto", phase="off")
        except Exception:
            pass
    jump battle_offensive_turn_legacy_entry


label battle_enemy_turn_1v1_impl:
    python:
        import renpy.store as S
        bs_prepare_1v1_turn_entry(owner="enemy")
        try:
            fn_route_log = getattr(S, "bs_log_turn_contract", None)
            if callable(fn_route_log):
                fn_route_log("battle_enemy_turn_legacy_entry", "1v1", owner="enemy", target="auto", phase="enemy")
        except Exception:
            pass
    jump battle_enemy_turn_legacy_entry


label battle_defensive_turn_1v1_impl:
    python:
        import renpy.store as S
        bs_prepare_1v1_turn_entry(owner="player")
        try:
            fn_route_log = getattr(S, "bs_log_turn_contract", None)
            if callable(fn_route_log):
                fn_route_log("battle_defensive_turn_legacy_entry", "1v1", owner="player", target="auto", phase="def")
        except Exception:
            pass
    jump battle_defensive_turn_legacy_entry
