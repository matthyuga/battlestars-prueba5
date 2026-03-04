# ============================================================
# 00_BATTLE_MODE_ROUTER.rpy – Router de entrada por modo (C1)
# ============================================================
# Objetivo C1:
# - Mantener contrato público de labels legacy:
#     battle_offensive_turn / battle_enemy_turn / battle_defensive_turn
# - Enrutar por battle_team_mode sin cambiar reglas de combate.
# - Preparar stubs 2v2 para migración incremental (C2/C3/C4).
# ============================================================

init -950 python:
    def bs_is_2v2_mode():
        try:
            import renpy.store as S
            mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
            return mode == "2v2"
        except Exception:
            return False


label battle_offensive_turn_router_entry:
    $ _is_2v2 = bool(bs_is_2v2_mode())
    python:
        import renpy.store as S
        try:
            fn_route_log = getattr(S, "bs_log_turn_contract", None)
            if callable(fn_route_log):
                fn_route_log(
                    "battle_offensive_turn_router_entry",
                    "2v2" if _is_2v2 else "1v1",
                    owner="player",
                    target="slot" if _is_2v2 else "auto",
                    phase="off",
                )
        except:
            pass
    $ _router_target = "battle_offensive_turn_2v2_entry" if _is_2v2 else "battle_offensive_turn_1v1_impl"
    jump expression _router_target


label battle_enemy_turn_router_entry:
    $ _is_2v2 = bool(bs_is_2v2_mode())
    python:
        import renpy.store as S
        try:
            fn_route_log = getattr(S, "bs_log_turn_contract", None)
            if callable(fn_route_log):
                fn_route_log(
                    "battle_enemy_turn_router_entry",
                    "2v2" if _is_2v2 else "1v1",
                    owner="enemy",
                    target="slot" if _is_2v2 else "auto",
                    phase="enemy",
                )
        except:
            pass
    $ _router_target = "battle_enemy_turn_2v2_entry" if _is_2v2 else "battle_enemy_turn_1v1_impl"
    jump expression _router_target


label battle_defensive_turn_router_entry:
    $ _is_2v2 = bool(bs_is_2v2_mode())
    python:
        import renpy.store as S
        try:
            fn_ensure = getattr(S, "bs_ui_gateway_ensure", None)
            if not callable(fn_ensure):
                fn_ensure = getattr(S, "ensure_renpy_ui_apis", None)
            if callable(fn_ensure):
                fn_ensure()
        except:
            pass
        try:
            fn_route_log = getattr(S, "bs_log_turn_contract", None)
            if callable(fn_route_log):
                fn_route_log(
                    "battle_defensive_turn_router_entry",
                    "2v2" if _is_2v2 else "1v1",
                    owner="player",
                    target="slot" if _is_2v2 else "auto",
                    phase="def",
                )
        except:
            pass
    $ _router_target = "battle_defensive_turn_2v2_entry" if _is_2v2 else "battle_defensive_turn_1v1_impl"
    jump expression _router_target


# ------------------------------------------------------------
# Stubs 2v2 (C1): por ahora delegan a legacy para no romper.
# ------------------------------------------------------------
label battle_offensive_turn_2v2_entry:
    python:
        import renpy.store as S
        try:
            fn_route_log = getattr(S, "bs_log_turn_contract", None)
            if callable(fn_route_log):
                fn_route_log("battle_offensive_turn_legacy_entry", "2v2", owner="player", target="slot", phase="off")
        except:
            pass
    jump battle_offensive_turn_legacy_entry


label battle_enemy_turn_2v2_entry:
    python:
        import renpy.store as S
        try:
            fn_route_log = getattr(S, "bs_log_turn_contract", None)
            if callable(fn_route_log):
                fn_route_log("battle_enemy_turn_legacy_entry", "2v2", owner="enemy", target="slot", phase="enemy")
        except:
            pass
    jump battle_enemy_turn_legacy_entry


label battle_defensive_turn_2v2_entry:
    python:
        import renpy.store as S
        try:
            fn_route_log = getattr(S, "bs_log_turn_contract", None)
            if callable(fn_route_log):
                fn_route_log("battle_defensive_turn_legacy_entry", "2v2", owner="player", target="slot", phase="def")
        except:
            pass
    jump battle_defensive_turn_legacy_entry
