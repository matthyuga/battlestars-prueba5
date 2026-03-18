# ============================================================
# 04D_AI_PLANS_DEFENSE.rpy – Plan defensivo + modos + concat
# v1.1 CLEAN (AI-only logic, HUD lives in HUD_CORE_DEFENSE)
# ------------------------------------------------------------
# Depende de helpers definidos en tu core de AI_PLANS:
# - _ai_level(ai)
# - _has_tech(ai, key)
# - _weighted_choice(weight_map)
# - _get_hp_ratio_damage(incoming_damage, enemy_hp)
# - _safe_set_plan(ai, actions, fallback_candidates)
# - _ai_focus_allowed()
# ============================================================

init -989 python:
    import renpy.store as S

    # --- valores válidos (para blindaje)
    _AI_DEF_TEST_MODES = (
        "normal",
        "stats",
        "force_extra",
        "force_reduct",
        "force_reflect",
        "force_strong",
    )

    def _norm_def_mode(mode):
        if not mode:
            return "normal"
        try:
            mode = str(mode)
        except:
            return "normal"
        return mode if mode in _AI_DEF_TEST_MODES else "normal"

    def _resolve_enemy_unit_key_for_plan():
        fn = getattr(S, "ai_get_current_enemy_unit_key", None)
        if callable(fn):
            try:
                return str(fn() or "")
            except:
                pass
        return str(getattr(S, "current_enemy_unit_key", "") or getattr(S, "current_actor_unit_key", "") or "enemy:0")

    def _effective_defense_mode_for_unit(unit_key):
        fn = getattr(S, "ai_effective_defense_mode", None)
        if callable(fn):
            try:
                return _norm_def_mode(fn(unit_key))
            except:
                pass
        return _norm_def_mode(getattr(S, "ai_defense_test_mode", "normal"))

    def _effective_defense_concat_for_unit(unit_key):
        fn = getattr(S, "ai_effective_defense_concat", None)
        if callable(fn):
            try:
                return bool(fn(unit_key))
            except:
                pass
        return bool(getattr(S, "ai_defense_concat", False))

    def _ensure_ai_def_defaults():
        """
        Defaults SOLO store (no persistent).
        El persistent y los botones viven en HUD_CORE_DEFENSE.
        Esto es para que AI_PLANS no crashee si el HUD no está cargado.
        """
        if not hasattr(S, "ai_defense_test_mode"):
            S.ai_defense_test_mode = "normal"
        else:
            S.ai_defense_test_mode = _norm_def_mode(getattr(S, "ai_defense_test_mode", "normal"))

        if not hasattr(S, "ai_defense_concat"):
            S.ai_defense_concat = False

        if not hasattr(S, "ai_defense_weights") or not isinstance(getattr(S, "ai_defense_weights", None), dict):
            S.ai_defense_weights = {
                "def_extra": 0.34,
                "def_reduct": 0.33,
                "def_reflect": 0.33,
            }
        else:
            w = getattr(S, "ai_defense_weights", {}) or {}
            for k in ("def_extra", "def_reduct", "def_reflect"):
                if k not in w:
                    w[k] = 0.33
            S.ai_defense_weights = w

        # Stats reales de picks (opcional pero útil para debug)
        if not hasattr(S, "ai_defense_stats") or not isinstance(getattr(S, "ai_defense_stats", None), dict):
            S.ai_defense_stats = {
                "def_extra": 0,
                "def_reduct": 0,
                "def_reflect": 0,
                "total": 0,
            }

    def ai_defense_stats_reset():
        _ensure_ai_def_defaults()
        S.ai_defense_stats = {
            "def_extra": 0,
            "def_reduct": 0,
            "def_reflect": 0,
            "total": 0,
        }

    def _ai_def_stats_add(key):
        _ensure_ai_def_defaults()
        try:
            S.ai_defense_stats["total"] = int(S.ai_defense_stats.get("total", 0) or 0) + 1
            if key in S.ai_defense_stats:
                S.ai_defense_stats[key] = int(S.ai_defense_stats.get(key, 0) or 0) + 1
        except:
            pass

    # ------------------------------------------------------------
    # Pick de UNA defensa (normal / stats / force)
    # ------------------------------------------------------------
    def _def_pick_one(ai, ratio, incoming_damage, unit_key=""):

        _ensure_ai_def_defaults()
        mode = _effective_defense_mode_for_unit(unit_key)
        concat = _effective_defense_concat_for_unit(unit_key)
        if mode == "force_extra" and concat:
            mode = "normal"

        # ---- FORCE
        if mode == "force_extra":
            return "def_extra"
        if mode == "force_reduct":
            return "def_reduct"
        if mode == "force_reflect":
            return "def_reflect"
        if mode == "force_strong":
            return "defense_strong_block"

        # ---- STATS (por pesos configurados en HUD_CORE_DEFENSE)
        if mode == "stats":
            w = getattr(S, "ai_defense_weights", {}) or {}
            wm = {
                "def_extra":   float(w.get("def_extra", 0.0)),
                "def_reduct":  float(w.get("def_reduct", 0.0)),
                "def_reflect": float(w.get("def_reflect", 0.0)),
            }

            # dataset-aware (si falta una tech, peso 0)
            for k in list(wm.keys()):
                try:
                    if not _has_tech(ai, k):
                        wm[k] = 0.0
                except:
                    pass

            pick = None
            try:
                pick = _weighted_choice(wm)
            except:
                pick = None

            pick = pick or "def_extra"
            _ai_def_stats_add(pick)
            return pick

        # ---- NORMAL (tu lógica por %HP, pero devolviendo UNA sola)
        level = None
        try:
            level = _ai_level(ai)
        except:
            level = "basic"

        if level == "basic":
            T1 = 0.12
            return "def_reduct" if ratio >= T1 else "def_extra"

        if level == "intermediate":
            T1 = 0.08
            T2 = 0.15
            T3 = 0.22
            if ratio < T1:
                return "def_extra"
            elif ratio < T2:
                return "def_reduct"
            elif ratio < T3:
                return "def_reduct"
            else:
                return "def_reflect"

        if level == "advanced":
            T1 = 0.06
            T2 = 0.12
            T3 = 0.18
            T4 = 0.26
            if ratio < T1:
                return "def_extra"
            elif ratio < T2:
                return "def_reduct"
            elif ratio < T3:
                return "def_reduct"
            elif ratio < T4:
                return "def_reflect"
            else:
                return "def_reflect"

        return "def_extra"

    def _def_should_focus(ai, ratio, incoming_damage, unit_key=""):

        # Focus defensivo es opcional, y se corta si el toggle está OFF.
        try:
            if not _ai_focus_allowed(unit_key):
                return False
        except:
            pass

        level = None
        try:
            level = _ai_level(ai)
        except:
            level = "basic"

        if level == "basic":
            return False
        if level == "intermediate":
            return (ratio >= 0.15)
        if level == "advanced":
            return (ratio >= 0.12)
        return False

    # ============================================================
    # PLAN DEFENSIVO (1 defensa, salvo concat ON)
    # ============================================================
    def ai_plan_defensive(ai, incoming_damage=None):
        _ensure_ai_def_defaults()

        if incoming_damage is None:
            incoming_damage = getattr(S, "incoming_damage", 0) or 0

        enemy_hp = getattr(S, "enemy_hp", 0) or 0

        try:
            ratio = _get_hp_ratio_damage(incoming_damage, enemy_hp)
        except:
            ratio = 0.0

        unit_key = _resolve_enemy_unit_key_for_plan()
        mode = _effective_defense_mode_for_unit(unit_key)
        forced_mode = str(mode or "").startswith("force_")

        concat = _effective_defense_concat_for_unit(unit_key)
        picked = _def_pick_one(ai, ratio, incoming_damage, unit_key=unit_key)

        plan = []

        if _def_should_focus(ai, ratio, incoming_damage, unit_key=unit_key):
            # (doble check por seguridad)
            try:
                if _ai_focus_allowed(unit_key):
                    plan.append("focus")
            except:
                pass

        # regla: por defecto 1 defensa; con concat: def_extra + picked
        if concat:
            plan.append("def_extra")
            if picked != "def_extra":
                plan.append(picked)
        else:
            plan.append(picked)

        try:
            plan = ai_filter_blocked_plan(plan, unit_key, forced=forced_mode, phase="defense")
        except:
            pass

        _safe_set_plan(
            ai,
            plan,
            fallback_candidates=["def_extra", "def_reduct", "def_reflect", "defense_strong_block"]
        )
