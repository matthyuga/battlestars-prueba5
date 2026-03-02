# ============================================================
# 04D_AI_REACTIVE_DEFENSE.rpy – Orchestrator (Thin Wrapper)
# v12.4 – Delegates to CORE + ENGINE ✅
# ------------------------------------------------------------
# - UI / identity / plan
# - llama a S.ai_defense_execute_plan(...)
# ============================================================

init -986 python:

    def enemy_compute_reactive_defense(total_damage):

        import renpy.store as S

        enemy = getattr(S, "enemy_ai", None)
        name  = getattr(enemy, "name", "ENEMY")

        team_mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        slot_txt = ""
        cur_key = str(getattr(S, "current_enemy_unit_key", "") or "")
        try:
            if team_mode == "2v2" and cur_key and callable(getattr(S, "bs_parse_unit_key", None)):
                info = S.bs_parse_unit_key(cur_key, default_side="enemy", default_slot=0)
                if str(info.get("team", "enemy") or "enemy") == "enemy":
                    slot_i = int(info.get("slot", 0) or 0)
                    if callable(getattr(S, "bs_slot_tag", None)):
                        slot_txt = " ({})".format(S.bs_slot_tag("enemy", slot_i))
                    else:
                        slot_txt = " (E{})".format(slot_i + 1)
                    if callable(getattr(S, "bs_get_unit_by_key", None)):
                        uu = S.bs_get_unit_by_key(cur_key)
                        if isinstance(uu, dict):
                            name = str(uu.get("char_id", name) or name)
        except:
            pass

        dmg_effective = int(total_damage or 0)

        # si no hay daño -> limpia debuff y fin
        if dmg_effective <= 0:
            try:
                if hasattr(S, "next_defense_reduction") and (S.next_defense_reduction or 0) > 0:
                    S.next_defense_reduction = 0.0
            except:
                pass
            return {"final_damage": 0, "reflected": 0}

        # Palette border (store-safe)
        PAL = getattr(S, "PALETTE", {}) or {}
        try:
            border = PAL.get("white", "#FFFFFF")
        except:
            border = "#FFFFFF"

        # identity reflect
        try:
            S.current_enemy_id = S.BATTLE_IDENTITIES.get(name, "ID_ENEMY_UNKNOWN")
        except:
            S.current_enemy_id = "ID_ENEMY_UNKNOWN"

        # UI
        try:
            if hasattr(S, "operation_clear"):
                S.operation_clear()
        except:
            pass
        try:
            if hasattr(S, "battle_log_phase"):
                S.battle_log_phase("TURNO DEFENSIVO{} – {}".format(slot_txt, name))
        except:
            pass
        try:
            if hasattr(S, "battle_popup_turn"):
                S.battle_popup_turn("Turno defensivo{} — {}".format(slot_txt, name), "#00FFFF", delay=0.6)
        except:
            pass
        try:
            import renpy
            renpy.pause(0.35, hard=True)
        except:
            pass

        # plan (del CORE)
        try:
            plan = S.ai_defense_build_plan(dmg_effective)
        except:
            plan = ["def_extra"]

        # decorativo/compat
        try:
            enemy.current_plan = list(plan)
            enemy.focus_active = False
        except:
            pass

        # ejecutar (ENGINE)
        fn = getattr(S, "ai_defense_execute_plan", None)
        if callable(fn):
            try:
                return fn(plan, dmg_effective, name, border)
            except:
                pass

        # fallback extremo (no rompe)
        return {"final_damage": dmg_effective, "reflected": 0}


# ✅ Export al store (para wrappers legacy)
init -985 python:
    try:
        import renpy.store as S
        S.enemy_compute_reactive_defense = enemy_compute_reactive_defense
    except:
        pass
