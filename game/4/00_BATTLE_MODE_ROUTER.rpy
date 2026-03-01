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


label battle_offensive_turn:
    python:
        import renpy
        import renpy.store as S
        _is_2v2 = bool(bs_is_2v2_mode())
        try:
            if callable(getattr(S, "battle_log_add", None)):
                S.battle_log_add("{color=#80DEEA}[DEBUG] ROUTER_ENTER label=battle_offensive_turn mode=%s{/color}" % ("2v2" if _is_2v2 else "1v1"))
        except:
            pass
        renpy.jump("battle_offensive_turn_2v2_entry" if _is_2v2 else "battle_offensive_turn_legacy_entry")


label battle_enemy_turn:
    python:
        import renpy
        import renpy.store as S
        _is_2v2 = bool(bs_is_2v2_mode())
        try:
            if callable(getattr(S, "battle_log_add", None)):
                S.battle_log_add("{color=#80DEEA}[DEBUG] ROUTER_ENTER label=battle_enemy_turn mode=%s{/color}" % ("2v2" if _is_2v2 else "1v1"))
        except:
            pass
        renpy.jump("battle_enemy_turn_2v2_entry" if _is_2v2 else "battle_enemy_turn_legacy_entry")


label battle_defensive_turn:
    python:
        import renpy
        import renpy.store as S
        _is_2v2 = bool(bs_is_2v2_mode())
        try:
            if callable(getattr(S, "battle_log_add", None)):
                S.battle_log_add("{color=#80DEEA}[DEBUG] ROUTER_ENTER label=battle_defensive_turn mode=%s{/color}" % ("2v2" if _is_2v2 else "1v1"))
        except:
            pass
        renpy.jump("battle_defensive_turn_2v2_entry" if _is_2v2 else "battle_defensive_turn_legacy_entry")


# ------------------------------------------------------------
# Stubs 2v2 (C1): por ahora delegan a legacy para no romper.
# ------------------------------------------------------------
label battle_offensive_turn_2v2_entry:
    jump battle_offensive_turn_legacy_entry


label battle_enemy_turn_2v2_entry:
    jump battle_enemy_turn_legacy_entry


label battle_defensive_turn_2v2_entry:
    jump battle_defensive_turn_legacy_entry
