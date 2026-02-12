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

        if getattr(S, "player_skip_attack", False):
            S.player_skip_attack = False

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
    $ player_name = "Harribel"
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
    call offensive_formula(total_damage, attack_records)

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


# ============================================================
# RESOLUTOR – Separa daño defendible & directo
# ============================================================

label battle_offensive_resolve_enemy:

    python:
        import renpy.store as S

        enemy_name = getattr(getattr(S, "enemy_ai", None), "name", "Enemigo")
        global direct_damage, final_damage
        direct_damage = 0

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

        fmt_gold = getattr(S, "fmt_gold", globals().get("fmt_gold", None))
        fmt_red  = getattr(S, "fmt_red",  globals().get("fmt_red", None))
        battle_fmt_num = getattr(S, "battle_fmt_num", globals().get("battle_fmt_num", None))

        # ====================================================
        # ⭐ ATAQUE DIRECTO CON ÉXITO → daño NO defendible
        # ====================================================
        if getattr(S, "direct_success", False) and int(getattr(S, "direct_pending_damage", 0) or 0) > 0:

            S.direct_success = False

            direct_damage = int(getattr(S, "direct_pending_damage", 0) or 0)
            S.direct_pending_damage = 0
            S.direct_base_damage    = 0

            try:
                if callable(fmt_gold) and callable(fmt_red) and callable(battle_fmt_num):
                    _blog(fmt_gold("Daño directo aplicado: ") + fmt_red(battle_fmt_num(direct_damage)))
                else:
                    _blog("Daño directo aplicado: {}".format(direct_damage), "#FFD700")
            except:
                _blog("Daño directo aplicado: {}".format(direct_damage), "#FFD700")

        # ====================================================
        # ⭐ DEFENSAS ENEMIGAS (STORE-safe)
        # ====================================================
        fn_def = getattr(S, "enemy_compute_reactive_defense", None)
        if callable(fn_def):
            info = fn_def(total_damage)
            try:
                final_damage = int(info.get("final_damage", total_damage) or 0)
            except:
                final_damage = int(total_damage or 0)
        else:
            final_damage = int(total_damage or 0)

        # ====================================================
        # ⭐ APLICAR DAÑOS (STORE HP = fuente real)
        # ====================================================
        try:
            cur_hp = int(getattr(S, "enemy_hp", 0) or 0)
            cur_hp = max(0, cur_hp - int(final_damage or 0))
            cur_hp = max(0, cur_hp - int(direct_damage or 0))
            S.enemy_hp = cur_hp
        except:
            pass

    # ============================================================
    # VISUALES
    # ============================================================
    if direct_damage > 0:
        $ battle_visual_float("enemy", direct_damage, "#FFDD55", is_final=True)
        $ renpy.pause(0.3, hard=True)

    $ battle_update_hp_bars(getattr(renpy.store, "player_hp", 0), getattr(renpy.store, "enemy_hp", 0))
    $ battle_visual_float("enemy", final_damage, "#FF4444", is_final=True)
    $ renpy.pause(0.5, hard=True)

    python:
        import renpy.store as S
        fn_reset = getattr(S, "battle_reset_used_by_type", None)
        if callable(fn_reset):
            fn_reset()

    # ============================================================
    # FIN DEL TURNO
    # ============================================================
    if getattr(renpy.store, "enemy_hp", 0) <= 0:
        $ battle_log_add(fmt_gold("¡Victoria!"))
        jump battle_end

    $ _fn_turn = getattr(renpy.store, "battle_turn_change", None)
    if _fn_turn:
        $ _fn_turn("enemy")

    $ renpy.show_screen("battle_popup_turn", text="Turno ofensivo — {}".format(enemy_name), color="#FFD700")
    $ renpy.pause(0.7, hard=True)
    $ renpy.hide_screen("battle_popup_turn")

    jump battle_enemy_turn
