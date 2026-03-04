# ============================================================
# battle_incoming_ctx_2v2.rpy — SSOT incoming context for 2v2
# ============================================================
# T8: aislar estado de daño entrante para 2v2 y evitar
# contaminación entre ataques consecutivos / unidades.
# ============================================================

default bs_incoming_ctx_2v2 = {
    "target_key": "",
    "source_key": "",
    "owner_team": "player",
    "owner_slot": 0,
    "phase": "",
}

init -947 python:
    def bs_get_incoming_ctx_2v2():
        try:
            import renpy.store as S
            ctx = getattr(S, "bs_incoming_ctx_2v2", None)
            return dict(ctx) if isinstance(ctx, dict) else {
                "target_key": "",
                "source_key": "",
                "owner_team": "player",
                "owner_slot": 0,
                "phase": "",
            }
        except Exception:
            return {
                "target_key": "",
                "source_key": "",
                "owner_team": "player",
                "owner_slot": 0,
                "phase": "",
            }

    def bs_set_incoming_ctx_2v2(target_key="", source_key="", owner_team="player", owner_slot=0, phase=""):
        try:
            import renpy.store as S
            tkey = str(target_key or "")
            skey = str(source_key or "")
            team = str(owner_team or "player")
            slot = int(owner_slot or 0)
            ph = str(phase or "")

            S.bs_incoming_ctx_2v2 = {
                "target_key": tkey,
                "source_key": skey,
                "owner_team": team,
                "owner_slot": slot,
                "phase": ph,
            }

            # espejos legacy usados por core actual
            S.incoming_damage_target_key = tkey
            S.incoming_damage_source_key = skey
            if skey:
                S.incoming_damage_sources = [skey]
            elif not isinstance(getattr(S, "incoming_damage_sources", None), list):
                S.incoming_damage_sources = []
        except Exception:
            pass

    def bs_clear_incoming_ctx_2v2(clear_plan=False):
        try:
            import renpy.store as S
            S.bs_incoming_ctx_2v2 = {
                "target_key": "",
                "source_key": "",
                "owner_team": "player",
                "owner_slot": 0,
                "phase": "",
            }
            S.incoming_damage_target_key = ""
            S.incoming_damage_source_key = ""
            S.incoming_damage_sources = []
            if hasattr(S, "defense_target_key"):
                S.defense_target_key = ""
            if clear_plan:
                S.enemy_damage_plan = None
        except Exception:
            pass

    # Compat alias usado por capas anteriores (1v1 entry, etc.)
    def bs_clear_incoming_ctx(clear_plan=False):
        return bs_clear_incoming_ctx_2v2(clear_plan=clear_plan)
