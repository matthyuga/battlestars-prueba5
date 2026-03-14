# ===============================================================
# 04Y_SLOT_POINT_ALLOCATOR_V1.rpy
# Core allocator de puntos por slot (Fase A)
# ===============================================================
# - Overlay por unit_key (team:slot), sin tocar TECH_STATS global
# - API segura: set/add/sub/get/reset/recompute
# - Persistencia opcional en persistent.battle_point_alloc_v1
# - Compatible 1v1/2v2 y extensible por keys dinámicas
# ===============================================================

default battle_point_alloc = {
    "version": 1,
    "defaults": {
        "available_points_per_slot": 2000,
        "max_bonus_per_tech": 1000,
        "enabled": True,
    },
    "slots": {}
}

default battle_point_alloc_autoload_done = False

default slot_points_persistence_enabled = True

init -940 python:
    import renpy
    import renpy.store as S

    def _spa_to_int(v, default=0):
        try:
            return int(v)
        except:
            try:
                return int(default)
            except:
                return 0

    def _spa_clamp(v, lo, hi):
        vv = _spa_to_int(v, lo)
        if vv < lo:
            vv = lo
        if vv > hi:
            vv = hi
        return vv

    def _spa_tech_exists(tech_id):
        tid = str(tech_id or "").strip()
        if not tid:
            return False

        zero = getattr(S, "SPECIAL_ZERO_COST", set())
        if isinstance(zero, (set, list, tuple)) and tid in zero:
            return False

        stats = getattr(S, "TECH_STATS", {})
        if isinstance(stats, dict):
            return tid in stats

        return False

    def _spa_normalize_unit_key(unit_key):
        # Prioridad: parser del facade (soporta team:slot y dict)
        fn_parse = getattr(S, "bs_parse_unit_key", None)
        if callable(fn_parse):
            info = fn_parse(unit_key, default_side="player", default_slot=0)
            team = str(info.get("team", "player") or "player").strip().lower()
            slot = _spa_to_int(info.get("slot", 0), 0)
            if slot < 0:
                slot = 0
            return "{}:{}".format(team, slot)

        # Fallback básico
        raw = str(unit_key or "").strip().lower()
        if not raw:
            return "player:0"

        if ":" in raw:
            side_s, slot_s = raw.split(":", 1)
            side = "enemy" if side_s in ("enemy", "e") else "player"
            slot = _spa_to_int(slot_s, 0)
            if slot < 0:
                slot = 0
            return "{}:{}".format(side, slot)

        side = "enemy" if raw in ("enemy", "e") else "player"
        return "{}:0".format(side)

    def _spa_defaults_obj(state=None):
        st = state if isinstance(state, dict) else spa_ensure_state()
        d = st.get("defaults", {}) if isinstance(st.get("defaults", {}), dict) else {}
        out = {
            "available_points_per_slot": max(0, _spa_to_int(d.get("available_points_per_slot", 2000), 2000)),
            "max_bonus_per_tech": max(0, _spa_to_int(d.get("max_bonus_per_tech", 1000), 1000)),
            "enabled": bool(d.get("enabled", True)),
        }
        return out

    def _spa_recompute_slot_data(slot_data, defaults):
        sd = dict(slot_data) if isinstance(slot_data, dict) else {}

        available = _spa_to_int(sd.get("available", defaults.get("available_points_per_slot", 2000)),
                                defaults.get("available_points_per_slot", 2000))
        if available < 0:
            available = 0

        mb = max(0, _spa_to_int(defaults.get("max_bonus_per_tech", 1000), 1000))

        raw_bonus = sd.get("tech_bonus", {})
        if not isinstance(raw_bonus, dict):
            raw_bonus = {}

        clean_bonus = {}
        spent = 0

        for k, v in raw_bonus.items():
            tid = str(k or "").strip()
            if not tid:
                continue

            # conservamos solo técnicas válidas y no especiales
            if not _spa_tech_exists(tid):
                continue

            vv = _spa_clamp(v, 0, mb)
            if vv <= 0:
                continue

            clean_bonus[tid] = vv
            spent += vv

        # Seguridad: si por carga externa se pasa del presupuesto, recortamos proporcional simple por orden
        if spent > available and available >= 0:
            target = available
            adjusted = {}
            acc = 0
            # orden estable por técnica para resultado determinista
            for tid in sorted(clean_bonus.keys()):
                if acc >= target:
                    break
                remain = target - acc
                vv = clean_bonus[tid]
                take = vv if vv <= remain else remain
                if take > 0:
                    adjusted[tid] = int(take)
                    acc += int(take)
            clean_bonus = adjusted
            spent = acc

        remaining = available - spent
        if remaining < 0:
            remaining = 0

        sd["available"] = int(available)
        sd["spent"] = int(spent)
        sd["remaining"] = int(remaining)
        sd["tech_bonus"] = dict(clean_bonus)
        return sd

    def _spa_compact_state(state):
        st = dict(state) if isinstance(state, dict) else {}
        st["version"] = 1

        defaults = _spa_defaults_obj(st)
        st["defaults"] = defaults

        slots = st.get("slots", {})
        if not isinstance(slots, dict):
            slots = {}

        out_slots = {}
        for raw_key, raw_slot in slots.items():
            uk = _spa_normalize_unit_key(raw_key)
            out_slots[uk] = _spa_recompute_slot_data(raw_slot, defaults)

        st["slots"] = out_slots
        return st

    def spa_ensure_state():
        st = getattr(S, "battle_point_alloc", None)
        if not isinstance(st, dict):
            st = {}

        st = _spa_compact_state(st)
        S.battle_point_alloc = st
        return st

    def spa_set_defaults(available_points_per_slot=None, max_bonus_per_tech=None, enabled=None, save=True):
        st = spa_ensure_state()
        d = _spa_defaults_obj(st)

        if available_points_per_slot is not None:
            d["available_points_per_slot"] = max(0, _spa_to_int(available_points_per_slot, d["available_points_per_slot"]))

        if max_bonus_per_tech is not None:
            d["max_bonus_per_tech"] = max(0, _spa_to_int(max_bonus_per_tech, d["max_bonus_per_tech"]))

        if enabled is not None:
            d["enabled"] = bool(enabled)

        st["defaults"] = d

        # Recalcular slots con nuevos defaults
        slots = st.get("slots", {}) if isinstance(st.get("slots", {}), dict) else {}
        for uk in list(slots.keys()):
            slots[uk] = _spa_recompute_slot_data(slots.get(uk, {}), d)
        st["slots"] = slots

        S.battle_point_alloc = st
        if save:
            spa_save_persistent()
        return dict(d)

    def spa_is_enabled():
        st = spa_ensure_state()
        d = _spa_defaults_obj(st)
        return bool(d.get("enabled", True))

    def spa_ensure_slot(unit_key):
        st = spa_ensure_state()
        d = _spa_defaults_obj(st)

        uk = _spa_normalize_unit_key(unit_key)
        slots = st.get("slots", {}) if isinstance(st.get("slots", {}), dict) else {}

        if uk not in slots or not isinstance(slots.get(uk), dict):
            slots[uk] = {
                "available": int(d.get("available_points_per_slot", 2000)),
                "spent": 0,
                "remaining": int(d.get("available_points_per_slot", 2000)),
                "tech_bonus": {}
            }
        slots[uk] = _spa_recompute_slot_data(slots.get(uk, {}), d)

        st["slots"] = slots
        S.battle_point_alloc = st
        return dict(slots[uk])

    def spa_get_slot(unit_key):
        st = spa_ensure_state()
        uk = _spa_normalize_unit_key(unit_key)
        slots = st.get("slots", {}) if isinstance(st.get("slots", {}), dict) else {}
        if uk not in slots:
            return spa_ensure_slot(uk)
        d = _spa_defaults_obj(st)
        slots[uk] = _spa_recompute_slot_data(slots.get(uk, {}), d)
        st["slots"] = slots
        S.battle_point_alloc = st
        return dict(slots[uk])

    def spa_get_available(unit_key):
        return int(spa_get_slot(unit_key).get("available", 0) or 0)

    def spa_get_spent(unit_key):
        return int(spa_get_slot(unit_key).get("spent", 0) or 0)

    def spa_get_remaining(unit_key):
        return int(spa_get_slot(unit_key).get("remaining", 0) or 0)

    def spa_get_bonus(unit_key, tech_id):
        tid = str(tech_id or "").strip()
        if not tid:
            return 0
        slot = spa_get_slot(unit_key)
        tb = slot.get("tech_bonus", {}) if isinstance(slot.get("tech_bonus", {}), dict) else {}
        return max(0, _spa_to_int(tb.get(tid, 0), 0))

    def spa_set_available(unit_key, new_available, save=True):
        st = spa_ensure_state()
        d = _spa_defaults_obj(st)
        uk = _spa_normalize_unit_key(unit_key)
        slot = spa_get_slot(uk)

        slot["available"] = max(0, _spa_to_int(new_available, slot.get("available", 0)))
        slot = _spa_recompute_slot_data(slot, d)

        slots = st.get("slots", {}) if isinstance(st.get("slots", {}), dict) else {}
        slots[uk] = slot
        st["slots"] = slots
        S.battle_point_alloc = st

        if save:
            spa_save_persistent()

        return dict(slot)

    def spa_set_bonus(unit_key, tech_id, new_bonus, save=True):
        tid = str(tech_id or "").strip()
        if not _spa_tech_exists(tid):
            return {"ok": False, "reason": "invalid_tech", "before": spa_get_slot(unit_key), "after": spa_get_slot(unit_key)}

        st = spa_ensure_state()
        d = _spa_defaults_obj(st)
        mb = max(0, _spa_to_int(d.get("max_bonus_per_tech", 1000), 1000))

        uk = _spa_normalize_unit_key(unit_key)
        slot = spa_get_slot(uk)
        before = dict(slot)

        tb = dict(slot.get("tech_bonus", {}) if isinstance(slot.get("tech_bonus", {}), dict) else {})
        old = max(0, _spa_to_int(tb.get(tid, 0), 0))
        target = _spa_clamp(new_bonus, 0, mb)

        available = max(0, _spa_to_int(slot.get("available", 0), 0))
        spent_wo_old = max(0, _spa_to_int(slot.get("spent", 0), 0) - old)

        if spent_wo_old + target > available:
            return {
                "ok": False,
                "reason": "over_budget",
                "before": before,
                "after": before,
            }

        if target <= 0:
            if tid in tb:
                del tb[tid]
        else:
            tb[tid] = int(target)

        slot["tech_bonus"] = tb
        slot = _spa_recompute_slot_data(slot, d)

        slots = st.get("slots", {}) if isinstance(st.get("slots", {}), dict) else {}
        slots[uk] = slot
        st["slots"] = slots
        S.battle_point_alloc = st

        if save:
            spa_save_persistent()

        return {
            "ok": True,
            "reason": "ok",
            "before": before,
            "after": dict(slot),
        }

    def spa_add_bonus(unit_key, tech_id, delta, save=True):
        cur = spa_get_bonus(unit_key, tech_id)
        dd = max(0, _spa_to_int(delta, 0))
        return spa_set_bonus(unit_key, tech_id, cur + dd, save=save)

    def spa_sub_bonus(unit_key, tech_id, delta, save=True):
        cur = spa_get_bonus(unit_key, tech_id)
        dd = max(0, _spa_to_int(delta, 0))
        return spa_set_bonus(unit_key, tech_id, cur - dd, save=save)

    def spa_reset_slot(unit_key, save=True):
        st = spa_ensure_state()
        d = _spa_defaults_obj(st)
        uk = _spa_normalize_unit_key(unit_key)

        slot = {
            "available": int(d.get("available_points_per_slot", 2000)),
            "spent": 0,
            "remaining": int(d.get("available_points_per_slot", 2000)),
            "tech_bonus": {}
        }
        slot = _spa_recompute_slot_data(slot, d)

        slots = st.get("slots", {}) if isinstance(st.get("slots", {}), dict) else {}
        slots[uk] = slot
        st["slots"] = slots
        S.battle_point_alloc = st

        if save:
            spa_save_persistent()

        return dict(slot)

    def spa_reset_all(save=True):
        st = spa_ensure_state()
        st["slots"] = {}
        st = _spa_compact_state(st)
        S.battle_point_alloc = st

        if save:
            spa_save_persistent()

        return dict(st)

    def spa_get_base_value(tech_id):
        tid = str(tech_id or "").strip()
        if not tid:
            return 0

        fn_base = getattr(S, "reiatsu_energy_base", None)
        if callable(fn_base):
            data = fn_base(tid)
            if isinstance(data, dict):
                return max(0, _spa_to_int(data.get("value", 0), 0))

        stats = getattr(S, "TECH_STATS", {})
        if isinstance(stats, dict):
            return max(0, _spa_to_int(stats.get(tid, {}).get("value", 0), 0))
        return 0

    def spa_get_final_value(unit_key, tech_id):
        base = spa_get_base_value(tech_id)
        bonus = spa_get_bonus(unit_key, tech_id)
        return max(0, _spa_to_int(base, 0) + _spa_to_int(bonus, 0))

    def spa_snapshot():
        st = spa_ensure_state()
        return _spa_compact_state(st)

    def spa_save_persistent():
        if not bool(getattr(S, "slot_points_persistence_enabled", True)):
            return False

        st = spa_snapshot()

        p = getattr(S, "persistent", None)
        if p is None:
            return False

        p.battle_point_alloc_v1 = st

        # opcional: forzar guardado inmediato si existe la API
        if hasattr(renpy, "save_persistent"):
            try:
                renpy.save_persistent()
            except:
                pass

        return True

    def spa_load_persistent():
        if not bool(getattr(S, "slot_points_persistence_enabled", True)):
            return False

        p = getattr(S, "persistent", None)
        if p is None:
            return False

        data = getattr(p, "battle_point_alloc_v1", None)
        if not isinstance(data, dict):
            return False

        S.battle_point_alloc = _spa_compact_state(data)
        return True

    def spa_load_or_init():
        loaded = spa_load_persistent()
        if not loaded:
            spa_ensure_state()
        return bool(loaded)

    # Autoload 1 sola vez por sesión
    if not bool(getattr(S, "battle_point_alloc_autoload_done", False)):
        spa_load_or_init()
        S.battle_point_alloc_autoload_done = True

    # -----------------------------------------------------------
    # Export API pública
    # -----------------------------------------------------------
    S.spa_ensure_state = spa_ensure_state
    S.spa_set_defaults = spa_set_defaults
    S.spa_is_enabled = spa_is_enabled
    S.spa_ensure_slot = spa_ensure_slot
    S.spa_get_slot = spa_get_slot
    S.spa_get_available = spa_get_available
    S.spa_get_spent = spa_get_spent
    S.spa_get_remaining = spa_get_remaining
    S.spa_get_bonus = spa_get_bonus
    S.spa_set_available = spa_set_available
    S.spa_set_bonus = spa_set_bonus
    S.spa_add_bonus = spa_add_bonus
    S.spa_sub_bonus = spa_sub_bonus
    S.spa_reset_slot = spa_reset_slot
    S.spa_reset_all = spa_reset_all
    S.spa_get_base_value = spa_get_base_value
    S.spa_get_final_value = spa_get_final_value
    S.spa_snapshot = spa_snapshot
    S.spa_save_persistent = spa_save_persistent
    S.spa_load_persistent = spa_load_persistent
    S.spa_load_or_init = spa_load_or_init
