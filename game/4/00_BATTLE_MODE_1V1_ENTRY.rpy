# ============================================================
# 00_BATTLE_MODE_1V1_ENTRY.rpy – Helper de preparación 1v1
# ============================================================
# Expone bs_prepare_1v1_turn_entry() para la implementación
# dedicada en modes/1v1 (T10: se retiran entries redundantes).
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

            fn_debug_enabled = getattr(S, "bs_route_debug_enabled", None)
            if callable(fn_debug_enabled) and fn_debug_enabled() and callable(getattr(S, "battle_log_add", None)):
                S.battle_log_add("{color=#80DEEA}[DEBUG] ROUTE_PREP mode=1v1 owner=%s cleared_incoming=1{/color}" % str(owner or "player"))
        except Exception:
            pass

