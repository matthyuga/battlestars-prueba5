# ============================================================
# 03_TECH_STATS_DATASET.RPY – Dataset dinámico de técnicas
# ============================================================
# Versión: v7.4 Hardened + CrossValidation (NO LEGACY)
# ------------------------------------------------------------
# - TECH_SCALE (casillas hasta subir energía)
# - TECH_STATS (valores editables por jugador/IA)
# - Reiatsu = 1:1 del valor base
# - Energía por bloques (10 / 20 / 30 / 40...)
# - Técnicas especiales sin entrada → costo 0 (focus/boost)
# - ✅ Validación cruzada contra battle_techniques (si existe)
# - ✅ Export a renpy.store (S.TECH_STATS, S.TECH_SCALE, helpers)
# ============================================================

init -970 python:

    import renpy.store as S

    # ------------------------------------------------------------
    # 🔒 Técnicas especiales SIN costo (no están en TECH_STATS)
    # ------------------------------------------------------------
    SPECIAL_ZERO_COST = set([
        "focus",          # Concentrar
        "defense_boost",  # Potenciar
    ])

    # ------------------------------------------------------------
    # 📌 TABLA DE ESCALAS (cuántas casillas para subir energía)
    # ------------------------------------------------------------
    TECH_SCALE = {
        "extra_attack":         9,
        "extra_tech":           7,
        "attack_reducer":       5,
        "direct_attack":        6,
        "noatk_attack":         6,
        "stronger_attack":      9,

        # defensivas modernas
        "defense_extra":        9,
        "defense_reducer":      5,
        "defense_reflect":      4,
        "defense_strong_block": 9,
    }

    # ------------------------------------------------------------
    # 📌 VALORES BASE por técnica (dam/def personalizable)
    # ------------------------------------------------------------
    TECH_STATS = {
        "extra_attack":         {"value": 100},
        "extra_tech":           {"value": 100},
        "attack_reducer":       {"value": 100},
        "direct_attack":        {"value": 100},
        "noatk_attack":         {"value": 100},
        "stronger_attack":      {"value": 100},

        # defensivas modernas
        "defense_extra":        {"value": 100},
        "defense_reducer":      {"value": 100},
        "defense_reflect":      {"value": 100},
        "defense_strong_block": {"value": 100},
    }

    # ============================================================
    # 📌 FUNCIÓN: Reiatsu = valor 1:1
    # ============================================================
    def calc_reiatsu(value):
        try:
            return int(value)
        except:
            return 0

    # ============================================================
    # 📌 FUNCIÓN: Energía por bloques según escala
    # - value=100..199 -> 10
    # - sube 10 cada "scale" casillas de 100
    # ============================================================
    def calc_energy(value, scale):
        try:
            v = int(value)
            sc = max(1, int(scale))
        except:
            v = 0
            sc = 1

        # clamp mínimo lógico
        if v < 100:
            v = 100

        cell  = v // 100              # 100 -> 1, 200 -> 2, ...
        block = (cell - 1) // sc      # 0.. según escala
        return 10 + block * 10

    # ============================================================
    # 📌 FUNCIÓN PRINCIPAL: Obtener costos de técnica (SEGURA)
    # ============================================================
    def get_tech_costs(tech_id):

        # None o vacío → costo 0
        if tech_id is None:
            return {"value": 0, "reiatsu": 0, "energy": 0, "scale": 1}

        # Técnicas especiales o desconocidas → costo 0
        if (tech_id in SPECIAL_ZERO_COST) or (tech_id not in TECH_STATS):
            return {
                "value":   0,
                "reiatsu": 0,
                "energy":  0,
                "scale":   TECH_SCALE.get(tech_id, 1),
            }

        # Valor base
        try:
            value = int(TECH_STATS.get(tech_id, {}).get("value", 0))
        except:
            value = 0

        if value < 100:
            value = 100

        rei   = calc_reiatsu(value)
        scale = TECH_SCALE.get(tech_id, 9)
        ene   = calc_energy(value, scale)

        return {
            "value":   value,
            "reiatsu": rei,
            "energy":  ene,
            "scale":   scale
        }

    # ============================================================
    # 📌 FUNCIÓN: Modificar valor de técnica (con guardas)
    # ============================================================
    def set_tech_value(tech_id, new_value):

        # No tocar especiales
        if tech_id in SPECIAL_ZERO_COST:
            return False

        # Si no existe, no creamos silenciosamente (evita basura)
        if tech_id not in TECH_STATS:
            return False

        try:
            v = int(new_value)
        except:
            return False

        if v < 100:  v = 100
        if v > 5000: v = 5000

        TECH_STATS[tech_id]["value"] = int(v)
        return True

    # ============================================================
    # ⭐ FUNCIÓN universal para verificar recursos
    # ============================================================
    def can_afford(tech_id, actor="player"):
        c = get_tech_costs(tech_id)
        rei = int(c.get("reiatsu", 0) or 0)
        ene = int(c.get("energy", 0) or 0)

        if actor == "enemy":
            return (getattr(S, "enemy_reiatsu", 0) >= rei) and (getattr(S, "enemy_energy", 0) >= ene)

        return (getattr(S, "player_reiatsu", 0) >= rei) and (getattr(S, "player_energy", 0) >= ene)

    # ============================================================
    # ⭐ FUNCIÓN de consumo SEGURO (actor)
    # ============================================================
    def pay_costs(tech_id, actor="player"):
        c = get_tech_costs(tech_id)
        rei = int(c.get("reiatsu", 0) or 0)
        ene = int(c.get("energy", 0) or 0)

        if actor == "enemy":
            S.enemy_reiatsu = max(0, int(getattr(S, "enemy_reiatsu", 0)) - rei)
            S.enemy_energy  = max(0, int(getattr(S, "enemy_energy", 0))  - ene)
            return rei, ene

        S.player_reiatsu = max(0, int(getattr(S, "player_reiatsu", 0)) - rei)
        S.player_energy  = max(0, int(getattr(S, "player_energy", 0))  - ene)
        return rei, ene

    # ============================================================
    # ✅ VALIDACIÓN CRUZADA contra battle_techniques (si existe)
    # - asegura que toda técnica MODERNA usada tenga TECH_STATS/TECH_SCALE
    # - ignora specials (costo 0) y legacy (tech["legacy"]==True)
    # ============================================================
    def tech_stats_validate_against_battle_techniques(show_log=False):
        bt = getattr(S, "battle_techniques", None)

        # Si todavía no cargó el dataset de técnicas, no rompemos.
        if not isinstance(bt, dict):
            return True

        missing_stats = []
        missing_scale = []

        for key, tech in bt.items():
            if not isinstance(tech, dict):
                continue

            # ignorar especiales por definición
            if key in SPECIAL_ZERO_COST:
                continue

            # ignorar legacy marcados en dataset de técnicas (si existieran)
            if tech.get("legacy", False):
                continue

            ttype = tech.get("type")
            if ttype not in ("offensive", "defensive"):
                # specials/otros no requieren TECH_STATS
                continue

            # Requerir stats/scale para pipeline moderno
            if key not in TECH_STATS:
                missing_stats.append(key)
            if key not in TECH_SCALE:
                missing_scale.append(key)

        ok = (len(missing_stats) == 0 and len(missing_scale) == 0)

        if show_log:
            try:
                if ok:
                    renpy.say(None, "[CHECK] TECH_STATS/TECH_SCALE OK vs battle_techniques (NO LEGACY).")
                else:
                    msg = "[CHECK] Faltan entradas:"
                    if missing_stats:
                        msg += "\n - TECH_STATS: " + ", ".join(missing_stats)
                    if missing_scale:
                        msg += "\n - TECH_SCALE: " + ", ".join(missing_scale)
                    renpy.say(None, msg)
            except:
                pass

        return ok

    # ------------------------------------------------------------
    # Export a store (para que 04X/selector/IA puedan importarlo)
    # ------------------------------------------------------------
    S.TECH_SCALE = TECH_SCALE
    S.TECH_STATS = TECH_STATS
    S.SPECIAL_ZERO_COST = SPECIAL_ZERO_COST

    S.calc_reiatsu = calc_reiatsu
    S.calc_energy  = calc_energy
    S.get_tech_costs = get_tech_costs
    S.set_tech_value = set_tech_value
    S.can_afford = can_afford
    S.pay_costs  = pay_costs
    S.tech_stats_validate_against_battle_techniques = tech_stats_validate_against_battle_techniques
