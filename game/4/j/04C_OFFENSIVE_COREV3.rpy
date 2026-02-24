# ============================================================
# 04C_OFFENSIVE_CORE.rpy – Turno ofensivo del jugador (Núcleo)
# ============================================================
# v8.5 – SafeLogHub + UsedFlag Strict + StoreSafe Dice/Text
# ------------------------------------------------------------
# - NO usa reset_concentrar() (legacy) porque rompe carry-over
# - Focus/Concentrar (cargas) se resuelve con:
#     S.battle_focus_end_turn("offensive", used)
# - Snapshot recursos = STORE real
# - Popup como SCREEN (show_screen + pause + hide)
# - HP/KO/UI usan STORE
# - DADOS hardened: no crashea si faltan helpers/loggers
# - Routing fix: Defense-for-Attack → salta al turno enemigo
# - ✅ NEW: player_skip_attack (Ataque Negador IA) salta turno jugador
# - ✅ FIX: Ataque Negador del jugador setea enemy_skip_attack (no player)
# ============================================================

label battle_offensive_turn:

    # ============================================================
    # ⭐ ROUTING FIX — si Defensa por ataque está activa,
    # saltar automáticamente al turno ofensivo de la IA
    # ============================================================
    python:
        import renpy.store as S

        if getattr(S, "defense_for_attack_active", False):
            S.defense_for_attack_active = False

            enemy_name = getattr(getattr(S, "enemy_ai", None), "name", "Enemigo")

            fn_turn_change = getattr(S, "battle_turn_change", None)
            if callable(fn_turn_change):
                fn_turn_change("enemy")

            try:
                renpy.show_screen("battle_popup_turn",
                                  text="Turno ofensivo — {}".format(enemy_name),
                                  color="#FFD700")
                renpy.pause(0.7, hard=True)
                renpy.hide_screen("battle_popup_turn")
            except:
                pass

            renpy.jump("battle_enemy_turn")

    # ============================================================
    # 🚫 ATAQUE NEGADOR (IA) — SKIP TURNO OFENSIVO DEL JUGADOR
    # (debe ir ANTES del snapshot/UI)
    # ============================================================
    python:
        import renpy.store as S

        S._reflect_consumed_this_turn = False
        if getattr(S, "player_skip_attack", False):
            S.player_skip_attack = False

            # Si el jugador no ataca este turno, reflect pendiente se desvanece.
            try:
                enemy_name_now = getattr(getattr(S, "enemy_ai", None), "name", None)
                if enemy_name_now:
                    enemy_target_id = getattr(S, "BATTLE_IDENTITIES", {}).get(
                        enemy_name_now,
                        getattr(S, "current_enemy_id", "ID_ENEMY_UNKNOWN")
                    )
                else:
                    enemy_target_id = getattr(S, "current_enemy_id", "ID_ENEMY_UNKNOWN")

                dropped_reflect = 0
                ref_source = None

                fn_consume = getattr(S, "reflect_consume_for", None)
                if callable(fn_consume):
                    dropped_reflect, ref_source = fn_consume(enemy_target_id)
                else:
                    rman = getattr(S, "reflect", None)
                    if rman and hasattr(rman, "consume_info"):
                        dropped_reflect, ref_source = rman.consume_info(enemy_target_id)
                    elif rman and hasattr(rman, "consume"):
                        dropped_reflect = rman.consume(enemy_target_id)

                dropped_reflect = int(dropped_reflect or 0)
                if dropped_reflect > 0:
                    S.battle_log_add(
                        "{color=#00FFFF}Reflect se desvanece (sin ataque): %s{/color}" %
                        S.battle_fmt_num(dropped_reflect)
                    )
            except:
                pass

            S._reflect_consumed_this_turn = True

            # Log (store-safe)
            try:
                fn = getattr(S, "safe_battle_log_add", None)
                if callable(fn):
                    fn("{color=#FF66CC}Ataque Negador: NO ATK este turno.{/color}")
                else:
                    S.battle_log_add("{color=#FF66CC}Ataque Negador: NO ATK este turno.{/color}")
            except:
                try:
                    battle_log_add("{color=#FF66CC}Ataque Negador: NO ATK este turno.{/color}")
                except:
                    pass

            # Cambiar turno (si existe helper)
            fn_turn_change = getattr(S, "battle_turn_change", None)
            if callable(fn_turn_change):
                fn_turn_change("enemy")

            # Popup opcional
            try:
                enemy_name = getattr(getattr(S, "enemy_ai", None), "name", "Enemigo")
                renpy.show_screen("battle_popup_turn",
                                  text="Turno ofensivo — {}".format(enemy_name),
                                  color="#FFD700")
                renpy.pause(0.7, hard=True)
                renpy.hide_screen("battle_popup_turn")
            except:
                pass

            renpy.jump("battle_enemy_turn")

    # ============================================================
    # Snapshot de recursos al inicio del turno (STORE = real)
    # ============================================================
    $ import renpy.store as S
    $ S.turn_reiatsu_start = getattr(S, "player_reiatsu", 0)
    $ S.turn_energy_start  = getattr(S, "player_energy", 0)
    $ S.turn_reiatsu_spent = 0
    $ S.turn_energy_spent  = 0

    # ============================================================
    # Estado base del turno ofensivo
    # ============================================================
    $ total_damage = 0
    $ actions = 1 + getattr(S, "extra_offensive_actions", 0)
    $ actions_available_start = actions

    # ⭐ Recursos simulados para selector (si el selector los usa)
    $ simulated_reiatsu = getattr(S, "player_reiatsu", 0)
    $ simulated_energy  = getattr(S, "player_energy", 0)

    # Limpiezas
    $ next_defense_reduction = 0
    $ S.extra_offensive_actions = 0
    $ combo_count = 0

    # ------------------------------------------------------------
    # ✅ Focus/Concentrar (NUEVO SISTEMA por CARGAS)
    # ------------------------------------------------------------
    $ concentrar_activo = False
    $ can_focus = True

    python:
        import renpy.store as S
        try:
            fn = getattr(S, "can_use_concentrar", None)
            if callable(fn):
                can_focus = fn("offensive")
        except:
            pass

    $ awaiting_turn_end = False
    python:
        import renpy.store as S
        _bp = getattr(S, "battle_player", None)
        if isinstance(_bp, dict):
            player_name = str(_bp.get("name", "") or "")
        else:
            player_name = ""
        if not player_name:
            player_name = str(getattr(S, "battle_player_id", "Harribel") or "Harribel")
    $ attack_records = []

    # Fuente de verdad del hook: la marca Offensive_Actions SOLO si ejecuta y paga
    $ S.turn_offensive_attack_used = False

    # ============================================================
    # Identidad para reflect (STORE)
    # ============================================================
    $ S.current_actor_id = getattr(S, "BATTLE_IDENTITIES", {}).get(player_name, "ID_PLAYER_UNKNOWN")

    # ============================================================
    # Encabezado del turno
    # ============================================================
    $ battle_log_phase("TURNO OFENSIVO – {}".format(player_name))

    $ renpy.show_screen("battle_popup_turn",
                        text="Turno ofensivo — {}".format(player_name),
                        color="#FFD700")
    $ renpy.pause(0.6, hard=True)
    $ renpy.hide_screen("battle_popup_turn")

    # ============================================================
    # UI selección
    # ============================================================
    $ battle_mode = "offensive"
    $ S.turn_confirmed = False
    $ actions_available = actions
    $ operation_clear()

    show screen battle_command_menu
    show screen technique_selector
    $ renpy.restart_interaction()

    python:
        import renpy.store as S
        while not getattr(S, "turn_confirmed", False):
            renpy.pause(0.1, hard=True)

    hide screen battle_command_menu
    hide screen technique_selector

    # ============================================================
    # Copiar técnicas seleccionadas (STORE-safe)
    # ============================================================
    $ selected = list(getattr(S, "player_action_queue", []))
    $ S.player_action_queue[:] = []
    $ S.last_selected_actions = selected[:]

    # ============================================================
    # PROCESAR ACCIONES OFENSIVAS (acá se consume realmente)
    # ============================================================
    call offensive_process_actions(selected)

    # ------------------------------------------------------------
    # ✅ UsedFlag STRICT:
    # - NO inventar "used" por total_damage (puede venir de reflect/otros).
    # - Si querés fallback, que sea conservador: solo si hubo consumo real.
    # ------------------------------------------------------------
    python:
        import renpy.store as S
        try:
            if (not getattr(S, "turn_offensive_attack_used", False)) and attack_records:
                # fallback conservador: si realmente gastó recursos en el turno
                spent_r = int(getattr(S, "turn_reiatsu_spent", 0) or 0)
                spent_e = int(getattr(S, "turn_energy_spent", 0) or 0)
                if (spent_r > 0) or (spent_e > 0):
                    S.turn_offensive_attack_used = True
        except:
            pass

    # ============================================================
    # Snapshot de consumo REAL (después del consumo)
    # ============================================================
    python:
        import renpy.store as S
        try:
            start_r = getattr(S, "turn_reiatsu_start", getattr(S, "player_reiatsu", 0))
            start_e = getattr(S, "turn_energy_start",  getattr(S, "player_energy", 0))
            cur_r   = getattr(S, "player_reiatsu", 0)
            cur_e   = getattr(S, "player_energy", 0)
            S.turn_reiatsu_spent = max(0, int(start_r) - int(cur_r))
            S.turn_energy_spent  = max(0, int(start_e) - int(cur_e))
        except:
            S.turn_reiatsu_spent = 0
            S.turn_energy_spent  = 0

    # ============================================================
    # 🎲 TIRADA DE DADOS (Directo / Negador) — HARDENED
    # ============================================================
    python:
        import renpy.store as S

        used_direct = ("Ataque Directo" in (selected or []))
        used_noatk  = ("Ataque Negador" in (selected or []))

        S.direct_success = False
        S.noatk_success  = False

        def _blog(t, c=None, border=None):
            try:
                fn = getattr(S, "safe_battle_log_add", None)
                if callable(fn):
                    try:
                        if c is None and border is None:
                            fn(t)
                        else:
                            fn(t, color=c, border=border)
                    except:
                        try:
                            if c is None: fn(t)
                            else: fn(t, c)
                        except:
                            pass
                    return
            except:
                pass
            try:
                g = globals().get("battle_log_add", None)
                if callable(g):
                    if c is None: g(t)
                    else: g(t, c)
                    return
            except:
                pass
            try:
                s = getattr(S, "battle_log_add", None)
                if callable(s):
                    if c is None: s(t)
                    else: s(t, c)
            except:
                pass

        # fmt_* store-safe
        fmt_purple = getattr(S, "fmt_purple", globals().get("fmt_purple", None))
        fmt_gold   = getattr(S, "fmt_gold",   globals().get("fmt_gold", None))
        fmt_white  = getattr(S, "fmt_white",  globals().get("fmt_white", None))
        fmt_red    = getattr(S, "fmt_red",    globals().get("fmt_red", None))

        battle_fmt_num = getattr(S, "battle_fmt_num", globals().get("battle_fmt_num", None))

        if used_direct or used_noatk:

            roll = None
            try:
                fn_roll = getattr(S, "roll_3d", None)
                if callable(fn_roll):
                    roll = fn_roll()
            except:
                roll = None

            if isinstance(roll, dict):

                # mostrar dados
                try:
                    fn_show = getattr(S, "show_dice_result", None)
                    if callable(fn_show):
                        fn_show(roll)
                    else:
                        try:
                            renpy.show_screen("dice_roll_result", rolls=roll.get("rolls", []))
                        except:
                            pass
                except:
                    pass

                # log de slots (preferir store-safe)
                try:
                    fn_slots = getattr(S, "log_dice_slots", None)
                    if not callable(fn_slots):
                        fn_slots = globals().get("log_dice_slots", None)
                    if callable(fn_slots):
                        _blog(fn_slots(roll.get("rolls", [])))
                except:
                    pass

                if roll.get("success", False):

                    if used_direct:
                        S.direct_success = True

                    if used_noatk:
                        S.noatk_success = True

                        # ✅ FIX: el Negador del JUGADOR cancela el turno del ENEMIGO
                        S.enemy_skip_attack = True

                        try:
                            if callable(fmt_purple) and callable(fmt_gold):
                                _blog(fmt_purple("Ataque Negador → ") + fmt_gold("ÉXITO"))
                            else:
                                _blog("Ataque Negador → ÉXITO", "#C586C0")
                        except:
                            _blog("Ataque Negador → ÉXITO", "#C586C0")

                # === ATAQUE DIRECTO FALLADO → daño defendible ===
                if (not getattr(S, "direct_success", False)) and ("Ataque Directo" in getattr(S, "last_selected_actions", [])):

                    try:
                        base_d = int(getattr(S, "direct_base_damage", 0) or 0)
                    except:
                        base_d = 0
                    try:
                        dmg_d  = int(getattr(S, "direct_pending_damage", 0) or base_d)
                    except:
                        dmg_d = base_d

                    if dmg_d > 0:
                        try:
                            attack_records.append((base_d, dmg_d))
                        except:
                            pass
                        try:
                            total_damage += dmg_d
                        except:
                            total_damage = int(total_damage or 0) + int(dmg_d or 0)

                        try:
                            if callable(fmt_white) and callable(fmt_red) and callable(battle_fmt_num):
                                _blog(
                                    fmt_white("Ataque Directo fallado → ") +
                                    fmt_red(battle_fmt_num(dmg_d)) +
                                    fmt_white(" daño defendible.")
                                )
                            else:
                                _blog("Ataque Directo fallado → {} daño defendible.".format(dmg_d), "#FFFFFF")
                        except:
                            _blog("Ataque Directo fallado → {} daño defendible.".format(dmg_d), "#FFFFFF")

                        S.direct_pending_damage = 0

                try:
                    renpy.pause(0.8, hard=True)
                except:
                    pass

    # ============================================================
    # Fórmula final (reflect + total defendible)
    # ============================================================
    python:
        import renpy.store as S

        reflected_bonus = 0
        ref_source = None

        if not bool(getattr(S, "_reflect_consumed_this_turn", False)):
            try:
                enemy_name_now = getattr(getattr(S, "enemy_ai", None), "name", None)
                if enemy_name_now:
                    enemy_target_id = getattr(S, "BATTLE_IDENTITIES", {}).get(
                        enemy_name_now,
                        getattr(S, "current_enemy_id", "ID_ENEMY_UNKNOWN")
                    )
                else:
                    enemy_target_id = getattr(S, "current_enemy_id", "ID_ENEMY_UNKNOWN")

                fn_consume = getattr(S, "reflect_consume_for", None)
                if callable(fn_consume):
                    reflected_bonus, ref_source = fn_consume(enemy_target_id)
                else:
                    rman = getattr(S, "reflect", None)
                    if rman and hasattr(rman, "consume_info"):
                        reflected_bonus, ref_source = rman.consume_info(enemy_target_id)
                    elif rman and hasattr(rman, "consume"):
                        reflected_bonus = rman.consume(enemy_target_id)
            except:
                reflected_bonus = 0
                ref_source = None
            finally:
                S._reflect_consumed_this_turn = True

        try:
            reflected_bonus = int(reflected_bonus or 0)
        except:
            reflected_bonus = 0

        if reflected_bonus < 0:
            reflected_bonus = 0

        if reflected_bonus > 0:
            if bool(getattr(S, "turn_offensive_attack_used", False)):
                total_damage = int(total_damage or 0) + reflected_bonus
                try:
                    src_txt = (" (fuente: %s)" % ref_source) if ref_source else ""
                    S.battle_log_add(
                        "{color=#00FFFF}Reflect +%s%s{/color}" %
                        (S.battle_fmt_num(reflected_bonus), src_txt)
                    )
                except:
                    pass
            else:
                try:
                    S.battle_log_add(
                        "{color=#00FFFF}Reflect se desvanece (sin ataque): %s{/color}" %
                        S.battle_fmt_num(reflected_bonus)
                    )
                except:
                    pass

    call offensive_formula(total_damage, attack_records)

    # ============================================================
    # B.1/B.2/B.3 – Targeting táctico + split manual + fallbacks
    # ============================================================
    python:
        import renpy.store as S

        S.offensive_target_key = ""
        S.offensive_damage_plan = None

        fn_valid = getattr(S, "bs_get_valid_target_keys", None)
        fn_resolve = getattr(S, "bs_resolve_target_keys", None)
        fn_parse = getattr(S, "bs_parse_unit_key", None)
        fn_get_unit = getattr(S, "bs_get_unit_by_key", None)
        fn_make_plan = getattr(S, "bs_make_damage_plan", None)

        if callable(fn_valid) and callable(fn_resolve):
            valid_keys = list(fn_valid("enemy") or [])
            total_available = max(0, int(total_damage or 0))
            used_attack = bool(getattr(S, "turn_offensive_attack_used", False))

            policy = str(getattr(S, "offensive_targeting_policy", "single_target") or "single_target").strip().lower()
            if policy not in ("single_target", "split_equal", "split_manual"):
                policy = "single_target"

            # B.2: paquetes manuales basados en ataques seleccionados (o único paquete total)
            raw_packages = []
            for pair in (attack_records or []):
                try:
                    _, dmg_i = pair
                    di = max(0, int(dmg_i or 0))
                    if di > 0:
                        raw_packages.append(di)
                except:
                    pass
            if (not raw_packages) and total_available > 0:
                raw_packages = [total_available]

            packages = []
            if total_available > 0:
                rem = total_available
                for amt in raw_packages:
                    if rem <= 0:
                        break
                    a = min(rem, max(0, int(amt or 0)))
                    if a > 0:
                        packages.append(a)
                        rem -= a
                if rem > 0:
                    packages.append(rem)

            assignment = {}
            manual_completed = False

            def _label_for_key(k):
                label = str(k)
                if callable(fn_parse):
                    info = fn_parse(k)
                    slot = int(info.get("slot", 0) or 0)
                    unit = fn_get_unit(k) if callable(fn_get_unit) else None
                    if isinstance(unit, dict):
                        hp = int(unit.get("hp", 0) or 0)
                        mx = int(unit.get("max_hp", 0) or 0)
                        name = str(unit.get("char_id", "") or "")
                        if name:
                            return "{} [HP {}/{}]".format(name, hp, mx)
                        return "Objetivo {} [HP {}/{}]".format(slot + 1, hp, mx)
                    return "Objetivo {}".format(slot + 1)
                return label

            # B.2: split manual (si hay múltiples objetivos y hubo ataque)
            if policy == "split_manual" and len(valid_keys) > 1 and used_attack and packages:
                manual_cancelled = False
                for i, amount in enumerate(packages):
                    menu_items = []
                    for k in valid_keys:
                        menu_items.append(("{}  ← paquete {} ({} daño)".format(_label_for_key(k), i + 1, amount), k))
                    menu_items.append(("[AUTO] usar fallback", "__AUTO__"))

                    chosen = None
                    try:
                        chosen = renpy.display_menu(menu_items)
                    except:
                        chosen = "__AUTO__"

                    if (not chosen) or (chosen == "__AUTO__"):
                        manual_cancelled = True
                        break

                    assignment[chosen] = int(assignment.get(chosen, 0) or 0) + int(amount or 0)

                assigned_total = 0
                for v in assignment.values():
                    assigned_total += max(0, int(v or 0))
                manual_completed = (not manual_cancelled) and (assigned_total == total_available) and bool(assignment)

            # B.3: fallback automático por política
            if not manual_completed:
                if policy == "split_equal" and len(valid_keys) > 1 and total_available > 0:
                    resolved = fn_resolve(mode="split_equal", target_team="enemy")
                    count = max(1, len(resolved))
                    base = total_available // count
                    rem = total_available % count
                    assignment = {}
                    for idx, k in enumerate(resolved):
                        assignment[k] = base + (1 if idx < rem else 0)
                else:
                    selected_key = None
                    if len(valid_keys) > 1 and used_attack:
                        menu_items = [(_label_for_key(k), k) for k in valid_keys]
                        try:
                            selected_key = renpy.display_menu(menu_items)
                        except:
                            selected_key = None

                    resolved = fn_resolve(
                        mode="single_target",
                        target_team="enemy",
                        selected_target_key=selected_key,
                    )
                    if resolved and total_available > 0:
                        assignment = {resolved[0]: total_available}
                    elif resolved:
                        assignment = {resolved[0]: 0}

            # Persistir target principal + damage plan
            if assignment:
                first_key = ""
                entries = []
                for k, amount in assignment.items():
                    if not first_key:
                        first_key = str(k or "")
                    amt_i = max(0, int(amount or 0))
                    if amt_i > 0:
                        entries.append({"target_key": str(k or ""), "amount": amt_i, "tags": ["offensive"]})

                S.offensive_target_key = first_key

                if entries and callable(fn_make_plan):
                    S.offensive_damage_plan = fn_make_plan(
                        source_key=getattr(S, "current_actor_unit_key", None),
                        entries=entries,
                        mode=("split_manual" if manual_completed else policy),
                        skill_id="offensive_turn",
                        meta={"total_expected": total_available, "manual_completed": bool(manual_completed)},
                    )

    # ------------------------------------------------------------
    # ✅ FIN DEL TURNO: Hook unificado (Concentrar por cargas)
    # ------------------------------------------------------------
    python:
        import renpy.store as S

        used = bool(getattr(S, "turn_offensive_attack_used", False))

        try:
            fn = getattr(S, "battle_focus_end_turn", None)
            if callable(fn):
                fn("offensive", used)
            else:
                raise Exception("no battle_focus_end_turn")
        except:
            try:
                fn2 = getattr(S, "focus_off_end_turn_decay", None)
                if callable(fn2):
                    fn2()
            except:
                pass

        try:
            S.focus_cost_active = False
        except:
            pass

    jump battle_offensive_resolve_enemy
