# ============================================================
# 04D_AI_REACTIVE_DEFENSE_ENGINE.rpy – Execution Engine
# v12.4.1 ReflectQueue Centralized (Target=Attacker, Source=Defender) ✅
# ------------------------------------------------------------
# Exporta:
#   S.ai_defense_execute_plan(plan, dmg_effective, name, border)
# Devuelve:
#   {"final_damage": int, "reflected": int}
#
# ✅ FIX REFLECT:
#   - ReflectManager guarda POR OBJETIVO (quien RECIBE el daño reflejado)
#   - source_id = quien lo GENERÓ (defensor que activó reflect)
#   - En defensa IA: target = current_actor_id (jugador que atacó)
#                   source = current_enemy_id (IA que defendió)
#   - Centraliza vía S.reflect_queue() si existe
# ============================================================

init -988 python:

    def ai_defense_execute_plan(plan, dmg_effective, name, border="#FFFFFF"):
        import renpy.store as S

        # -------------------------------
        # 🎨 PALETTE store-safe
        # -------------------------------
        PAL = getattr(S, "PALETTE", {}) or {}
        def _pal(key, fallback="#FFFFFF"):
            try:
                return PAL.get(key, fallback)
            except:
                return fallback

        # Helpers: chequeo/consumo (store-safe)
        can_pay_fn = getattr(S, "ai_can_pay", None)
        if not callable(can_pay_fn):
            can_pay_fn = globals().get("ai_can_pay", None)

        def _enemy_unit_key():
            try:
                fnk = getattr(S, "ai_get_current_enemy_unit_key", None)
                if callable(fnk):
                    k = str(fnk() or "")
                    if k:
                        return k
            except:
                pass
            try:
                k = str(getattr(S, "current_enemy_unit_key", "") or "")
                if k:
                    return k
            except:
                pass
            return "enemy:0"

        def _consume_for(real_id):
            """
            Consume recursos para real_id y devuelve (rei_cost, ene_cost).
            NO aplica enemy_focus_cost_pending (solo ofensivo).
            """
            def_mult = 1
            try:
                fn_def_mult = getattr(S, "defensive_boost_multiplier_peek", None)
                if callable(fn_def_mult):
                    def_mult = int(fn_def_mult() or 1)
                    if def_mult < 1:
                        def_mult = 1
            except:
                def_mult = 1

            try:
                cost = S.reiatsu_energy_dynamic_cost(real_id, S, force_focus_mult=def_mult, unit_key=_enemy_unit_key())
            except:
                cost = {}

            try:
                rei_cost = int(cost.get("reiatsu_cost", 0) or 0)
            except:
                rei_cost = 0
            try:
                ene_cost = int(cost.get("energy_cost", 0) or 0)
            except:
                ene_cost = 0

            try:
                if hasattr(S, "consume_resources"):
                    S.consume_resources(rei_cost, ene_cost, "enemy")
            except:
                pass

            return rei_cost, ene_cost

        def _focus_allowed_unit():
            try:
                fnk = getattr(S, "ai_get_current_enemy_unit_key", None)
                unit_key = str(fnk() or "") if callable(fnk) else str(getattr(S, "current_enemy_unit_key", "") or "")
            except:
                unit_key = ""
            try:
                fnf = getattr(S, "ai_effective_allow_focus", None)
                if callable(fnf):
                    return bool(fnf(unit_key))
            except:
                pass
            return bool(getattr(S, "ai_allow_focus", True))

        fn_cost_meta = getattr(S, "log_cost_meta", None)
        if not callable(fn_cost_meta):
            fn_cost_meta = globals().get("log_cost_meta", None)

        # -------------------------------
        # ACUMULADORES
        # -------------------------------
        blocks_list     = []
        total_block     = 0
        reflected_total = 0
        reduc_val       = 0
        reduc_percent   = 0.0
        summary_lines   = []
        focus_used      = False
        ref_pct_used    = 0.0

        # -------------------------------
        # LOOP técnicas
        # -------------------------------
        for key in (plan or []):

            # ⭐ Focus defensivo (gratis)
            if key == "focus":
                if not _focus_allowed_unit():
                    try:
                        S.battle_log_add("%s intenta Potenciar, pero Focus IA(unidad) está OFF" % name, "#888888")
                    except:
                        pass
                    continue

                try:
                    if hasattr(S, "activate_defensive_focus"):
                        S.activate_defensive_focus()
                    elif hasattr(S, "activate_focus_defense"):
                        S.activate_focus_defense()
                except:
                    pass

                focus_used = True
                continue

            tech = getattr(S, "battle_techniques", {}).get(key, {})
            if not tech:
                try:
                    S.battle_log_add("{color=#FF6666}[IA DEF] tech missing: %s{/color}" % key)
                except:
                    pass
                continue

            real_id = tech.get("id", key) or key

            # ✅ Chequeo recursos (si existe ai_can_pay)
            if callable(can_pay_fn):
                try:
                    ok, fr, fe = can_pay_fn(real_id, "enemy")
                except:
                    ok, fr, fe = True, 0, 0

                if not ok:
                    try:
                        msg = "%s no puede usar %s (" % (name, tech.get("name", real_id))
                        if fr > 0 and fe > 0:
                            msg += "falta Reiatsu y Energía)"
                        elif fr > 0:
                            msg += "falta Reiatsu)"
                        else:
                            msg += "falta Energía)"
                        S.battle_log_add(msg, "#999999")
                    except:
                        pass
                    continue

            # ✅ Consumir
            rei_cost, ene_cost = _consume_for(real_id)

            # ✅ Valor real
            try:
                base_blk = S.final_value_factory(real_id, S)
            except:
                base_blk = 0

            try:
                blk = S.apply_defensive_focus(base_blk)
            except:
                blk = int(base_blk or 0)

            blocks_list.append((base_blk, blk))
            total_block += int(blk)

            # Logs por tipo
            if key == "def_extra":
                try:
                    summary_lines.append(S.log_defense_extra(base_blk, blk))
                except:
                    pass
                try:
                    summary_lines.append(fn_cost_meta(rei_cost, ene_cost) if callable(fn_cost_meta) else "(Reiatsu %s / Energía %s)" % (S.battle_fmt_num(rei_cost), S.battle_fmt_num(ene_cost)))
                except:
                    pass
                continue

            if key == "def_reduct":
                try:
                    atkred = float(tech.get("attack_reduction", 0.10))
                except:
                    atkred = 0.10

                reduc_val_tmp = int(dmg_effective * atkred)
                reduc_val += reduc_val_tmp
                reduc_percent += atkred

                try:
                    summary_lines.append(
                        S.log_defense_reducer(base_blk, int(atkred * 100), reduc_val_tmp, final=blk)
                    )
                except:
                    pass

                try:
                    summary_lines.append(fn_cost_meta(rei_cost, ene_cost) if callable(fn_cost_meta) else "(Reiatsu %s / Energía %s)" % (S.battle_fmt_num(rei_cost), S.battle_fmt_num(ene_cost)))
                except:
                    pass
                continue

            if key == "defense_strong_block":
                try:
                    fn_strong = getattr(S, "log_defense_strong", None)
                    if callable(fn_strong):
                        summary_lines.append(fn_strong(base_blk, blk))
                    else:
                        summary_lines.append("Defensa Fuerte → Bloquea %s" % S.battle_fmt_num(blk))
                except:
                    pass

                try:
                    summary_lines.append(fn_cost_meta(rei_cost, ene_cost) if callable(fn_cost_meta) else "(Reiatsu %s / Energía %s)" % (S.battle_fmt_num(rei_cost), S.battle_fmt_num(ene_cost)))
                except:
                    pass
                continue

            if key == "def_reflect":
                try:
                    ref_pct = float(tech.get("attack_reflect", 0.10))
                except:
                    ref_pct = 0.10

                ref_pct_used = ref_pct
                reflected_now = int(dmg_effective * ref_pct)
                if reflected_now < 0:
                    reflected_now = 0

                reflected_total += reflected_now

                try:
                    summary_lines.append(
                        S.log_defense_reflect(base_blk, int(ref_pct * 100), reflected_now, final=blk)
                    )
                except:
                    pass

                try:
                    summary_lines.append(fn_cost_meta(rei_cost, ene_cost) if callable(fn_cost_meta) else "(Reiatsu %s / Energía %s)" % (S.battle_fmt_num(rei_cost), S.battle_fmt_num(ene_cost)))
                except:
                    pass
                continue

        # -------------------------------
        # LOG de focus + técnicas
        # -------------------------------
        if focus_used:
            try:
                if hasattr(S, "battle_log_add"):
                    fn_boost = getattr(S, "log_potenciar_unified", None)
                    if callable(fn_boost):
                        S.battle_log_add(fn_boost())
                    else:
                        S.battle_log_add(S.log_focus_unified("defense"))
            except:
                pass

        try:
            if hasattr(S, "battle_log_add"):
                for line in summary_lines:
                    S.battle_log_add(line)
        except:
            pass

        # -------------------------------
        # (1) REDUCTOR
        # -------------------------------
        after_reduc = max(0, int(dmg_effective) - int(reduc_val))

        if reduc_val > 0:
            try:
                S.operation_add(
                    S.op_def_enemy(
                        S.battle_fmt_num(dmg_effective),
                        "{}%".format(int(reduc_percent * 100)),
                        S.battle_fmt_num(reduc_val),
                        S.battle_fmt_num(after_reduc),
                        color_key="effect"
                    ),
                    border
                )
            except:
                pass

        # -------------------------------
        # (2) DEFENSAS con debuff
        # -------------------------------
        block_debuff_percent = float(getattr(S, "next_defense_reduction", 0.0) or 0.0)
        defender_key = str(getattr(S, "current_enemy_unit_key", "") or "")
        allowed_targets = list(getattr(S, "pending_split_effect_targets_enemy", []) or [])
        if allowed_targets and defender_key and defender_key not in allowed_targets:
            block_debuff_percent = 0.0

        block_parts = []
        for base, blk in blocks_list:
            try:
                if int(blk) != int(base):
                    block_parts.append(
                        "{color=%s}%s{/color} ×2 ({color=%s}%s{/color})" % (
                            _pal("blue", "#66CCFF"),
                            S.battle_fmt_num(base),
                            _pal("blue", "#66CCFF"),
                            S.battle_fmt_num(blk)
                        )
                    )
                else:
                    block_parts.append("{color=%s}%s{/color}" % (_pal("blue", "#66CCFF"), S.battle_fmt_num(blk)))
            except:
                pass

        fb_safe = globals().get("fmt_blue", None)
        parts_txt = " + ".join(block_parts) if block_parts else (fb_safe("0") if callable(fb_safe) else "{color=%s}0{/color}" % _pal("blue", "#66CCFF"))

        effective_block = int(total_block)

        try:
            fc = globals().get("fmt_cyan_text", lambda x: x)
            fo = globals().get("fmt_blue", lambda x: x)
            fb = globals().get("fmt_blue", lambda x: x)
        except:
            fc = fo = fb = (lambda x: x)

        if total_block > 0 and block_debuff_percent > 0:
            deb_val = int(total_block * block_debuff_percent)
            effective_block = max(0, int(total_block) - deb_val)

            try:
                S.operation_add(
                    "{}: {} = {} - {}({}) = {}".format(
                        fc("Defensas"),
                        parts_txt,
                        fb(S.battle_fmt_num(total_block)),
                        fo("{}%".format(int(block_debuff_percent * 100))),
                        fb(S.battle_fmt_num(deb_val)),
                        fb(S.battle_fmt_num(effective_block))
                    ),
                    border
                )
            except:
                pass
        else:
            try:
                S.operation_add(
                    "{}: {} = {}".format(fc("Defensas"), parts_txt, fb(S.battle_fmt_num(total_block))),
                    border
                )
            except:
                pass

        # -------------------------------
        # (3) DAÑO FINAL
        # -------------------------------
        final_damage = max(0, int(after_reduc) - int(effective_block))

        try:
            S.operation_add(
                S.op_def_damage(S.battle_fmt_num(after_reduc), S.battle_fmt_num(effective_block), S.battle_fmt_num(final_damage)),
                border
            )
        except:
            pass

        # -------------------------------
        # (4) RECUBRIMIENTO + HP
        # -------------------------------
        hp_before = int(getattr(S, "enemy_hp", 0) or 0)
        coating_type = "Hierro"
        coating_cover = 0
        coating_dura_before = 0
        coating_active = False
        try:
            mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        except:
            mode = "1v1"
        if mode == "2v2" and callable(getattr(S, "bs_get_unit_by_key", None)):
            cu = S.bs_get_unit_by_key(str(getattr(S, "current_enemy_unit_key", "") or ""))
            if isinstance(cu, dict):
                hp_before = int(cu.get("hp", hp_before) or hp_before)
                coating_type = str(cu.get("coating_type", "hierro") or "hierro").capitalize()
                coating_cover = max(0, int(cu.get("coating_cover", 0) or 0))
                coating_dura_before = max(0, int(cu.get("coating_durability_current", 0) or 0))
                coating_active = bool(cu.get("coating_active", False))
        elif callable(getattr(S, "bs_get_unit_by_key", None)):
            cu = S.bs_get_unit_by_key(str(getattr(S, "current_enemy_unit_key", "") or "enemy:0"))
            if isinstance(cu, dict):
                hp_before = int(cu.get("hp", hp_before) or hp_before)
                coating_type = str(cu.get("coating_type", "hierro") or "hierro").capitalize()
                coating_cover = max(0, int(cu.get("coating_cover", 0) or 0))
                coating_dura_before = max(0, int(cu.get("coating_durability_current", 0) or 0))
                coating_active = bool(cu.get("coating_active", False))

        if not (coating_active and coating_cover > 0 and coating_dura_before > 0):
            coating_cover = 0
            coating_dura_before = 0

        after_cover = max(0, int(final_damage) - int(coating_cover))
        coating_dura_after_raw = int(coating_dura_before) - int(after_cover)
        coating_dura_after = max(0, int(coating_dura_after_raw))
        hp_spill = max(0, int(after_cover) - int(coating_dura_before))

        def _fmt_signed(v):
            vv = int(v or 0)
            if vv < 0:
                return "-" + S.battle_fmt_num(abs(vv))
            return S.battle_fmt_num(vv)

        hp_after  = max(0, hp_before - int(hp_spill))

        try:
            S.operation_add(
                "    ◉ {}:".format(str(coating_type or "Recubrimiento")),
                border
            )
            S.operation_add(
                "      cubre: {} - {} = {}".format(
                    S.battle_fmt_num(coating_cover),
                    S.battle_fmt_num(final_damage),
                    S.battle_fmt_num(after_cover)
                ),
                border
            )
            S.operation_add(
                "      durabilidad: {} - {} = {}".format(
                    S.battle_fmt_num(coating_dura_before),
                    S.battle_fmt_num(after_cover),
                    _fmt_signed(coating_dura_after_raw)
                ),
                border
            )
            try:
                fw = globals().get("fmt_white", lambda x: x)
                fr = globals().get("fmt_red", lambda x: x)
                fg = globals().get("fmt_green", lambda x: "{color=%s}%s{/color}" % (_pal("green", "#00FF00"), x))
            except:
                fw = fr = fg = (lambda x: x)

            S.operation_add(
                "      ◉ " + fw("HP:") + " " +
                fg(S.battle_fmt_num(hp_before)) +
                fw(" - ") +
                fr(S.battle_fmt_num(hp_spill)) +
                fw(" = ") +
                (fg(S.battle_fmt_num(hp_after)) if hp_after > 0 else fr("{} KO".format(S.battle_fmt_num(hp_after)))),
                border
            )
        except:
            pass


        # En 1v1, si hubo daño directo del jugador este turno, mostrar HP total esperado.
        direct_pending = 0
        _mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        if _mode != "2v2":
            fn_get_direct = getattr(S, "bs_get_direct_pending", None)
            if callable(fn_get_direct):
                direct_pending = int(fn_get_direct("enemy") or 0)
            else:
                direct_pending = int(getattr(S, "_last_player_direct_damage", 0) or 0)

        if direct_pending > 0:
            hp_after_total = max(0, int(hp_after) - int(direct_pending))
            try:
                try:
                    fw = globals().get("fmt_white", lambda x: x)
                    fo = globals().get("fmt_orange", lambda x: x)
                    fr = globals().get("fmt_red", lambda x: x)
                    _green = _pal("green", "#00FF00")
                    hp_after_fmt = ("{color=%s}%s{/color}" % (_green, S.battle_fmt_num(hp_after))) if hp_after > 0 else fr("{} KO".format(S.battle_fmt_num(hp_after)))
                    hp_total_fmt = ("{color=%s}%s{/color}" % (_green, S.battle_fmt_num(hp_after_total))) if hp_after_total > 0 else fr("{} KO".format(S.battle_fmt_num(hp_after_total)))
                except:
                    fw = lambda x: x
                    fo = lambda x: x
                    fr = lambda x: x
                    hp_after_fmt = S.battle_fmt_num(hp_after)
                    hp_total_fmt = S.battle_fmt_num(hp_after_total)
                S.operation_add(
                    fw("Daño directo pendiente:") + " " + fo(S.battle_fmt_num(direct_pending)),
                    border
                )
                S.operation_add(
                    fw("HP total:") + " " + hp_after_fmt + fw(" - ") + fr(S.battle_fmt_num(direct_pending)) + fw(" = ") + hp_total_fmt,
                    border
                )
            except:
                pass

        # -------------------------------
        # (5) REFLECT (commit a ReflectManager)
        # -------------------------------
        if reflected_total > 0:
            try:
                S.operation_add(
                    S.op_reflect_clean("{}%".format(int(ref_pct_used * 100)), S.battle_fmt_num(reflected_total)),
                    border
                )
            except:
                pass

            # target = atacante (jugador) / source = defensor (IA)
            attacker_id = getattr(S, "current_actor_id", "ID_ACTOR_UNKNOWN")
            defender_id = getattr(S, "current_enemy_id", "ID_ENEMY_UNKNOWN")

            # ✅ hardening: sólo helper público (sin acceso directo al manager)
            try:
                fnq = getattr(S, "reflect_queue", None) or globals().get("reflect_queue", None)
                if callable(fnq):
                    fnq(attacker_id, defender_id, int(reflected_total))
                else:
                    try:
                        S.battle_log_add(
                            "{color=#FFA500}[WARN] reflect_queue no disponible; reflect omitido por hardening{/color}"
                        )
                    except:
                        pass
            except:
                pass

        # Dump final
        try:
            if hasattr(S, "operation_dump_to_battle_log"):
                S.operation_dump_to_battle_log()
        except:
            pass

        # Consumir debuff
        if block_debuff_percent > 0:
            try:
                S.next_defense_reduction = 0.0
            except:
                pass

        if defender_key and allowed_targets:
            try:
                S.pending_split_effect_targets_enemy = [k for k in allowed_targets if str(k or "") != defender_key]
            except:
                pass

        # limpiar marcador temporal de daño directo ofensivo
        try:
            fn_consume_direct = getattr(S, "bs_consume_direct_pending", None)
            if callable(fn_consume_direct):
                fn_consume_direct("enemy")
            else:
                S._last_player_direct_damage = 0
        except:
            pass

        return {"final_damage": final_damage, "reflected": reflected_total}


# ✅ Export al store
init -987 python:
    try:
        import renpy.store as S
        S.ai_defense_execute_plan = ai_defense_execute_plan
    except:
        pass
