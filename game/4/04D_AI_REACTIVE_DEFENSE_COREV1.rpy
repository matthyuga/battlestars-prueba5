# ============================================================
# 04D_AI_REACTIVE_DEFENSE_CORE.rpy – Helpers + Plan Builder
# v12.4 – DefenseModes + Concat (OnePick) CORE ✅
# ------------------------------------------------------------
# - Defaults store-safe (modo/concat/pesos)
# - Picks: normal/stats/force_*
# - Build plan final (focus opcional + concat)
# - Validación: existencia + pago (fallback)
# ============================================================

init -988 python:

    import renpy.store as S
    import random

    # -------------------------------
    # Defaults / Config (store-safe)
    # -------------------------------
    def ai_defense_ensure_defaults():
        # modos:
        #   "normal", "stats",
        #   "force_extra", "force_reduct", "force_reflect"
        if not hasattr(S, "ai_defense_test_mode"):
            S.ai_defense_test_mode = "normal"

        if not hasattr(S, "ai_defense_concat"):
            S.ai_defense_concat = False

        if not hasattr(S, "ai_defense_weights") or not isinstance(getattr(S, "ai_defense_weights", None), dict):
            S.ai_defense_weights = {
                "def_extra":   0.34,
                "def_reduct":  0.33,
                "def_reflect": 0.33,
            }
        else:
            w = getattr(S, "ai_defense_weights", {}) or {}
            for k in ("def_extra", "def_reduct", "def_reflect"):
                if k not in w:
                    w[k] = 0.33
            S.ai_defense_weights = w

    # -------------------------------
    # Helpers
    # -------------------------------
    def ai_defense_weighted_pick(weight_map):
        total = 0.0
        for w in weight_map.values():
            try:
                total += float(w)
            except:
                pass
        if total <= 0.0:
            return None

        r = random.random() * total
        acc = 0.0
        items = list(weight_map.items())
        for k, w in items:
            try:
                acc += float(w)
            except:
                continue
            if r <= acc:
                return k
        return items[-1][0] if items else None

    def ai_defense_tech_exists(alias_key):
        try:
            return bool(getattr(S, "battle_techniques", {}).get(alias_key, {}))
        except:
            return True

    def ai_defense_real_id_for(alias_key):
        """
        Alias (def_extra/def_reduct/def_reflect) → real_id moderno (tech["id"])
        """
        try:
            tech = getattr(S, "battle_techniques", {}).get(alias_key, {})
        except:
            tech = {}
        try:
            return tech.get("id", alias_key) or alias_key
        except:
            return alias_key

    def ai_defense_can_pay_alias(alias_key):
        """
        Chequea pago usando real_id (si ai_can_pay existe).
        Si no existe, asume True (no rompe).
        """
        can_pay_fn = getattr(S, "ai_can_pay", None)
        if not callable(can_pay_fn):
            can_pay_fn = globals().get("ai_can_pay", None)
        if not callable(can_pay_fn):
            return True

        rid = ai_defense_real_id_for(alias_key)
        try:
            ok, fr, fe = can_pay_fn(rid, "enemy")
            return bool(ok)
        except:
            return True

    # -------------------------------
    # Pick de UNA defensa según modo
    # -------------------------------
    def ai_defense_pick_one(dmg_effective):
        ai_defense_ensure_defaults()

        mode = getattr(S, "ai_defense_test_mode", "normal") or "normal"
        try:
            mode = str(mode)
        except:
            mode = "normal"

        if mode == "force_extra":
            return "def_extra"
        if mode == "force_reduct":
            return "def_reduct"
        if mode == "force_reflect":
            return "def_reflect"

        if mode == "stats":
            w = getattr(S, "ai_defense_weights", {}) or {}
            choice = ai_defense_weighted_pick({
                "def_extra":   float(w.get("def_extra", 0.34) or 0.0),
                "def_reduct":  float(w.get("def_reduct", 0.33) or 0.0),
                "def_reflect": float(w.get("def_reflect",0.33) or 0.0),
            })
            return choice or "def_extra"

        # normal por umbrales (1 sola)
        if dmg_effective < 1500:
            return "def_extra"
        elif dmg_effective < 5000:
            return "def_reduct"
        else:
            return "def_reflect"

    # -------------------------------
    # Build plan final (focus + concat)
    # -------------------------------
    def ai_defense_build_plan(dmg_effective):
        ai_defense_ensure_defaults()

        picked = ai_defense_pick_one(dmg_effective)

        plan = []

        # Focus solo si daño alto y si allow_focus
        if dmg_effective >= 3000 and bool(getattr(S, "ai_allow_focus", True)):
            plan.append("focus")

        concat = bool(getattr(S, "ai_defense_concat", False))

        if concat:
            plan.append("def_extra")
            if picked and picked != "def_extra":
                plan.append(picked)
        else:
            plan.append(picked or "def_extra")

        # -------------------------------
        # Validación: existencia + pago
        # -------------------------------
        cleaned = []
        for k in plan:
            if k == "focus":
                cleaned.append(k)
                continue
            if not ai_defense_tech_exists(k):
                k = "def_extra"
            cleaned.append(k)

        # quitar duplicados consecutivos
        tmp = []
        for k in cleaned:
            if not tmp or tmp[-1] != k:
                tmp.append(k)

        # si no puede pagar una defensa (no focus), fallback a extra
        for i, k in enumerate(list(tmp)):
            if k == "focus":
                continue
            if not ai_defense_can_pay_alias(k):
                tmp[i] = "def_extra"

        # quitar duplicados otra vez
        final_plan = []
        for k in tmp:
            if not final_plan or final_plan[-1] != k:
                final_plan.append(k)

        return final_plan
