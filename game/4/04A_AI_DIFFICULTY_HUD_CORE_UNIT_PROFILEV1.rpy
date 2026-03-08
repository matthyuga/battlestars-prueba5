# ============================================================
# 04A_AI_DIFFICULTY_HUD_CORE_UNIT_PROFILEV1.rpy
# Perfil IA por unidad (Fase A) + targeting forzado (Fase B)
# ------------------------------------------------------------
# - SSOT de perfiles por unit_key enemigo (enemy:0, enemy:1, ...)
# - Compat total: si no hay perfil, usa configuración global actual
# - Hook de targeting: force_slot -> player slot específico
# ============================================================

default ai_unit_profile_version = 1
default ai_unit_profiles = {}
default ai_ui_selected_enemy_slot = 0

init -18 python:
    import renpy.store as S

    _AI_UNIT_PROFILE_VERSION = 1
    _AI_TARGET_MODES = ("auto", "force_slot")
    _AI_OFFENSE_MODES = (
        "inherit",
        "normal",
        "stats",
        "force_reducer",
        "force_stronger",
        "force_direct",
        "force_noatk",
        "force_extra_attack",
        "force_extra_tech",
    )
    _AI_DEFENSE_MODES = (
        "inherit",
        "normal",
        "stats",
        "force_extra",
        "force_reduct",
        "force_reflect",
    )

    def ai_unit_profile_default():
        return {
            "enabled": True,
            "target_mode": "auto",
            "target_slot": 0,
            "offense_mode": "inherit",
            "offense_concat": "inherit",
            "defense_mode": "inherit",
            "defense_concat": "inherit",
            "allow_focus": "inherit",
        }

    def _ai_unit_profile_norm_bool_or_inherit(v):
        if v == "inherit":
            return "inherit"
        try:
            return bool(v)
        except:
            return "inherit"

    def _ai_unit_profile_norm_mode(v, valid, default_value):
        try:
            s = str(v or default_value)
        except:
            s = str(default_value)
        return s if s in valid else str(default_value)

    def _ai_unit_profile_norm_offense_concat(v):
        if v == "inherit":
            return "inherit"
        try:
            s = str(v)
        except:
            return "inherit"
        if s in ("off", "level1_attack", "level1_tech", "level2_full"):
            return s
        return "inherit"

    def _ai_unit_profile_sanitize(raw):
        base = ai_unit_profile_default()
        p = dict(base)

        if isinstance(raw, dict):
            p.update(raw)

        try:
            p["enabled"] = bool(p.get("enabled", True))
        except:
            p["enabled"] = True

        p["target_mode"] = _ai_unit_profile_norm_mode(
            p.get("target_mode", "auto"),
            _AI_TARGET_MODES,
            "auto"
        )

        try:
            p["target_slot"] = max(0, int(p.get("target_slot", 0) or 0))
        except:
            p["target_slot"] = 0

        p["offense_mode"] = _ai_unit_profile_norm_mode(
            p.get("offense_mode", "inherit"),
            _AI_OFFENSE_MODES,
            "inherit"
        )

        p["offense_concat"] = _ai_unit_profile_norm_offense_concat(
            p.get("offense_concat", "inherit")
        )

        p["defense_mode"] = _ai_unit_profile_norm_mode(
            p.get("defense_mode", "inherit"),
            _AI_DEFENSE_MODES,
            "inherit"
        )

        p["defense_concat"] = _ai_unit_profile_norm_bool_or_inherit(
            p.get("defense_concat", "inherit")
        )
        p["allow_focus"] = _ai_unit_profile_norm_bool_or_inherit(
            p.get("allow_focus", "inherit")
        )

        return p

    def _ai_unit_profile_clone_map(mp):
        out = {}
        if not isinstance(mp, dict):
            return out
        for k, v in mp.items():
            key = str(k or "")
            if not key:
                continue
            out[key] = _ai_unit_profile_sanitize(v)
        return out

    def ai_unit_profiles_ensure_defaults():
        if not hasattr(S, "ai_unit_profile_version"):
            S.ai_unit_profile_version = int(_AI_UNIT_PROFILE_VERSION)
        else:
            try:
                S.ai_unit_profile_version = int(getattr(S, "ai_unit_profile_version", _AI_UNIT_PROFILE_VERSION) or _AI_UNIT_PROFILE_VERSION)
            except:
                S.ai_unit_profile_version = int(_AI_UNIT_PROFILE_VERSION)

        cur = getattr(S, "ai_unit_profiles", None)
        S.ai_unit_profiles = _ai_unit_profile_clone_map(cur)

    def ai_unit_profile_get(unit_key, create=True):
        ai_unit_profiles_ensure_defaults()
        key = str(unit_key or "")
        if not key:
            return ai_unit_profile_default()

        profiles = getattr(S, "ai_unit_profiles", None)
        if not isinstance(profiles, dict):
            profiles = {}
            S.ai_unit_profiles = profiles

        if key not in profiles:
            if create:
                profiles[key] = ai_unit_profile_default()
            else:
                return ai_unit_profile_default()

        prof = _ai_unit_profile_sanitize(profiles.get(key, {}))
        profiles[key] = dict(prof)
        return dict(prof)

    def ai_unit_profile_set(unit_key, patch_dict):
        ai_unit_profiles_ensure_defaults()
        key = str(unit_key or "")
        if not key:
            return

        cur = ai_unit_profile_get(key, create=True)
        if isinstance(patch_dict, dict):
            cur.update(patch_dict)

        cur = _ai_unit_profile_sanitize(cur)
        S.ai_unit_profiles[key] = dict(cur)
        ai_unit_profile_save_if_needed()

    def ai_unit_profile_reset(unit_key=None):
        ai_unit_profiles_ensure_defaults()
        if unit_key is None:
            S.ai_unit_profiles = {}
        else:
            key = str(unit_key or "")
            if key and isinstance(getattr(S, "ai_unit_profiles", None), dict) and key in S.ai_unit_profiles:
                del S.ai_unit_profiles[key]
        ai_unit_profile_save_if_needed()

    def ai_unit_profile_sync_from_persistent_if_needed():
        ai_unit_profiles_ensure_defaults()
        if not bool(getattr(S, "ai_difficulty_save", False)):
            return

        try:
            p = getattr(S, "persistent", None)
            pv = getattr(p, "ai_unit_profiles", None)
            S.ai_unit_profiles = _ai_unit_profile_clone_map(pv)

            pver = getattr(p, "ai_unit_profile_version", _AI_UNIT_PROFILE_VERSION)
            try:
                S.ai_unit_profile_version = int(pver or _AI_UNIT_PROFILE_VERSION)
            except:
                S.ai_unit_profile_version = int(_AI_UNIT_PROFILE_VERSION)
        except:
            pass

    def ai_unit_profile_save_if_needed():
        ai_unit_profiles_ensure_defaults()
        if not bool(getattr(S, "ai_difficulty_save", False)):
            return

        try:
            p = getattr(S, "persistent", None)
            p.ai_unit_profiles = _ai_unit_profile_clone_map(getattr(S, "ai_unit_profiles", {}))
            p.ai_unit_profile_version = int(getattr(S, "ai_unit_profile_version", _AI_UNIT_PROFILE_VERSION) or _AI_UNIT_PROFILE_VERSION)
        except:
            pass

    def ai_effective_allow_focus(unit_key):
        prof = ai_unit_profile_get(unit_key, create=False)
        pv = prof.get("allow_focus", "inherit") if isinstance(prof, dict) else "inherit"
        if pv == "inherit":
            return bool(getattr(S, "ai_allow_focus", True))
        return bool(pv)

    def ai_effective_defense_concat(unit_key):
        prof = ai_unit_profile_get(unit_key, create=False)
        pv = prof.get("defense_concat", "inherit") if isinstance(prof, dict) else "inherit"
        if pv == "inherit":
            return bool(getattr(S, "ai_defense_concat", False))
        return bool(pv)

    def ai_effective_offense_mode(unit_key):
        prof = ai_unit_profile_get(unit_key, create=False)
        mode = str(prof.get("offense_mode", "inherit") or "inherit") if isinstance(prof, dict) else "inherit"
        if mode == "inherit":
            try:
                mode = str(getattr(S, "ai_finisher_test_mode", "normal") or "normal")
            except:
                mode = "normal"
        if mode in ("force_extra_attack", "force_extra_tech"):
            try:
                if str(ai_effective_offense_concat(unit_key) or "level2_full") != "off":
                    return "normal"
            except:
                return "normal"
        return mode

    def ai_effective_offense_concat(unit_key):
        prof = ai_unit_profile_get(unit_key, create=False)
        mode = str(prof.get("offense_concat", "inherit") or "inherit") if isinstance(prof, dict) else "inherit"
        if mode == "inherit":
            try:
                return str(getattr(S, "ai_offense_concat_mode", "level2_full") or "level2_full")
            except:
                return "level2_full"
        return mode

    def ai_effective_defense_mode(unit_key):
        prof = ai_unit_profile_get(unit_key, create=False)
        mode = str(prof.get("defense_mode", "inherit") or "inherit") if isinstance(prof, dict) else "inherit"
        if mode == "inherit":
            try:
                return str(getattr(S, "ai_defense_test_mode", "normal") or "normal")
            except:
                return "normal"
        return mode

    def ai_effective_target_rule(unit_key):
        prof = ai_unit_profile_get(unit_key, create=False)
        if not isinstance(prof, dict):
            return {"mode": "auto", "slot": 0}
        if not bool(prof.get("enabled", True)):
            return {"mode": "auto", "slot": 0}
        return {
            "mode": str(prof.get("target_mode", "auto") or "auto"),
            "slot": max(0, int(prof.get("target_slot", 0) or 0)),
        }

    def ai_resolve_forced_target_key(enemy_unit_key, valid_player_keys):
        """
        Devuelve target_key forzado si aplica y está vivo/valido.
        Si no aplica, devuelve "" para que el caller use heurística auto.
        """
        try:
            valid = list(valid_player_keys or [])
        except:
            valid = []

        if not valid:
            return ""

        rule = ai_effective_target_rule(enemy_unit_key)
        mode = str(rule.get("mode", "auto") or "auto")
        if mode != "force_slot":
            return ""

        try:
            slot = max(0, int(rule.get("slot", 0) or 0))
        except:
            slot = 0

        fn_key = getattr(S, "bs_unit_key", None)
        if callable(fn_key):
            try:
                target = str(fn_key("player", slot) or "")
            except:
                target = ""
        else:
            target = "player:{}".format(slot)

        if target and target in valid:
            return target
        return ""


    def ai_get_current_enemy_unit_key():
        """Best-effort key de unidad enemy activa en contexto actual."""
        key = ""
        try:
            key = str(getattr(S, "current_actor_unit_key", "") or "")
            if key and str(key).startswith("enemy:"):
                return key
        except:
            key = ""

        try:
            key = str(getattr(S, "current_enemy_unit_key", "") or "")
            if key:
                return key
        except:
            key = ""

        fn_ctx = getattr(S, "bs_get_turn_ctx", None)
        fn_key = getattr(S, "bs_unit_key", None)
        if callable(fn_ctx) and callable(fn_key):
            try:
                ctx = fn_ctx() or {}
                team = str(ctx.get("owner_team", "enemy") or "enemy")
                slot = int(ctx.get("owner_slot", 0) or 0)
                if team == "enemy":
                    return str(fn_key("enemy", slot) or "")
            except:
                pass

        if callable(fn_key):
            try:
                return str(fn_key("enemy", 0) or "")
            except:
                return ""

        return "enemy:0"

    def _ai_ui_enemy_slot_count():
        try:
            mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        except:
            mode = "1v1"
        if mode != "2v2":
            return 1
        try:
            ids = list(getattr(S, "battle_enemy_ids", []) or [])
            return max(1, min(2, len(ids) if ids else 2))
        except:
            return 2

    def _ai_ui_player_slot_count():
        try:
            mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        except:
            mode = "1v1"
        if mode != "2v2":
            return 1
        try:
            ids = list(getattr(S, "battle_player_ids", []) or [])
            return max(1, min(2, len(ids) if ids else 2))
        except:
            return 2

    def ai_ui_get_selected_enemy_unit_key():
        cnt = _ai_ui_enemy_slot_count()
        try:
            slot = int(getattr(S, "ai_ui_selected_enemy_slot", 0) or 0)
        except:
            slot = 0
        slot = max(0, min(cnt - 1, slot))
        S.ai_ui_selected_enemy_slot = slot

        fn_key = getattr(S, "bs_unit_key", None)
        if callable(fn_key):
            try:
                return str(fn_key("enemy", slot) or "")
            except:
                pass
        return "enemy:{}".format(slot)

    def ai_ui_cycle_enemy_slot():
        cnt = _ai_ui_enemy_slot_count()
        try:
            cur = int(getattr(S, "ai_ui_selected_enemy_slot", 0) or 0)
        except:
            cur = 0
        S.ai_ui_selected_enemy_slot = (cur + 1) % max(1, cnt)
        try:
            import renpy.exports as R
            R.restart_interaction()
        except:
            pass

    def ai_ui_enemy_slot_text():
        key = ai_ui_get_selected_enemy_unit_key()
        try:
            fn_desc = getattr(S, "bs_describe_unit_key", None)
            if callable(fn_desc):
                lbl = str(fn_desc(key, default_side="enemy", default_slot=0) or key)
            else:
                lbl = key
        except:
            lbl = key
        return "👥 Perfil IA: {}".format(lbl)

    def ai_ui_cycle_target_rule():
        key = ai_ui_get_selected_enemy_unit_key()
        prof = ai_unit_profile_get(key, create=True)

        slots = list(range(_ai_ui_player_slot_count()))
        seq = [("auto", 0)] + [("force_slot", s) for s in slots]

        cur = (str(prof.get("target_mode", "auto") or "auto"), int(prof.get("target_slot", 0) or 0))
        idx = 0
        for i, e in enumerate(seq):
            if e == cur:
                idx = i
                break
        nxt = seq[(idx + 1) % len(seq)]
        ai_unit_profile_set(key, {"target_mode": nxt[0], "target_slot": int(nxt[1])})

        try:
            import renpy.exports as R
            R.restart_interaction()
        except:
            pass

    def ai_ui_target_rule_text():
        key = ai_ui_get_selected_enemy_unit_key()
        prof = ai_unit_profile_get(key, create=False)
        mode = str(prof.get("target_mode", "auto") or "auto") if isinstance(prof, dict) else "auto"
        slot = int(prof.get("target_slot", 0) or 0) if isinstance(prof, dict) else 0
        if mode == "force_slot":
            return "🎯 Target: Forzar P{}".format(slot + 1)
        return "🎯 Target: Auto"

    def _ai_ui_offense_force_extra_locked_for_unit(unit_key):
        try:
            fn = getattr(S, "ai_effective_offense_concat", None)
            if callable(fn):
                return str(fn(unit_key) or "level2_full") != "off"
        except:
            pass
        return True

    def ai_ui_cycle_offense_mode():
        key = ai_ui_get_selected_enemy_unit_key()
        prof = ai_unit_profile_get(key, create=True)
        seq = list(_AI_OFFENSE_MODES)
        if _ai_ui_offense_force_extra_locked_for_unit(key):
            seq = [m for m in seq if m not in ("force_extra_attack", "force_extra_tech")]
        cur = str(prof.get("offense_mode", "inherit") or "inherit")
        try:
            i = seq.index(cur)
        except:
            i = 0
        ai_unit_profile_set(key, {"offense_mode": seq[(i + 1) % len(seq)]})
        try:
            import renpy.exports as R
            R.restart_interaction()
        except:
            pass

    def ai_ui_offense_mode_text():
        key = ai_ui_get_selected_enemy_unit_key()
        prof = ai_unit_profile_get(key, create=False)
        m = str(prof.get("offense_mode", "inherit") or "inherit") if isinstance(prof, dict) else "inherit"
        if m in ("force_extra_attack", "force_extra_tech") and _ai_ui_offense_force_extra_locked_for_unit(key):
            m = "normal"
        return "⚔️ Ofensiva (unidad): {}".format(m)

    def ai_ui_cycle_offense_concat_rule():
        key = ai_ui_get_selected_enemy_unit_key()
        prof = ai_unit_profile_get(key, create=True)
        cur = str(prof.get("offense_concat", "inherit") or "inherit")
        seq = ["inherit", "off", "level1_attack", "level1_tech", "level2_full"]
        try:
            i = seq.index(cur)
        except:
            i = 0
        ai_unit_profile_set(key, {"offense_concat": seq[(i + 1) % len(seq)]})
        try:
            import renpy.exports as R
            R.restart_interaction()
        except:
            pass

    def ai_ui_offense_concat_rule_text():
        key = ai_ui_get_selected_enemy_unit_key()
        prof = ai_unit_profile_get(key, create=False)
        cur = str(prof.get("offense_concat", "inherit") or "inherit") if isinstance(prof, dict) else "inherit"
        if cur == "inherit":
            return "⚔️ Concat (unidad): Heredar"
        if cur == "off":
            return "⚔️ Concat (unidad): OFF"
        if cur == "level1_attack":
            return "⚔️ Concat (unidad): L1-A (ExtraAtk)"
        if cur == "level1_tech":
            return "⚔️ Concat (unidad): L1-B (ExtraTech)"
        return "⚔️ Concat (unidad): L2 (Atk+Tech)"

    def ai_ui_cycle_defense_mode():
        key = ai_ui_get_selected_enemy_unit_key()
        prof = ai_unit_profile_get(key, create=True)
        seq = list(_AI_DEFENSE_MODES)
        cur = str(prof.get("defense_mode", "inherit") or "inherit")
        try:
            i = seq.index(cur)
        except:
            i = 0
        ai_unit_profile_set(key, {"defense_mode": seq[(i + 1) % len(seq)]})
        try:
            import renpy.exports as R
            R.restart_interaction()
        except:
            pass

    def ai_ui_defense_mode_text():
        key = ai_ui_get_selected_enemy_unit_key()
        prof = ai_unit_profile_get(key, create=False)
        m = str(prof.get("defense_mode", "inherit") or "inherit") if isinstance(prof, dict) else "inherit"
        return "🛡️ Defensa (unidad): {}".format(m)

    def ai_ui_cycle_concat_rule():
        key = ai_ui_get_selected_enemy_unit_key()
        prof = ai_unit_profile_get(key, create=True)
        cur = prof.get("defense_concat", "inherit")
        seq = ["inherit", True, False]
        try:
            i = seq.index(cur)
        except:
            i = 0
        ai_unit_profile_set(key, {"defense_concat": seq[(i + 1) % len(seq)]})
        try:
            import renpy.exports as R
            R.restart_interaction()
        except:
            pass

    def ai_ui_concat_rule_text():
        key = ai_ui_get_selected_enemy_unit_key()
        prof = ai_unit_profile_get(key, create=False)
        cur = prof.get("defense_concat", "inherit") if isinstance(prof, dict) else "inherit"
        if cur == "inherit":
            return "🔗 Concat (unidad): Heredar"
        return "🔗 Concat (unidad): {}".format("ON" if bool(cur) else "OFF")

    def ai_ui_cycle_focus_rule():
        key = ai_ui_get_selected_enemy_unit_key()
        prof = ai_unit_profile_get(key, create=True)
        cur = prof.get("allow_focus", "inherit")
        seq = ["inherit", True, False]
        try:
            i = seq.index(cur)
        except:
            i = 0
        ai_unit_profile_set(key, {"allow_focus": seq[(i + 1) % len(seq)]})
        try:
            import renpy.exports as R
            R.restart_interaction()
        except:
            pass

    def ai_ui_focus_rule_text():
        key = ai_ui_get_selected_enemy_unit_key()
        prof = ai_unit_profile_get(key, create=False)
        cur = prof.get("allow_focus", "inherit") if isinstance(prof, dict) else "inherit"
        if cur == "inherit":
            return "🧿 Focus (unidad): Heredar"
        return "🧿 Focus (unidad): {}".format("ON" if bool(cur) else "OFF")
