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

label battle_enemy_turn:

    $ battle_turn_change("enemy")
    $ enemy_name = enemy_ai.name

    python:
        import renpy.store as S
        S._enemy_reflect_consumed_this_turn = False

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

        if getattr(S, "enemy_skip_attack", False):

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

            renpy.pause(0.5, hard=True)

            # Diseño elegido: NO limpiamos reflect aquí.
            S.battle_turn_change("player")
            try:
                _bp = getattr(S, "battle_player", None)
                if isinstance(_bp, dict):
                    _pname = str(_bp.get("name", "") or "")
                else:
                    _pname = ""
                if not _pname:
                    _pname = str(getattr(S, "battle_player_id", "Harribel") or "Harribel")
                S.battle_popup_turn("Turno ofensivo — {}".format(_pname), "#FFD700", 0.7)
            except:
                pass
            renpy.jump("battle_offensive_turn")

    # ============================================================
    # ⭐ ENCABEZADO IA
    # ============================================================
    $ battle_popup_turn("Turno ofensivo — {}".format(enemy_name), "#FFD700", delay=0.6)
    $ battle_log_phase("TURNO OFENSIVO – {}".format(enemy_name))
    $ renpy.pause(0.8, hard=True)

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

        # ID store-safe
        S.current_enemy_id = getattr(S, "BATTLE_IDENTITIES", {}).get(enemy_name, "ID_ENEMY_UNKNOWN")
        try:
            fn_active_key = getattr(S, "bs_get_active_unit_key", None)
            if callable(fn_active_key):
                S.current_enemy_unit_key = str(fn_active_key("enemy") or "")
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
            renpy.pause(0.35, hard=True)

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
            primary = scored[0]["key"] if scored else ""

            # C.3: policy burst vs presión distribuida
            policy = "single_target"
            alive_n = len(scored)
            lowest_hp = min([x.get("hp", 0) for x in scored]) if scored else 0
            can_secure_ko = bool(total_damage > 0 and lowest_hp > 0 and total_damage >= lowest_hp)

            if alive_n <= 1:
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

            try:
                if callable(getattr(S, "battle_log_add", None)) and primary:
                    S.battle_log_add("{color=#B0E0E6}AI target policy: %s → %s{/color}" % (policy, primary))
            except:
                pass

        try:
            S.battle_log_add(
                S.log_operation(
                    formula_text,
                    enemy_reflect_bonus if enemy_attack_executed else 0,
                    total_damage
                )
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
            fmt_gold   = getattr(S, "fmt_gold",   globals().get("fmt_gold", None))
            fmt_red    = getattr(S, "fmt_red",    globals().get("fmt_red", None))
            fmt_white  = getattr(S, "fmt_white",  globals().get("fmt_white", None))
            fmt_orange = getattr(S, "fmt_orange", globals().get("fmt_orange", None))
        except:
            fmt_gold = fmt_red = fmt_white = fmt_orange = None

        if dmg_directo == 0:
            if debuff_pct > 0:
                try:
                    S.battle_log_add(
                        fmt_gold("Daño total: ") +
                        fmt_red(S.battle_fmt_num(dmg_defendible)) +
                        fmt_white(" defendibles ") +
                        fmt_orange("(-{}% defensa general)".format(int(debuff_pct * 100)))
                    )
                except:
                    pass
            else:
                try:
                    S.battle_log_add(
                        fmt_gold("Daño total: ") +
                        fmt_red(S.battle_fmt_num(dmg_defendible)) +
                        fmt_white(" defendibles")
                    )
                except:
                    pass
        else:
            total_final = dmg_defendible + dmg_directo
            try:
                S.battle_log_add(
                    fmt_gold("Daño total: ") +
                    fmt_red(S.battle_fmt_num(dmg_defendible)) +
                    fmt_white(" defendibles + ") +
                    fmt_red(S.battle_fmt_num(dmg_directo)) +
                    fmt_white(" directos = ") +
                    fmt_red(S.battle_fmt_num(total_final))
                )
            except:
                pass

    # ============================================================
    # ⭐ IMPORTANTE: traer el daño a variable Ren’Py
    # ============================================================
    $ incoming_damage = renpy.store.incoming_damage

    # ============================================================
    # ⭐ VISUAL DAMAGE AL JUGADOR
    # ============================================================
    $ battle_visual_float("player", incoming_damage, "#FF4444", is_final=True)
    $ renpy.pause(0.5, hard=True)

    # ============================================================
    # ⭐ MANIOBRA
    # ============================================================
    $ maneuver_selected = "none"
    show screen battle_maneuver_choice(damage=incoming_damage)

    python:
        while maneuver_selected == "none":
            renpy.pause(0.1, hard=True)

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
            except:
                pass

        $ extra_offensive_actions = 0
        $ extra_defensive_actions += 1
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
        $ battle_popup_turn("Turno defensivo — {}".format(_pname), "#00BFFF", delay=0.6)
        jump battle_defensive_turn

    # ============================================================
    # ⭐ DEFENSA NORMAL
    # ============================================================
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
    $ battle_popup_turn("Turno defensivo — {}".format(_pname), "#00BFFF", delay=0.8)
    call battle_defensive_turn

    return
