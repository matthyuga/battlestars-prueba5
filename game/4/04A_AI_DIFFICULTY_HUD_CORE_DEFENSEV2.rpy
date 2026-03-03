# ============================================================
# 04A_AI_DIFFICULTY_HUD_CORE_DEFENSE.rpy – Core HUD AI (DEFENSE)
# v1.6.1 DEFENSE (BLINDED + CONCAT + WEIGHTS) ✅ PATCHED
# ------------------------------------------------------------
# Contiene:
# - defensa IA: modos
# - concat ON/OFF
# - pesos defensivos (stats)
# - sync store / persistent
# - helpers de texto / color
#
# Parches BLINDED:
# - ✅ Normaliza y asegura claves mínimas (store/persistent)
# - ✅ Clamp de pesos (0..1) + fallback seguro
# - ✅ Persistent dict-safe para ai_defense_weights
# - ✅ ai_defense_color blindado (startswith safe)
# - ✅ Sync: si SAVE OFF, normaliza store también
# ============================================================

init -20 python:
    import renpy.store as S
    import renpy.exports as R

    # ------------------------------------------------------------
    # DEF: modos disponibles
    # ------------------------------------------------------------
    AI_DEF_TEST_MODES = [
        "normal",
        "stats",
        "force_extra",
        "force_reduct",
        "force_reflect",
    ]

    _DEF_KEYS = ("def_extra", "def_reduct", "def_reflect")

    # ------------------------------------------------------------
    # Helpers: normalize (BLINDED)
    # ------------------------------------------------------------
    def _norm_defense_mode(mode):
        if not mode:
            return "normal"
        try:
            s = str(mode)
        except:
            return "normal"
        if s not in AI_DEF_TEST_MODES:
            return "normal"
        return s

    def _norm_bool(v, default=False):
        try:
            return bool(v)
        except:
            return default

    def _clamp01(x, default=0.33):
        try:
            v = float(x)
        except:
            v = float(default)
        if v < 0.0:
            v = 0.0
        if v > 1.0:
            v = 1.0
        return v

    def _ensure_persistent_defense_weights_dict():
        try:
            p = S.persistent
            if (not hasattr(p, "ai_defense_weights")) or (not isinstance(getattr(p, "ai_defense_weights", None), dict)):
                p.ai_defense_weights = {}
        except:
            pass

    # ------------------------------------------------------------
    # Defaults STORE (DEFENSE ONLY)
    # ------------------------------------------------------------
    def _ensure_defense_store_defaults():
        # mode
        if not hasattr(S, "ai_defense_test_mode"):
            S.ai_defense_test_mode = "normal"
        else:
            S.ai_defense_test_mode = _norm_defense_mode(getattr(S, "ai_defense_test_mode", "normal"))

        # concat
        if not hasattr(S, "ai_defense_concat"):
            S.ai_defense_concat = False
        else:
            S.ai_defense_concat = _norm_bool(getattr(S, "ai_defense_concat", False), False)

        # weights
        if (not hasattr(S, "ai_defense_weights")) or (not isinstance(getattr(S, "ai_defense_weights", None), dict)):
            S.ai_defense_weights = {
                "def_extra":   0.34,
                "def_reduct":  0.33,
                "def_reflect": 0.33,
            }
        else:
            w = getattr(S, "ai_defense_weights", {}) or {}
            # asegurar claves mínimas
            for k in _DEF_KEYS:
                if k not in w:
                    w[k] = 0.33
                else:
                    w[k] = _clamp01(w.get(k, 0.33), 0.33)
            S.ai_defense_weights = w

    # ------------------------------------------------------------
    # Defaults PERSISTENT (DEFENSE ONLY)
    # ------------------------------------------------------------
    def _ensure_defense_persistent_defaults():
        _ensure_defense_store_defaults()
        try:
            p = S.persistent

            # mode
            if not hasattr(p, "ai_defense_test_mode") or not getattr(p, "ai_defense_test_mode", None):
                p.ai_defense_test_mode = "normal"
            else:
                p.ai_defense_test_mode = _norm_defense_mode(getattr(p, "ai_defense_test_mode", "normal"))

            # concat
            if not hasattr(p, "ai_defense_concat"):
                p.ai_defense_concat = False
            else:
                p.ai_defense_concat = _norm_bool(getattr(p, "ai_defense_concat", False), False)

            # weights dict-safe + claves mínimas
            if (not hasattr(p, "ai_defense_weights")) or (not isinstance(getattr(p, "ai_defense_weights", None), dict)):
                p.ai_defense_weights = {
                    "def_extra":   0.34,
                    "def_reduct":  0.33,
                    "def_reflect": 0.33,
                }
            else:
                pw = getattr(p, "ai_defense_weights", {}) or {}
                for k in _DEF_KEYS:
                    if k not in pw:
                        pw[k] = 0.33
                    else:
                        pw[k] = _clamp01(pw.get(k, 0.33), 0.33)
                p.ai_defense_weights = pw

        except:
            pass

    _ensure_defense_persistent_defaults()

    # ------------------------------------------------------------
    # Sync desde persistent (cuando SAVE = ON)
    # ------------------------------------------------------------
    def ai_defense_sync_from_persistent_if_needed():
        _ensure_defense_persistent_defaults()

        if getattr(S, "ai_difficulty_save", False):
            try:
                S.ai_defense_test_mode = _norm_defense_mode(getattr(S.persistent, "ai_defense_test_mode", "normal"))
            except:
                pass

            try:
                S.ai_defense_concat = _norm_bool(getattr(S.persistent, "ai_defense_concat", False), False)
            except:
                pass

            try:
                dw = getattr(S.persistent, "ai_defense_weights", None)
                if isinstance(dw, dict):
                    # clonar + normalizar
                    dwn = dict(dw)
                    for k in _DEF_KEYS:
                        dwn[k] = _clamp01(dwn.get(k, 0.33), 0.33)
                    S.ai_defense_weights = dwn
            except:
                pass
        else:
            # SAVE OFF → store es fuente, pero lo normalizamos igual
            _ensure_defense_store_defaults()

    # ------------------------------------------------------------
    # Defense mode
    # ------------------------------------------------------------
    def ai_defense_mode_get():
        _ensure_defense_store_defaults()
        return _norm_defense_mode(getattr(S, "ai_defense_test_mode", "normal"))

    def ai_defense_mode_set(mode):
        _ensure_defense_store_defaults()
        mode = _norm_defense_mode(mode)
        S.ai_defense_test_mode = mode

        if getattr(S, "ai_difficulty_save", False):
            try:
                S.persistent.ai_defense_test_mode = mode
            except:
                pass

    def ai_cycle_defense_mode():
        cur = ai_defense_mode_get()
        try:
            i = AI_DEF_TEST_MODES.index(cur)
        except:
            i = 0
        ai_defense_mode_set(AI_DEF_TEST_MODES[(i + 1) % len(AI_DEF_TEST_MODES)])
        R.restart_interaction()

    # ------------------------------------------------------------
    # Concat toggle
    # ------------------------------------------------------------
    def ai_defense_concat_get():
        _ensure_defense_store_defaults()
        return bool(getattr(S, "ai_defense_concat", False))

    def ai_toggle_defense_concat():
        _ensure_defense_store_defaults()
        S.ai_defense_concat = not bool(getattr(S, "ai_defense_concat", False))

        if getattr(S, "ai_difficulty_save", False):
            try:
                S.persistent.ai_defense_concat = bool(S.ai_defense_concat)
            except:
                pass

        R.restart_interaction()

    # ------------------------------------------------------------
    # Defense weights (stats)
    # ------------------------------------------------------------
    AI_WEIGHT_STEPS = [0.25, 0.50, 0.75, 1.00]

    def ai_defense_weight_get(key):
        _ensure_defense_store_defaults()
        try:
            w = getattr(S, "ai_defense_weights", {}) or {}
            return float(w.get(key, 0.33))
        except:
            return 0.33

    def ai_defense_weight_set(key, value):
        _ensure_defense_store_defaults()

        v = _clamp01(value, 0.33)

        try:
            if (not hasattr(S, "ai_defense_weights")) or (not isinstance(getattr(S, "ai_defense_weights", None), dict)):
                S.ai_defense_weights = {}
            S.ai_defense_weights[key] = float(v)
        except:
            pass

        if getattr(S, "ai_difficulty_save", False):
            try:
                _ensure_persistent_defense_weights_dict()
                S.persistent.ai_defense_weights[key] = float(v)
            except:
                pass

    def ai_cycle_defense_weight(key):
        cur = ai_defense_weight_get(key)

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

        ai_defense_weight_set(key, AI_WEIGHT_STEPS[(idx + 1) % len(AI_WEIGHT_STEPS)])
        R.restart_interaction()

    def ai_defense_weight_pct_text(key, prefix):
        try:
            return "{}{}%".format(prefix, int(round(ai_defense_weight_get(key) * 100)))
        except:
            return "{}25%".format(prefix)

    # ------------------------------------------------------------
    # Reset stats (hook)
    # ------------------------------------------------------------
    def ai_reset_defense_stats():
        try:
            fn = getattr(S, "ai_defense_stats_reset", None)
            if callable(fn):
                fn()
        except:
            pass
        R.restart_interaction()

    # ------------------------------------------------------------
    # Text / Colors
    # ------------------------------------------------------------
    def ai_defense_mode_text():
        m = ai_defense_mode_get()
        tag = " +Concat" if ai_defense_concat_get() else ""

        if m == "normal":        return "🛡️ Defensa: Normal%s" % tag
        if m == "stats":         return "🛡️ Defensa: Stats%s" % tag
        if m == "force_extra":   return "🛡️ Forzar: Extra%s" % tag
        if m == "force_reduct":  return "🛡️ Forzar: Reduct%s" % tag
        if m == "force_reflect": return "🛡️ Forzar: Reflect%s" % tag
        return "🛡️ Defensa: Normal%s" % tag

    def ai_defense_color():
        m = ai_defense_mode_get()
        try:
            if str(m).startswith("force_"):
                return "#FF66CC"
        except:
            pass
        if m == "stats":
            return "#FFD700"
        return "#55FFFF"

    def ai_defense_concat_text():
        return "🔗 Concat: ON" if ai_defense_concat_get() else "🔗 Concat: OFF"

    def ai_defense_concat_color():
        return "#66FF99" if ai_defense_concat_get() else "#FF7777"
