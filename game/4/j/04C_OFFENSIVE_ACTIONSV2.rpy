# ============================================================
# 04C_OFFENSIVE_ACTIONS.rpy – Offensive Core (Action Objects)
# ============================================================
# v12.5 – SafeLogHub + StoreSafe LogRefs + BaseValue SafeCall Fix + 04X SSOT
# ------------------------------------------------------------
# ✔ Costos finales salen de 04X (reiatsu_energy_dynamic_cost)
# ✔ Focus/Concentrar multiplica daño y EP con el MISMO mult (x2 / x4 ...)
# ✔ EC NO se duplica
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

    def _off_player_unit_key():
        """Unit key del jugador para costos/valor final en ejecución."""
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


    def _off_enemy_unit_key():
        """Unit key objetivo enemigo para efectos especiales ofensivos."""
        try:
            fn_ctx = getattr(S, "bs_get_turn_ctx", None)
            fn_key = getattr(S, "bs_unit_key", None)
            if callable(fn_ctx) and callable(fn_key):
                ctx = fn_ctx() or {}
                team = str(ctx.get("owner_team", "player") or "player").strip().lower()
                if team == "player":
                    es = int(getattr(S, "enemy_active_slot", 0) or 0)
                    return str(fn_key("enemy", es) or "enemy:0")
        except:
            pass
        try:
            fn_akt = getattr(S, "bs_get_active_unit_key", None)
            if callable(fn_akt):
                return str(fn_akt("enemy") or "enemy:0")
        except:
            pass
        return str(getattr(S, "current_enemy_unit_key", "enemy:0") or "enemy:0")

    def _offensive_fx_hit_pause(default_delay=0.26):
        try:
            mode = str(getattr(S, "bs_battle_fx_speed_mode", "normal") or "normal").strip().lower()
        except:
            mode = "normal"
        if mode in ("fast", "rapido", "rapida"):
            delay = 0.12
        elif mode in ("slow", "lento", "lenta"):
            delay = 0.36
        else:
            delay = float(default_delay or 0.26)
        try:
            fn_pause = getattr(S, "bs_ui_pause", None) or globals().get("bs_ui_pause", None)
            if callable(fn_pause):
                fn_pause(delay, hard=True)
            else:
                renpy.pause(delay, hard=True)
        except:
            pass

    def _pick_enemy_tech_to_block(block_kind):
        """Selecciona técnica objetivo por tipo para bloqueo de 1 turno."""
        techniques = getattr(S, "battle_techniques", {}) or {}

        preferred_off = ["attack_reducer", "direct_attack", "noatk_attack", "stronger_attack", "extra_attack", "extra_tech"]
        preferred_def = ["defense_reducer", "defense_reflect", "defense_strong_block", "defense_extra", "salvaguarda_principiante"]

        if block_kind == "focus":
            return "focus"

        pool = preferred_off if block_kind == "offense" else preferred_def
        for tid in pool:
            t = techniques.get(tid, {}) if isinstance(techniques, dict) else {}
            if isinstance(t, dict) and t:
                return tid

        # fallback robusto por type
        for tid, t in (techniques.items() if isinstance(techniques, dict) else []):
            if not isinstance(t, dict):
                continue
            ttype = str(t.get("type", "") or "")
            if block_kind == "offense" and ttype == "offensive":
                return str(tid)
            if block_kind == "defense" and ttype == "defensive":
                return str(tid)

        return ""

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
    log_cost_meta      = _get_style("log_cost_meta")

    def _cost_line(rei, ene):
        if callable(log_cost_meta):
            return log_cost_meta(rei, ene)
        if callable(fmt_white):
            return fmt_white("(EP {} / EC {})".format(_fmt_num(rei), _fmt_num(ene)))
        return "(EP {} / EC {})".format(_fmt_num(rei), _fmt_num(ene))


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
            "Ataque básico":  "stronger_attack",
            "Ataque más fuerte":  "stronger_attack",  # alias legacy
            "Ladrón ofensivo":    "ladron_ofensivo",
            "Ladrón defensivo":   "ladron_defensivo",
            "Ladrón de concentrar": "ladron_concentrar",

            "Concentrar":         "focus",
            "Concentrar x2":      "focus",
            "Dados de furia":     "fury_dice",
            "Descansar":          "rest_recovery",
            "Efecto especial":    "character_special_effect",
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

        # Telemetría de consumo ofensivo por turno (para registro detallado)
        S.turn_off_rei_before = int(getattr(S, "player_reiatsu", 0) or 0)
        S.turn_off_ene_before = int(getattr(S, "player_energy", 0) or 0)
        S.turn_off_rei_tech_sum = 0
        S.turn_off_ene_tech_sum = 0
        S.turn_offensive_damage_records = []

        def _add_turn_start_damage_payload(payload):
            global total_damage, combo_count
            if not isinstance(payload, dict):
                return
            defensible = max(0, int(payload.get("defensible", 0) or 0))
            direct = max(0, int(payload.get("direct", 0) or 0))
            amount = int(defensible) + int(direct)
            if amount <= 0:
                return
            base = max(amount, int(payload.get("base", amount) or amount))
            tech_id = str(payload.get("tech_id", "turn_start_effect") or "turn_start_effect")
            tech_name = str(payload.get("tech_name", "Efecto de inicio") or "Efecto de inicio")
            total_damage += int(amount)
            combo_count += 1
            try:
                attack_records.append((int(base), int(amount)))
                S.turn_offensive_damage_records.append({
                    "queue_index": -1,
                    "tech_id": tech_id,
                    "tech_name": tech_name,
                    "base": int(base),
                    "damage": int(amount),
                    "attack_record_index": int(len(attack_records) - 1),
                })
            except:
                pass
            if direct > 0:
                try:
                    S.direct_guaranteed_base_damage = int(getattr(S, "direct_guaranteed_base_damage", 0) or 0) + int(direct)
                    S.direct_guaranteed_pending_damage = int(getattr(S, "direct_guaranteed_pending_damage", 0) or 0) + int(direct)
                except:
                    pass
            try:
                S.turn_offensive_attack_used = True
            except:
                pass

        try:
            fn_hanabi_keep = getattr(S, "bs_hanabi_juken_player_turn_maintenance", None)
            if callable(fn_hanabi_keep):
                fn_hanabi_keep()
        except:
            pass
        try:
            fn_shino_keep = getattr(S, "bs_shino_insects_player_turn_maintenance", None)
            if callable(fn_shino_keep):
                fn_shino_keep()
        except:
            pass
        try:
            fn_nobara_keep = getattr(S, "bs_nobara_nails_player_turn_maintenance", None)
            if callable(fn_nobara_keep):
                fn_nobara_keep()
        except:
            pass
        try:
            fn_maki_turn = getattr(S, "bs_maki_ritual_player_turn_start", None)
            if callable(fn_maki_turn):
                fn_maki_turn()
        except:
            pass
        try:
            fn_shadow_keep = getattr(S, "bs_shadowheart_shar_player_turn_maintenance", None)
            if callable(fn_shadow_keep):
                fn_shadow_keep()
        except:
            pass
        try:
            fn_elizabeth_boost_turn = getattr(S, "bs_elizabeth_attack_boost_turn_start", None)
            if callable(fn_elizabeth_boost_turn):
                fn_elizabeth_boost_turn()
        except:
            pass
        try:
            fn_elizabeth_assist = getattr(S, "bs_elizabeth_assist_player_turn_start", None)
            if callable(fn_elizabeth_assist):
                fn_elizabeth_assist()
        except:
            pass
        try:
            fn_gotenks = getattr(S, "bs_gotenks_player_turn_start", None)
            if callable(fn_gotenks):
                _gotenks_carry = max(0, int(fn_gotenks() or 0))
                if _gotenks_carry > 0:
                    total_damage += int(_gotenks_carry)
                    combo_count += 1
                    try:
                        attack_records.append((int(_gotenks_carry), int(_gotenks_carry)))
                        S.turn_offensive_damage_records.append({
                            "queue_index": -1,
                            "tech_id": "gotenks_clown_carry",
                            "tech_name": "Ataque Payaso acumulado",
                            "base": int(_gotenks_carry),
                            "damage": int(_gotenks_carry),
                            "attack_record_index": int(len(attack_records) - 1),
                        })
                    except:
                        pass
        except:
            pass
        try:
            fn_gorou_male = getattr(S, "bs_gorou_male_player_turn_start", None)
            if callable(fn_gorou_male):
                _gorou_carry = max(0, int(fn_gorou_male() or 0))
                if _gorou_carry > 0:
                    total_damage += int(_gorou_carry)
                    combo_count += 1
                    try:
                        attack_records.append((int(_gorou_carry), int(_gorou_carry)))
                        S.turn_offensive_damage_records.append({
                            "queue_index": -1,
                            "tech_id": "gorou_male_formation_carry",
                            "tech_name": "Formacion Defensiva acumulada",
                            "base": int(_gorou_carry),
                            "damage": int(_gorou_carry),
                            "attack_record_index": int(len(attack_records) - 1),
                        })
                    except:
                        pass
        except:
            pass
        try:
            fn_u1196 = getattr(S, "bs_u1196_player_turn_start", None)
            if callable(fn_u1196):
                _u1196_carry = max(0, int(fn_u1196() or 0))
                if _u1196_carry > 0:
                    total_damage += int(_u1196_carry)
                    combo_count += 1
                    try:
                        attack_records.append((int(_u1196_carry), int(_u1196_carry)))
                        S.turn_offensive_damage_records.append({
                            "queue_index": -1,
                            "tech_id": "u1196_neutralization_carry",
                            "tech_name": "Neutralizacion de Amenaza acumulada",
                            "base": int(_u1196_carry),
                            "damage": int(_u1196_carry),
                            "attack_record_index": int(len(attack_records) - 1),
                        })
                    except:
                        pass
        except:
            pass
        try:
            fn_canoness_regen = getattr(S, "bs_canoness_player_turn_start", None)
            if callable(fn_canoness_regen):
                fn_canoness_regen()
        except:
            pass
        try:
            fn_kuki = getattr(S, "bs_kuki_ring_player_turn_start", None)
            if callable(fn_kuki):
                fn_kuki()
        except:
            pass
        try:
            fn_juri = getattr(S, "bs_juri_player_turn_start", None)
            if callable(fn_juri):
                fn_juri()
        except:
            pass
        try:
            fn_yuji = getattr(S, "bs_yuji_player_turn_start", None)
            if callable(fn_yuji):
                fn_yuji()
        except:
            pass
        try:
            fn_power = getattr(S, "bs_power_player_turn_start", None)
            if callable(fn_power):
                _add_turn_start_damage_payload(fn_power())
        except:
            pass
        try:
            fn_tayuya = getattr(S, "bs_tayuya_player_turn_start", None)
            if callable(fn_tayuya):
                _add_turn_start_damage_payload(fn_tayuya())
        except:
            pass
        try:
            fn_sasori = getattr(S, "bs_sasori_player_turn_start", None)
            if callable(fn_sasori):
                _add_turn_start_damage_payload(fn_sasori())
        except:
            pass
        try:
            fn_ajisai = getattr(S, "bs_ajisai_pain_player_turn_start", None)
            if callable(fn_ajisai):
                _add_turn_start_damage_payload(fn_ajisai())
        except:
            pass
        try:
            fn_lae_extra = getattr(S, "bs_lae_zel_pending_extra_actions_start", None)
            if callable(fn_lae_extra):
                _lae_extra = max(0, int(fn_lae_extra() or 0))
                if _lae_extra > 0:
                    actions += int(_lae_extra)
        except:
            pass
        try:
            fn_revy = getattr(S, "bs_revy_barrage_player_turn_start", None)
            if callable(fn_revy):
                _revy_damage = max(0, int(fn_revy() or 0))
                if _revy_damage > 0:
                    try:
                        fn_elizabeth_boost = getattr(S, "bs_elizabeth_apply_attack_boost", None)
                        if callable(fn_elizabeth_boost):
                            _revy_boosted = int(fn_elizabeth_boost(int(_revy_damage), "revy_barrage_tick") or int(_revy_damage))
                            if _revy_boosted != int(_revy_damage):
                                _blog("Asistencia Ingeniosa: +50% ataque general en Lluvia de balas ({} -> {}).".format(_fmt_num(_revy_damage), _fmt_num(_revy_boosted)), "#7FE3FF")
                            _revy_damage = max(0, int(_revy_boosted))
                    except:
                        pass
                    total_damage += int(_revy_damage)
                    combo_count += 1
                    try:
                        attack_records.append((int(_revy_damage), int(_revy_damage)))
                        S.turn_offensive_damage_records.append({
                            "queue_index": -1,
                            "tech_id": "revy_barrage_tick",
                            "tech_name": "Lluvia de balas",
                            "base": int(_revy_damage),
                            "damage": int(_revy_damage),
                            "attack_record_index": int(len(attack_records) - 1),
                        })
                    except:
                        pass
        except:
            pass

        # ----------------------------------------------------
        # 1) Strings → OffAction
        # ----------------------------------------------------
        selected_actions = []
        for i, tech_name in enumerate(selected or []):
            act = make_action_from_name(tech_name, i)
            if act:
                selected_actions.append(act)

        try:
            _has_visual_attack = False
            for _vis_act in selected_actions:
                _tid = str(getattr(_vis_act, "tech_id", "") or "")
                _typ = str(getattr(_vis_act, "type", "") or "")
                if _tid == "character_special_effect" or _typ == "offensive":
                    _has_visual_attack = True
                    break
            if _has_visual_attack:
                _pose_fn = getattr(S, "bs_battle_show_character_pose", None)
                if callable(_pose_fn):
                    _pose_fn("player", trigger="offensive")
        except:
            pass

        # ----------------------------------------------------
        # 2) Loop principal
        # ----------------------------------------------------
        for action in selected_actions:

            if awaiting_turn_end:
                break

            # -------------------------
            # 🔹 CONCENTRAR (focus)
            # -------------------------
            if action.tech_id == "character_special_effect":
                if actions <= 0:
                    _blog("No quedan acciones para usar Efecto especial.", "#FF8888")
                    action.used = True
                    continue

                try:
                    fn_avail = getattr(S, "bs_character_special_effect_available", None)
                    if callable(fn_avail) and (not bool(fn_avail("player"))):
                        _blog("Efecto especial no disponible en esta fase.", "#FFD166")
                        action.used = True
                        continue
                except:
                    pass

                focus_mult = _focus_mult_peek_offensive()
                if focus_mult < 1:
                    focus_mult = 1

                special_effect_already_used = False
                try:
                    fn_used = getattr(S, "bs_character_special_effect_used", None)
                    special_effect_already_used = bool(fn_used("player")) if callable(fn_used) else False
                except:
                    special_effect_already_used = False

                base_value = 100
                try:
                    fn_val = getattr(S, "final_value_factory", None)
                    if callable(fn_val):
                        base_value = int(fn_val(action.tech_id, S, unit_key=_off_player_unit_key()) or 100)
                except:
                    base_value = 100

                try:
                    cost = S.reiatsu_energy_dynamic_cost(action.tech_id, S, force_focus_mult=focus_mult, unit_key=_off_player_unit_key())
                except:
                    cost = {}
                rei_cost = int(cost.get("reiatsu_cost", 0) or 0)
                ene_cost = int(cost.get("energy_cost", 0) or 0)
                if special_effect_already_used:
                    ene_cost = 0
                try:
                    fn_maki_zero = getattr(S, "bs_maki_special_forces_zero_ec", None)
                    if callable(fn_maki_zero) and bool(fn_maki_zero("player", "character_special_effect")):
                        ene_cost = 0
                except:
                    pass

                seal_free_costs = False
                try:
                    seal_mode = str(getattr(S, "bs_seal_free_resources_mode", "") or "").strip().lower()
                    cur_mode = str(getattr(S, "battle_mode", "") or "").strip().lower()
                    seal_free_costs = bool(getattr(S, "bs_seal_free_resources_turn_active", False)) and ((not seal_mode) or seal_mode == cur_mode)
                except:
                    seal_free_costs = False

                try:
                    pr = int(getattr(S, "player_reiatsu", 0) or 0)
                    pe = int(getattr(S, "player_energy", 0) or 0)
                except:
                    pr, pe = 0, 0
                if (not seal_free_costs) and (pr < rei_cost or pe < ene_cost):
                    _blog("No puedes usar Efecto especial: Recursos insuficientes.", "#FF8888")
                    action.used = True
                    continue

                try:
                    spent_r, spent_e = S.consume_resources(rei_cost, ene_cost, actor="player")
                except:
                    spent_r, spent_e = rei_cost, ene_cost
                S.turn_off_rei_tech_sum += int(spent_r or 0)
                S.turn_off_ene_tech_sum += int(spent_e or 0)

                final_value = int(base_value or 100)
                try:
                    fn_apply = getattr(S, "apply_offensive_focus", None)
                    if callable(fn_apply):
                        final_value = int(fn_apply(base_value) or base_value)
                    elif focus_mult > 1:
                        final_value = int(base_value) * int(focus_mult)
                except:
                    if focus_mult > 1:
                        final_value = int(base_value) * int(focus_mult)

                S.bs_character_special_effect_runtime_value = int(final_value)
                S.bs_character_special_effect_runtime_base = int(base_value)
                S.bs_character_special_effect_damage_pending = 0
                S.bs_character_special_effect_direct_pending = 0
                S.bs_character_special_effect_extra_actions_pending = 0
                try:
                    fn_fx = getattr(S, "bs_use_character_special_effect", None)
                    ok_fx = bool(fn_fx("player")) if callable(fn_fx) else False
                except:
                    ok_fx = False
                try:
                    special_damage = max(0, int(getattr(S, "bs_character_special_effect_damage_pending", 0) or 0))
                except:
                    special_damage = 0
                try:
                    special_direct = max(0, int(getattr(S, "bs_character_special_effect_direct_pending", 0) or 0))
                except:
                    special_direct = 0
                try:
                    special_extra_actions = max(0, int(getattr(S, "bs_character_special_effect_extra_actions_pending", 0) or 0))
                except:
                    special_extra_actions = 0
                try:
                    fn_elizabeth_boost = getattr(S, "bs_elizabeth_apply_attack_boost", None)
                    if callable(fn_elizabeth_boost):
                        _sd_before = int(special_damage or 0)
                        _sg_before = int(special_direct or 0)
                        special_damage = int(fn_elizabeth_boost(_sd_before, "character_special_effect") or _sd_before)
                        special_direct = int(fn_elizabeth_boost(_sg_before, "character_special_effect") or _sg_before)
                        _sd_before_total = int(_sd_before) + int(_sg_before)
                        _sd_after_total = int(special_damage or 0) + int(special_direct or 0)
                        if _sd_after_total != _sd_before_total:
                            _blog("Asistencia Ingeniosa: +50% ataque general ({} -> {}).".format(_fmt_num(_sd_before_total), _fmt_num(_sd_after_total)), "#7FE3FF")
                except:
                    pass
                try:
                    del S.bs_character_special_effect_runtime_value
                    del S.bs_character_special_effect_runtime_base
                    del S.bs_character_special_effect_damage_pending
                    del S.bs_character_special_effect_direct_pending
                    del S.bs_character_special_effect_extra_actions_pending
                except:
                    pass
                if not ok_fx:
                    _blog("Efecto especial no disponible para este heroe.", "#FFD166")
                elif special_damage > 0 or special_direct > 0:
                    _special_total = int(special_damage) + int(special_direct)
                    total_damage += int(_special_total)
                    combo_count += 1
                    try:
                        attack_records.append((int(final_value or base_value or 0), int(_special_total)))
                        S.turn_offensive_damage_records.append({
                            "queue_index": int(action.position or 0),
                            "tech_id": str(action.tech_id or ""),
                            "tech_name": str(action.name or ""),
                            "base": int(final_value or base_value or 0),
                            "damage": int(_special_total),
                            "attack_record_index": int(len(attack_records) - 1),
                        })
                    except:
                        pass
                    if special_direct > 0:
                        try:
                            S.direct_guaranteed_base_damage = int(getattr(S, "direct_guaranteed_base_damage", 0) or 0) + int(special_direct)
                            S.direct_guaranteed_pending_damage = int(getattr(S, "direct_guaranteed_pending_damage", 0) or 0) + int(special_direct)
                        except:
                            pass
                    try:
                        S.turn_offensive_attack_used = True
                    except:
                        pass
                    try:
                        fx_hit_red(int(_special_total), "#FF6666", 0.35)
                    except:
                        pass
                    try:
                        battle_visual_float("enemy", int(_special_total), "#FF6666", is_final=False)
                    except:
                        pass
                    _offensive_fx_hit_pause()
                if ok_fx and special_extra_actions > 0:
                    actions += int(special_extra_actions)
                    try:
                        _blog("Efecto especial: +%s accion(es) ofensiva(s) disponible(s)." % str(int(special_extra_actions)), "#FFAA66")
                    except:
                        pass
                actions -= 1
                action.used = True
                can_focus = False
                continue

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
                try:
                    fn_hbreak = getattr(S, "bs_battle_enqueue_focus_break", None)
                    if callable(fn_hbreak):
                        fn_hbreak("enemy", "CONCENTRAR")
                except:
                    pass
                _offensive_fx_hit_pause(0.18)

                can_focus = False
                continue

            # -------------------------
            # 🔹 DADOS DE FURIA (especial implícita tipo Concentrar)
            # -------------------------
            if action.tech_id == "fury_dice":
                try:
                    fn_can_f = getattr(S, "can_use_fury_dice", None)
                    _can_f = bool(fn_can_f("player")) if callable(fn_can_f) else False
                except:
                    _can_f = False

                if not _can_f:
                    _blog("Dados de furia no disponible: requiere HP ≤ 25% (o ítem).", "#FF8888")
                    action.used = True
                    continue

                try:
                    fn_pay_f = getattr(S, "can_pay_fury_activation", None)
                    _pay_f = bool(fn_pay_f("player")) if callable(fn_pay_f) else True
                except:
                    _pay_f = True

                if not _pay_f:
                    try:
                        fn_fc = getattr(S, "fury_activation_costs", None)
                        _fc = fn_fc("player") if callable(fn_fc) else {}
                    except:
                        _fc = {}
                    _blog("Dados de furia no disponible: coste base R {} / E {}.".format(
                        _fmt_num(int((_fc or {}).get("reiatsu_need", 0) or 0)),
                        _fmt_num(int((_fc or {}).get("energy_need", 0) or 0)),
                    ), "#FF8888")
                    action.used = True
                    continue

                _target_pos = -1
                _target_name = ""
                for _nx in selected_actions:
                    if int(getattr(_nx, "position", -1) or -1) <= int(action.position or 0):
                        continue
                    if str(getattr(_nx, "type", "") or "") == "offensive":
                        _target_pos = int(getattr(_nx, "position", -1) or -1)
                        _target_name = str(getattr(_nx, "name", "") or "")
                        break

                if _target_pos < 0:
                    _blog("Dados de furia requiere una técnica ofensiva posterior en la cola.", "#FF8888")
                    action.used = True
                    continue

                try:
                    S.fury_selected_turn_index = int(_target_pos)
                    S.fury_selection = {
                        "queue_index": int(_target_pos),
                        "tech_name": str(_target_name),
                        "tech_id": str(getattr(_nx, "tech_id", "") or ""),
                        "armed": True,
                    }
                except:
                    pass

                _blog("🔥 Dados de furia cargados sobre '{}' (posibles: x1 / x2 / x3).".format(_target_name), "#FF9966")
                action.used = True
                can_focus = False
                continue

            # -------------------------
            # 🔹 DESCANSAR (+5% HP base, +25% R/E base)
            # -------------------------
            if action.tech_id == "rest_recovery":
                try:
                    fn_rest = getattr(S, "battle_apply_rest_recovery", None)
                    if not callable(fn_rest):
                        fn_rest = globals().get("battle_apply_rest_recovery", None)
                    if callable(fn_rest):
                        prev_hp = int(getattr(S, "player_hp", 0) or 0)
                        prev_rei = int(getattr(S, "player_reiatsu", 0) or 0)
                        prev_ene = int(getattr(S, "player_energy", 0) or 0)
                        fn_rest()
                        gain_hp = max(0, int(getattr(S, "player_hp", 0) or 0) - prev_hp)
                        gain_rei = max(0, int(getattr(S, "player_reiatsu", 0) or 0) - prev_rei)
                        gain_ene = max(0, int(getattr(S, "player_energy", 0) or 0) - prev_ene)
                        _blog("Descansar → +{} HP / +{} EP / +{} EC.".format(_fmt_num(gain_hp), _fmt_num(gain_rei), _fmt_num(gain_ene)), "#A5D6A7")
                    else:
                        _blog("Descansar no disponible (falta helper).", "#FF8888")
                except:
                    _blog("Descansar no disponible (error).", "#FF8888")
                actions -= 1
                action.used = True
                can_focus = True
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
                    action.base_value = int(fn_val(action.tech_id, S, unit_key=_off_player_unit_key()) or 0)
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
                    cost = cost_fn(action.tech_id, S, force_focus_mult=focus_mult, unit_key=_off_player_unit_key())
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
            try:
                fn_maki_zero = getattr(S, "bs_maki_special_forces_zero_ec", None)
                if callable(fn_maki_zero) and bool(fn_maki_zero("player", action.tech_id)):
                    ene_cost = 0
            except:
                pass

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

            seal_free_costs = False
            try:
                seal_mode = str(getattr(S, "bs_seal_free_resources_mode", "") or "").strip().lower()
                cur_mode = str(getattr(S, "battle_mode", "") or "").strip().lower()
                seal_free_costs = bool(getattr(S, "bs_seal_free_resources_turn_active", False)) and ((not seal_mode) or seal_mode == cur_mode)
            except:
                seal_free_costs = False

            if (not seal_free_costs) and (pr < rei_cost or pe < ene_cost):
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

            # ----------------------------------------------------
            # ===== LADRÓN ... (bloqueo de técnica por 1 turno) =====
            # ----------------------------------------------------
            if tech in ("ladron_ofensivo", "ladron_defensivo", "ladron_concentrar"):

                block_kind = "offense"
                phase = "offense"
                if tech == "ladron_defensivo":
                    block_kind = "defense"
                    phase = "defense"
                elif tech == "ladron_concentrar":
                    block_kind = "focus"
                    phase = "offense"

                target_key = _off_enemy_unit_key()
                target_tech = _pick_enemy_tech_to_block(block_kind)
                blocked_ok = False
                try:
                    fn_block = getattr(S, "ai_block_tech_for_unit", None)
                    if callable(fn_block) and target_tech:
                        blocked_ok = bool(fn_block(target_key, target_tech, turns=1, phase=phase, reason=tech))
                except:
                    blocked_ok = False

                try:
                    S.consume_resources(rei_cost, ene_cost, actor="player")
                except:
                    try:
                        S.consume_resources(rei_cost, ene_cost, "player")
                    except:
                        pass

                S.turn_off_rei_tech_sum += int(rei_cost or 0)
                S.turn_off_ene_tech_sum += int(ene_cost or 0)

                actions -= 1
                action.used = True
                can_focus = True

                if blocked_ok and target_tech:
                    _blog("{} → bloquea {} en {} por 1 turno. {}".format(action.name, str(target_tech), str(target_key), _cost_line(rei_cost, ene_cost)), "#B39DDB")
                else:
                    _blog("{} ejecutada (sin objetivo válido de bloqueo). {}".format(action.name, _cost_line(rei_cost, ene_cost)), "#B39DDB")

                continue

            try:
                fn_maki_bonus = getattr(S, "bs_maki_apply_ritual_damage", None)
                if callable(fn_maki_bonus):
                    _maki_before = int(dmg or 0)
                    _maki_after = int(fn_maki_bonus(_maki_before, tech) or _maki_before)
                    if _maki_after != _maki_before:
                        dmg = int(_maki_after)
                        action.final_value = int(_maki_after)
                        _pct = float(getattr(S, "bs_maki_ritual_last_bonus_pct", 0.0) or 0.0)
                        _blog("Ritual sagrado: +{}% ataque fisico ({} -> {}).".format(int(round(_pct * 100.0)), _fmt_num(_maki_before), _fmt_num(_maki_after)), "#F5D76E")
            except:
                pass

            try:
                fn_elizabeth_boost = getattr(S, "bs_elizabeth_apply_attack_boost", None)
                if callable(fn_elizabeth_boost):
                    _elizabeth_before = int(dmg or 0)
                    _elizabeth_after = int(fn_elizabeth_boost(_elizabeth_before, tech) or _elizabeth_before)
                    if _elizabeth_after != _elizabeth_before:
                        dmg = int(_elizabeth_after)
                        action.final_value = int(_elizabeth_after)
                        _blog("Asistencia Ingeniosa: +50% ataque general ({} -> {}).".format(_fmt_num(_elizabeth_before), _fmt_num(_elizabeth_after)), "#7FE3FF")
            except:
                pass

            # Guardar para fórmula
            try:
                attack_records.append((action.base_value, action.final_value))
                S.turn_offensive_damage_records.append({
                    "queue_index": int(action.position or 0),
                    "tech_id": str(action.tech_id or ""),
                    "tech_name": str(action.name or ""),
                    "base": int(action.base_value or 0),
                    "damage": int(action.final_value or 0),
                    "attack_record_index": int(len(attack_records) - 1),
                })
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

                S.direct_base_damage    = int(getattr(S, "direct_base_damage", 0) or 0) + int(action.base_value)
                S.direct_pending_damage = int(getattr(S, "direct_pending_damage", 0) or 0) + int(dmg)
                total_damage += dmg
                combo_count += 1

                try:
                    if callable(fmt_red) and callable(fmt_white) and callable(fmt_orange):
                        _blog(
                            fmt_red("Ataque Directo") +
                            fmt_white(" → Inflige {} de daño. ".format(make_dmg_text(action.base_value, dmg))) +
                            fmt_orange("Si saca 2/3 dados de éxito, este ataque es indefendible. ") +
                            _cost_line(rei_cost, ene_cost)
                        )
                    else:
                        _blog("Ataque Directo → Inflige {} de daño. (EP {} / EC {})".format(
                            make_dmg_text(action.base_value, dmg), _fmt_num(rei_cost), _fmt_num(ene_cost)
                        ), "#FFDD44")
                except:
                    _blog("Ataque Directo → Inflige {} de daño. (EP {} / EC {})".format(
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
                _offensive_fx_hit_pause()

                try:
                    S.consume_resources(rei_cost, ene_cost, actor="player")
                except:
                    try:
                        S.consume_resources(rei_cost, ene_cost, "player")
                    except:
                        pass

                S.turn_off_rei_tech_sum += int(rei_cost or 0)
                S.turn_off_ene_tech_sum += int(ene_cost or 0)

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
                _offensive_fx_hit_pause()

                try:
                    if callable(fmt_red) and callable(fmt_white) and callable(fmt_orange):
                        _blog(
                            fmt_red("Ataque Negador") +
                            fmt_white(" → Inflige {} de daño. ".format(make_dmg_text(action.base_value, dmg))) +
                            _cost_line(rei_cost, ene_cost) + " " +
                            fmt_orange("Si saca 2/3 dados de éxito, el enemigo no puede atacar en su siguiente turno.")
                        )
                    else:
                        _blog("Ataque Negador → Inflige {} de daño. (EP {} / EC {})".format(
                            make_dmg_text(action.base_value, dmg), _fmt_num(rei_cost), _fmt_num(ene_cost)
                        ), "#FF66CC")
                except:
                    _blog("Ataque Negador → Inflige {} de daño. (EP {} / EC {})".format(
                        make_dmg_text(action.base_value, dmg), _fmt_num(rei_cost), _fmt_num(ene_cost)
                    ), "#FF66CC")

                try:
                    S.consume_resources(rei_cost, ene_cost, actor="player")
                except:
                    try:
                        S.consume_resources(rei_cost, ene_cost, "player")
                    except:
                        pass

                S.turn_off_rei_tech_sum += int(rei_cost or 0)
                S.turn_off_ene_tech_sum += int(ene_cost or 0)

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
                    _inc_red = float(action.data.get("defense_reduction", 0.10) or 0.10)
                except:
                    _inc_red = 0.10
                try:
                    _cur_red = float(getattr(S, "next_defense_reduction", 0.0) or 0.0)
                except:
                    _cur_red = 0.0
                S.next_defense_reduction = min(0.90, _cur_red + max(0.0, _inc_red))

                try:
                    fx_hit_red(dmg, "#FF9966", 0.28)
                except:
                    pass
                try:
                    battle_visual_float("enemy", dmg, "#FF9966", is_final=False)
                except:
                    pass
                _offensive_fx_hit_pause()

                try:
                    if callable(log_attack_reducer) and callable(fmt_white):
                        _blog(
                            log_attack_reducer(
                                action.name,
                                make_dmg_text(action.base_value, dmg),
                                int((getattr(S, "next_defense_reduction", 0.10) or 0.10) * 100)
                            ) +
                            fmt_white(" ") + _cost_line(rei_cost, ene_cost)
                        )
                    else:
                        _blog("{} → {} daño. (-{}% DEF) (EP {} / EC {})".format(
                            action.name,
                            make_dmg_text(action.base_value, dmg),
                            int((getattr(S, "next_defense_reduction", 0.10) or 0.10) * 100),
                            _fmt_num(rei_cost),
                            _fmt_num(ene_cost)
                        ), "#FF9966")
                except:
                    _blog("{} → {} daño. (-{}% DEF) (EP {} / EC {})".format(
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

                S.turn_off_rei_tech_sum += int(rei_cost or 0)
                S.turn_off_ene_tech_sum += int(ene_cost or 0)

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
                _offensive_fx_hit_pause()

                try:
                    if callable(fmt_red) and callable(fmt_white):
                        _blog(
                            fmt_red("Ataque básico") +
                            fmt_white(" → Inflige ") +
                            fmt_red(make_dmg_text(action.base_value, dmg)) +
                            fmt_white(" de daño. ") +
                            _cost_line(rei_cost, ene_cost)
                        )
                    else:
                        _blog("Ataque básico → {} daño. (EP {} / EC {})".format(
                            make_dmg_text(action.base_value, dmg), _fmt_num(rei_cost), _fmt_num(ene_cost)
                        ), "#FF4444")
                except:
                    _blog("Ataque básico → {} daño. (EP {} / EC {})".format(
                        make_dmg_text(action.base_value, dmg), _fmt_num(rei_cost), _fmt_num(ene_cost)
                    ), "#FF4444")

                try:
                    S.consume_resources(rei_cost, ene_cost, actor="player")
                except:
                    try:
                        S.consume_resources(rei_cost, ene_cost, "player")
                    except:
                        pass

                S.turn_off_rei_tech_sum += int(rei_cost or 0)
                S.turn_off_ene_tech_sum += int(ene_cost or 0)

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
                _offensive_fx_hit_pause()

                try:
                    if callable(log_attack_simple) and callable(fmt_white):
                        _blog(
                            log_attack_simple(action.name, make_dmg_text(action.base_value, dmg)) +
                            _cost_line(rei_cost, ene_cost)
                        )
                    else:
                        _blog("{} → {} daño. (EP {} / EC {})".format(
                            action.name,
                            make_dmg_text(action.base_value, dmg),
                            _fmt_num(rei_cost),
                            _fmt_num(ene_cost)
                        ), "#FF8888")
                except:
                    _blog("{} → {} daño. (EP {} / EC {})".format(
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

                S.turn_off_rei_tech_sum += int(rei_cost or 0)
                S.turn_off_ene_tech_sum += int(ene_cost or 0)

                action.used = True
                continue


        # ----------------------------------------------------
        # RESET visual (simulación HUD)
        # ----------------------------------------------------
        if hasattr(S, "simulated_reiatsu"):
            S.simulated_reiatsu = getattr(S, "player_reiatsu", 0)
        if hasattr(S, "simulated_energy"):
            S.simulated_energy = getattr(S, "player_energy", 0)

        S.turn_off_rei_after = int(getattr(S, "player_reiatsu", 0) or 0)
        S.turn_off_ene_after = int(getattr(S, "player_energy", 0) or 0)

    return
