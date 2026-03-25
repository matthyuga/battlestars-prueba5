# ===============================================================
# 10A_RPG_PANEL_CORE_V1.rpy
# Fase 1 — Core de cálculo panel de asignación RPG (Ren'Py)
# ===============================================================

init -880 python:
    import copy

    # -------------------------
    # Constantes de contrato v1
    # -------------------------
    RPGP_MAX_LEVEL = 500
    RPGP_MAX_REGISTER = 50
    RPGP_EXP_MAX = 100

    RPGP_BASE_HP = 1000
    RPGP_BASE_ENERGY = 100
    RPGP_BASE_REIATSU = 1000

    RPGP_POOL_INITIAL = 200
    RPGP_POOL_PER_REGISTER = 100

    RPGP_STAT_SOFT_CAP = 20
    RPGP_STAT_HARD_CAP = 25

    RPGP_MAIN_STATS = ("fuerza", "agilidad", "resistencia", "inteligencia", "espiritu")
    RPGP_UTILITY_STATS = ("suerte", "carisma", "percepcion")
    RPGP_ALL_STATS = RPGP_MAIN_STATS + RPGP_UTILITY_STATS

    RPGP_PRINCIPAL_BUCKETS = ("ataque", "defensa", "hp", "reiatsu", "energia")
    RPGP_PRINCIPAL_ALLOWED_STEPS = (0, 25, 50, 75, 100)
    RPGP_PRINCIPAL_MAX_ACTIVE_BUCKETS = 4

    # +100 por punto según contrato
    RPGP_STAT_EFFECT_KEYS = {
        "fuerza": "ataque",
        "agilidad": "defensa",
        "resistencia": "hp",
        "inteligencia": "energia",
        "espiritu": "reiatsu",
    }

    # Tier blocks para caps (idénticos a la planilla de registros)
    RPGP_TIER_BLOCKS = (
        ("D", 0, 1, 900, 1000, 1.00),
        ("C", 2, 3, 2000, 2300, 1.00),
        ("B", 4, 5, 5000, 5500, 1.00),
        ("A", 6, 7, 12000, 13000, 1.00),
        ("S", 8, 9, 25000, 27000, 0.95),
        ("SS", 10, 29, 80000, 90000, 0.85),
        ("SSS", 30, 50, 200000, 240000, 0.75),
    )

    def _rpgp_to_int(v, default=0):
        try:
            return int(v)
        except:
            return int(default)

    def _rpgp_clamp(v, lo, hi):
        vv = _rpgp_to_int(v, lo)
        if vv < lo:
            return lo
        if vv > hi:
            return hi
        return vv

    def _rpgp_empty_distribution():
        return {k: 0 for k in RPGP_PRINCIPAL_BUCKETS}

    def _rpgp_empty_stats():
        return {k: 0 for k in RPGP_ALL_STATS}

    def _rpgp_default_state():
        register = compute_register(1)
        total_pool = compute_pool_total(register)
        st = {
            "player": {
                "level": 1,
                "max_level": RPGP_MAX_LEVEL,
                "register": register,
                "max_register": RPGP_MAX_REGISTER,
                "exp_current": 0,
                "exp_max": RPGP_EXP_MAX,
            },
            "pending": {
                "stat_points": 0,
                "tech_pool_points": total_pool,
            },
            "stats": _rpgp_empty_stats(),
            "limits": {
                "stat_soft_cap": RPGP_STAT_SOFT_CAP,
                "stat_hard_cap": RPGP_STAT_HARD_CAP,
            },
            "principal": {
                "selected": None,
                "distribution": _rpgp_empty_distribution(),
                "distribution_total": 0,
                "active_slots": 0,
                "max_slots": RPGP_PRINCIPAL_MAX_ACTIVE_BUCKETS,
            },
            "pool": {
                "base_initial": RPGP_POOL_INITIAL,
                "per_register_gain": RPGP_POOL_PER_REGISTER,
                "total": total_pool,
                "offensive_spent": 0,
                "defensive_spent": 0,
                "available": total_pool,
            },
            "mode": {
                "view": "pve",
            },
            "preview": {
                "hp_before": RPGP_BASE_HP,
                "hp_after": RPGP_BASE_HP,
                "energia_before": RPGP_BASE_ENERGY,
                "energia_after": RPGP_BASE_ENERGY,
                "reiatsu_before": RPGP_BASE_REIATSU,
                "reiatsu_after": RPGP_BASE_REIATSU,
                "atk_before": 0,
                "atk_after": 0,
                "def_before": 0,
                "def_after": 0,
            },
            "validation": {
                "is_valid": False,
                "errors": [],
                "warnings": [],
            },
        }
        return st

    def _rpgp_recompute_principal_meta(state):
        principal = state.get("principal", {})
        dist = principal.get("distribution", {}) if isinstance(principal.get("distribution", {}), dict) else {}

        total = 0
        active = 0
        clean = {}
        for k in RPGP_PRINCIPAL_BUCKETS:
            v = _rpgp_to_int(dist.get(k, 0), 0)
            if v not in RPGP_PRINCIPAL_ALLOWED_STEPS:
                # normalizamos al paso válido más cercano inferior
                if v < 25:
                    v = 0
                elif v < 50:
                    v = 25
                elif v < 75:
                    v = 50
                elif v < 100:
                    v = 75
                else:
                    v = 100
            clean[k] = v
            total += v
            if v > 0:
                active += 1

        principal["distribution"] = clean
        principal["distribution_total"] = int(total)
        principal["active_slots"] = int(active)
        principal["max_slots"] = RPGP_PRINCIPAL_MAX_ACTIVE_BUCKETS
        state["principal"] = principal
        return state

    def _rpgp_tier_and_caps_for_register(register):
        reg = _rpgp_clamp(register, 0, RPGP_MAX_REGISTER)

        prev_off = 400
        prev_def = 450

        for name, rs, re, off_end, def_end, pvp_factor in RPGP_TIER_BLOCKS:
            if rs <= reg <= re:
                n = (re - rs + 1)
                off_start = prev_off + 1
                def_start = prev_def + 1
                idx = (reg - rs)
                t = (float(idx) / float(max(1, n - 1))) if n > 1 else 0.0

                off_base = int(round(off_start + (off_end - off_start) * t))
                def_base = int(round(def_start + (def_end - def_start) * t))

                return {
                    "tier": name,
                    "off_base": off_base,
                    "def_base": def_base,
                    "pvp_factor": float(pvp_factor),
                }

            prev_off = off_end
            prev_def = def_end

        # Fallback extremo (no debería ocurrir)
        return {
            "tier": "SSS",
            "off_base": 200000,
            "def_base": 240000,
            "pvp_factor": 0.75,
        }

    # ===================================================
    # API pública de Fase 1 (según contrato documental)
    # ===================================================

    def compute_register(level):
        lvl = _rpgp_clamp(level, 1, RPGP_MAX_LEVEL)
        if lvl <= 1:
            return 0
        reg = lvl // 10
        return _rpgp_clamp(reg, 0, RPGP_MAX_REGISTER)

    def compute_pool_total(register):
        reg = _rpgp_clamp(register, 0, RPGP_MAX_REGISTER)
        return int(RPGP_POOL_INITIAL + (reg * RPGP_POOL_PER_REGISTER))

    def compute_stat_effects(stats):
        st = stats if isinstance(stats, dict) else {}
        out = {"ataque": 0, "defensa": 0, "hp": 0, "energia": 0, "reiatsu": 0}
        for skey, target in RPGP_STAT_EFFECT_KEYS.items():
            vv = max(0, _rpgp_to_int(st.get(skey, 0), 0))
            out[target] += vv * 100
        return out

    def compute_principal_bonus(principal_selected, distribution):
        if principal_selected not in RPGP_MAIN_STATS:
            return {"ataque": 0, "defensa": 0, "hp": 0, "energia": 0, "reiatsu": 0}

        dist = distribution if isinstance(distribution, dict) else {}
        out = {"ataque": 0, "defensa": 0, "hp": 0, "energia": 0, "reiatsu": 0}
        for k in RPGP_PRINCIPAL_BUCKETS:
            v = _rpgp_to_int(dist.get(k, 0), 0)
            if v in RPGP_PRINCIPAL_ALLOWED_STEPS:
                out[k] = v
        return out

    def compute_caps_for_register(register, mode):
        base = _rpgp_tier_and_caps_for_register(register)
        md = str(mode or "pve").strip().lower()
        is_pvp = (md == "pvp")

        off_base = int(base["off_base"])
        def_base = int(base["def_base"])

        if is_pvp:
            off_value = int(round(off_base * base["pvp_factor"]))
            def_value = int(round(def_base * base["pvp_factor"]))
        else:
            off_value = off_base
            def_value = def_base

        return {
            "tier": base["tier"],
            "offensive_cap": int(off_value),
            "defensive_cap": int(def_value),
            "off_base": off_base,
            "def_base": def_base,
            "pvp_factor": float(base["pvp_factor"]),
        }

    def compute_preview(panel_state):
        st = copy.deepcopy(panel_state if isinstance(panel_state, dict) else _rpgp_default_state())

        player = st.get("player", {})
        level = _rpgp_clamp(player.get("level", 1), 1, RPGP_MAX_LEVEL)
        register = compute_register(level)
        player["level"] = level
        player["register"] = register
        player["max_level"] = RPGP_MAX_LEVEL
        player["max_register"] = RPGP_MAX_REGISTER
        player["exp_max"] = RPGP_EXP_MAX
        player["exp_current"] = _rpgp_clamp(player.get("exp_current", 0), 0, RPGP_EXP_MAX)
        st["player"] = player

        # stats normalizados
        stats = st.get("stats", {}) if isinstance(st.get("stats", {}), dict) else {}
        clean_stats = {}
        hard_cap = _rpgp_to_int(st.get("limits", {}).get("stat_hard_cap", RPGP_STAT_HARD_CAP), RPGP_STAT_HARD_CAP)
        for k in RPGP_ALL_STATS:
            clean_stats[k] = _rpgp_clamp(stats.get(k, 0), 0, hard_cap)
        st["stats"] = clean_stats

        # principal normalizado
        principal = st.get("principal", {}) if isinstance(st.get("principal", {}), dict) else {}
        sel = principal.get("selected", None)
        if sel not in RPGP_MAIN_STATS:
            principal["selected"] = None
        st["principal"] = principal
        st = _rpgp_recompute_principal_meta(st)

        # pool
        total_pool = compute_pool_total(register)
        pool = st.get("pool", {}) if isinstance(st.get("pool", {}), dict) else {}
        off_spent = max(0, _rpgp_to_int(pool.get("offensive_spent", 0), 0))
        def_spent = max(0, _rpgp_to_int(pool.get("defensive_spent", 0), 0))
        spent = off_spent + def_spent
        if spent > total_pool:
            overflow = spent - total_pool
            # recorte simple desde defensivo
            cut_def = min(def_spent, overflow)
            def_spent -= cut_def
            overflow -= cut_def
            if overflow > 0:
                off_spent = max(0, off_spent - overflow)
            spent = off_spent + def_spent

        available = max(0, total_pool - spent)
        pool["base_initial"] = RPGP_POOL_INITIAL
        pool["per_register_gain"] = RPGP_POOL_PER_REGISTER
        pool["total"] = int(total_pool)
        pool["offensive_spent"] = int(off_spent)
        pool["defensive_spent"] = int(def_spent)
        pool["available"] = int(available)
        st["pool"] = pool

        # pending (v1: por ahora espejo de available pool, stat_points definido por runtime)
        pending = st.get("pending", {}) if isinstance(st.get("pending", {}), dict) else {}
        pending["tech_pool_points"] = int(available)
        pending["stat_points"] = max(0, _rpgp_to_int(pending.get("stat_points", 0), 0))
        st["pending"] = pending

        # bonus
        stat_bonus = compute_stat_effects(clean_stats)
        principal_bonus = compute_principal_bonus(st.get("principal", {}).get("selected", None), st.get("principal", {}).get("distribution", {}))

        # preview before/after
        prev = st.get("preview", {}) if isinstance(st.get("preview", {}), dict) else {}
        prev["hp_before"] = RPGP_BASE_HP
        prev["energia_before"] = RPGP_BASE_ENERGY
        prev["reiatsu_before"] = RPGP_BASE_REIATSU
        prev["atk_before"] = 0
        prev["def_before"] = 0

        prev["hp_after"] = RPGP_BASE_HP + stat_bonus["hp"] + principal_bonus["hp"]
        prev["energia_after"] = RPGP_BASE_ENERGY + stat_bonus["energia"] + principal_bonus["energia"]
        prev["reiatsu_after"] = RPGP_BASE_REIATSU + stat_bonus["reiatsu"] + principal_bonus["reiatsu"]
        prev["atk_after"] = stat_bonus["ataque"] + principal_bonus["ataque"]
        prev["def_after"] = stat_bonus["defensa"] + principal_bonus["defensa"]
        st["preview"] = prev

        st["validation"] = validate_panel_state(st)
        return st

    def validate_panel_state(panel_state):
        st = panel_state if isinstance(panel_state, dict) else _rpgp_default_state()
        errors = []
        warnings = []

        principal = st.get("principal", {}) if isinstance(st.get("principal", {}), dict) else {}
        selected = principal.get("selected", None)
        if selected not in RPGP_MAIN_STATS:
            errors.append("Debes seleccionar un atributo principal.")

        dist = principal.get("distribution", {}) if isinstance(principal.get("distribution", {}), dict) else {}
        active = 0
        total = 0
        for k in RPGP_PRINCIPAL_BUCKETS:
            v = _rpgp_to_int(dist.get(k, 0), 0)
            if v not in RPGP_PRINCIPAL_ALLOWED_STEPS:
                errors.append("Distribución inválida en '%s'." % k)
            if v > 0:
                active += 1
            total += v

        if total != 100:
            errors.append("La distribución del principal debe sumar exactamente 100.")

        if active > RPGP_PRINCIPAL_MAX_ACTIVE_BUCKETS:
            errors.append("No puedes activar más de 4 categorías del principal.")

        pool = st.get("pool", {}) if isinstance(st.get("pool", {}), dict) else {}
        total_pool = _rpgp_to_int(pool.get("total", 0), 0)
        off_spent = _rpgp_to_int(pool.get("offensive_spent", 0), 0)
        def_spent = _rpgp_to_int(pool.get("defensive_spent", 0), 0)
        if off_spent < 0 or def_spent < 0:
            errors.append("No se permiten valores negativos en el pool técnico.")

        if (off_spent + def_spent) > total_pool:
            errors.append("Intento de gasto de pool superior al disponible.")

        # caps por tier/mode
        player = st.get("player", {}) if isinstance(st.get("player", {}), dict) else {}
        register = compute_register(player.get("level", 1))
        mode = st.get("mode", {}).get("view", "pve") if isinstance(st.get("mode", {}), dict) else "pve"
        caps = compute_caps_for_register(register, mode)

        if off_spent > caps["offensive_cap"]:
            errors.append("Excedes cap ofensivo para el registro/modo actual.")
        if def_spent > caps["defensive_cap"]:
            errors.append("Excedes cap defensivo para el registro/modo actual.")

        # warning suave: utilitarios altos sin inversión de combate
        stats = st.get("stats", {}) if isinstance(st.get("stats", {}), dict) else {}
        util_total = sum(max(0, _rpgp_to_int(stats.get(k, 0), 0)) for k in RPGP_UTILITY_STATS)
        combat_total = sum(max(0, _rpgp_to_int(stats.get(k, 0), 0)) for k in RPGP_MAIN_STATS)
        if util_total > 0 and combat_total == 0:
            warnings.append("Tienes inversión utilitaria sin stats de combate.")

        return {
            "is_valid": (len(errors) == 0),
            "errors": errors,
            "warnings": warnings,
        }

    # ------------------------
    # Helpers de semillas QA
    # ------------------------
    def rpgp_seed_new_player():
        st = _rpgp_default_state()
        return compute_preview(st)

    def rpgp_seed_reg10_balanced():
        st = _rpgp_default_state()
        st["player"]["level"] = 100
        st["stats"].update({
            "fuerza": 3,
            "agilidad": 3,
            "resistencia": 2,
            "inteligencia": 1,
            "espiritu": 1,
        })
        st["principal"]["selected"] = "agilidad"
        st["principal"]["distribution"].update({
            "ataque": 25,
            "defensa": 50,
            "hp": 0,
            "reiatsu": 0,
            "energia": 25,
        })
        st["pool"]["offensive_spent"] = 600
        st["pool"]["defensive_spent"] = 600
        return compute_preview(st)

    def rpgp_seed_reg35_specialized():
        st = _rpgp_default_state()
        st["player"]["level"] = 350
        st["stats"].update({
            "fuerza": 18,
            "agilidad": 10,
            "resistencia": 8,
            "inteligencia": 4,
            "espiritu": 5,
            "suerte": 2,
        })
        st["principal"]["selected"] = "fuerza"
        st["principal"]["distribution"].update({
            "ataque": 75,
            "defensa": 25,
            "hp": 0,
            "reiatsu": 0,
            "energia": 0,
        })
        st["pool"]["offensive_spent"] = 70000
        st["pool"]["defensive_spent"] = 40000
        st["mode"]["view"] = "pve"
        return compute_preview(st)


default rpg_panel_state_v1 = None

default rpg_panel_state_seed_name = "new_player"

label rpgp_debug_bootstrap_v1:
    $ rpg_panel_state_v1 = rpgp_seed_new_player()
    $ rpg_panel_state_seed_name = "new_player"
    return

label rpgp_debug_seed_reg10:
    $ rpg_panel_state_v1 = rpgp_seed_reg10_balanced()
    $ rpg_panel_state_seed_name = "reg10_balanced"
    return

label rpgp_debug_seed_reg35:
    $ rpg_panel_state_v1 = rpgp_seed_reg35_specialized()
    $ rpg_panel_state_seed_name = "reg35_specialized"
    return
