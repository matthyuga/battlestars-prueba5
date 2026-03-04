# ============================================================
# battle_router_2v2.rpy — Implementación dedicada de entradas 2v2
# ============================================================
# T7/T8: separa orquestación de entrada 2v2 del router general
# y usa incoming ctx aislado para evitar contaminación cruzada.
# ============================================================

init -948 python:
    def bs_prepare_2v2_turn_entry(owner="player", phase=""):
        """Prepara contexto mínimo de entrada para flujo 2v2."""
        try:
            import renpy.store as S

            S.battle_team_mode = "2v2"

            slot_idx = int(getattr(S, "turn_owner_slot", 0) or 0)
            fn_ctx = getattr(S, "bs_get_turn_ctx", None)
            if callable(fn_ctx):
                ctx = fn_ctx()
                if isinstance(ctx, dict):
                    c_team = str(ctx.get("owner_team", owner) or owner)
                    c_slot = int(ctx.get("owner_slot", slot_idx) or slot_idx)
                    if c_team == str(owner or "player"):
                        slot_idx = c_slot

            S.turn_owner_team = str(owner or "player")
            S.turn_owner_slot = int(slot_idx or 0)

            # T8: limpiar incoming ctx al inicio de fases de ataque,
            # mantenerlo en defensivo para no perder target seleccionado.
            fn_clear_ctx = getattr(S, "bs_clear_incoming_ctx_2v2", None)
            if phase in ("off", "enemy") and callable(fn_clear_ctx):
                fn_clear_ctx(clear_plan=False)

            fn_debug_enabled = getattr(S, "bs_route_debug_enabled", None)
            if callable(fn_debug_enabled) and fn_debug_enabled() and callable(getattr(S, "battle_log_add", None)):
                S.battle_log_add(
                    "{color=#80DEEA}[DEBUG] ROUTE_PREP mode=2v2 phase=%s owner=%s slot=%s{/color}" % (
                        str(phase or "?"),
                        str(owner or "player"),
                        str(int(slot_idx or 0)),
                    )
                )
        except Exception:
            pass


label battle_offensive_turn_2v2_impl:
    python:
        import renpy.store as S
        bs_prepare_2v2_turn_entry(owner="player", phase="off")
        try:
            fn_route_log = getattr(S, "bs_log_turn_contract", None)
            if callable(fn_route_log):
                fn_route_log("battle_offensive_turn_legacy_entry", "2v2", owner="player", target="slot", phase="off")
        except Exception:
            pass
    jump battle_offensive_turn_legacy_entry


label battle_enemy_turn_2v2_impl:
    python:
        import renpy.store as S
        bs_prepare_2v2_turn_entry(owner="enemy", phase="enemy")
        try:
            fn_route_log = getattr(S, "bs_log_turn_contract", None)
            if callable(fn_route_log):
                fn_route_log("battle_enemy_turn_legacy_entry", "2v2", owner="enemy", target="slot", phase="enemy")
        except Exception:
            pass
    jump battle_enemy_turn_legacy_entry


label battle_defensive_turn_2v2_impl:
    python:
        import renpy.store as S
        bs_prepare_2v2_turn_entry(owner="player", phase="def")
        try:
            fn_route_log = getattr(S, "bs_log_turn_contract", None)
            if callable(fn_route_log):
                fn_route_log("battle_defensive_turn_legacy_entry", "2v2", owner="player", target="slot", phase="def")
        except Exception:
            pass
    jump battle_defensive_turn_legacy_entry
