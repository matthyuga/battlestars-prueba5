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
                return str(getattr(S, "ai_finisher_test_mode", "normal") or "normal")
            except:
                return "normal"
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
