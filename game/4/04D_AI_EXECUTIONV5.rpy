# ============================================================
# 04D_AI_EXECUTION.rpy – Ejecución ofensiva y defensiva
# v12.6.2 ReflectQueue Centralized (Target=Attacker, Source=Defender) ✅
# ------------------------------------------------------------
# ✔ IA usa final_value_factory() igual que el jugador
# ✔ IA usa apply_offensive_focus / apply_defensive_focus
# ✔ IA usa reiatsu_energy_dynamic_cost()
# ✔ Logs 100% seguros
# ✔ Marca ai_used_strong_attack cuando usa stronger_attack
# ✔ "duda" ahora dice qué key faltó (debug real)
# ✔ Concentrar IA aplica costo x2 de Reiatsu al próximo ataque (focus target)
# ✔ IA tira dados en direct_attack / noatk_attack
#     - Directo éxito => daño NO defendible (pendiente)
#     - Negador éxito => player_skip_attack = True
# ✅ FIX: Respeta toggle S.ai_allow_focus (OFF bloquea focus ofensivo/defensivo)
# ✅ BLINDAJE: si Focus IA está OFF, limpia enemy_focus_cost_pending automáticamente
# ✅ Exporta ai_can_pay al store: S.ai_can_pay = ai_can_pay (para módulos reactivos)
# ✅ FIX REFLECT: guarda reflect como:
#     target = atacante (quien RECIBIRÁ el reflect)
#     source = defensor (quien lo GENERÓ)
# ============================================================

init -988 python:

    # ------------------------------------------------------------
    # 🔍 FUNCIÓN LOCAL: Chequeo de recursos IA (con FocusCost)
    # ------------------------------------------------------------
    def ai_can_pay(tech_id, actor="enemy"):
        import renpy.store as S

        # Focus siempre gratis
        if tech_id == "focus":
            return True, 0, 0

        cost = S.reiatsu_energy_dynamic_cost(tech_id, S, unit_key=_ai_enemy_unit_key())

        rei = int(cost.get("reiatsu_cost", 0) or 0)
        ene = int(cost.get("energy_cost", 0) or 0)

        # ✅ FocusCost IA: duplicar SOLO Reiatsu del próximo ataque
        if actor == "enemy" and getattr(S, "enemy_focus_cost_pending", False):
            rei *= 2

        if actor == "enemy":
            falt_rei = max(0, rei - int(getattr(S, "enemy_reiatsu", 0) or 0))
            falt_ene = max(0, ene - int(getattr(S, "enemy_energy", 0) or 0))
        else:
            falt_rei = max(0, rei - int(getattr(S, "player_reiatsu", 0) or 0))
            falt_ene = max(0, ene - int(getattr(S, "player_energy", 0) or 0))

        ok = (falt_rei == 0 and falt_ene == 0)
        return ok, falt_rei, falt_ene

    # ------------------------------------------------------------
    # ✅ EXPORT AL STORE (PARA OTROS MÓDULOS)
    # ------------------------------------------------------------
    try:
        import renpy.store as S
        S.ai_can_pay = ai_can_pay
    except:
        pass


    def _ai_enemy_unit_key():
        import renpy.store as S

        try:
            fnk = getattr(S, "ai_get_current_enemy_unit_key", None)
            if callable(fnk):
                k = str(fnk() or "")
                if k:
                    return k
        except:
            pass

        try:
            fn_ctx = getattr(S, "bs_get_turn_ctx", None)
            fn_key = getattr(S, "bs_unit_key", None)
            if callable(fn_ctx) and callable(fn_key):
                ctx = fn_ctx() or {}
                team = str(ctx.get("owner_team", "enemy") or "enemy").strip().lower()
                slot = int(ctx.get("owner_slot", 0) or 0)
                if team == "enemy":
                    return str(fn_key("enemy", slot) or "enemy:0")
        except:
            pass

        try:
            fn_akt = getattr(S, "bs_get_active_unit_key", None)
            if callable(fn_akt):
                return str(fn_akt("enemy") or "enemy:0")
        except:
            pass

        return "enemy:0"

    # ------------------------------------------------------------
    # ⭐ FUNCIÓN — Valor REAL de técnica (base + escala + bonus)
    # ------------------------------------------------------------
    def ai_get_base_and_final(tech_id):
        import renpy.store as S

        base  = S.reiatsu_energy_base(tech_id)["value"]
        final = S.final_value_factory(tech_id, S, unit_key=_ai_enemy_unit_key())

        return base, final

    def _ai_focus_allowed_enemy_unit():
        import renpy.store as S
        unit_key = ""
        try:
            fnk = getattr(S, "ai_get_current_enemy_unit_key", None)
            if callable(fnk):
                unit_key = str(fnk() or "")
        except:
            unit_key = ""

        try:
            fn = getattr(S, "ai_effective_allow_focus", None)
            if callable(fn):
                return bool(fn(unit_key))
        except:
            pass
        return bool(getattr(S, "ai_allow_focus", True))


    # ------------------------------------------------------------
    # ⭐ EJECUCIÓN OFENSIVA IA (DAÑO) – con FocusCost real
    # ------------------------------------------------------------
    def ai_execute_offensive_action(ai):
        import renpy.store as S

        key = ai.next_action()
        if key == "none":
            return "none"

        # ✅ BLINDAJE: si Focus IA está OFF, nunca debe quedar pending de costo
        if not _ai_focus_allowed_enemy_unit():
            try:
                S.enemy_focus_cost_pending = False
            except:
                pass

        # --------------------------------------------------------
        # FOCUS OFENSIVO (exponencial x2 → x4 → x8)
        # --------------------------------------------------------
        if key == "focus":

            # ✅ CANDADO: si Focus IA está OFF, no permitir concentrar
            if not _ai_focus_allowed_enemy_unit():

                # seguridad: por si quedó algo pendiente colgado
                try:
                    S.enemy_focus_cost_pending = False
                except:
                    pass

                # log opcional (seguro)
                try:
                    S.battle_log_add(
                        "%s intenta Concentrar, pero Focus IA(unidad) está OFF" % ai.name,
                        "#888888"
                    )
                except:
                    pass

                return "none"

            S.activate_offensive_focus(owner_team="enemy")

            # ✅ marca que el PRÓXIMO ataque paga Reiatsu x2
            S.enemy_focus_cost_pending = True

            S.battle_log_add(S.log_focus_unified("attack"))
            S.battle_popup_turn("%s activa Concentrar" % ai.name, "#C586C0", 0.6)
            return "focus"

        fn_cost_meta = getattr(S, "log_cost_meta", None)
        if not callable(fn_cost_meta):
            fn_cost_meta = globals().get("log_cost_meta", None)

        fn_fmt_orange = getattr(S, "fmt_orange", None) or globals().get("fmt_orange", None)
        fn_fmt_purple = getattr(S, "fmt_purple", None) or globals().get("fmt_purple", None)

        # --------------------------------------------------------
        # Obtener técnica (store-safe) + debug si falta
        # --------------------------------------------------------
        tech = ai.get_tech(key)
        if not tech:
            try:
                S.debug_log("AI missing tech key=%r | plan_rest=%r" % (key, ai.current_plan))
            except:
                pass
            S.battle_log_add("%s duda un instante… (falta: %s)" % (ai.name, key), "#AAAAAA")
            return "none"

        # --------------------------------------------------------
        # Chequeo de recursos (ya contempla FocusCost)
        # --------------------------------------------------------
        ok, fr, fe = ai_can_pay(key, "enemy")
        if not ok:
            msg = "%s no puede usar %s (" % (ai.name, tech.get("name", key))
            if fr > 0 and fe > 0:
                msg += "falta Reiatsu y Energía)"
            elif fr > 0:
                msg += "falta Reiatsu)"
            else:
                msg += "falta Energía)"
            S.battle_log_add(msg, "#888888")
            return "nopay"

        # --------------------------------------------------------
        # Consumir recursos (aplicando FocusCost si está pendiente)
        # --------------------------------------------------------
        cost = S.reiatsu_energy_dynamic_cost(key, S, unit_key=_ai_enemy_unit_key())

        rei_cost = int(cost.get("reiatsu_cost", 0) or 0)
        ene_cost = int(cost.get("energy_cost", 0) or 0)

        if not hasattr(S, "turn_enemy_off_rei_tech_sum"):
            S.turn_enemy_off_rei_tech_sum = 0
        if not hasattr(S, "turn_enemy_off_ene_tech_sum"):
            S.turn_enemy_off_ene_tech_sum = 0

        focus_cost_applied = False
        if getattr(S, "enemy_focus_cost_pending", False):
            rei_cost *= 2
            S.enemy_focus_cost_pending = False
            focus_cost_applied = True

        S.consume_resources(rei_cost, ene_cost, "enemy")
        S.turn_enemy_off_rei_tech_sum = int(getattr(S, "turn_enemy_off_rei_tech_sum", 0) or 0) + int(rei_cost or 0)
        S.turn_enemy_off_ene_tech_sum = int(getattr(S, "turn_enemy_off_ene_tech_sum", 0) or 0) + int(ene_cost or 0)

        # --------------------------------------------------------
        # Calcular daño REAL (con Focus de daño)
        # --------------------------------------------------------
        base, final = ai_get_base_and_final(key)
        dmg = S.apply_offensive_focus(final, owner_team="enemy")

        # --------------------------------------------------------
        # 🎲 ATAQUES CON DADOS (IA): Directo / Negador
        # --------------------------------------------------------
        if key in ("direct_attack", "noatk_attack"):

            roll = None
            try:
                fn_roll = getattr(S, "roll_3d", None)
                if callable(fn_roll):
                    roll = fn_roll()
            except:
                roll = None

            # Mostrar dados si existe
            if isinstance(roll, dict):
                _dice_lbl = str(tech.get("name", key) if isinstance(tech, dict) else key)
                try:
                    fn_show = getattr(S, "show_dice_result", None)
                    if callable(fn_show):
                        fn_show(roll, label_text=_dice_lbl)
                    else:
                        import renpy.exports as R
                        R.show_screen("dice_roll_result", rolls=roll.get("rolls", []), label_text=_dice_lbl)
                except:
                    pass

                # Log opcional de slots si existe tu helper
                try:
                    fn_slots = getattr(S, "log_dice_slots", None)
                    if callable(fn_slots):
                        S.battle_log_add(fn_slots(roll.get("rolls", [])))
                except:
                    pass

            success = bool(isinstance(roll, dict) and roll.get("success", False))
            successes = int(roll.get("successes", 0)) if isinstance(roll, dict) else 0

            # ✅ asegurar flags store-safe
            if not hasattr(S, "player_skip_attack"):
                S.player_skip_attack = False

            # ----------------------------------------------------
            # ✅ DIRECTO: éxito → daño NO defendible (pendiente)
            # ----------------------------------------------------
            if key == "direct_attack":
                if success:
                    if not hasattr(S, "enemy_direct_pending_damage"):
                        S.enemy_direct_pending_damage = 0
                    if not hasattr(S, "enemy_direct_base_damage"):
                        S.enemy_direct_base_damage = 0

                    fn_add_direct = getattr(S, "bs_add_direct_pending", None)
                    if callable(fn_add_direct):
                        fn_add_direct("player", int(dmg), mirror_legacy=True)
                        S.enemy_direct_pending_damage = int(getattr(S, "enemy_direct_pending_damage", 0) or 0)
                    else:
                        S.enemy_direct_pending_damage += int(dmg)

                    S.enemy_direct_base_damage = int(base)

                    log_text = "%s usa %s → Inflige %s de daño." % (ai.name, tech.get("name", key), S.battle_fmt_num(dmg))
                    _rule_txt = "Si saca 2/3 dados de éxito, este ataque es indefendible. (%d/3)" % successes
                    if callable(fn_fmt_orange):
                        log_text += " " + fn_fmt_orange(_rule_txt)
                    else:
                        log_text += " " + _rule_txt
                    if callable(fn_cost_meta):
                        log_text += " " + fn_cost_meta(rei_cost, ene_cost)
                    else:
                        log_text += " (Reiatsu %s / Energía %s)" % (S.battle_fmt_num(rei_cost), S.battle_fmt_num(ene_cost))
                    S.battle_log_add(log_text)

                    # ⚠️ No se suma a incoming_damage (no defendible)
                    return key
                # si falla: cae al flujo normal (defendible)

            # ----------------------------------------------------
            # ✅ NEGADOR: éxito → cancelar PRÓXIMO TURNO DEL JUGADOR
            # ----------------------------------------------------
            if key == "noatk_attack":
                if success:
                    _mode_noatk = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
                    if _mode_noatk == "2v2":
                        S.enemy_noatk_success = True
                        S.player_skip_attack = False
                    else:
                        S.player_skip_attack = True
                    S.offense_cancelled = True
                    status = "el enemigo no puede atacar en su siguiente turno"
                    try:
                        if callable(getattr(S, "battle_log_add", None)):
                            S.battle_log_add("{color=#80DEEA}[DEBUG] OFFENSE_CANCELLED actor_id=%s reason=noatk_attack{/color}" % str(getattr(S, "current_actor_unit_key", "") or ""))
                    except:
                        pass
                else:
                    status = "no activa negación"

                log_text = "%s usa %s → Inflige %s de daño." % (ai.name, tech.get("name", key), S.battle_fmt_num(dmg))
                _rule_txt = "Si saca 2/3 dados de éxito, %s. (%d/3)" % (status, successes)
                if callable(fn_fmt_orange):
                    log_text += " " + fn_fmt_orange(_rule_txt)
                else:
                    log_text += " " + _rule_txt
                if callable(fn_cost_meta):
                    log_text += " " + fn_cost_meta(rei_cost, ene_cost)
                else:
                    log_text += " (Reiatsu %s / Energía %s)" % (S.battle_fmt_num(rei_cost), S.battle_fmt_num(ene_cost))
                S.battle_log_add(log_text)
                # el daño sigue siendo defendible (flujo normal)

        # --------------------------------------------------------
        # Registrar daño defendible (normal)
        # --------------------------------------------------------
        S.incoming_damage += dmg
        S.enemy_attack_records.append((final, dmg))

        # Marcar flag si fue el golpe más fuerte (para forzar reductor next turn)
        if key == "stronger_attack":
            S.ai_used_strong_attack = True

        # Visual
        S.battle_visual_float("player", dmg, "#FF6666", is_final=False)

        # --------------------------------------------------------
        # Log normal
        # --------------------------------------------------------
        log_text  = S.log_attack_simple(tech.get("name", key), S.battle_fmt_num(dmg))
        if callable(fn_cost_meta):
            log_text += " " + fn_cost_meta(rei_cost, ene_cost)
        else:
            log_text += " (Reiatsu %s / Energía %s)" % (S.battle_fmt_num(rei_cost), S.battle_fmt_num(ene_cost))

        S.battle_log_add(log_text)

        return key


    # ------------------------------------------------------------
    # ⭐ EJECUCIÓN DEFENSIVA IA (BLOQUEO / REFLECT / REDUCTOR)
    # (sin FocusCost aquí, porque tu Focus de costo es ofensivo-target)
    # ------------------------------------------------------------
    def ai_execute_defensive_action(ai):
        import renpy.store as S

        key = ai.next_action()
        if key == "none":
            return "none"

        # --------------------------------------------------------
        # FOCUS DEFENSIVO (x2 → x4 → x8)
        # --------------------------------------------------------
        if key == "focus":

            # ✅ CANDADO: si Focus IA está OFF, no permitir potenciar defensa
            if not _ai_focus_allowed_enemy_unit():

                # log opcional (seguro)
                try:
                    S.battle_log_add(
                        "%s intenta Potenciar, pero Focus IA(unidad) está OFF" % ai.name,
                        "#888888"
                    )
                except:
                    pass

                return "none"

            S.activate_defensive_focus()
            fn_boost = getattr(S, "log_potenciar_unified", None)
            if callable(fn_boost):
                S.battle_log_add(fn_boost())
            else:
                S.battle_log_add(S.log_focus_unified("defense"))
            S.battle_popup_turn("%s potencia defensa" % ai.name, "#C586C0", 0.4)
            return "focus"

        tech = getattr(S, "battle_techniques", {}).get(key, {})

        # --------------------------------------------------------
        # Chequeo de recursos
        # --------------------------------------------------------
        ok, fr, fe = ai_can_pay(key, "enemy")
        if not ok:
            msg = "%s no puede usar %s (" % (ai.name, tech.get("name", key))
            if fr > 0 and fe > 0:
                msg += "falta Reiatsu y Energía)"
            elif fr > 0:
                msg += "falta Reiatsu)"
            else:
                msg += "falta Energía)"
            S.battle_log_add(msg, "#999999")
            return "nopay"

        # Consumir recursos
        cost = S.reiatsu_energy_dynamic_cost(key, S, unit_key=_ai_enemy_unit_key())
        rei_cost = int(cost.get("reiatsu_cost", 0) or 0)
        ene_cost = int(cost.get("energy_cost", 0) or 0)
        S.consume_resources(rei_cost, ene_cost, "enemy")

        # --------------------------------------------------------
        # Bloqueo REAL
        # --------------------------------------------------------
        base_blk, final_blk = ai_get_base_and_final(key)
        blk = S.apply_defensive_focus(final_blk)

        S.total_block += blk

        # --------------------------------------------------------
        # Log
        # --------------------------------------------------------
        log_text = "%s usa %s → bloquea %s daño" % (ai.name, tech.get("name", key), S.battle_fmt_num(blk))
        if callable(fn_cost_meta):
            log_text += " " + fn_cost_meta(rei_cost, ene_cost)
        else:
            log_text += " (Reiatsu %s / Energía %s)" % (S.battle_fmt_num(rei_cost), S.battle_fmt_num(ene_cost))

        S.battle_log_add(log_text, "#55FFFF")

        # --------------------------------------------------------
        # REFLECT (target=attacker_id, source=defender_id)
        # --------------------------------------------------------
        if tech.get("attack_reflect", 0) > 0:

            try:
                ref_pct = float(tech.get("attack_reflect", 0) or 0)
            except:
                ref_pct = 0.0

            reflected = int((getattr(S, "incoming_damage", 0) or 0) * ref_pct)
            if reflected < 0:
                reflected = 0

            attacker_id = getattr(S, "current_actor_id", "ID_ACTOR_UNKNOWN")   # Jugador (Harribel)
            defender_id = getattr(S, "current_enemy_id", "ID_ENEMY_UNKNOWN")   # IA (Grimmjow)

            # ✅ usar helper unificado si existe (lo haremos en el script central)
            try:
                fn = getattr(S, "reflect_queue", None) or globals().get("reflect_queue", None)
                if callable(fn):
                    fn(attacker_id, defender_id, reflected)
                else:
                    # fallback seguro si aún no existe helper:
                    ref_obj = getattr(S, "reflect", None) or globals().get("reflect", None)
                    if ref_obj is not None:
                        try:
                            ref_obj.add(attacker_id, reflected, source_id=defender_id)
                        except TypeError:
                            ref_obj.add(attacker_id, reflected)
            except:
                pass

            S.battle_log_add("{color=#00FFFF}Reflect: %d{/color}" % reflected)

        return key
