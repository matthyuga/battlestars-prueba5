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

        # -------------------------------
        # 🪞 Reflect store-safe
        # -------------------------------
        REF = getattr(S, "reflect", None)

        # Helpers: chequeo/consumo (store-safe)
        can_pay_fn = getattr(S, "ai_can_pay", None)
        if not callable(can_pay_fn):
            can_pay_fn = globals().get("ai_can_pay", None)

        def _consume_for(real_id):
            """
            Consume recursos para real_id y devuelve (rei_cost, ene_cost).
            NO aplica enemy_focus_cost_pending (solo ofensivo).
            """
            try:
                cost = S.reiatsu_energy_dynamic_cost(real_id, S)
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
                if not bool(getattr(S, "ai_allow_focus", True)):
                    try:
                        S.battle_log_add("%s intenta Potenciar, pero Focus IA está OFF" % name, "#888888")
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
                    summary_lines.append(S.log_defense_extra(S.battle_fmt_num(base_blk), S.battle_fmt_num(blk)))
                except:
                    pass
                try:
                    S.battle_log_add("{color=#999}(R %s / E %s){/color}" % (S.battle_fmt_num(rei_cost), S.battle_fmt_num(ene_cost)))
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
                        S.log_defense_reducer(S.battle_fmt_num(blk), int(atkred * 100), reduc_val_tmp)
                    )
                except:
                    pass

                try:
                    S.battle_log_add("{color=#999}(R %s / E %s){/color}" % (S.battle_fmt_num(rei_cost), S.battle_fmt_num(ene_cost)))
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
                        S.log_defense_reflect(S.battle_fmt_num(blk), int(ref_pct * 100), reflected_now)
                    )
                except:
                    pass

                try:
                    S.battle_log_add("{color=#999}(R %s / E %s){/color}" % (S.battle_fmt_num(rei_cost), S.battle_fmt_num(ene_cost)))
                except:
                    pass
                continue

        # -------------------------------
        # LOG de focus + técnicas
        # -------------------------------
        if focus_used:
            try:
                if hasattr(S, "battle_log_add"):
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

        block_parts = []
        for base, blk in blocks_list:
            try:
                if int(blk) != int(base):
                    block_parts.append(
                        "{color=%s}%s×2(%s){/color}" % (
                            _pal("blue", "#66CCFF"),
                            S.battle_fmt_num(base),
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
            fo = globals().get("fmt_orange", lambda x: x)
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
        # (4) HP
        # -------------------------------
        hp_before = int(getattr(S, "enemy_hp", 0) or 0)
        hp_after  = max(0, hp_before - int(final_damage))

        try:
            S.operation_add(
                S.op_def_hp(S.battle_fmt_num(hp_before), S.battle_fmt_num(final_damage), S.battle_fmt_num(hp_after)),
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

            # ✅ centralizado (si existe helper)
            try:
                fnq = getattr(S, "reflect_queue", None) or globals().get("reflect_queue", None)
                if callable(fnq):
                    fnq(attacker_id, defender_id, int(reflected_total))
                else:
                    # fallback directo al manager si no existe helper aún
                    if REF is not None:
                        try:
                            # Limpio sólo el target (para que no acumule basura de turnos raros)
                            REF.clear(attacker_id)
                            REF.add(attacker_id, int(reflected_total), source_id=defender_id)
                        except TypeError:
                            REF.clear(attacker_id)
                            REF.add(attacker_id, int(reflected_total))
                    else:
                        try:
                            reflect.clear(attacker_id)
                            reflect.add(attacker_id, int(reflected_total))
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

        return {"final_damage": final_damage, "reflected": reflected_total}


# ✅ Export al store
init -987 python:
    try:
        import renpy.store as S
        S.ai_defense_execute_plan = ai_defense_execute_plan
    except:
        pass
