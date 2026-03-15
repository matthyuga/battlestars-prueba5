# ============================================================
# 04D_BATTLE_TURN_ENEMY.RPY – Turno ofensivo IA (MANEUVER EXTENDED)
# Versión v12.3.1 Reflect RESOLVE ON TARGET HP (SyntaxFix + Sync) ✅
# ------------------------------------------------------------
# ✔ Reflect se aplica al HP de la IA (target = IA)
# ✔ Reflect NO se suma al daño ofensivo
# ✔ Usa ReflectManager (target+source)
# ✔ Logs y operación limpios
# ✔ FIX: NO usa "$" dentro de python:
# ✔ Sync HP bars si muere/recibe reflect
# ============================================================

label battle_enemy_turn_legacy_entry:

    $ battle_turn_change("enemy")

    python:
        import renpy.store as S
        S._enemy_reflect_consumed_this_turn = False

        enemy_name = str(getattr(getattr(S, "enemy_ai", None), "name", "Enemigo") or "Enemigo")
        slot_idx = 0

        fn_ctx = getattr(S, "bs_get_turn_ctx", None)
        fn_key = getattr(S, "bs_unit_key", None)
        fn_get = getattr(S, "bs_get_unit_by_key", None)

        if callable(fn_ctx):
            ctx = fn_ctx()
            if str(ctx.get("owner_team", "enemy") or "enemy") == "enemy":
                slot_idx = int(ctx.get("owner_slot", 0) or 0)

        if callable(fn_key):
            S.current_enemy_unit_key = str(fn_key("enemy", slot_idx) or "")

        if callable(fn_get):
            uu = fn_get(getattr(S, "current_enemy_unit_key", ""))
            if isinstance(uu, dict):
                enemy_name = str(uu.get("char_id", enemy_name) or enemy_name)

        S.turn_owner_slot = int(slot_idx or 0)
        S.turn_owner_team = "enemy"

    # ============================================================
    # ⭐ DEFENSA DIFERIDA 2v2 (solo si este actor recibió daño en cola)
    # ============================================================
    python:
        import renpy.store as S
        _enemy_pending_damage = 0
        _enemy_pending_ko = False
        _enemy_actor_alive = True

        _mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        if _mode == "2v2":
            pend = getattr(S, "enemy_pending_damage_by_key", None)
            if not isinstance(pend, dict):
                pend = {}

            akey = str(getattr(S, "current_enemy_unit_key", "") or "")
            _enemy_pending_damage = max(0, int(pend.get(akey, 0) or 0))

            if _enemy_pending_damage > 0:
                # preparar identidad visual/legacy del defensor actual
                try:
                    S.battle_enemy_id = str(enemy_name or getattr(S, "battle_enemy_id", "Enemigo"))
                    if callable(getattr(S, "get_character", None)):
                        ch = S.get_character(S.battle_enemy_id)
                        if isinstance(ch, dict):
                            S.battle_enemy = ch
                except:
                    pass

                fn_def = getattr(S, "enemy_compute_reactive_defense", None)
                final_in = int(_enemy_pending_damage)

                # aplicar debuff acumulado por target en 2v2
                _deb_map = getattr(S, "enemy_pending_def_reduction_by_key", None)
                _saved_red = float(getattr(S, "next_defense_reduction", 0.0) or 0.0)
                _applied_red = 0.0
                if isinstance(_deb_map, dict) and akey:
                    try:
                        _applied_red = float(_deb_map.get(akey, 0.0) or 0.0)
                    except:
                        _applied_red = 0.0
                if _applied_red > 0.0:
                    S.next_defense_reduction = float(_applied_red)

                if callable(fn_def):
                    try:
                        info = fn_def(_enemy_pending_damage)
                        final_in = max(0, int(info.get("final_damage", _enemy_pending_damage) or _enemy_pending_damage))
                    except:
                        final_in = int(_enemy_pending_damage)

                # consumir debuff acumulado de este target y restaurar valor temporal
                try:
                    if isinstance(_deb_map, dict) and akey:
                        _deb_map[akey] = 0.0
                        S.enemy_pending_def_reduction_by_key = _deb_map
                except:
                    pass
                if _applied_red <= 0.0:
                    S.next_defense_reduction = _saved_red

                try:
                    fn_apply_key = getattr(S, "bs_apply_damage_to_unit_key", None)
                    if callable(fn_apply_key) and akey:
                        fn_apply_key(akey, int(final_in), source_key=getattr(S, "current_actor_unit_key", None), reason="combat_deferred_enemy", tags=["deferred", "enemy_defense"])
                    else:
                        fn_set = getattr(S, "bs_set_hp", None)
                        cur = int(getattr(S, "enemy_hp", 0) or 0)
                        nxt = max(0, cur - int(final_in or 0))
                        if callable(fn_set):
                            fn_set("enemy", nxt)
                        else:
                            S.enemy_hp = nxt
                except:
                    pass

                # consumir cola del actor actual
                pend[akey] = 0
                S.enemy_pending_damage_by_key = pend

                try:
                    fn_sync = getattr(S, "bs_sync_hp_ui", None)
                    if callable(fn_sync):
                        fn_sync()
                except:
                    pass

                try:
                    if callable(getattr(S, "battle_log_add", None)):
                        S.battle_log_add("{color=#90CAF9}Defensa diferida {}: {}{/color}".format(enemy_name, int(final_in)))
                except:
                    pass

                try:
                    fn_alive = getattr(S, "bs_is_unit_alive", None)
                    _enemy_actor_alive = bool(fn_alive(akey)) if callable(fn_alive) else True
                except:
                    _enemy_actor_alive = True

                try:
                    fn_defeated = getattr(S, "bs_is_team_defeated", None)
                    _enemy_pending_ko = bool(fn_defeated("enemy")) if callable(fn_defeated) else False
                except:
                    _enemy_pending_ko = False

    if _enemy_pending_ko:
        $ battle_log_add("{color=#FFD700}¡Victoria!{/color}")
        jump battle_end

    if _enemy_pending_damage > 0 and not _enemy_actor_alive:
        python:
            import renpy.store as S
            _mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
            _next = "player"
            if _mode == "2v2" and callable(getattr(S, "bs_turn_advance", None)) and callable(getattr(S, "bs_parse_unit_key", None)):
                nk = str(S.bs_turn_advance(mirror_legacy=True) or "")
                _next = str(S.bs_parse_unit_key(nk, default_side="player", default_slot=0).get("team", "player") or "player")
                try:
                    fn_desc = getattr(S, "bs_describe_unit_key", None)
                    nm = str(fn_desc(nk) if callable(fn_desc) else nk)
                    if callable(getattr(S, "battle_log_add", None)):
                        S.battle_log_add("{color=#80DEEA}[DEBUG] TURN_ADVANCE next_actor_id=%s next_name=%s{/color}" % (str(nk), str(nm)))
                except:
                    pass

        if _next == "enemy":
            jump battle_enemy_turn
        else:
            jump battle_offensive_turn

    # ============================================================
    # ⭐ ATAQUE NEGADOR — cancelar turno ofensivo IA
    # ============================================================
    python:
        player_name_turn = (
            getattr(S, "player_name", None)
            or getattr(getattr(S, "player_ai", None), "name", None)
            or (
                getattr(S, "battle_player", {}).get("name", None)
                if isinstance(getattr(S, "battle_player", None), dict)
                else None
            )
            or "Jugador"
        )
        player_target_id_turn = (
            getattr(S, "current_player_id", None)
            or getattr(S, "player_id", None)
            or getattr(S, "BATTLE_PLAYER_ID", None)
            or getattr(S, "BATTLE_IDENTITIES", {}).get(player_name_turn, "ID_PLAYER_UNKNOWN")
        )

        _enemy_actor_key = str(getattr(S, "current_enemy_unit_key", "") or "")
        _emap_skip = getattr(S, "enemy_skip_attack_by_key", None)
        _enemy_skip_for_actor = bool(isinstance(_emap_skip, dict) and _enemy_actor_key and _emap_skip.get(_enemy_actor_key, False))

        if _enemy_skip_for_actor or getattr(S, "enemy_skip_attack", False):

            if _enemy_skip_for_actor:
                try:
                    _emap_skip[_enemy_actor_key] = False
                    S.enemy_skip_attack_by_key = _emap_skip
                except:
                    pass
            S.enemy_skip_attack = False

            # Si IA no ataca, reflect pendiente contra jugador se consume y se pierde.
            try:
                dropped_reflect = 0
                ref_source = None
                fn_consume = getattr(S, "reflect_consume_for", None)
                if callable(fn_consume):
                    dropped_reflect, ref_source = fn_consume(player_target_id_turn)
                else:
                    rman = getattr(S, "reflect", None)
                    if rman and hasattr(rman, "consume_info"):
                        dropped_reflect, ref_source = rman.consume_info(player_target_id_turn)
                    elif rman and hasattr(rman, "consume"):
                        dropped_reflect = rman.consume(player_target_id_turn)
                dropped_reflect = int(dropped_reflect or 0)
                if dropped_reflect > 0:
                    S.battle_log_add("{color=#00FFFF}Reflect se desvanece (IA sin ataque): %s{/color}" % S.battle_fmt_num(dropped_reflect))
            except:
                pass
            S._enemy_reflect_consumed_this_turn = True

            try:
                S.battle_log_add(
                    "{color=#FF66CC}%s queda incapacitado y no puede atacar este turno{/color}"
                    % enemy_name
                )
            except:
                pass

            try:
                S.battle_popup_turn("%s no puede atacar" % enemy_name, "#FF66CC", 0.6)
            except:
                pass

            bs_ui_pause(0.5, hard=True)

            # Diseño elegido: NO limpiamos reflect aquí.
            _mode_skip = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
            _next_team = "player"
            _next_key = ""
            if _mode_skip == "2v2" and callable(getattr(S, "bs_turn_advance", None)) and callable(getattr(S, "bs_parse_unit_key", None)):
                _next_key = str(S.bs_turn_advance(mirror_legacy=True) or "")
                _next_team = str(S.bs_parse_unit_key(_next_key, default_side="player", default_slot=0).get("team", "player") or "player")

            S.battle_turn_change(_next_team)
            if _next_team == "enemy":
                try:
                    fn_desc = getattr(S, "bs_describe_unit_key", None)
                    _ename = str(fn_desc(_next_key) if callable(fn_desc) and _next_key else enemy_name)
                    S.battle_popup_turn("Turno ofensivo — {}".format(_ename or enemy_name), "#FFD700", 0.7)
                except:
                    pass
                renpy.jump("battle_enemy_turn")
            else:
                try:
                    fn_desc = getattr(S, "bs_describe_unit_key", None)
                    _pname = ""
                    if callable(fn_desc) and _next_key:
                        _pname = str(fn_desc(_next_key) or "")
                    if not _pname:
                        _bp = getattr(S, "battle_player", None)
                        if isinstance(_bp, dict):
                            _pname = str(_bp.get("name", "") or "")
                    if not _pname:
                        _pname = str(getattr(S, "battle_player_id", "Harribel") or "Harribel")
                    S.battle_popup_turn("Turno ofensivo — {}".format(_pname), "#FFD700", 0.7)
                except:
                    pass
                renpy.jump("battle_offensive_turn")

    # ============================================================
    # ⭐ ENCABEZADO IA
    # ============================================================
    $ _slot_txt = " ({})".format(store.bs_slot_tag(getattr(store, "turn_owner_team", "enemy"), int(getattr(store, "turn_owner_slot", 0) or 0)) if hasattr(store, "bs_slot_tag") else "S{}".format(int(getattr(store, "turn_owner_slot", 0) or 0) + 1)) if str(getattr(store, "battle_team_mode", "1v1") or "1v1").lower() == "2v2" else ""
    $ battle_popup_turn("Turno ofensivo{} — {}".format(_slot_txt, enemy_name), "#FFD700", delay=0.6)
    $ battle_log_phase("TURNO OFENSIVO{} – {}".format(_slot_txt, enemy_name))
    $ bs_ui_pause(0.8, hard=True)

    python:
        import renpy.store as S

        # --------------------------------------------------------
        # PLAN + RESET
        # --------------------------------------------------------
        ai_plan_offensive(enemy_ai)

        S.enemy_total_damage      = 0
        S.incoming_damage         = 0
        S.incoming_direct_damage  = 0
        S.enemy_attack_records    = []
        S.enemy_noatk_success     = False

        # ID store-safe
        S.current_enemy_id = getattr(S, "BATTLE_IDENTITIES", {}).get(enemy_name, "ID_ENEMY_UNKNOWN")
        try:
            fn_ctx = getattr(S, "bs_get_turn_ctx", None)
            fn_key = getattr(S, "bs_unit_key", None)
            if callable(fn_ctx) and callable(fn_key):
                c = fn_ctx()
                eslot = int(c.get("owner_slot", 0) or 0) if str(c.get("owner_team", "enemy") or "enemy") == "enemy" else int(getattr(S, "turn_owner_slot", 0) or 0)
                S.current_enemy_unit_key = str(fn_key("enemy", eslot) or "")
        except:
            S.current_enemy_unit_key = ""

        # --------------------------------------------------------
        # --------------------------------------------------------
        # Reflect contra IA se resuelve en turno ofensivo del jugador
        # (target_id = current_enemy_id), no aquí.
        # --------------------------------------------------------

        # ============================================================
        # ⭐ LOOP REAL DE EJECUCIÓN IA
        # ============================================================
        NON_ATTACK_KEYS = set(["none", "focus", "nopay", None])
        enemy_attack_executed = False
        while enemy_ai.current_plan:
            executed_key = ai_execute_offensive_action(enemy_ai)
            if executed_key not in NON_ATTACK_KEYS:
                enemy_attack_executed = True
            bs_ui_pause(0.35, hard=True)

        # ============================================================
        # ⭐ FÓRMULA OFENSIVA IA (SIN REFLECT)
        # ============================================================
        parts = []
        for base, dmg in (S.enemy_attack_records or []):
            try:
                if dmg != base:
                    parts.append("%s×2(%s)" % (S.battle_fmt_num(base), S.battle_fmt_num(dmg)))
                else:
                    parts.append(S.battle_fmt_num(base))
            except:
                pass

        formula_text = " + ".join(parts) if parts else "0"

        enemy_reflect_bonus = 0
        ref_source = None
        if not bool(getattr(S, "_enemy_reflect_consumed_this_turn", False)):
            try:
                fn_consume = getattr(S, "reflect_consume_for", None)
                if callable(fn_consume):
                    enemy_reflect_bonus, ref_source = fn_consume(player_target_id_turn)
                else:
                    rman = getattr(S, "reflect", None)
                    if rman and hasattr(rman, "consume_info"):
                        enemy_reflect_bonus, ref_source = rman.consume_info(player_target_id_turn)
                    elif rman and hasattr(rman, "consume"):
                        enemy_reflect_bonus = rman.consume(player_target_id_turn)
            except:
                enemy_reflect_bonus = 0
                ref_source = None
            finally:
                S._enemy_reflect_consumed_this_turn = True

        try:
            enemy_reflect_bonus = int(enemy_reflect_bonus or 0)
        except:
            enemy_reflect_bonus = 0
        if enemy_reflect_bonus < 0:
            enemy_reflect_bonus = 0

        if enemy_reflect_bonus > 0:
            if enemy_attack_executed:
                S.incoming_damage = int(S.incoming_damage or 0) + enemy_reflect_bonus
                try:
                    src_txt = (" (fuente: %s)" % ref_source) if ref_source else ""
                    S.battle_log_add("{color=#00FFFF}Reflect +%s%s{/color}" % (S.battle_fmt_num(enemy_reflect_bonus), src_txt))
                except:
                    pass
            else:
                try:
                    S.battle_log_add("{color=#00FFFF}Reflect se desvanece (IA sin ataque): %s{/color}" % S.battle_fmt_num(enemy_reflect_bonus))
                except:
                    pass

        total_damage = int(S.incoming_damage or 0)

        # ============================================================
        # C.1/C.2/C.3 – Priorización AI + contexto reflect + split policy
        # ============================================================
        S.enemy_target_key = ""
        S.enemy_damage_plan = None
        S.enemy_split_policy_used = "single_target"

        fn_valid = getattr(S, "bs_get_valid_target_keys", None)
        fn_get_unit = getattr(S, "bs_get_unit_by_key", None)
        fn_make_plan = getattr(S, "bs_make_damage_plan", None)
        fn_active_key = getattr(S, "bs_get_active_unit_key", None)
        fn_reflect_peek = getattr(S, "bs_reflect_peek_for", None)

        if callable(fn_valid):
            target_keys = list(fn_valid("player") or [])
            plan_entries = []

            # C.2: medir reflect acumulado en unidad activa de IA para decisión táctica
            ai_active_key = ""
            ai_reflect_ready = 0
            if callable(fn_active_key):
                try:
                    ai_active_key = str(fn_active_key("enemy") or "")
                except:
                    ai_active_key = ""
            if ai_active_key and callable(fn_reflect_peek):
                try:
                    ai_reflect_ready = max(0, int(fn_reflect_peek(ai_active_key) or 0))
                except:
                    ai_reflect_ready = 0

            # C.1: heurísticas simples por target
            scored = []
            for k in target_keys:
                unit = fn_get_unit(k) if callable(fn_get_unit) else None
                hp = 0
                mx = 1
                threat = 0
                if isinstance(unit, dict):
                    hp = max(0, int(unit.get("hp", 0) or 0))
                    mx = max(1, int(unit.get("max_hp", 1) or 1))
                    # amenaza inicial: explícita si existe, sino proxy por max_hp
                    threat = max(0, int(unit.get("threat", unit.get("danger", mx)) or 0))
                hp_ratio = float(hp) / float(mx or 1)
                score_focus_low_hp = (1.0 - hp_ratio) * 100.0
                score_punish_threat = float(threat)
                score = score_focus_low_hp + (0.35 * score_punish_threat)
                scored.append({"key": k, "hp": hp, "mx": mx, "threat": threat, "score": score})

            scored.sort(key=lambda x: x.get("score", 0.0), reverse=True)
            primary_auto = scored[0]["key"] if scored else ""
            forced_primary = ""
            try:
                fn_forced = getattr(S, "ai_resolve_forced_target_key", None)
                if callable(fn_forced):
                    forced_primary = str(fn_forced(ai_active_key, target_keys) or "")
            except:
                forced_primary = ""
            primary = forced_primary if forced_primary else primary_auto

            # C.3: policy burst vs presión distribuida
            policy = "single_target"
            alive_n = len(scored)
            lowest_hp = min([x.get("hp", 0) for x in scored]) if scored else 0
            can_secure_ko = bool(total_damage > 0 and lowest_hp > 0 and total_damage >= lowest_hp)

            if forced_primary:
                policy = "single_target"
            elif alive_n <= 1:
                policy = "single_target"
            elif can_secure_ko:
                policy = "single_target"   # burst para confirmar KO
            elif ai_reflect_ready >= max(1, int(total_damage * 0.35)):
                policy = "split_equal"      # presión distribuida cuando reflect habilita daño extra
            elif alive_n >= 3:
                policy = "split_equal"
            else:
                policy = "single_target"

            # C.1 adicional: proteger unidad crítica propia => priorizar KO rápido para bajar presión
            if ai_active_key and callable(fn_get_unit):
                ai_u = fn_get_unit(ai_active_key)
                if isinstance(ai_u, dict):
                    ai_hp = max(0, int(ai_u.get("hp", 0) or 0))
                    ai_mx = max(1, int(ai_u.get("max_hp", 1) or 1))
                    if ai_hp <= int(ai_mx * 0.30) and primary:
                        policy = "single_target"

            if policy == "split_equal" and alive_n > 1 and total_damage > 0:
                base = total_damage // alive_n
                rem = total_damage % alive_n
                for idx, row in enumerate(scored):
                    amt = base + (1 if idx < rem else 0)
                    if amt > 0:
                        plan_entries.append({"target_key": row["key"], "amount": amt, "tags": ["ai", "split_equal"]})
            elif primary:
                if total_damage > 0:
                    plan_entries.append({"target_key": primary, "amount": total_damage, "tags": ["ai", "burst"]})

            if primary:
                S.enemy_target_key = str(primary)
            S.enemy_split_policy_used = str(policy)

            # Negador en 2v2: aplicar NO ATK al target real (primary), no al siguiente actor global.
            if bool(getattr(S, "enemy_noatk_success", False)):
                try:
                    if str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower() == "2v2" and primary:
                        pskip_map = getattr(S, "player_skip_attack_by_key", None)
                        if not isinstance(pskip_map, dict):
                            pskip_map = {}
                        pskip_map[str(primary)] = True
                        S.player_skip_attack_by_key = pskip_map
                        S.player_skip_attack = False
                    elif str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower() != "2v2":
                        S.player_skip_attack = True
                except:
                    pass

            if plan_entries and callable(fn_make_plan):
                S.enemy_damage_plan = fn_make_plan(
                    source_key=ai_active_key,
                    entries=plan_entries,
                    mode=policy,
                    skill_id="enemy_offensive_ai",
                    meta={
                        "reflect_ready": int(ai_reflect_ready or 0),
                        "targets_alive": int(alive_n),
                        "can_secure_ko": bool(can_secure_ko),
                    },
                )

            target_assignment_line = None

            try:
                if callable(getattr(S, "battle_log_add", None)) and primary:
                    fn_desc = getattr(S, "bs_describe_unit_key", None)
                    if callable(fn_desc):
                        if policy == "split_equal" and plan_entries:
                            lbls = []
                            for pe in plan_entries:
                                tk = str(pe.get("target_key", "") or "")
                                if tk:
                                    lbls.append(str(fn_desc(tk, default_side="player", default_slot=0) or tk))
                            target_txt = " + ".join(lbls) if lbls else str(fn_desc(primary, default_side="player", default_slot=0) or primary)
                        else:
                            target_txt = str(fn_desc(primary, default_side="player", default_slot=0) or primary)
                    else:
                        target_txt = primary
                    _policy_log = policy
                    if forced_primary:
                        try:
                            info_forced = S.bs_parse_unit_key(forced_primary, default_side="player", default_slot=0) if callable(getattr(S, "bs_parse_unit_key", None)) else {}
                            _forced_slot = int(info_forced.get("slot", 0) or 0)
                            _policy_log = "force_slot(P{})".format(_forced_slot + 1)
                        except:
                            _policy_log = "force_slot"
                    target_assignment_line = "{color=#B0E0E6}Target asignado: %s{/color}" % (target_txt)
            except:
                pass

        try:
            S.battle_log_add(
                S.log_operation(
                    formula_text,
                    enemy_reflect_bonus if enemy_attack_executed else 0,
                    total_damage
                ),
                group="operation"
            )
        except:
            pass

        # ============================================================
        # ⭐ MENSAJE FINAL DETALLADO
        # ============================================================
        debuff_pct     = getattr(S, "next_defense_reduction", 0.0) or 0.0
        dmg_defendible = total_damage

        # Commit C: priorizar SSOT (battle_state.direct_pending[player])
        dmg_directo = 0
        try:
            fn_get_direct = getattr(S, "bs_get_direct_pending", None)
            if callable(fn_get_direct):
                dmg_directo = int(fn_get_direct("player") or 0)
            else:
                dmg_directo = int(getattr(S, "incoming_direct_damage", 0) or 0)
                if dmg_directo <= 0:
                    dmg_directo = int(getattr(S, "enemy_direct_pending_damage", 0) or 0)
        except:
            dmg_directo = int(getattr(S, "incoming_direct_damage", 0) or 0)
            if dmg_directo <= 0:
                dmg_directo = int(getattr(S, "enemy_direct_pending_damage", 0) or 0)

        # espejo legacy para formateadores/consumidores históricos
        try:
            S.incoming_direct_damage = int(dmg_directo or 0)
        except:
            pass

        if dmg_directo < 0:
            dmg_directo = 0

        try:
            tot_fn = getattr(S, "log_total", None) or globals().get("log_total", None)
            if callable(tot_fn):
                S.battle_log_add(
                    tot_fn(
                        dmg_defendible + dmg_directo,
                        int(debuff_pct * 100),
                        defendible=dmg_defendible,
                        directo=dmg_directo
                    )
                )
            else:
                total_final = dmg_defendible + dmg_directo
                if dmg_directo > 0:
                    S.battle_log_add("Daño total: {} defendibles + {} directos = {}".format(
                        S.battle_fmt_num(dmg_defendible),
                        S.battle_fmt_num(dmg_directo),
                        S.battle_fmt_num(total_final)
                    ))
                else:
                    S.battle_log_add("Daño total: {} defendibles".format(S.battle_fmt_num(dmg_defendible)))
        except:
            pass

        try:
            if target_assignment_line:
                S.battle_log_add(target_assignment_line, group="target_assignment")
        except:
            pass

    # ============================================================
    # ⭐ 2v2: daño diferido al turno del defensor (sin maniobra inmediata)
    # ============================================================
    python:
        import renpy.store as S
        _mode2 = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        _deferred_2v2 = False
        if _mode2 == "2v2":
            plan = getattr(S, "enemy_damage_plan", None)
            ppend = getattr(S, "player_pending_damage_by_key", None)
            if not isinstance(ppend, dict):
                ppend = {}

            if isinstance(plan, dict):
                for e in (list(plan.get("entries", []) or [])):
                    if not isinstance(e, dict):
                        continue
                    tk = str(e.get("target_key", "") or "")
                    amt = max(0, int(e.get("amount", 0) or 0))
                    if tk and amt > 0:
                        ppend[tk] = int(ppend.get(tk, 0) or 0) + amt
                        _deferred_2v2 = True

            if _deferred_2v2:
                S.player_pending_damage_by_key = ppend
                try:
                    if callable(getattr(S, "battle_log_add", None)):
                        fn_desc = getattr(S, "bs_describe_unit_key", None)
                        parts = []
                        for _k, _v in ppend.items():
                            if int(_v or 0) <= 0:
                                continue
                            if callable(fn_desc):
                                parts.append("{}:+{}".format(fn_desc(_k, default_side="player", default_slot=0), int(_v or 0)))
                            else:
                                parts.append("{}:+{}".format(_k, int(_v or 0)))
                        S.battle_log_add("{color=#B39DDB}Daño entrante en cola 2v2 → %s{/color}" % (" | ".join(parts)), group="queue_2v2")
                except:
                    pass

                # limpiar plan de este turno y avanzar
                S.enemy_damage_plan = None
                S.enemy_target_key = ""

    # ============================================================
    # ⭐ IMPORTANTE: traer el daño a variable Ren’Py
    # ============================================================
    $ incoming_damage = renpy.store.incoming_damage

    if _deferred_2v2:
        python:
            import renpy.store as S
            _next_team = "player"
            nk = ""
            if callable(getattr(S, "bs_turn_advance", None)) and callable(getattr(S, "bs_parse_unit_key", None)):
                nk = str(S.bs_turn_advance(mirror_legacy=True) or "")
                _next_team = str(S.bs_parse_unit_key(nk, default_side="player", default_slot=0).get("team", "player") or "player")
            try:
                if callable(getattr(S, "battle_log_add", None)) and nk:
                    fn_desc = getattr(S, "bs_describe_unit_key", None)
                    nm = str(fn_desc(nk) if callable(fn_desc) else nk)
                    S.battle_log_add("{color=#80DEEA}[DEBUG] TURN_ADVANCE next_actor_id=%s next_name=%s{/color}" % (str(nk), str(nm)))
            except:
                pass

        if _next_team == "enemy":
            jump battle_enemy_turn
        else:
            jump battle_offensive_turn

    # ============================================================
    # ⭐ VISUAL DAMAGE AL JUGADOR
    # ============================================================
    $ battle_visual_float("player", incoming_damage, "#FF4444", is_final=True)
    $ bs_ui_pause(0.5, hard=True)

    # ============================================================
    # ⭐ MANIOBRA
    # ============================================================
    $ maneuver_selected = "none"
    show screen battle_maneuver_choice(damage=incoming_damage)

    python:
        while maneuver_selected == "none":
            bs_ui_pause(0.1, hard=True)

    # ============================================================
    # ⭐ ATAQUE POR DEFENSA
    # ============================================================
    if maneuver_selected == "atk_from_def":

        python:
            import renpy.store as S
            plan = getattr(S, "enemy_damage_plan", None)
            target_key = str(getattr(S, "enemy_target_key", "") or "")

            fn_apply_plan = getattr(S, "bs_apply_damage_plan", None)
            fn_apply_key = getattr(S, "bs_apply_damage_to_unit_key", None)
            fn_apply = getattr(S, "bs_apply_damage", None)

            if isinstance(plan, dict) and callable(fn_apply_plan):
                fn_apply_plan(plan, reason="combat")
            elif target_key and callable(fn_apply_key):
                fn_apply_key(target_key, incoming_damage, source_key=getattr(S, "current_enemy_unit_key", None), reason="combat")
            elif callable(fn_apply):
                fn_apply("player", incoming_damage, source="enemy", reason="combat")
            else:
                player_hp = max(0, player_hp - incoming_damage)
                battle_update_hp_bars(player_hp, enemy_hp)

            fn_sync = getattr(S, "bs_sync_hp_ui", None)
            if callable(fn_sync):
                fn_sync()
            player_hp = int(getattr(S, "player_hp", 0) or 0)

            try:
                S.enemy_damage_plan = None
                S.enemy_target_key = ""
            except:
                pass

        $ extra_offensive_actions += 1
        $ enemy_ai.reset_turn()

        $ battle_turn_change("player")
        python:
            import renpy.store as S
            _bp = getattr(S, "battle_player", None)
            if isinstance(_bp, dict):
                _pname = str(_bp.get("name", "") or "")
            else:
                _pname = ""
            if not _pname:
                _pname = str(getattr(S, "battle_player_id", "Harribel") or "Harribel")
        $ battle_popup_turn("Turno ofensivo — {}".format(_pname), "#FFD700", delay=0.7)
        jump battle_offensive_turn

    # ============================================================
    # ⭐ DEFENSA POR ATAQUE
    # ============================================================
    if maneuver_selected == "def_from_atk":

        python:
            import renpy.store as S
            S.defense_for_attack_active = True

            # M6 MVP: la defensa se hace sobre la unidad objetivo principal.
            try:
                mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
                tkey = str(getattr(S, "enemy_target_key", "") or "")
                fn_parse = getattr(S, "bs_parse_unit_key", None)
                fn_set_ctx = getattr(S, "bs_set_turn_ctx", None)
                if mode == "2v2" and tkey and callable(fn_parse) and callable(fn_set_ctx):
                    info = fn_parse(tkey, default_side="player", default_slot=0)
                    if str(info.get("team", "player") or "player") == "player":
                        fn_set_ctx(owner_team="player", owner_slot=int(info.get("slot", 0) or 0), phase="defensive", mirror_legacy=True)
                fn_set_incoming_ctx = getattr(S, "bs_set_incoming_ctx_2v2", None)
                _src_key = str(getattr(S, "current_enemy_unit_key", "") or "")
                if mode == "2v2" and callable(fn_set_incoming_ctx):
                    fn_set_incoming_ctx(target_key=str(tkey or ""), source_key=_src_key, owner_team="player", owner_slot=int(getattr(S, "turn_owner_slot", 0) or 0), phase="def")
                else:
                    S.incoming_damage_target_key = str(tkey or "")
                    S.incoming_damage_source_key = _src_key
                    S.incoming_damage_sources = [_src_key]
            except:
                pass

        $ extra_offensive_actions = 0
        $ extra_defensive_actions += 1
        $ enemy_ai.reset_turn()

        python:
            import renpy.store as S

            _pname = ""
            _slot_idx = 0
            _mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()

            fn_parse = getattr(S, "bs_parse_unit_key", None)
            fn_set_ctx = getattr(S, "bs_set_turn_ctx", None)
            fn_get = getattr(S, "bs_get_unit_by_key", None)
            fn_key = getattr(S, "bs_unit_key", None)
            fn_sync = getattr(S, "bs_sync_to_legacy", None)

            if _mode == "2v2" and callable(fn_parse) and callable(fn_set_ctx):
                tkey = str(getattr(S, "enemy_target_key", "") or "")
                info = fn_parse(tkey, default_side="player", default_slot=0)
                if str(info.get("team", "player") or "player") == "player":
                    _slot_idx = int(info.get("slot", 0) or 0)
                    fn_set_ctx(owner_team="player", owner_slot=_slot_idx, phase="defensive", mirror_legacy=True)

            try:
                if callable(fn_sync):
                    fn_sync()
            except:
                pass

            if callable(fn_key) and callable(fn_get):
                uk = str(fn_key("player", _slot_idx) or "")
                uu = fn_get(uk) if uk else None
                if isinstance(uu, dict):
                    _pname = str(uu.get("char_id", "") or "")

            if not _pname:
                _bp = getattr(S, "battle_player", None)
                if isinstance(_bp, dict):
                    _pname = str(_bp.get("name", "") or "")
            if not _pname:
                _pname = str(getattr(S, "battle_player_id", "Harribel") or "Harribel")

            _slot_txt = " ({})".format(S.bs_slot_tag("player", int(_slot_idx or 0)) if callable(getattr(S, "bs_slot_tag", None)) else "S{}".format(int(_slot_idx or 0) + 1)) if _mode == "2v2" else ""

        python:
            import renpy.store as S
            _mode_dbg = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
            _slot_dbg = int(getattr(S, "turn_owner_slot", 0) or 0)
            _target_dbg = str(getattr(S, "incoming_damage_target_key", "") or getattr(S, "enemy_target_key", "") or "")
            _shown_dbg = False
            if _mode_dbg == "2v2" and callable(getattr(S, "battle_log_add", None)):
                S.battle_log_add("{color=#80DEEA}[DEBUG] POPUP_TRANSITION enemy->def attempt mode=2v2 slot=%s target=%s branch=def_from_atk{/color}" % (
                    str(_slot_dbg), str(_target_dbg or "?")))
            try:
                battle_popup_turn("Turno defensivo{} — {}".format(_slot_txt, _pname), "#00BFFF", delay=0.6)
                _shown_dbg = True
            except Exception as e:
                _shown_dbg = False
                if _mode_dbg == "2v2" and callable(getattr(S, "battle_log_add", None)):
                    S.battle_log_add("{color=#FF8A80}[DEBUG] POPUP_TRANSITION enemy->def omitted mode=2v2 slot=%s target=%s branch=def_from_atk err=%s{/color}" % (
                        str(_slot_dbg), str(_target_dbg or "?"), str(e)))
            if _mode_dbg == "2v2" and callable(getattr(S, "battle_log_add", None)):
                S.battle_log_add("{color=#80DEEA}[DEBUG] POPUP_TRANSITION enemy->def result=%s mode=2v2 slot=%s target=%s branch=def_from_atk{/color}" % (
                    "shown" if _shown_dbg else "omitted",
                    str(_slot_dbg),
                    str(_target_dbg or "?")))
        jump battle_defensive_turn

    # ============================================================
    # ⭐ DEFENSA NORMAL
    # ============================================================
    $ enemy_ai.reset_turn()
    python:
        import renpy.store as S

        _pname = ""
        _slot_idx = 0
        _mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()

        fn_parse = getattr(S, "bs_parse_unit_key", None)
        fn_set_ctx = getattr(S, "bs_set_turn_ctx", None)
        fn_get = getattr(S, "bs_get_unit_by_key", None)
        fn_key = getattr(S, "bs_unit_key", None)
        fn_sync = getattr(S, "bs_sync_to_legacy", None)

        if _mode == "2v2" and callable(fn_parse) and callable(fn_set_ctx):
            tkey = str(getattr(S, "enemy_target_key", "") or "")
            info = fn_parse(tkey, default_side="player", default_slot=0)
            if str(info.get("team", "player") or "player") == "player":
                _slot_idx = int(info.get("slot", 0) or 0)
                fn_set_ctx(owner_team="player", owner_slot=_slot_idx, phase="defensive", mirror_legacy=True)
            fn_set_incoming_ctx = getattr(S, "bs_set_incoming_ctx_2v2", None)
            _src_key = str(getattr(S, "current_enemy_unit_key", "") or "")
            if _mode == "2v2" and callable(fn_set_incoming_ctx):
                fn_set_incoming_ctx(target_key=str(tkey or ""), source_key=_src_key, owner_team="player", owner_slot=int(_slot_idx or 0), phase="def")
            else:
                S.incoming_damage_target_key = str(tkey or "")
                S.incoming_damage_source_key = _src_key
                S.incoming_damage_sources = [_src_key]

        try:
            if callable(fn_sync):
                fn_sync()
        except:
            pass

        if callable(fn_key) and callable(fn_get):
            uk = str(fn_key("player", _slot_idx) or "")
            uu = fn_get(uk) if uk else None
            if isinstance(uu, dict):
                _pname = str(uu.get("char_id", "") or "")

        if not _pname:
            _bp = getattr(S, "battle_player", None)
            if isinstance(_bp, dict):
                _pname = str(_bp.get("name", "") or "")
        if not _pname:
            _pname = str(getattr(S, "battle_player_id", "Harribel") or "Harribel")

        _slot_txt = " ({})".format(S.bs_slot_tag("player", int(_slot_idx or 0)) if callable(getattr(S, "bs_slot_tag", None)) else "S{}".format(int(_slot_idx or 0) + 1)) if _mode == "2v2" else ""

    python:
        import renpy.store as S
        _mode_dbg = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        _slot_dbg = int(getattr(S, "turn_owner_slot", 0) or 0)
        _target_dbg = str(getattr(S, "incoming_damage_target_key", "") or getattr(S, "enemy_target_key", "") or "")
        _shown_dbg = False
        if _mode_dbg == "2v2" and callable(getattr(S, "battle_log_add", None)):
            S.battle_log_add("{color=#80DEEA}[DEBUG] POPUP_TRANSITION enemy->def attempt mode=2v2 slot=%s target=%s branch=def_normal{/color}" % (
                str(_slot_dbg), str(_target_dbg or "?")))
        try:
            battle_popup_turn("Turno defensivo{} — {}".format(_slot_txt, _pname), "#00BFFF", delay=0.8)
            _shown_dbg = True
        except Exception as e:
            _shown_dbg = False
            if _mode_dbg == "2v2" and callable(getattr(S, "battle_log_add", None)):
                S.battle_log_add("{color=#FF8A80}[DEBUG] POPUP_TRANSITION enemy->def omitted mode=2v2 slot=%s target=%s branch=def_normal err=%s{/color}" % (
                    str(_slot_dbg), str(_target_dbg or "?"), str(e)))
        if _mode_dbg == "2v2" and callable(getattr(S, "battle_log_add", None)):
            S.battle_log_add("{color=#80DEEA}[DEBUG] POPUP_TRANSITION enemy->def result=%s mode=2v2 slot=%s target=%s branch=def_normal{/color}" % (
                "shown" if _shown_dbg else "omitted",
                str(_slot_dbg),
                str(_target_dbg or "?")))
    call battle_defensive_turn

    return
