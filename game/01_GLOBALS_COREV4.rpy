# ===========================================================
# 01_GLOBALS_CORE.RPY – Estado base del combate + Focus/Boost
# ===========================================================
# v3.0 FocusCharges+Decay Edition (LegacyCompat)
# -----------------------------------------------------------
# - Mantiene estado base del combate (turn state, winner, etc.)
# - Focus/Boost migrados a sistema por CARGAS (0..2 => x1/x2/x4)
# - Decay suave por turnos sin consumir (pierde 1 carga al 2º turno idle)
# - focus_cost_active queda SOLO como compat legacy (NO SSOT de costos)
# - reset_focus_multipliers resetea cargas + compat legacy flag
# ===========================================================

init -985 python:

    import renpy.store as S

    # -----------------------------
    # Estado maestro de combate
    # -----------------------------
    if not hasattr(S, "battle_turn_state"):    S.battle_turn_state = "offensive"
    if not hasattr(S, "battle_active"):        S.battle_active = False
    if not hasattr(S, "battle_first_turn"):    S.battle_first_turn = True
    if not hasattr(S, "battle_winner"):        S.battle_winner = None

    # Player/enemy (si tu get_character existe acá)
    try:
        if not hasattr(S, "battle_player"): S.battle_player = get_character("Harribel")
        if not hasattr(S, "battle_enemy"):  S.battle_enemy  = get_character("Hollow")
    except:
        pass

    # Multiplicadores antiguos (deprecated, quedan por compat)
    if not hasattr(S, "battle_attack_multiplier"):  S.battle_attack_multiplier  = 1.0
    if not hasattr(S, "battle_defense_multiplier"): S.battle_defense_multiplier = 1.0

    # Técnicas usadas (log/hud)
    if not hasattr(S, "battle_turn_tech_sequence"): S.battle_turn_tech_sequence = []

    def battle_register_technique(name, dmg):
        try:
            S.battle_turn_tech_sequence.append({"name": name, "damage": dmg})
        except:
            pass

    def battle_reset_tech_sequence():
        S.battle_turn_tech_sequence = []

    def battle_reset_state():
        S.battle_attack_multiplier  = 1.0
        S.battle_defense_multiplier = 1.0


# ===========================================================
# 🔥 CONCENTRAR OFENSIVO – Sistema por CARGAS (x2 / x4) + Decay suave
# ===========================================================
init -984 python:
    import renpy.store as S

    FOCUS_OFF_CAN_STORE   = True
    FOCUS_OFF_MAX_CHARGES = 2  # 0..2 -> x1/x2/x4

    # Bootstrap (save/rollback safe)
    if not hasattr(S, "focus_off_charges"): S.focus_off_charges = 0
    if not hasattr(S, "focus_off_decay"):   S.focus_off_decay   = 0
    if not hasattr(S, "focus_off_consumed_this_turn"): S.focus_off_consumed_this_turn = False

    # Compat legacy (NO SSOT de costos)
    if not hasattr(S, "focus_cost_active"): S.focus_cost_active = False

    def offensive_focus_multiplier_peek():
        try:
            c = int(S.focus_off_charges or 0)
        except:
            c = 0
        if c <= 0: return 1
        if c == 1: return 2
        return 4

    def activate_offensive_focus():
        try:
            c = int(S.focus_off_charges or 0)
        except:
            c = 0
        c += 1
        if c > FOCUS_OFF_MAX_CHARGES:
            c = FOCUS_OFF_MAX_CHARGES
        S.focus_off_charges = c

        # seguridad: legacy flag no gobierna costos
        S.focus_cost_active = False

    def apply_offensive_focus(value):
        mult = offensive_focus_multiplier_peek()
        if mult <= 1:
            return value

        try:
            result = int(int(value) * int(mult))
        except:
            try:
                result = int(value * mult)
            except:
                result = value

        S.focus_off_charges = 0
        S.focus_off_decay   = 0
        S.focus_off_consumed_this_turn = True
        S.focus_cost_active = False
        return result

    def focus_off_end_turn_decay():
        if not FOCUS_OFF_CAN_STORE:
            S.focus_off_charges = 0
            S.focus_off_decay = 0
            S.focus_off_consumed_this_turn = False
            return

        if getattr(S, "focus_off_consumed_this_turn", False):
            S.focus_off_decay = 0
            S.focus_off_consumed_this_turn = False
            return

        try:
            c = int(S.focus_off_charges or 0)
        except:
            c = 0

        if c > 0:
            try:
                d = int(S.focus_off_decay or 0)
            except:
                d = 0

            if d >= 1:
                c = max(0, c - 1)
                S.focus_off_charges = c

            S.focus_off_decay = 1

        S.focus_off_consumed_this_turn = False
        S.focus_cost_active = False

    # Export
    S.offensive_focus_multiplier_peek = offensive_focus_multiplier_peek
    S.activate_offensive_focus        = activate_offensive_focus
    S.apply_offensive_focus           = apply_offensive_focus
    S.focus_off_end_turn_decay        = focus_off_end_turn_decay


# ===========================================================
# 🔵 POTENCIAR DEFENSIVO – Sistema por CARGAS (x2 / x4) + Decay suave
# ===========================================================
init -983 python:
    import renpy.store as S

    BOOST_DEF_CAN_STORE   = True
    BOOST_DEF_MAX_CHARGES = 2

    if not hasattr(S, "boost_def_charges"): S.boost_def_charges = 0
    if not hasattr(S, "boost_def_decay"):   S.boost_def_decay   = 0
    if not hasattr(S, "boost_def_consumed_this_turn"): S.boost_def_consumed_this_turn = False

    def defensive_boost_multiplier_peek():
        try:
            c = int(S.boost_def_charges or 0)
        except:
            c = 0
        if c <= 0: return 1
        if c == 1: return 2
        return 4

    def activate_defensive_focus():
        try:
            c = int(S.boost_def_charges or 0)
        except:
            c = 0
        c += 1
        if c > BOOST_DEF_MAX_CHARGES:
            c = BOOST_DEF_MAX_CHARGES
        S.boost_def_charges = c

    def apply_defensive_focus(value):
        mult = defensive_boost_multiplier_peek()
        if mult <= 1:
            return value

        try:
            result = int(int(value) * int(mult))
        except:
            try:
                result = int(value * mult)
            except:
                result = value

        S.boost_def_charges = 0
        S.boost_def_decay   = 0
        S.boost_def_consumed_this_turn = True
        return result

    def boost_def_end_turn_decay():
        if not BOOST_DEF_CAN_STORE:
            S.boost_def_charges = 0
            S.boost_def_decay = 0
            S.boost_def_consumed_this_turn = False
            return

        if getattr(S, "boost_def_consumed_this_turn", False):
            S.boost_def_decay = 0
            S.boost_def_consumed_this_turn = False
            return

        try:
            c = int(S.boost_def_charges or 0)
        except:
            c = 0

        if c > 0:
            try:
                d = int(S.boost_def_decay or 0)
            except:
                d = 0

            if d >= 1:
                c = max(0, c - 1)
                S.boost_def_charges = c

            S.boost_def_decay = 1

        S.boost_def_consumed_this_turn = False

    S.defensive_boost_multiplier_peek = defensive_boost_multiplier_peek
    S.activate_defensive_focus        = activate_defensive_focus
    S.apply_defensive_focus           = apply_defensive_focus
    S.boost_def_end_turn_decay        = boost_def_end_turn_decay


# ===========================================================
# 🧹 RESET SEGURO (cargas + compat legacy)
# ===========================================================
init -982 python:
    import renpy.store as S

    def reset_focus_multipliers():
        S.focus_off_charges = 0
        S.focus_off_decay = 0
        S.focus_off_consumed_this_turn = False

        S.boost_def_charges = 0
        S.boost_def_decay = 0
        S.boost_def_consumed_this_turn = False

        # compat legacy
        try:
            S.focus_cost_active = False
        except:
            pass

    S.reset_focus_multipliers = reset_focus_multipliers
