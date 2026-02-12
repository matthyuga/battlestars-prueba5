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

        cost = S.reiatsu_energy_dynamic_cost(tech_id, S)

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


    # ------------------------------------------------------------
    # ⭐ FUNCIÓN — Valor REAL de técnica (base + escala + bonus)
    # ------------------------------------------------------------
    def ai_get_base_and_final(tech_id):
        import renpy.store as S

        base  = S.reiatsu_energy_base(tech_id)["value"]
        final = S.final_value_factory(tech_id, S)

        return base, final


    # ------------------------------------------------------------
    # ⭐ EJECUCIÓN OFENSIVA IA (DAÑO) – con FocusCost real
    # ------------------------------------------------------------
    def ai_execute_offensive_action(ai):
        import renpy.store as S

        key = ai.next_action()
        if key == "none":
            return "none"

        # ✅ BLINDAJE: si Focus IA está OFF, nunca debe quedar pending de costo
        if not bool(getattr(S, "ai_allow_focus", True)):
            try:
                S.enemy_focus_cost_pending = False
            except:
                pass

        # --------------------------------------------------------
        # FOCUS OFENSIVO (exponencial x2 → x4 → x8)
        # --------------------------------------------------------
        if key == "focus":

            # ✅ CANDADO: si Focus IA está OFF, no permitir concentrar
            if not bool(getattr(S, "ai_allow_focus", True)):

                # seguridad: por si quedó algo pendiente colgado
                try:
                    S.enemy_focus_cost_pending = False
                except:
                    pass

                # log opcional (seguro)
                try:
                    S.battle_log_add(
                        "%s intenta Concentrar, pero Focus IA está OFF" % ai.name,
                        "#888888"
                    )
                except:
                    pass

                return "none"

            S.activate_offensive_focus()

            # ✅ marca que el PRÓXIMO ataque paga Reiatsu x2
            S.enemy_focus_cost_pending = True

            S.battle_log_add(S.log_focus_unified("attack"))
            S.battle_popup_turn("%s activa Concentrar" % ai.name, "#C586C0", 0.6)
            return "focus"

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
        cost = S.reiatsu_energy_dynamic_cost(key, S)

        rei_cost = int(cost.get("reiatsu_cost", 0) or 0)
        ene_cost = int(cost.get("energy_cost", 0) or 0)

        focus_cost_applied = False
        if getattr(S, "enemy_focus_cost_pending", False):
            rei_cost *= 2
            S.enemy_focus_cost_pending = False
            focus_cost_applied = True

        S.consume_resources(rei_cost, ene_cost, "enemy")

        # --------------------------------------------------------
        # Calcular daño REAL (con Focus de daño)
        # --------------------------------------------------------
        base, final = ai_get_base_and_final(key)
        dmg = S.apply_offensive_focus(final)

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
                try:
                    fn_show = getattr(S, "show_dice_result", None)
                    if callable(fn_show):
                        fn_show(roll)
                    else:
                        import renpy.exports as R
                        R.show_screen("dice_roll_result", rolls=roll.get("rolls", []))
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

                    S.enemy_direct_pending_damage += int(dmg)
                    S.enemy_direct_base_damage = int(base)

                    log_text = "%s usa %s → %s daño {color=#FF66CC}%d/3 éxitos = DIRECTO{/color}" % (
                        ai.name, tech.get("name", key), S.battle_fmt_num(dmg), successes
                    )
                    if focus_cost_applied:
                        log_text += " {color=#C586C0}(Focus: costo R×2){/color}"
                    log_text += " {color=#999}(R %s / E %s){/color}" % (
                        S.battle_fmt_num(rei_cost),
                        S.battle_fmt_num(ene_cost)
                    )
                    S.battle_log_add(log_text)

                    # ⚠️ No se suma a incoming_damage (no defendible)
                    return key
                # si falla: cae al flujo normal (defendible)

            # ----------------------------------------------------
            # ✅ NEGADOR: éxito → cancelar PRÓXIMO TURNO DEL JUGADOR
            # ----------------------------------------------------
            if key == "noatk_attack":
                if success:
                    S.player_skip_attack = True
                    status = "NO ATK"
                else:
                    status = "FALLÓ"

                log_text = "%s usa %s → %s daño {color=#FF66CC}%d/3 éxitos = %s{/color}" % (
                    ai.name, tech.get("name", key), S.battle_fmt_num(dmg), successes, status
                )
                if focus_cost_applied:
                    log_text += " {color=#C586C0}(Focus: costo R×2){/color}"
                log_text += " {color=#999}(R %s / E %s){/color}" % (
                    S.battle_fmt_num(rei_cost),
                    S.battle_fmt_num(ene_cost)
                )
                S.battle_log_add(log_text)
                # el daño sigue siendo defendible (flujo normal)

        # --------------------------------------------------------
        # Registrar daño defendible (normal)
        # --------------------------------------------------------
        S.incoming_damage += dmg
        S.enemy_attack_records.append((base, dmg))

        # Marcar flag si fue el golpe más fuerte (para forzar reductor next turn)
        if key == "stronger_attack":
            S.ai_used_strong_attack = True

        # Visual
        S.battle_visual_float("player", dmg, "#FF6666", is_final=False)

        # --------------------------------------------------------
        # Log normal
        # --------------------------------------------------------
        log_text  = S.log_attack_simple(tech.get("name", key), S.battle_fmt_num(dmg))
        if focus_cost_applied:
            log_text += " {color=#C586C0}(Focus: costo R×2){/color}"
        log_text += " {color=#999}(R %s / E %s){/color}" % (
            S.battle_fmt_num(rei_cost),
            S.battle_fmt_num(ene_cost)
        )

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
            if not bool(getattr(S, "ai_allow_focus", True)):

                # log opcional (seguro)
                try:
                    S.battle_log_add(
                        "%s intenta Potenciar, pero Focus IA está OFF" % ai.name,
                        "#888888"
                    )
                except:
                    pass

                return "none"

            S.activate_defensive_focus()
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
        cost = S.reiatsu_energy_dynamic_cost(key, S)
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
        log_text = "%s usa %s → bloquea %s daño {color=#999}(R %s / E %s){/color}" % (
            ai.name,
            tech.get("name", key),
            S.battle_fmt_num(blk),
            S.battle_fmt_num(rei_cost),
            S.battle_fmt_num(ene_cost)
        )

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
