# ============================================================
# 04D_DEFENSIVE_ACTIONS.rpy – Defensive Actions (v14.0 ONE-SHOT)
# ============================================================
# ✔ Arquitectura Action (igual a ofensivo)
# ✔ Potenciar = ONE-SHOT: afecta SOLO la siguiente defensa real
# ✔ Potenciar duplica BLOQUE y REIATSU
# ✔ Energía NO se duplica
# ✔ Costos calculados una sola vez
# ✔ Estado store-safe (S.*), sin globals
# ============================================================

init python:

    import renpy.store as S

    # --------------------------------------------------------
    # UTILIDADES (preferir central si existe)
    # --------------------------------------------------------
    def _fmt_num(n):
        # Usa el formatter central si está disponible
        fn = getattr(S, "battle_fmt_num", None)
        if callable(fn):
            return fn(n)
        try:
            return "{:,}".format(int(n)).replace(",", ".")
        except:
            return str(n)

    def blk_text(base, final):
        if base != final:
            return "{}×({})".format(_fmt_num(base), _fmt_num(final))
        return _fmt_num(final)

    # --------------------------------------------------------
    # CLASE ACTION DEFENSIVA
    # --------------------------------------------------------
    class DefensiveAction(object):
        def __init__(self, tech_id, name, position, data):
            self.tech_id   = tech_id
            self.name      = name
            self.position  = position
            self.data      = data or {}

            self.base_block  = 0
            self.final_block = 0

            self.rei_cost = 0
            self.ene_cost = 0

            # “Potenciar” en esta arquitectura es ONE-SHOT sobre
            # la siguiente defensa real, así que marcamos sólo UNA.
            self.after_focus = False
            self.used = False


    # --------------------------------------------------------
    # CONSTRUCTOR
    # --------------------------------------------------------
    def make_defensive_action_from_name(name, index):

        TECH_MAP = {
            "Defensa Extra":       "defense_extra",
            "Defensa Reductora":   "defense_reducer",
            "Defensa Reflectora":  "defense_reflect",
            "Defensa Fuerte":      "defense_strong_block",
            "Potenciar":           "defense_boost",
        }

        tech_id = TECH_MAP.get(name, None)
        if tech_id is None:
            return None

        techniques = getattr(S, "battle_techniques", {})
        data = techniques.get(tech_id, {}) if isinstance(techniques, dict) else {}

        return DefensiveAction(tech_id, name, index, data)


    # --------------------------------------------------------
    # LOG DEFENSA FUERTE (usa fmt del sistema si existe)
    # --------------------------------------------------------
    def log_defense_strong(base_blk, final_blk=None):
        if final_blk is None:
            final_blk = base_blk

        fmt_blue  = getattr(S, "fmt_blue",  lambda t: str(t))
        fmt_white = getattr(S, "fmt_white", lambda t: str(t))

        return (
            fmt_blue("Defensa fuerte ") +
            fmt_white("→ Bloquea {} ({} → {}).".format(
                _fmt_num(final_blk),
                _fmt_num(base_blk),
                _fmt_num(final_blk)
            ))
        )


# ============================================================
# PROCESAMIENTO DEFENSIVO
# ============================================================
label defensive_process_actions(selected, base_damage):

    python:
        import renpy.store as S

        # ----------------------------------------------------
        # Estado store-safe con defaults
        # ----------------------------------------------------
        if not hasattr(S, "summary_lines"):
            S.summary_lines = []

        # Variables de turno (en tu CORE las seteás antes; acá hacemos “fallback”)
        if not hasattr(S, "reduc_val"):
            S.reduc_val = 0
        if not hasattr(S, "total_block"):
            S.total_block = 0
        if not hasattr(S, "blocks_list"):
            S.blocks_list = []
        if not hasattr(S, "reflected"):
            S.reflected = 0
        if not hasattr(S, "awaiting_turn_end"):
            S.awaiting_turn_end = False

        # ONE-SHOT: Potenciar pendiente para la próxima defensa real
        if not hasattr(S, "def_boost_pending"):
            S.def_boost_pending = False

        # Helpers de formato
        fmt_pink  = getattr(S, "fmt_pink",  lambda t: str(t))
        fmt_blue  = getattr(S, "fmt_blue",  lambda t: str(t))
        fmt_white = getattr(S, "fmt_white", lambda t: str(t))

        # Logs existentes (deben estar en tu proyecto)
        log_potenciar_unified = getattr(S, "log_potenciar_unified", None)
        log_defense_extra     = getattr(S, "log_defense_extra", None)
        log_defense_reflect   = getattr(S, "log_defense_reflect", None)
        log_defense_reducer   = getattr(S, "log_defense_reducer", None)

        summary_lines = []

        # ----------------------------------------------------
        # 1) STRINGS → ACTIONS
        # ----------------------------------------------------
        actions = []
        for i, name in enumerate(selected):
            act = make_defensive_action_from_name(name, i)
            if act:
                actions.append(act)

        # ----------------------------------------------------
        # 2) DETECTAR POTENCIAR → MARCAR SOLO LA SIGUIENTE DEFENSA
        # ----------------------------------------------------
        focus_seen = False
        for act in actions:
            if act.name == "Potenciar":
                focus_seen = True
                continue
            if focus_seen:
                act.after_focus = True
                break

        # ----------------------------------------------------
        # 3) LOOP PRINCIPAL
        # ----------------------------------------------------
        for action in actions:

            if S.awaiting_turn_end:
                break

            # ----------------------------
            # POTENCIAR (ONE-SHOT, SIN COSTO DIRECTO)
            # ----------------------------
            if action.name == "Potenciar":
                # Marcamos el boost pendiente. El “consumo” real ocurre en la próxima defensa.
                S.def_boost_pending = True

                if callable(log_potenciar_unified):
                    summary_lines.append(log_potenciar_unified())
                else:
                    summary_lines.append(fmt_blue("Potenciar ") + fmt_white("→ Próxima defensa ×2."))

                continue

            if action.used:
                continue

            # ----------------------------
            # COSTOS BASE (Single Source: get_tech_costs)
            # ----------------------------
            costs = S.get_tech_costs(action.tech_id) if hasattr(S, "get_tech_costs") else get_tech_costs(action.tech_id)
            rei_cost = int(costs.get("reiatsu", 0))
            ene_cost = int(costs.get("energy", 0))

            # ✅ Potenciar duplica SOLO REIATSU (y solo 1 defensa)
            if action.after_focus and S.def_boost_pending:
                rei_cost *= 2

            action.rei_cost = rei_cost
            action.ene_cost = ene_cost

            if S.player_reiatsu < rei_cost or S.player_energy < ene_cost:
                summary_lines.append(
                    fmt_pink("No puedes usar {}: Recursos insuficientes".format(action.name))
                )
                # Si era la defensa “objetivo” del Potenciar, NO consumimos el pending,
                # porque el boost todavía no fue aplicado realmente.
                continue

            # ----------------------------
            # BLOQUE (Single Source: final_value_factory) + Potenciar ONE-SHOT
            # ----------------------------
            action.base_block = S.final_value_factory(action.tech_id, S)

            # ✅ Potenciar duplica BLOQUE solo en la próxima defensa real aplicada
            if action.after_focus and S.def_boost_pending:
                action.final_block = int(action.base_block) * 2
                # Consumimos el ONE-SHOT acá: ya se aplicó de verdad
                S.def_boost_pending = False
            else:
                action.final_block = int(action.base_block)

            S.total_block += action.final_block
            S.blocks_list.append((action.base_block, action.final_block))

            # ----------------------------
            # EFECTOS
            # ----------------------------
            if action.tech_id == "defense_extra":

                if callable(log_defense_extra):
                    summary_lines.append(
                        log_defense_extra(
                            blk_text(action.base_block, action.final_block),
                            action.final_block
                        )
                    )
                else:
                    summary_lines.append(fmt_blue("Defensa extra ") + fmt_white("→ Bloque {}.".format(_fmt_num(action.final_block))))

            elif action.tech_id == "defense_reflect":

                ref_pct = float(action.data.get("attack_reflect", 0.10))
                S.reflected = int(base_damage * ref_pct)
                S.awaiting_turn_end = True

                if callable(log_defense_reflect):
                    summary_lines.append(
                        log_defense_reflect(
                            blk_text(action.base_block, action.final_block),
                            int(ref_pct * 100),
                            S.reflected
                        )
                    )
                else:
                    summary_lines.append(fmt_blue("Defensa reflectora ") + fmt_white("→ Refleja {}.".format(_fmt_num(S.reflected))))

            elif action.tech_id == "defense_reducer":

                atk_red = float(action.data.get("attack_reduction", 0.10))
                S.reduc_val = int(base_damage * atk_red)
                S.awaiting_turn_end = True

                if callable(log_defense_reducer):
                    summary_lines.append(
                        log_defense_reducer(
                            blk_text(action.base_block, action.final_block),
                            int(atk_red * 100),
                            S.reduc_val
                        )
                    )
                else:
                    summary_lines.append(fmt_blue("Defensa reductora ") + fmt_white("→ Reduce {}.".format(_fmt_num(S.reduc_val))))

            elif action.tech_id == "defense_strong_block":

                S.awaiting_turn_end = True
                summary_lines.append(
                    log_defense_strong(
                        blk_text(action.base_block, action.final_block)
                    )
                )

            # ----------------------------
            # CONSUMO REAL (UNA VEZ)
            # ----------------------------
            S.consume_resources(action.rei_cost, action.ene_cost, actor="player")
            action.used = True

        # Export para el Operation (y logs)
        S.summary_lines = summary_lines

    return
