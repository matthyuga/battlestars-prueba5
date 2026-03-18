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

    def _def_player_unit_key():
        """Unit key del jugador para costos/valor final en defensa."""
        try:
            mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        except:
            mode = "1v1"

        if mode == "2v2":
            try:
                fn_ctx = getattr(S, "bs_get_turn_ctx", None)
                fn_key = getattr(S, "bs_unit_key", None)
                if callable(fn_ctx) and callable(fn_key):
                    ctx = fn_ctx() or {}
                    team = str(ctx.get("owner_team", "player") or "player").strip().lower()
                    slot = int(ctx.get("owner_slot", 0) or 0)
                    if team == "player":
                        return str(fn_key("player", slot) or "player:0")
            except:
                pass

        try:
            fn_akt = getattr(S, "bs_get_active_unit_key", None)
            if callable(fn_akt):
                return str(fn_akt("player") or "player:0")
        except:
            pass

        return "player:0"

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
            "Salvaguarda principiante": "salvaguarda_principiante",
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

        fmt_cyan  = getattr(S, "fmt_cyan",  lambda t: str(t))
        fmt_white = getattr(S, "fmt_white", lambda t: str(t))

        if int(base_blk or 0) != int(final_blk or 0):
            block_txt = (
                fmt_cyan(_fmt_num(base_blk)) +
                fmt_white(" ×2 (") +
                fmt_cyan(_fmt_num(final_blk)) +
                fmt_white(")")
            )
        else:
            block_txt = fmt_cyan(_fmt_num(final_blk))

        return fmt_cyan("Defensa Fuerte") + fmt_white(" → Bloquea ") + block_txt + fmt_white(" de daño.")


# ============================================================
# PROCESAMIENTO DEFENSIVO
# ============================================================
label defensive_process_actions(selected, base_damage):

    python:
        import renpy.store as S

        _mode_direct = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        if _mode_direct == "2v2":
            _direct_ctx = int(getattr(S, "pending_direct_damage_for_defense", 0) or 0)
        else:
            _fn_get_direct = getattr(S, "bs_get_direct_pending", None)
            if callable(_fn_get_direct):
                _direct_ctx = int(_fn_get_direct("player") or 0)
            else:
                _direct_ctx = int(getattr(S, "enemy_direct_pending_damage", 0) or 0)
        _reduc_base = int(base_damage or 0)
        if _reduc_base <= 0 and _direct_ctx > 0:
            _reduc_base = int(_direct_ctx)

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
        if not hasattr(S, "special_defense_reduction_pct"):
            S.special_defense_reduction_pct = 0.0
        else:
            S.special_defense_reduction_pct = 0.0

        # ONE-SHOT: Potenciar pendiente para la próxima defensa real
        if not hasattr(S, "def_boost_pending"):
            S.def_boost_pending = False

        # Telemetría de consumo defensivo por turno (para registro detallado)
        S.turn_def_rei_before = int(getattr(S, "player_reiatsu", 0) or 0)
        S.turn_def_ene_before = int(getattr(S, "player_energy", 0) or 0)
        S.turn_def_rei_tech_sum = 0
        S.turn_def_ene_tech_sum = 0

        # Helpers de formato
        fmt_pink  = getattr(S, "fmt_pink",  lambda t: str(t))
        fmt_cyan  = getattr(S, "fmt_cyan",  lambda t: str(t))
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

            # ----------------------------
            # POTENCIAR (ONE-SHOT, SIN COSTO DIRECTO)
            # ----------------------------
            if action.name == "Potenciar":
                # Marcamos el boost pendiente. El “consumo” real ocurre en la próxima defensa.
                S.def_boost_pending = True

                if callable(log_potenciar_unified):
                    summary_lines.append(log_potenciar_unified())
                else:
                    summary_lines.append(fmt_cyan("Potenciar") + fmt_white(" Activado → Próxima defensa ") + fmt_cyan("×2"))

                continue

            if action.used:
                continue

            # ----------------------------
            # COSTOS BASE (Single Source: get_tech_costs)
            # ----------------------------
            # SSOT dinámico (Fase C): usa unit_key para overlay por slot
            try:
                costs = S.reiatsu_energy_dynamic_cost(action.tech_id, S, unit_key=_def_player_unit_key())
            except:
                costs = {}
            rei_cost = int(costs.get("reiatsu_cost", 0) or 0)
            ene_cost = int(costs.get("energy_cost", 0) or 0)

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
            action.base_block = S.final_value_factory(action.tech_id, S, unit_key=_def_player_unit_key())

            # ✅ Potenciar duplica BLOQUE solo en la próxima defensa real aplicada
            if action.after_focus and S.def_boost_pending:
                action.final_block = int(action.base_block) * 2
                # Consumimos el ONE-SHOT acá: ya se aplicó de verdad
                S.def_boost_pending = False
            else:
                action.final_block = int(action.base_block)

            if action.tech_id == "salvaguarda_principiante":
                action.base_block = 0
                action.final_block = 0

            S.total_block += action.final_block
            S.blocks_list.append((action.base_block, action.final_block))

            # ----------------------------
            # EFECTOS
            # ----------------------------
            if action.tech_id == "defense_extra":

                if callable(log_defense_extra):
                    summary_lines.append(
                        log_defense_extra(
                            action.base_block,
                            action.final_block
                        )
                    )
                else:
                    summary_lines.append(fmt_cyan("Defensa Extra") + fmt_white(" → Bloquea {} de daño.".format(_fmt_num(action.final_block))))

            elif action.tech_id == "defense_reflect":

                ref_pct = float(action.data.get("attack_reflect", 0.10))
                S.reflected = int(base_damage * ref_pct)
                if callable(log_defense_reflect):
                    summary_lines.append(
                        log_defense_reflect(
                            action.base_block,
                            int(ref_pct * 100),
                            S.reflected,
                            final=action.final_block
                        )
                    )
                else:
                    summary_lines.append(fmt_cyan("Defensa Reflectora") + fmt_white(" → Refleja {} de daño.".format(_fmt_num(S.reflected))))

            elif action.tech_id == "defense_reducer":

                atk_red = float(action.data.get("attack_reduction", 0.10))
                S.reduc_val = int(_reduc_base * atk_red)
                if callable(log_defense_reducer):
                    summary_lines.append(
                        log_defense_reducer(
                            action.base_block,
                            int(atk_red * 100),
                            S.reduc_val,
                            final=action.final_block
                        )
                    )
                else:
                    summary_lines.append(fmt_cyan("Defensa Reductora") + fmt_white(" → Reduce {} de daño.".format(_fmt_num(S.reduc_val))))

            elif action.tech_id == "salvaguarda_principiante":

                S.special_defense_reduction_pct = 0.50
                summary_lines.append(
                    fmt_cyan("Salvaguarda principiante") + fmt_white(" → Reduce 50% del daño defendible restante.")
                )

            elif action.tech_id == "defense_strong_block":

                summary_lines.append(
                    log_defense_strong(
                        action.base_block,
                        action.final_block
                    )
                )

            # ----------------------------
            # CONSUMO REAL (UNA VEZ)
            # ----------------------------
            S.consume_resources(action.rei_cost, action.ene_cost, actor="player")
            S.turn_def_rei_tech_sum += int(action.rei_cost or 0)
            S.turn_def_ene_tech_sum += int(action.ene_cost or 0)
            action.used = True


        # Export para el Operation (y logs)
        S.summary_lines = summary_lines
        S.turn_def_rei_after = int(getattr(S, "player_reiatsu", 0) or 0)
        S.turn_def_ene_after = int(getattr(S, "player_energy", 0) or 0)

    return
