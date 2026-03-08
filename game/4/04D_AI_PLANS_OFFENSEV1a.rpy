# ============================================================
# 04D_AI_PLANS_OFFENSE.rpy – Plan ofensivo (AI-only)
# v1.1 CLEAN
# ------------------------------------------------------------
# HUD / modos / pesos viven en:
#   04A_AI_DIFFICULTY_HUD_CORE_BASE.rpy
#
# Este módulo SOLO:
# - decide el finisher
# - arma el plan
# - lleva stats reales (opcional)
#
# Depende de helpers globales:
# - _ai_level(ai)
# - _has_tech(ai, tech_id)
# - _pick_from_candidates(ai, list, weights)
# - _safe_set_plan(ai, actions, fallback_candidates)
# - _ai_focus_allowed()
# ============================================================

init -989 python:
    import renpy.store as S

    _AI_FIN_TEST_MODES = (
        "normal",
        "stats",
        "force_reducer",
        "force_stronger",
        "force_direct",
        "force_noatk",
    )

    _AI_OFFENSE_CONCAT_MODES = (
        "off",
        "level1_attack",
        "level1_tech",
        "level2_full",
    )

    def _norm_finisher_mode(mode):
        if not mode:
            return "normal"
        try:
            mode = str(mode)
        except:
            return "normal"
        return mode if mode in _AI_FIN_TEST_MODES else "normal"

    def _norm_offense_concat_mode(mode):
        if not mode:
            return "level2_full"
        try:
            mode = str(mode)
        except:
            return "level2_full"
        return mode if mode in _AI_OFFENSE_CONCAT_MODES else "level2_full"

    def _resolve_enemy_unit_key_for_plan():
        fn = getattr(S, "ai_get_current_enemy_unit_key", None)
        if callable(fn):
            try:
                return str(fn() or "")
            except:
                pass
        return str(getattr(S, "current_enemy_unit_key", "") or getattr(S, "current_actor_unit_key", "") or "enemy:0")

    def _effective_finisher_mode_for_unit(unit_key):
        fn = getattr(S, "ai_effective_offense_mode", None)
        if callable(fn):
            try:
                return _norm_finisher_mode(fn(unit_key))
            except:
                pass
        return _norm_finisher_mode(getattr(S, "ai_finisher_test_mode", "normal"))

    def _effective_offense_concat_for_unit(unit_key):
        fn = getattr(S, "ai_effective_offense_concat", None)
        if callable(fn):
            try:
                return _norm_offense_concat_mode(fn(unit_key))
            except:
                pass
        return _norm_offense_concat_mode(getattr(S, "ai_offense_concat_mode", "level2_full"))

    # ------------------------------------------------------------
    # Defaults SOLO store (HUD se encarga del persistent)
    # ------------------------------------------------------------
    def _ensure_ai_fin_defaults():
        if not hasattr(S, "ai_finisher_test_mode"):
            S.ai_finisher_test_mode = "normal"
        else:
            S.ai_finisher_test_mode = _norm_finisher_mode(getattr(S, "ai_finisher_test_mode", "normal"))

        if not hasattr(S, "ai_offense_concat_mode"):
            S.ai_offense_concat_mode = "level2_full"
        else:
            S.ai_offense_concat_mode = _norm_offense_concat_mode(getattr(S, "ai_offense_concat_mode", "level2_full"))

        if not hasattr(S, "ai_finisher_weights") or not isinstance(getattr(S, "ai_finisher_weights", None), dict):
            S.ai_finisher_weights = {
                "attack_reducer": 0.25,
                "stronger_attack": 0.25,
                "direct_attack": 0.25,
                "noatk_attack": 0.25,
            }
        else:
            w = getattr(S, "ai_finisher_weights", {}) or {}
            for k in ("attack_reducer", "stronger_attack", "direct_attack", "noatk_attack"):
                if k not in w:
                    w[k] = 0.25
            S.ai_finisher_weights = w

        # Stats reales (solo para debug / HUD)
        if not hasattr(S, "ai_finisher_stats") or not isinstance(getattr(S, "ai_finisher_stats", None), dict):
            S.ai_finisher_stats = {
                "attack_reducer": 0,
                "stronger_attack": 0,
                "direct_attack": 0,
                "noatk_attack": 0,
                "total": 0,
            }

    def ai_finisher_stats_reset():
        _ensure_ai_fin_defaults()
        S.ai_finisher_stats = {
            "attack_reducer": 0,
            "stronger_attack": 0,
            "direct_attack": 0,
            "noatk_attack": 0,
            "total": 0,
        }

    def _ai_finisher_stats_add(key):
        _ensure_ai_fin_defaults()
        try:
            S.ai_finisher_stats["total"] = int(S.ai_finisher_stats.get("total", 0) or 0) + 1
            if key in S.ai_finisher_stats:
                S.ai_finisher_stats[key] = int(S.ai_finisher_stats.get(key, 0) or 0) + 1
        except:
            pass

    # ============================================================
    # PICK DE FINISHER (normal / stats / force)
    # ============================================================
    def _pick_finisher(ai):
        _ensure_ai_fin_defaults()
        unit_key = _resolve_enemy_unit_key_for_plan()
        mode = _effective_finisher_mode_for_unit(unit_key)

        # ---- FORCE
        if mode == "force_reducer":
            return "attack_reducer"
        if mode == "force_stronger":
            return "stronger_attack"
        if mode == "force_direct":
            return "direct_attack"
        if mode == "force_noatk":
            return "noatk_attack"

        finishers = [
            "attack_reducer",
            "stronger_attack",
            "direct_attack",
            "noatk_attack",
        ]

        base_weights = {
            "attack_reducer": 0.25,
            "stronger_attack": 0.25,
            "direct_attack": 0.25,
            "noatk_attack": 0.25,
        }

        weights = getattr(S, "ai_finisher_weights", {}) or base_weights
        if mode != "stats":
            weights = base_weights

        # --- Burst rule: si ya usó stronger_attack, forzamos variar
        if getattr(S, "ai_used_strong_attack", False):
            S.ai_used_strong_attack = False

            if _has_tech(ai, "attack_reducer"):
                return "attack_reducer"

            alt = ["direct_attack", "noatk_attack", "stronger_attack"]
            fin = _pick_from_candidates(ai, alt, weights)
            return fin or "stronger_attack"

        fin = _pick_from_candidates(ai, finishers, weights)
        return fin or "attack_reducer"

    # ============================================================
    # PLAN OFENSIVO
    # ============================================================
    def ai_plan_offensive(ai):
        _ensure_ai_fin_defaults()

        fin = _pick_finisher(ai)

        unit_key = _resolve_enemy_unit_key_for_plan()
        if _effective_finisher_mode_for_unit(unit_key) == "stats":
            _ai_finisher_stats_add(fin)

        concat_mode = _effective_offense_concat_for_unit(unit_key)
        plan = []

        if concat_mode == "level1_attack":
            plan.append("extra_attack")
        elif concat_mode == "level1_tech":
            plan.append("extra_tech")
        elif concat_mode == "level2_full":
            plan.append("extra_attack")
            plan.append("extra_tech")

        try:
            if _ai_focus_allowed(unit_key):
                plan.append("focus")
        except:
            pass

        plan.append(fin)

        _safe_set_plan(
            ai,
            plan,
            fallback_candidates=[
                "extra_attack",
                "extra_tech",
                "attack_reducer",
                "stronger_attack",
            ]
        )
