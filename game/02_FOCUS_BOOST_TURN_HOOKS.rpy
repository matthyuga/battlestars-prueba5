# ============================================================
# 02_FOCUS_BOOST_TURN_HOOKS.rpy – Turn Hooks centralizados
# ============================================================
# v1.1 – Charges-first + LegacyFallback
# ------------------------------------------------------------
# Objetivo:
# - Centralizar el “fin de turno” para Focus/Boost
# - Preferir sistema NUEVO por CARGAS:
#     - focus_off_end_turn_decay()
#     - boost_def_end_turn_decay()
# - Si esos no existen, fallback a legacy:
#     - carry_over_offensive_focus() + decay por stored_mult
#     - carry_over_defensive_focus() + decay por stored_mult
# ============================================================

init -984 python:
    import renpy.store as S

    # ----------------------------
    # Helpers legacy (solo si hace falta)
    # ----------------------------
    def _int(v, d=1):
        try:
            return int(v)
        except:
            return d

    def _legacy_get_base(which):
        if which == "off":
            return max(2, _int(getattr(S, "FOCUS_OFF_BASE", 2), 2))
        else:
            return max(2, _int(getattr(S, "BOOST_DEF_BASE", 2), 2))

    def _legacy_decay_one_charge(which):
        base = _legacy_get_base(which)

        if which == "off":
            sto_name = "focus_off_stored_mult"
        else:
            sto_name = "boost_def_stored_mult"

        sto = _int(getattr(S, sto_name, 1), 1)
        if sto > 1:
            sto = max(1, sto // base)
            setattr(S, sto_name, sto)

    # ----------------------------
    # Hook principal
    # ----------------------------
    def battle_focus_end_turn(mode, used_class_action):
        """
        mode: "offensive" o "defensive"
        used_class_action: bool -> si se ejecutó acción real (y pagó)
        """
        try:
            used = bool(used_class_action)
        except:
            used = False

        # ============================
        # OFENSIVO (Concentrar)
        # ============================
        if mode == "offensive":

            # Preferido: sistema nuevo por cargas
            fn_new = getattr(S, "focus_off_end_turn_decay", None)
            if callable(fn_new):
                # La función nueva ya sabe si consumió o no (usa flags internos)
                # Pero nosotros igual aseguramos consistencia:
                try:
                    # Si se usó acción real este turno, puede haber consumido.
                    # La flag S.focus_off_consumed_this_turn la setea apply_offensive_focus().
                    # Si NO hubo consumo, decay suave aplica.
                    fn_new()
                except:
                    pass
            else:
                # Legacy fallback (si aún lo tenés)
                if not used:
                    fn = getattr(S, "carry_over_offensive_focus", None)
                    if callable(fn):
                        fn()
                    _legacy_decay_one_charge("off")

            # seguridad: legacy flag nunca se arrastra
            try:
                S.focus_cost_active = False
            except:
                pass
            return

        # ============================
        # DEFENSIVO (Potenciar)
        # ============================
        if mode == "defensive":

            fn_new = getattr(S, "boost_def_end_turn_decay", None)
            if callable(fn_new):
                try:
                    fn_new()
                except:
                    pass
            else:
                if not used:
                    fn = getattr(S, "carry_over_defensive_focus", None)
                    if callable(fn):
                        fn()
                    _legacy_decay_one_charge("def")

            try:
                S.focus_cost_active = False
            except:
                pass
            return

    S.battle_focus_end_turn = battle_focus_end_turn
