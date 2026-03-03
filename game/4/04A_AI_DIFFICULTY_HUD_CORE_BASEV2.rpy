# ============================================================
# 04A_AI_DIFFICULTY_HUD_CORE_BASE.rpy – Core HUD AI (BASE)
# v1.6.1 BASE (BLINDED + OFFENSE ONLY) ✅ PATCHED
# ------------------------------------------------------------
# Contiene:
# - dificultad IA
# - guardar ON/OFF
# - focus toggle
# - ofensiva (finisher modes + pesos 25/50/75/100)
# - sync store / persistent
#
# Parches:
# - ✅ BLINDED: persistent.ai_finisher_weights siempre dict
# - ✅ Sync: cuando Guardar OFF, normaliza store (modo/focus/pesos)
# ============================================================

init -21 python:
    import renpy.store as S
    import renpy.exports as R

    AI_LEVELS = ["basic", "intermediate", "advanced"]

    AI_FIN_TEST_MODES = [
        "normal",
        "stats",
        "force_reducer",
        "force_stronger",
        "force_direct",
        "force_noatk",
    ]

    # ------------------------------------------------------------
    # Helpers: normalize (BLINDED)
    # ------------------------------------------------------------
    def _norm_ai_level(lvl):
        try:
            if lvl in AI_LEVELS:
                return lvl
        except:
            pass
        return "basic"

    def _norm_finisher_mode(mode):
        if not mode:
            return "normal"
        try:
            s = str(mode)
        except:
            return "normal"
        if s not in AI_FIN_TEST_MODES:
            return "normal"
        return s

    def _norm_bool(v, default=False):
        try:
            return bool(v)
        except:
            return default

    # ------------------------------------------------------------
    # Helpers: persistent dict-safe
    # ------------------------------------------------------------
    def _ensure_persistent_finisher_weights_dict():
        try:
            p = S.persistent
            if (not hasattr(p, "ai_finisher_weights")) or (not isinstance(getattr(p, "ai_finisher_weights", None), dict)):
                p.ai_finisher_weights = {}
        except:
            pass

    # ------------------------------------------------------------
    # Defaults STORE
    # ------------------------------------------------------------
    def _ensure_store_defaults():
        if not hasattr(S, "ai_difficulty"):
            S.ai_difficulty = "basic"
        else:
            S.ai_difficulty = _norm_ai_level(getattr(S, "ai_difficulty", "basic"))

        if not hasattr(S, "ai_difficulty_save"):
            S.ai_difficulty_save = False
        else:
            S.ai_difficulty_save = _norm_bool(getattr(S, "ai_difficulty_save", False), False)

        if not hasattr(S, "ai_finisher_test_mode"):
            S.ai_finisher_test_mode = "normal"
        else:
            S.ai_finisher_test_mode = _norm_finisher_mode(getattr(S, "ai_finisher_test_mode", "normal"))

        if not hasattr(S, "ai_allow_focus"):
            S.ai_allow_focus = True
        else:
            S.ai_allow_focus = _norm_bool(getattr(S, "ai_allow_focus", True), True)

        if (not hasattr(S, "ai_finisher_weights")) or (not isinstance(getattr(S, "ai_finisher_weights", None), dict)):
            S.ai_finisher_weights = {
                "attack_reducer": 0.25,
                "stronger_attack": 0.25,
                "direct_attack": 0.25,
                "noatk_attack": 0.25,
            }
        else:
            # asegurar claves mínimas
            w = getattr(S, "ai_finisher_weights", {}) or {}
            for k in ("attack_reducer", "stronger_attack", "direct_attack", "noatk_attack"):
                if k not in w:
                    w[k] = 0.25
            S.ai_finisher_weights = w

    # ------------------------------------------------------------
    # Defaults PERSISTENT
    # ------------------------------------------------------------
    def _ensure_persistent_defaults():
        _ensure_store_defaults()
        try:
            p = S.persistent

            if not hasattr(p, "ai_difficulty") or not getattr(p, "ai_difficulty", None):
                p.ai_difficulty = "basic"
            else:
                p.ai_difficulty = _norm_ai_level(getattr(p, "ai_difficulty", "basic"))

            if not hasattr(p, "ai_difficulty_save"):
                p.ai_difficulty_save = False
            else:
                p.ai_difficulty_save = _norm_bool(getattr(p, "ai_difficulty_save", False), False)

            if not hasattr(p, "ai_finisher_test_mode") or not getattr(p, "ai_finisher_test_mode", None):
                p.ai_finisher_test_mode = "normal"
            else:
                p.ai_finisher_test_mode = _norm_finisher_mode(getattr(p, "ai_finisher_test_mode", "normal"))

            if not hasattr(p, "ai_allow_focus"):
                p.ai_allow_focus = True
            else:
                p.ai_allow_focus = _norm_bool(getattr(p, "ai_allow_focus", True), True)

            if (not hasattr(p, "ai_finisher_weights")) or (not isinstance(getattr(p, "ai_finisher_weights", None), dict)):
                p.ai_finisher_weights = {
                    "attack_reducer": 0.25,
                    "stronger_attack": 0.25,
                    "direct_attack": 0.25,
                    "noatk_attack": 0.25,
                }
            else:
                w = getattr(p, "ai_finisher_weights", {}) or {}
                for k in ("attack_reducer", "stronger_attack", "direct_attack", "noatk_attack"):
                    if k not in w:
                        w[k] = 0.25
                p.ai_finisher_weights = w

        except:
            pass

    _ensure_persistent_defaults()

    # ------------------------------------------------------------
    # Labels
    # ------------------------------------------------------------
    def _label_for_level(lvl):
        return {
            "basic": "🧠 Básico",
            "intermediate": "🧠 Intermedio",
            "advanced": "🧠 Avanzado",
        }.get(_norm_ai_level(lvl), "🧠 Básico")

    def _label_for_test_mode(mode):
        return {
            "normal": "🎯 Probabilidad: Normal",
            "stats":  "🎯 Probabilidad: Stats",
            "force_reducer":  "🎯 Forzar: Reductor",
            "force_stronger": "🎯 Forzar: Stronger",
            "force_direct":   "🎯 Forzar: Directo",
            "force_noatk":    "🎯 Forzar: Negador",
        }.get(_norm_finisher_mode(mode), "🎯 Probabilidad: Normal")

    # ------------------------------------------------------------
    # Level get / apply
    # ------------------------------------------------------------
    def ai_get_level():
        _ensure_store_defaults()
        if getattr(S, "ai_difficulty_save", False):
            try:
                return _norm_ai_level(getattr(S.persistent, "ai_difficulty", "basic"))
            except:
                return "basic"
        return _norm_ai_level(getattr(S, "ai_difficulty", "basic"))

    def ai_apply_level_to_store(lvl):
        _ensure_store_defaults()
        lvl = _norm_ai_level(lvl)
        S.ai_difficulty = lvl
        if getattr(S, "ai_difficulty_save", False):
            try:
                S.persistent.ai_difficulty = lvl
            except:
                pass

    # ------------------------------------------------------------
    # Sync from persistent
    # ------------------------------------------------------------
    def ai_sync_from_persistent_if_needed():
        _ensure_persistent_defaults()

        try:
            S.ai_difficulty_save = _norm_bool(getattr(S.persistent, "ai_difficulty_save", False), False)
        except:
            S.ai_difficulty_save = False

        ai_apply_level_to_store(ai_get_level())

        if S.ai_difficulty_save:
            try:
                S.ai_finisher_test_mode = _norm_finisher_mode(getattr(S.persistent, "ai_finisher_test_mode", "normal"))
            except:
                S.ai_finisher_test_mode = _norm_finisher_mode(getattr(S, "ai_finisher_test_mode", "normal"))

            try:
                S.ai_allow_focus = _norm_bool(getattr(S.persistent, "ai_allow_focus", True), True)
            except:
                S.ai_allow_focus = _norm_bool(getattr(S, "ai_allow_focus", True), True)

            try:
                w = getattr(S.persistent, "ai_finisher_weights", None)
                if isinstance(w, dict):
                    S.ai_finisher_weights = dict(w)
            except:
                pass
        else:
            # Guardar OFF → dejamos store como fuente y lo normalizamos
            _ensure_store_defaults()
            S.ai_finisher_test_mode = _norm_finisher_mode(getattr(S, "ai_finisher_test_mode", "normal"))
            S.ai_allow_focus = _norm_bool(getattr(S, "ai_allow_focus", True), True)

            if (not hasattr(S, "ai_finisher_weights")) or (not isinstance(getattr(S, "ai_finisher_weights", None), dict)):
                S.ai_finisher_weights = {
                    "attack_reducer": 0.25,
                    "stronger_attack": 0.25,
                    "direct_attack": 0.25,
                    "noatk_attack": 0.25,
                }

    # ------------------------------------------------------------
    # UI actions
    # ------------------------------------------------------------
    def ai_cycle_level():
        cur = ai_get_level()
        try:
            i = AI_LEVELS.index(cur)
        except:
            i = 0
        nxt = AI_LEVELS[(i + 1) % len(AI_LEVELS)]
        ai_apply_level_to_store(nxt)
        R.restart_interaction()

    def ai_toggle_save():
        _ensure_persistent_defaults()

        S.ai_difficulty_save = not bool(getattr(S, "ai_difficulty_save", False))
        try:
            S.persistent.ai_difficulty_save = bool(S.ai_difficulty_save)
        except:
            pass

        if S.ai_difficulty_save:
            try:
                S.persistent.ai_difficulty = ai_get_level()
            except:
                pass

            try:
                S.persistent.ai_finisher_test_mode = ai_finisher_mode_get()
            except:
                pass

            try:
                S.persistent.ai_allow_focus = bool(getattr(S, "ai_allow_focus", True))
            except:
                pass

            try:
                _ensure_persistent_finisher_weights_dict()
                S.persistent.ai_finisher_weights = dict(getattr(S, "ai_finisher_weights", {}) or {})
            except:
                pass

        R.restart_interaction()

    # ------------------------------------------------------------
    # Offense: finisher mode
    # ------------------------------------------------------------
    def ai_finisher_mode_get():
        _ensure_store_defaults()
        return _norm_finisher_mode(getattr(S, "ai_finisher_test_mode", "normal"))

    def ai_finisher_mode_set(mode):
        _ensure_store_defaults()
        mode = _norm_finisher_mode(mode)
        S.ai_finisher_test_mode = mode
        if getattr(S, "ai_difficulty_save", False):
            try:
                S.persistent.ai_finisher_test_mode = mode
            except:
                pass

    def ai_cycle_finisher_mode():
        cur = ai_finisher_mode_get()
        try:
            i = AI_FIN_TEST_MODES.index(cur)
        except:
            i = 0
        ai_finisher_mode_set(AI_FIN_TEST_MODES[(i + 1) % len(AI_FIN_TEST_MODES)])
        R.restart_interaction()

    def ai_reset_finisher_stats():
        try:
            fn = getattr(S, "ai_finisher_stats_reset", None)
            if callable(fn):
                fn()
        except:
            pass
        R.restart_interaction()

    def ai_finisher_mode_text():
        return _label_for_test_mode(ai_finisher_mode_get())

    # ------------------------------------------------------------
    # Offense weights (25 / 50 / 75 / 100)
    # ------------------------------------------------------------
    AI_WEIGHT_STEPS = [0.25, 0.50, 0.75, 1.00]

    def ai_weight_get(key):
        try:
            w = getattr(S, "ai_finisher_weights", {}) or {}
            return float(w.get(key, 0.25))
        except:
            return 0.25

    def ai_weight_set(key, value):
        _ensure_store_defaults()

        try:
            if (not hasattr(S, "ai_finisher_weights")) or (not isinstance(getattr(S, "ai_finisher_weights", None), dict)):
                S.ai_finisher_weights = {}
            S.ai_finisher_weights[key] = float(value)
        except:
            pass

        if getattr(S, "ai_difficulty_save", False):
            try:
                _ensure_persistent_finisher_weights_dict()
                S.persistent.ai_finisher_weights[key] = float(value)
            except:
                pass

    def ai_cycle_weight(key):
        cur = ai_weight_get(key)

        idx = 0
        try:
            best_i = 0
            best_d = 999
            for i, s in enumerate(AI_WEIGHT_STEPS):
                d = abs(float(cur) - float(s))
                if d < best_d:
                    best_d = d
                    best_i = i
            idx = best_i
        except:
            idx = 0

        ai_weight_set(key, AI_WEIGHT_STEPS[(idx + 1) % len(AI_WEIGHT_STEPS)])
        R.restart_interaction()

    def ai_weight_pct_text(key, prefix):
        try:
            return "{}{}%".format(prefix, int(round(ai_weight_get(key) * 100)))
        except:
            return "{}25%".format(prefix)

    # ------------------------------------------------------------
    # Focus toggle
    # ------------------------------------------------------------
    def ai_focus_text():
        return "🧿 Focus IA: ON" if bool(getattr(S, "ai_allow_focus", True)) else "🧿 Focus IA: OFF"

    def ai_focus_color():
        return "#66FF99" if bool(getattr(S, "ai_allow_focus", True)) else "#FF7777"

    def ai_toggle_focus():
        _ensure_store_defaults()
        S.ai_allow_focus = not bool(getattr(S, "ai_allow_focus", True))

        if getattr(S, "ai_difficulty_save", False):
            try:
                S.persistent.ai_allow_focus = bool(getattr(S, "ai_allow_focus", True))
            except:
                pass

        R.restart_interaction()

    # ------------------------------------------------------------
    # Text / Colors
    # ------------------------------------------------------------
    def ai_level_text():
        return _label_for_level(ai_get_level())

    def ai_level_color():
        return {
            "basic": "#55FFFF",
            "intermediate": "#FFD700",
            "advanced": "#C586C0",
        }.get(ai_get_level(), "#55FFFF")

    def ai_save_text():
        return "💾 Guardar: ON" if getattr(S, "ai_difficulty_save", False) else "💾 Guardar: OFF"

    def ai_save_color():
        return "#66FF99" if getattr(S, "ai_difficulty_save", False) else "#FF7777"

    def ai_test_color():
        mode = ai_finisher_mode_get()
        try:
            if str(mode).startswith("force_"):
                return "#FF66CC"
        except:
            pass
        if mode == "stats":
            return "#FFD700"
        return "#55FFFF"
