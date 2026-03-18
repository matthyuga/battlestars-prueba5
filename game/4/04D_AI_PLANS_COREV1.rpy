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

    def _ai_focus_allowed(unit_key=None):
        try:
            fn = getattr(S, "ai_effective_allow_focus", None)
            if callable(fn):
                return bool(fn(unit_key))
        except:
            pass
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


    # ============================================================
    # Bloqueo de técnicas por unidad (Fase 4)
    # ============================================================
    def _ai_block_store():
        data = getattr(S, "ai_blocked_techniques_by_unit", None)
        if not isinstance(data, dict):
            data = {}
            S.ai_blocked_techniques_by_unit = data
        return data

    def ai_block_tech_for_unit(unit_key, tech_id, turns=1, phase="any", reason=""):
        uk = str(unit_key or "").strip() or str(getattr(S, "current_enemy_unit_key", "enemy:0") or "enemy:0")
        tid = str(tech_id or "").strip()
        if not tid:
            return False

        ph = str(phase or "any").strip().lower()
        if ph not in ("any", "offense", "defense"):
            ph = "any"

        try:
            rem = int(turns)
        except:
            rem = 1
        if rem < 1:
            rem = 1

        st = _ai_block_store()
        unit_map = st.get(uk, {})
        if not isinstance(unit_map, dict):
            unit_map = {}

        unit_map[tid] = {
            "remaining": rem,
            "phase": ph,
            "reason": str(reason or ""),
        }
        st[uk] = unit_map
        S.ai_blocked_techniques_by_unit = st
        return True

    def ai_is_tech_blocked(unit_key, tech_id, phase="any", consume=False):
        uk = str(unit_key or "").strip() or str(getattr(S, "current_enemy_unit_key", "enemy:0") or "enemy:0")
        tid = str(tech_id or "").strip()
        if not tid:
            return False

        ph = str(phase or "any").strip().lower()
        if ph not in ("any", "offense", "defense"):
            ph = "any"

        st = _ai_block_store()
        unit_map = st.get(uk, {})
        if not isinstance(unit_map, dict):
            return False

        row = unit_map.get(tid, None)
        if not isinstance(row, dict):
            return False

        remaining = int(row.get("remaining", 0) or 0)
        if remaining <= 0:
            try:
                unit_map.pop(tid, None)
                st[uk] = unit_map
                S.ai_blocked_techniques_by_unit = st
            except:
                pass
            return False

        row_phase = str(row.get("phase", "any") or "any").strip().lower()
        if row_phase not in ("any", "offense", "defense"):
            row_phase = "any"

        applies = (row_phase == "any") or (ph == "any") or (row_phase == ph)
        if not applies:
            return False

        if consume:
            row["remaining"] = max(0, remaining - 1)
            if int(row.get("remaining", 0) or 0) <= 0:
                unit_map.pop(tid, None)
            else:
                unit_map[tid] = row
            st[uk] = unit_map
            S.ai_blocked_techniques_by_unit = st

        return True

    def ai_filter_blocked_plan(plan, unit_key, forced=False, phase="any"):
        p = list(plan or [])
        out = []
        for tid in p:
            t = str(tid or "").strip()
            if not t:
                continue
            blocked = False
            try:
                blocked = bool(ai_is_tech_blocked(unit_key, t, phase=phase, consume=False))
            except:
                blocked = False

            # Regla: en forzado no reemplaza técnica bloqueada.
            if forced:
                out.append(t)
                continue

            # Regla: en normal/concat se omite la bloqueada y sigue con válidas.
            if not blocked:
                out.append(t)

        return out



    try:
        S.ai_block_tech_for_unit = ai_block_tech_for_unit
        S.ai_is_tech_blocked = ai_is_tech_blocked
        S.ai_filter_blocked_plan = ai_filter_blocked_plan
    except:
        pass
