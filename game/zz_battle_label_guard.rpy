# ============================================================
# zz_battle_label_guard.rpy – Guard final de labels públicas
# ============================================================
# Se carga al final para garantizar que las labels públicas
# apunten siempre al router, incluso si existen definiciones
# legacy residuales en builds/cache antiguos.
# ============================================================

init 999 python:
    def _zz_is_2v2_mode():
        try:
            import renpy.store as S
            return str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower() == "2v2"
        except:
            return False


label battle_offensive_turn:
    jump battle_offensive_turn_router_entry


label battle_enemy_turn:
    jump battle_enemy_turn_router_entry


label battle_defensive_turn:
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

    jump battle_defensive_turn_router_entry
