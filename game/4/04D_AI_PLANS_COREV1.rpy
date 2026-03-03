# ============================================================
# 04D_AI_PLANS_CORE.rpy – Core helpers compartidos
# v1.0
# ------------------------------------------------------------
# - _ai_focus_allowed
# - _ai_level / _has_tech
# - _filter_existing / _safe_set_plan
# - _get_hp_ratio_damage / _weighted_choice
# - _pick_from_candidates (general)
# ============================================================

init -990 python:
    import random
    import renpy.store as S

    DEFAULT_AI_LEVEL = "basic"

    def _ai_focus_allowed():
        try:
            return bool(getattr(S, "ai_allow_focus", True))
        except:
            return True

    def _ai_level(ai):
        lvl = getattr(ai, "behavior_mode", None)
        if lvl in ("basic", "intermediate", "advanced"):
            return lvl
        lvl = getattr(S, "ai_difficulty", None)
        if lvl in ("basic", "intermediate", "advanced"):
            return lvl
        return DEFAULT_AI_LEVEL

    def _has_tech(ai, key):
        # focus “existe” como acción, pero se filtra por _ai_focus_allowed() al construir plan
        if key == "focus":
            return True
        try:
            return ai.has_tech(key)
        except:
            return True  # compat

    def _filter_existing(ai, actions):
        out = []
        for a in actions:
            if _has_tech(ai, a):
                out.append(a)
        return out

    def _safe_set_plan(ai, actions, fallback_candidates=None):
        plan = _filter_existing(ai, actions)

        if not plan and fallback_candidates:
            for cand in fallback_candidates:
                if _has_tech(ai, cand):
                    plan = [cand]
                    break

        ai.current_plan = list(plan)

    def _clamp(v, a, b):
        return a if v < a else b if v > b else v

    def _get_hp_ratio_damage(incoming_damage, enemy_hp):
        try:
            hp = float(enemy_hp)
            if hp <= 0:
                return 0.0
            return _clamp(float(incoming_damage) / hp, 0.0, 1.0)
        except:
            return 0.0

    def _weighted_choice(weight_map):
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

    def _pick_from_candidates(ai, candidates, weights):
        """
        candidates = lista de keys
        weights = dict {key: weight}
        dataset-aware: filtra lo que no exista en ai
        """
        existing = [c for c in candidates if _has_tech(ai, c)]
        if not existing:
            return None

        wm = {}
        for c in existing:
            try:
                wm[c] = float(weights.get(c, 0.0))
            except:
                wm[c] = 0.0

        if sum(wm.values()) <= 0.0:
            uniform = 1.0 / float(len(existing))
            wm = {c: uniform for c in existing}

        return _weighted_choice(wm)
