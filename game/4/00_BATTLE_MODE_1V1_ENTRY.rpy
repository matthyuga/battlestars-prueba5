# ============================================================
# 00_BATTLE_MODE_1V1_ENTRY.rpy – Entry points dedicados 1v1
# ============================================================
# Fase 1 (plan maestro): línea de vida 1v1 explícita.
# Mantiene labels públicas/routing estables y evita acoplar
# accidentalmente decisiones 1v1 a estado 2v2.
# ============================================================

init -949 python:
    def bs_prepare_1v1_turn_entry(owner="player"):
        """Aísla 1v1 de residuos de contexto 2v2 antes de cada turno."""
        try:
            import renpy.store as S

            # Modo explícito: cualquier ruta 1v1 debe operar en 1v1.
            S.battle_team_mode = "1v1"

            # Evitar que defensivo 1v1 consuma contexto stale de incoming 2v2.
            for attr in ("incoming_damage_target_key", "defense_target_key"):
                if hasattr(S, attr):
                    setattr(S, attr, "")

            # Limpieza segura de incoming ctx (si existe API SSOT).
            fn_clear = getattr(S, "bs_clear_incoming_ctx", None)
            if callable(fn_clear):
                fn_clear()

            # Turn owner coherente para logs/HUD en 1v1.
            S.turn_owner_team = str(owner or "player")
            S.turn_owner_slot = 0

            if callable(getattr(S, "battle_log_add", None)):
                S.battle_log_add("{color=#80DEEA}[DEBUG] ROUTE_PREP mode=1v1 owner=%s cleared_incoming=1{/color}" % str(owner or "player"))
        except Exception:
            pass

label battle_offensive_turn_1v1_entry:
    python:
        import renpy.store as S
        bs_prepare_1v1_turn_entry(owner="player")
        try:
            fn_route_log = getattr(S, "bs_log_turn_contract", None)
            if callable(fn_route_log):
                fn_route_log("battle_offensive_turn_legacy_entry", "1v1", owner="player", target="auto")
            elif callable(getattr(S, "battle_log_add", None)):
                S.battle_log_add("{color=#80DEEA}[DEBUG] ROUTE mode=1v1 owner=player target=auto label=battle_offensive_turn_legacy_entry{/color}")
        except:
            pass
    jump battle_offensive_turn_legacy_entry


label battle_enemy_turn_1v1_entry:
    python:
        import renpy.store as S
        bs_prepare_1v1_turn_entry(owner="enemy")
        try:
            fn_route_log = getattr(S, "bs_log_turn_contract", None)
            if callable(fn_route_log):
                fn_route_log("battle_enemy_turn_legacy_entry", "1v1", owner="enemy", target="auto")
            elif callable(getattr(S, "battle_log_add", None)):
                S.battle_log_add("{color=#80DEEA}[DEBUG] ROUTE mode=1v1 owner=enemy target=auto label=battle_enemy_turn_legacy_entry{/color}")
        except:
            pass
    jump battle_enemy_turn_legacy_entry


label battle_defensive_turn_1v1_entry:
    python:
        import renpy.store as S
        bs_prepare_1v1_turn_entry(owner="player")
        try:
            fn_route_log = getattr(S, "bs_log_turn_contract", None)
            if callable(fn_route_log):
                fn_route_log("battle_defensive_turn_legacy_entry", "1v1", owner="player", target="auto")
            elif callable(getattr(S, "battle_log_add", None)):
                S.battle_log_add("{color=#80DEEA}[DEBUG] ROUTE mode=1v1 owner=player target=auto label=battle_defensive_turn_legacy_entry{/color}")
        except:
            pass
    jump battle_defensive_turn_legacy_entry
