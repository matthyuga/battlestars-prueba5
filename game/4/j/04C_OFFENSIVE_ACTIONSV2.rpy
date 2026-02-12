# ============================================================
# 04C_OFFENSIVE_ACTIONS.rpy – Offensive Core (Action Objects)
# ============================================================
# v12.5 – SafeLogHub + StoreSafe LogRefs + BaseValue SafeCall Fix + 04X SSOT
# ------------------------------------------------------------
# ✔ Costos finales salen de 04X (reiatsu_energy_dynamic_cost)
# ✔ Focus/Concentrar multiplica daño y Reiatsu con el MISMO mult (x2 / x4 ...)
# ✔ Energía NO se duplica
# ✔ Sin doble cobro / sin costos fantasmas
# ✔ NO resetea focus acá (carry-over/decay lo maneja el hook de fin de turno)
# ✔ Store-safe (battle_techniques via S)
#
# FIXES:
# - base_value: llamada segura a S.final_value_factory (sin getattr(...)(...) )
# - logging: usa S.safe_battle_log_add() si existe (fallback suave)
# - fmt/log helpers: preferir S.fmt_* / S.log_* (evita dependencia de globals)
# ============================================================

init python:

    import renpy.store as S

    # ------------------------------------------------------------
    # Helpers locales (store-safe)
    # ------------------------------------------------------------
    def _fmt_num(n):
        try:
            fn = getattr(S, "battle_fmt_num", None)
            if callable(fn):
                return fn(n)
        except:
            pass
        try:
            return "{:,}".format(int(n)).replace(",", ".")
        except:
            return str(n)

    def make_dmg_text(base, dmg):
        if dmg != base:
            return "{} × ({})".format(_fmt_num(base), _fmt_num(dmg))
        return _fmt_num(base)

    def _focus_mult_peek_offensive():
        """
        Peek del multiplicador ofensivo SIN consumir.
        Preferencia:
          1) Sistema nuevo por cargas: S.offensive_focus_multiplier_peek()
          2) Fallback legacy: focus_off_current_mult * focus_off_stored_mult
          3) Default: 1
        """
        # 1) Nuevo (cargas)
        try:
            fn = getattr(S, "offensive_focus_multiplier_peek", None)
            if callable(fn):
                m = int(fn() or 1)
                if m < 1:
                    m = 1
                return m
        except:
            pass

        # 2) Legacy
        try:
            cur = int(getattr(S, "focus_off_current_mult", 1) or 1)
        except:
            cur = 1
        try:
            sto = int(getattr(S, "focus_off_stored_mult", 1) or 1)
        except:
            sto = 1

        m = cur * sto
        if m < 1:
            m = 1
        return m

    def _blog(text, color=None, border=None):
        """
        Wrapper universal:
        - Preferido: S.safe_battle_log_add (00_BATTLE_STYLE v4.3)
        - Fallback: globals().battle_log_add o S.battle_log_add
        """
        # preferido
        try:
            fn = getattr(S, "safe_battle_log_add", None)
            if callable(fn):
                # soporta kwargs color/border
                try:
                    if color is None and border is None:
                        fn(text)
                    else:
                        fn(text, color=color, border=border)
                except:
                    # fallback por firma
                    try:
                        if color is None:
                            fn(text)
                        else:
                            fn(text, color)
                    except:
                        pass
                return
        except:
            pass

        # fallback global/store
        try:
            g = globals().get("battle_log_add", None)
            if callable(g):
                if color is None:
                    g(text)
                else:
                    g(text, color)
                return
        except:
            pass
        try:
            s = getattr(S, "battle_log_add", None)
            if callable(s):
                if color is None:
                    s(text)
                else:
                    s(text, color)
        except:
            pass


    # ------------------------------------------------------------
    # Helpers de estilo / logs (preferir STORE para orden de carga)
    # ------------------------------------------------------------
    def _get_style(name):
        try:
            fn = getattr(S, name, None)
            if callable(fn):
                return fn
        except:
            pass
        try:
            fn = globals().get(name, None)
            if callable(fn):
                return fn
        except:
            pass
        return None

    fmt_red    = _get_style("fmt_red")
    fmt_white  = _get_style("fmt_white")
    fmt_orange = _get_style("fmt_orange")
    fmt_pink   = _get_style("fmt_pink")

    log_focus_unified  = _get_style("log_focus_unified")
    log_attack_simple  = _get_style("log_attack_simple")
    log_attack_reducer = _get_style("log_attack_reducer")


    # ------------------------------------------------------------
    # Clase de acción (no choca con 01_ACTION_MODEL)
    # ------------------------------------------------------------
    class OffAction(object):
        def __init__(self, tech_id, name, position, data):
            self.tech_id   = tech_id
            self.name      = name
            self.position  = position
            self.data      = data or {}

            self.type      = self.data.get("type")
            self.special   = self.data.get("special")

            self.base_value  = 0
            self.final_value = 0

            self.rei_cost = 0
            self.ene_cost = 0

            self.used = False


    # ------------------------------------------------------------
    # Constructor desde nombre visual del selector
    # ------------------------------------------------------------
    def make_action_from_name(name, index):

        TECH_MAP = {
            "Ataque Extra":       "extra_attack",
            "Técnica Extra":      "extra_tech",
            "Ataque Reductor":    "attack_reducer",
            "Ataque Directo":     "direct_attack",
            "Ataque Negador":     "noatk_attack",
            "Ataque más fuerte":  "stronger_attack",

            "Concentrar":         "focus",
            "Concentrar x2":      "focus",
        }

        tech_id = TECH_MAP.get(name)
        if tech_id is None:
            return None

        techniques = getattr(S, "battle_techniques", {}) or {}
        data = techniques.get(tech_id, {})
        return OffAction(tech_id, name, index, data)



# ============================================================
# 🟥 PROCESO OFENSIVO
# ============================================================
label offensive_process_actions(selected):

    python:
        import renpy.store as S
        global total_damage, combo_count, actions
        global attack_records, can_focus
        global awaiting_turn_end, player_name

        # flag para hook/diagnóstico
        if not hasattr(S, "turn_offensive_attack_used"):
            S.turn_offensive_attack_used = False

        # ----------------------------------------------------
        # 1) Strings → OffAction
        # ----------------------------------------------------
        selected_actions = []
        for i, tech_name in enumerate(selected or []):
            act = make_action_from_name(tech_name, i)
            if act:
                selected_actions.append(act)

        # ----------------------------------------------------
        # 2) Loop principal
        # ----------------------------------------------------
        for action in selected_actions:

            if awaiting_turn_end:
                break

            # -------------------------
            # 🔹 CONCENTRAR (focus)
            # -------------------------
            if action.tech_id == "focus":

                # Activar carga (no consume nada)
                try:
                    fn = getattr(S, "activate_offensive_focus", None)
                    if callable(fn):
                        fn()
                except:
                    pass

                # Log / popup (si existen)
                try:
                    if callable(log_focus_unified):
                        _blog(log_focus_unified("attack"))
                    else:
                        _blog("Concentrar activado.", "#C586C0")
                except:
                    _blog("Concentrar activado.", "#C586C0")

                try:
                    battle_popup_turn("{} incrementa Concentrar".format(player_name), "#C586C0")
                except:
                    pass

                can_focus = False
                continue

            # Solo ofensivas
            if action.type != "offensive":
                continue

            if action.used or actions <= 0:
                continue

            # ----------------------------------------------------
            # ⭐ 3) Peek del mult de focus ANTES de consumirlo
            # ----------------------------------------------------
            focus_mult = _focus_mult_peek_offensive()
            if focus_mult < 1:
                focus_mult = 1

            # ----------------------------------------------------
            # ⭐ 4) Valor base (sin focus) para fórmula/logs
            #     FIX: llamada segura a final_value_factory
            # ----------------------------------------------------
            action.base_value = 0
            try:
                fn_val = getattr(S, "final_value_factory", None)
                if callable(fn_val):
                    action.base_value = int(fn_val(action.tech_id, S) or 0)
            except:
                action.base_value = 0

            # ----------------------------------------------------
            # ⭐ 5) Costos (ANTES de consumir focus)
            # ----------------------------------------------------
            rei_cost = 0
            ene_cost = 0
            try:
                cost_fn = getattr(S, "reiatsu_energy_dynamic_cost", None)
                if callable(cost_fn):
                    cost = cost_fn(action.tech_id, S, force_focus_mult=focus_mult)
                    try:
                        rei_cost = int(cost.get("reiatsu_cost", 0) or 0)
                    except:
                        rei_cost = 0
                    try:
                        ene_cost = int(cost.get("energy_cost", 0) or 0)
                    except:
                        ene_cost = 0
                else:
                    rei_cost = int(action.base_value or 0) * int(focus_mult or 1)
                    ene_cost = 0
            except:
                rei_cost = int(action.base_value or 0) * int(focus_mult or 1)
                ene_cost = 0

            if rei_cost < 0: rei_cost = 0
            if ene_cost < 0: ene_cost = 0

            action.rei_cost = rei_cost
            action.ene_cost = ene_cost

            # ----------------------------------------------------
            # ⭐ 6) CHECK REAL (ANTES de consumir focus)
            # ----------------------------------------------------
            try:
                pr = int(getattr(S, "player_reiatsu", 0) or 0)
            except:
                pr = 0
            try:
                pe = int(getattr(S, "player_energy", 0) or 0)
            except:
                pe = 0

            if pr < rei_cost or pe < ene_cost:
                try:
                    if callable(fmt_pink):
                        _blog(fmt_pink("No puedes usar {}: Recursos insuficientes".format(action.name)))
                    else:
                        _blog("No puedes usar {}: Recursos insuficientes".format(action.name), "#FF66CC")
                except:
                    _blog("No puedes usar {}: Recursos insuficientes".format(action.name), "#FF66CC")
                continue

            # ----------------------------------------------------
            # ⭐ 7) Aplicar focus real (consume cargas si estaban)
            #     Ahora sí, porque ya sabemos que se puede pagar.
            # ----------------------------------------------------
            try:
                fn_apply = getattr(S, "apply_offensive_focus", None)
                if callable(fn_apply):
                    action.final_value = int(fn_apply(action.base_value) or 0)
                else:
                    action.final_value = int(action.base_value or 0)
            except:
                action.final_value = int(action.base_value or 0)

            dmg  = action.final_value
            tech = action.tech_id

            # Guardar para fórmula
            try:
                attack_records.append((action.base_value, action.final_value))
            except:
                pass

            # Ya ejecutó una ofensiva real (para hook)
            try:
                S.turn_offensive_attack_used = True
            except:
                pass

            # ----------------------------------------------------
            # ===== ATAQUE DIRECTO =====
            # ----------------------------------------------------
            if tech == "direct_attack":

                S.direct_base_damage    = action.base_value
                S.direct_pending_damage = dmg

                try:
                    if callable(fmt_red) and callable(fmt_white) and callable(fmt_orange):
                        _blog(
                            fmt_red("Ataque Directo") +
                            fmt_white(" → {} daño. ".format(make_dmg_text(action.base_value, dmg))) +
                            fmt_orange("2/3 éxitos = INDEFENDIBLE. ") +
                            fmt_white("(Reiatsu {} / Ene {})".format(_fmt_num(rei_cost), _fmt_num(ene_cost)))
                        )
                    else:
                        _blog("Ataque Directo → {} daño. (Reiatsu {} / Ene {})".format(
                            make_dmg_text(action.base_value, dmg), _fmt_num(rei_cost), _fmt_num(ene_cost)
                        ), "#FFDD44")
                except:
                    _blog("Ataque Directo → {} daño. (Reiatsu {} / Ene {})".format(
                        make_dmg_text(action.base_value, dmg), _fmt_num(rei_cost), _fmt_num(ene_cost)
                    ), "#FFDD44")

                try:
                    fx_hit_red(dmg, "#FFDD44", 0.30)
                except:
                    pass
                try:
                    battle_visual_float("enemy", dmg, "#FFDD44", is_final=False)
                except:
                    pass

                try:
                    S.consume_resources(rei_cost, ene_cost, actor="player")
                except:
                    try:
                        S.consume_resources(rei_cost, ene_cost, "player")
                    except:
                        pass

                actions -= 1
                action.used = True
                can_focus = True
                continue

            # ----------------------------------------------------
            # ===== ATAQUE NEGADOR =====
            # ----------------------------------------------------
            if tech == "noatk_attack":

                total_damage += dmg
                combo_count += 1
                actions -= 1

                try:
                    fx_hit_red(dmg, "#FFCCCC", 0.28)
                except:
                    pass
                try:
                    battle_visual_float("enemy", dmg, "#FFCCCC", is_final=False)
                except:
                    pass

                try:
                    if callable(fmt_pink) and callable(fmt_white) and callable(fmt_orange):
                        _blog(
                            fmt_pink("Ataque Negador") +
                            fmt_white(" → {} daño. ".format(make_dmg_text(action.base_value, dmg))) +
                            fmt_white("(Reiatsu {} / Ene {}) ".format(_fmt_num(rei_cost), _fmt_num(ene_cost))) +
                            fmt_orange("2/3 éxitos = NO ATK enemigo.")
                        )
                    else:
                        _blog("Ataque Negador → {} daño. (Reiatsu {} / Ene {})".format(
                            make_dmg_text(action.base_value, dmg), _fmt_num(rei_cost), _fmt_num(ene_cost)
                        ), "#FF66CC")
                except:
                    _blog("Ataque Negador → {} daño. (Reiatsu {} / Ene {})".format(
                        make_dmg_text(action.base_value, dmg), _fmt_num(rei_cost), _fmt_num(ene_cost)
                    ), "#FF66CC")

                try:
                    S.consume_resources(rei_cost, ene_cost, actor="player")
                except:
                    try:
                        S.consume_resources(rei_cost, ene_cost, "player")
                    except:
                        pass

                action.used = True
                continue

            # ----------------------------------------------------
            # ===== ATAQUE REDUCTOR =====
            # ----------------------------------------------------
            if tech == "attack_reducer":

                total_damage += dmg
                combo_count += 1
                actions -= 1

                try:
                    S.next_defense_reduction = action.data.get("defense_reduction", 0.10)
                except:
                    S.next_defense_reduction = 0.10

                try:
                    fx_hit_red(dmg, "#FF9966", 0.28)
                except:
                    pass
                try:
                    battle_visual_float("enemy", dmg, "#FF9966", is_final=False)
                except:
                    pass

                try:
                    if callable(log_attack_reducer) and callable(fmt_white):
                        _blog(
                            log_attack_reducer(
                                action.name,
                                make_dmg_text(action.base_value, dmg),
                                int((getattr(S, "next_defense_reduction", 0.10) or 0.10) * 100)
                            ) +
                            fmt_white(" (Reiatsu {} / Ene {})".format(_fmt_num(rei_cost), _fmt_num(ene_cost)))
                        )
                    else:
                        _blog("{} → {} daño. (-{}% DEF) (Reiatsu {} / Ene {})".format(
                            action.name,
                            make_dmg_text(action.base_value, dmg),
                            int((getattr(S, "next_defense_reduction", 0.10) or 0.10) * 100),
                            _fmt_num(rei_cost),
                            _fmt_num(ene_cost)
                        ), "#FF9966")
                except:
                    _blog("{} → {} daño. (-{}% DEF) (Reiatsu {} / Ene {})".format(
                        action.name,
                        make_dmg_text(action.base_value, dmg),
                        int((getattr(S, "next_defense_reduction", 0.10) or 0.10) * 100),
                        _fmt_num(rei_cost),
                        _fmt_num(ene_cost)
                    ), "#FF9966")

                try:
                    S.consume_resources(rei_cost, ene_cost, actor="player")
                except:
                    try:
                        S.consume_resources(rei_cost, ene_cost, "player")
                    except:
                        pass

                action.used = True
                continue

            # ----------------------------------------------------
            # ===== ATAQUE MÁS FUERTE =====
            # ----------------------------------------------------
            if tech == "stronger_attack":

                total_damage += dmg
                combo_count += 1
                actions -= 1

                try:
                    fx_hit_red(dmg, "#FF4444", 0.32)
                except:
                    pass
                try:
                    battle_visual_float("enemy", dmg, "#FF4444", is_final=False)
                except:
                    pass

                try:
                    if callable(fmt_red) and callable(fmt_white):
                        _blog(
                            fmt_red("Ataque más fuerte") +
                            fmt_white(" → {} daño. ".format(make_dmg_text(action.base_value, dmg))) +
                            fmt_white("(Reiatsu {} / Ene {})".format(_fmt_num(rei_cost), _fmt_num(ene_cost)))
                        )
                    else:
                        _blog("Ataque más fuerte → {} daño. (Reiatsu {} / Ene {})".format(
                            make_dmg_text(action.base_value, dmg), _fmt_num(rei_cost), _fmt_num(ene_cost)
                        ), "#FF4444")
                except:
                    _blog("Ataque más fuerte → {} daño. (Reiatsu {} / Ene {})".format(
                        make_dmg_text(action.base_value, dmg), _fmt_num(rei_cost), _fmt_num(ene_cost)
                    ), "#FF4444")

                try:
                    S.consume_resources(rei_cost, ene_cost, actor="player")
                except:
                    try:
                        S.consume_resources(rei_cost, ene_cost, "player")
                    except:
                        pass

                action.used = True
                continue

            # ----------------------------------------------------
            # ===== ATAQUE EXTRA / TÉCNICA EXTRA =====
            # ----------------------------------------------------
            if tech in ("extra_attack", "extra_tech"):

                total_damage += dmg
                combo_count += 1
                try:
                    bonus = int(action.data.get("bonus_actions", 1) or 1)
                except:
                    bonus = 1
                actions = actions - 1 + bonus

                try:
                    fx_hit_red(dmg, "#FF8888", 0.25)
                except:
                    pass
                try:
                    battle_visual_float("enemy", dmg, "#FF8888", is_final=False)
                except:
                    pass

                try:
                    if callable(log_attack_simple) and callable(fmt_white):
                        _blog(
                            log_attack_simple(action.name, make_dmg_text(action.base_value, dmg)) +
                            fmt_white("(Reiatsu {} / Ene {})".format(_fmt_num(rei_cost), _fmt_num(ene_cost)))
                        )
                    else:
                        _blog("{} → {} daño. (Reiatsu {} / Ene {})".format(
                            action.name,
                            make_dmg_text(action.base_value, dmg),
                            _fmt_num(rei_cost),
                            _fmt_num(ene_cost)
                        ), "#FF8888")
                except:
                    _blog("{} → {} daño. (Reiatsu {} / Ene {})".format(
                        action.name,
                        make_dmg_text(action.base_value, dmg),
                        _fmt_num(rei_cost),
                        _fmt_num(ene_cost)
                    ), "#FF8888")

                try:
                    S.consume_resources(rei_cost, ene_cost, actor="player")
                except:
                    try:
                        S.consume_resources(rei_cost, ene_cost, "player")
                    except:
                        pass

                action.used = True
                continue


        # ----------------------------------------------------
        # RESET visual (simulación HUD)
        # ----------------------------------------------------
        if hasattr(S, "simulated_reiatsu"):
            S.simulated_reiatsu = getattr(S, "player_reiatsu", 0)
        if hasattr(S, "simulated_energy"):
            S.simulated_energy = getattr(S, "player_energy", 0)

    return
