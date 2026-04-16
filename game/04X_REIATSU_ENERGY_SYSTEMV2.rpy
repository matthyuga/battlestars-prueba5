# ===============================================================
# 04X_REIATSU_ENERGY_SYSTEM.rpy
# Sistema central de Costos (Reiatsu / Energía)
# ===============================================================
# Versión v5.4 – Single Source of Truth + Charges Focus Safe
# ---------------------------------------------------------------
# - Daño y costo SIEMPRE sincronizados
# - Soporta Focus / Potenciar con cargas (x2 / x4)
# - Compatible Ren'Py 7.4.9 (Python 2.7)
# ===============================================================

init -950 python:

    import renpy.store as S

    # -----------------------------------------------------------
    # 🔧 Helpers base: acceso seguro a datasets
    # -----------------------------------------------------------
    def _get_tech_stats():
        return getattr(S, "TECH_STATS", {}) or {}

    def _get_tech_scale():
        return getattr(S, "TECH_SCALE", {}) or {}

    def _calc_energy(value, scale):
        fn = getattr(S, "calc_energy", None)
        if callable(fn):
            try:
                return int(fn(value, scale))
            except:
                pass

        # fallback simple por bloques
        try:
            v = int(value or 0)
        except:
            v = 0
        if v < 100:
            v = 100
        try:
            sc = int(scale or 1)
        except:
            sc = 1
        if sc < 1:
            sc = 1

        cell  = v // 100
        block = (cell - 1) // sc
        return 10 + block * 10

    # -----------------------------------------------------------
    # ✅ Técnicas especiales (costo 0)
    # -----------------------------------------------------------
    def _is_special_zero_cost(tech_id):
        zero = getattr(S, "SPECIAL_ZERO_COST", None)
        if isinstance(zero, (set, list, tuple)):
            return tech_id in zero
        return tech_id in ("focus", "defense_boost", "strong_attack")

    def _is_basic_no_energy(tech_id):
        ids = getattr(S, "BASIC_NO_ENERGY", None)
        if isinstance(ids, (set, list, tuple)):
            return tech_id in ids
        return tech_id in ("stronger_attack", "defense_strong_block")

    # -----------------------------------------------------------
    # ✅ Detectar objetivo real de Focus / Potenciar por cola
    # -----------------------------------------------------------
    def focus_target_from_queue(queue, mode):
        try:
            q = list(queue or [])
        except:
            q = []

        # helper del selector (si existe)
        idx = None
        try:
            fn = getattr(S, "selector_find_focus_target_index", None)
            if callable(fn):
                idx = fn(q, mode)
        except:
            idx = None

        if idx is not None:
            try:
                idx = int(idx)
                if 0 <= idx < len(q):
                    return q[idx]
            except:
                pass
            return None

        # fallback local
        focus_seen = False
        boost_seen = False

        for name in q:
            if mode == "offensive":
                if name in ("Concentrar", "Concentrar x2"):
                    focus_seen = True
                    continue
                if focus_seen:
                    return name
            else:
                if name == "Potenciar":
                    boost_seen = True
                    continue
                if boost_seen:
                    return name

        return None

    def focus_affects_this_action(action_name, queue, mode):
        tgt = focus_target_from_queue(queue, mode)
        return (tgt is not None) and (str(tgt) == str(action_name))

    # -----------------------------------------------------------
    # 📌 1) Valores base (sin buffs)
    # -----------------------------------------------------------
    def reiatsu_energy_base(tech_id):
        if tech_id is None or _is_special_zero_cost(tech_id):
            return {"value": 0, "reiatsu": 0, "energy": 0, "scale": 1}

        stats = _get_tech_stats()
        scale_map = _get_tech_scale()

        try:
            value = int(stats.get(tech_id, {}).get("value", 0) or 0)
        except:
            value = 0
        if value < 100:
            value = 100

        scale = scale_map.get(tech_id, 1)
        reiatsu = int(value)
        energy  = 0 if _is_basic_no_energy(tech_id) else int(_calc_energy(value, scale))

        return {
            "value": value,
            "reiatsu": reiatsu,
            "energy": energy,
            "scale": scale
        }

    # -----------------------------------------------------------
    # 📌 2) Valor final real (base + bonus futuros)
    # -----------------------------------------------------------
    def final_value_factory(tech_id, user, unit_key=None):
        base_info = reiatsu_energy_base(tech_id)
        try:
            base_value = int(base_info.get("value", 0) or 0)
        except:
            base_value = 0

        if base_value <= 0:
            return 0

        # -------------------------------------------------------
        # Overlay por slot (Fase B): usa allocator si está activo
        # -------------------------------------------------------
        if unit_key is not None:
            fn_enabled = getattr(S, "spa_is_enabled", None)
            fn_final = getattr(S, "spa_get_final_value", None)
            if callable(fn_final):
                enabled = True
                if callable(fn_enabled):
                    try:
                        enabled = bool(fn_enabled())
                    except:
                        enabled = True
                if enabled:
                    try:
                        vv = int(fn_final(unit_key, tech_id))
                        if vv >= 0:
                            return vv
                    except:
                        pass

        # Fallback actual (sin bonus externos)
        bonus = 0  # placeholder

        try:
            value_final = int(base_value) + int(bonus)
        except:
            value_final = base_value

        if value_final < 0:
            value_final = 0

        return int(value_final)

    # -----------------------------------------------------------
    # 📌 3) COSTO FINAL — SINGLE SOURCE OF TRUTH
    # -----------------------------------------------------------
    def reiatsu_energy_dynamic_cost(tech_id, user, **kwargs):
        """
        kwargs opcionales:
          action_name : nombre visible en selector
          queue       : cola de acciones (strings)
          mode        : "offensive" | "defensive"
          force_focus_mult : override manual
          unit_key    : clave de unidad (team:slot), opcional
        """

        action_name = kwargs.get("action_name", None)
        queue       = kwargs.get("queue", None)
        mode        = kwargs.get("mode", None)
        force_focus_mult = kwargs.get("force_focus_mult", None)
        unit_key = kwargs.get("unit_key", None)

        if tech_id is None or _is_special_zero_cost(tech_id):
            return {
                "value_final": 0,
                "reiatsu_cost": 0,
                "energy_cost": 0,
                "mult_reiatsu": 1
            }

        value_final = final_value_factory(tech_id, user, unit_key=unit_key)

        try:
            reiatsu_cost = int(value_final)
        except:
            reiatsu_cost = 0

        base = reiatsu_energy_base(tech_id)
        try:
            scale = int(base.get("scale", 1) or 1)
        except:
            scale = 1
        if scale < 1:
            scale = 1

        # Energía escala por valor final (base + bonus por slot)
        # y mantiene independencia del multiplicador de focus.
        if _is_basic_no_energy(tech_id):
            energy_cost = 0
        else:
            try:
                energy_cost = int(_calc_energy(value_final, scale))
            except:
                try:
                    energy_cost = int(base.get("energy", 0) or 0)
                except:
                    energy_cost = 0

        mult = 1

        # -------------------------------------------------------
        # 1) Override explícito
        # -------------------------------------------------------
        if force_focus_mult is not None:
            try:
                mult = int(force_focus_mult)
            except:
                mult = 1

        # -------------------------------------------------------
        # 2) Target real por cola + PEEK del multiplicador (x2/x4)
        # -------------------------------------------------------
        elif action_name and queue and mode:
            if focus_affects_this_action(action_name, queue, mode):

                if mode == "offensive":
                    fn = getattr(S, "offensive_focus_multiplier_peek", None)
                    if callable(fn):
                        try:
                            mult = int(fn())
                        except:
                            mult = 2
                    else:
                        mult = 2

                elif mode == "defensive":
                    fn = getattr(S, "defensive_boost_multiplier_peek", None)
                    if callable(fn):
                        try:
                            mult = int(fn())
                        except:
                            mult = 2
                    else:
                        mult = 2

        # -------------------------------------------------------
        # 3) Fallback legacy (compatibilidad vieja)
        # -------------------------------------------------------
        elif getattr(S, "focus_cost_active", False):
            mult = 2

        # cap duro anti-bugs
        try:
            mult = int(mult)
        except:
            mult = 1
        if mult < 1:
            mult = 1
        if mult > 4:
            mult = 4

        try:
            reiatsu_cost = int(reiatsu_cost) * mult
        except:
            reiatsu_cost = 0

        if reiatsu_cost < 0:
            reiatsu_cost = 0
        if energy_cost < 0:
            energy_cost = 0

        return {
            "value_final": int(value_final or 0),
            "reiatsu_cost": int(reiatsu_cost),
            "energy_cost": int(energy_cost),
            "mult_reiatsu": int(mult)
        }

    # -----------------------------------------------------------
    # 📌 4) Consumo real de recursos (clamp-safe)
    # -----------------------------------------------------------
    def consume_resources(reiatsu_cost, energy_cost, actor="player"):
        try:
            r = int(reiatsu_cost or 0)
        except:
            r = 0
        try:
            e = int(energy_cost or 0)
        except:
            e = 0

        if r < 0: r = 0
        if e < 0: e = 0

        mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        consumed_r = r
        consumed_e = e

        can_consume_by_unit = callable(getattr(S, "bs_consume_unit_resources", None)) and callable(getattr(S, "bs_unit_key", None))

        if can_consume_by_unit:
            side = actor if actor in ("player", "enemy") else "player"
            slot = 0

            # En 2v2 respetamos owner_team/owner_slot del turno; en 1v1 usamos slot 0.
            if mode == "2v2" and callable(getattr(S, "bs_get_turn_ctx", None)):
                ctx = S.bs_get_turn_ctx() or {}
                side = str(ctx.get("owner_team", side) or side)
                slot = int(ctx.get("owner_slot", 0) or 0)
                if actor in ("player", "enemy"):
                    side = actor

            ukey = str(S.bs_unit_key(side, slot) or "")
            info = S.bs_consume_unit_resources(ukey, r, e)
            consumed_r = int(info.get("reiatsu_spent", 0) or 0)
            consumed_e = int(info.get("energy_spent", 0) or 0)

            # sincronizar aliases legacy para HUD/flujos 1v1 que leen player_* y enemy_*
            if callable(getattr(S, "bs_get_active_unit_key", None)) and callable(getattr(S, "bs_get_unit_resources", None)):
                try:
                    akt = str(S.bs_get_active_unit_key(side) or ukey)
                    rs = S.bs_get_unit_resources(akt)
                    if side == "enemy":
                        S.enemy_reiatsu = int(rs.get("reiatsu", 0) or 0)
                        S.enemy_energy = int(rs.get("energy", 0) or 0)
                    else:
                        S.player_reiatsu = int(rs.get("reiatsu", 0) or 0)
                        S.player_energy = int(rs.get("energy", 0) or 0)
                except:
                    pass
        else:
            if actor == "enemy":
                S.enemy_reiatsu = max(0, int(getattr(S, "enemy_reiatsu", 0) or 0) - r)
                S.enemy_energy  = max(0, int(getattr(S, "enemy_energy", 0)  or 0) - e)
            else:
                S.player_reiatsu = max(0, int(getattr(S, "player_reiatsu", 0) or 0) - r)
                S.player_energy  = max(0, int(getattr(S, "player_energy", 0)  or 0) - e)

        return consumed_r, consumed_e

    # -----------------------------------------------------------
    # Export a store (API pública)
    # -----------------------------------------------------------
    S.reiatsu_energy_base          = reiatsu_energy_base
    S.final_value_factory          = final_value_factory
    S.reiatsu_energy_dynamic_cost  = reiatsu_energy_dynamic_cost
    S.consume_resources            = consume_resources

    # helpers
    S.focus_target_from_queue      = focus_target_from_queue
    S.focus_affects_this_action    = focus_affects_this_action
