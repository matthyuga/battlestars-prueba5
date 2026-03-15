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

label battle_offensive_turn_legacy_entry:

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
                bs_ui_show("battle_popup_turn",
                                  text="Turno ofensivo — {}".format(enemy_name),
                                  color="#FFD700")
                bs_ui_pause(0.7, hard=True)
                bs_ui_hide("battle_popup_turn")
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
        _should_skip_offense = bool(getattr(S, "player_skip_attack", False))
        _consumed_keyed_skip = False

        _actor_key_skip = ""
        if callable(getattr(S, "bs_current_actor_key", None)):
            _actor_key_skip = str(S.bs_current_actor_key() or "")

        _pmap_skip = getattr(S, "player_skip_attack_by_key", None)
        if _actor_key_skip and isinstance(_pmap_skip, dict) and bool(_pmap_skip.get(_actor_key_skip, False)):
            _should_skip_offense = True
            _consumed_keyed_skip = True

        # En 2v2, si este actor tiene daño pendiente, primero debe resolver
        # su ventana defensiva/maniobra antes de perder el turno ofensivo.
        if _should_skip_offense:
            try:
                _mode_skip = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
                if _mode_skip == "2v2" and callable(getattr(S, "bs_current_actor_key", None)):
                    _akey_skip = str(S.bs_current_actor_key() or "")
                    _ppend_skip = getattr(S, "player_pending_damage_by_key", None)
                    if _akey_skip and isinstance(_ppend_skip, dict):
                        _pend_skip = max(0, int(_ppend_skip.get(_akey_skip, 0) or 0))
                        if _pend_skip > 0:
                            _should_skip_offense = False
            except:
                pass

        if _should_skip_offense:
            if _consumed_keyed_skip:
                try:
                    _pmap_skip[_actor_key_skip] = False
                    S.player_skip_attack_by_key = _pmap_skip
                except:
                    pass
            S.player_skip_attack = False
            S.offense_cancelled = True

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

            _mode_skip_flow = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
            _next_team = "enemy"
            _next_key = ""
            if _mode_skip_flow == "2v2" and callable(getattr(S, "bs_turn_advance", None)) and callable(getattr(S, "bs_parse_unit_key", None)):
                _next_key = str(S.bs_turn_advance(mirror_legacy=True) or "")
                _next_team = str(S.bs_parse_unit_key(_next_key, default_side="enemy", default_slot=0).get("team", "enemy") or "enemy")

            # Cambiar turno (si existe helper)
            fn_turn_change = getattr(S, "battle_turn_change", None)
            if callable(fn_turn_change):
                fn_turn_change(_next_team)

            # Popup opcional
            try:
                fn_desc = getattr(S, "bs_describe_unit_key", None)
                if _next_team == "enemy":
                    enemy_name = str(fn_desc(_next_key) if callable(fn_desc) and _next_key else getattr(getattr(S, "enemy_ai", None), "name", "Enemigo"))
                    bs_ui_show("battle_popup_turn", text="Turno ofensivo — {}".format(enemy_name), color="#FFD700")
                else:
                    player_name = str(fn_desc(_next_key) if callable(fn_desc) and _next_key else getattr(S, "battle_player_id", "Harribel"))
                    bs_ui_show("battle_popup_turn", text="Turno ofensivo — {}".format(player_name), color="#FFD700")
                bs_ui_pause(0.7, hard=True)
                bs_ui_hide("battle_popup_turn")
            except:
                pass

            if _next_team == "enemy":
                renpy.jump("battle_enemy_turn")
            else:
                renpy.jump("battle_offensive_turn")

    # ============================================================
    # ⭐ 2v2: resolver daño entrante SOLO cuando le toca al defensor
    # ============================================================
    python:
        import renpy.store as S
        _mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        if _mode == "2v2" and callable(getattr(S, "bs_current_actor_key", None)) and callable(getattr(S, "bs_parse_unit_key", None)):
            akey = str(S.bs_current_actor_key() or "")
            ainfo = S.bs_parse_unit_key(akey, default_side="player", default_slot=0)
            if str(ainfo.get("team", "player") or "player") != "player":
                akey = ""
            ppend = getattr(S, "player_pending_damage_by_key", None)
            if akey and isinstance(ppend, dict):
                pend_amt = max(0, int(ppend.get(akey, 0) or 0))
                if pend_amt > 0:
                    ppend[akey] = 0
                    S.player_pending_damage_by_key = ppend
                    S.incoming_damage = int(pend_amt)
                    fn_set_incoming_ctx = getattr(S, "bs_set_incoming_ctx_2v2", None)
                    _src_key = str(getattr(S, "current_enemy_unit_key", "") or "")
                    if _mode == "2v2" and callable(fn_set_incoming_ctx):
                        fn_set_incoming_ctx(target_key=str(akey), source_key=_src_key, owner_team="player", owner_slot=int(ainfo.get("slot", 0) or 0), phase="def")
                    else:
                        S.incoming_damage_target_key = str(akey)
                        S.incoming_damage_source_key = _src_key
                        S.incoming_damage_sources = [_src_key]

                    info = S.bs_parse_unit_key(akey, default_side="player", default_slot=0) if callable(getattr(S, "bs_parse_unit_key", None)) else {"slot":0}
                    slot_idx = int(info.get("slot", 0) or 0)
                    if callable(getattr(S, "bs_set_turn_ctx", None)):
                        S.bs_set_turn_ctx(owner_team="player", owner_slot=slot_idx, phase="defensive", mirror_legacy=True)

                    def_name = akey
                    try:
                        fn_desc = getattr(S, "bs_describe_unit_key", None)
                        if callable(fn_desc):
                            def_name = str(fn_desc(akey, default_side="player", default_slot=0) or akey)
                    except:
                        pass

                    try:
                        if callable(getattr(S, "battle_log_add", None)):
                            S.battle_log_add("{color=#80DEEA}[DEBUG] INCOMING_DAMAGE defender_id=%s defender_name=%s pending_amount=%s sources=%s{/color}" % (
                                str(akey), str(def_name), str(int(pend_amt)), str(getattr(S, "incoming_damage_sources", []) or [])))
                    except:
                        pass

                    S.deferred_defense_return_to_offense = True
                    S.deferred_defense_actor_key = str(akey)

                    try:
                        bs_ui_show("battle_popup_turn", text="Daño entrante — {}".format(def_name), color="#00BFFF")
                        bs_ui_pause(0.7, hard=True)
                        bs_ui_hide("battle_popup_turn")
                    except:
                        try:
                            S.battle_popup_turn("Daño entrante — {}".format(def_name), "#00BFFF", 0.6)
                        except:
                            pass

                    try:
                        battle_visual_float("player", int(pend_amt or 0), "#FF4444", is_final=True)
                        bs_ui_pause(0.35, hard=True)
                    except:
                        pass

                    S.maneuver_selected = "none"
                    bs_ui_show("battle_maneuver_choice", damage=int(pend_amt or 0))
                    while getattr(S, "maneuver_selected", "none") == "none":
                        bs_ui_pause(0.1, hard=True)

                    msel = str(getattr(S, "maneuver_selected", "none") or "none")
                    if msel == "atk_from_def":
                        fn_apply_key = getattr(S, "bs_apply_damage_to_unit_key", None)
                        if callable(fn_apply_key):
                            fn_apply_key(str(akey), int(pend_amt or 0), source_key=_src_key, reason="combat")
                        else:
                            S.player_hp = max(0, int(getattr(S, "player_hp", 0) or 0) - int(pend_amt or 0))
                        S.extra_offensive_actions = int(getattr(S, "extra_offensive_actions", 0) or 0) + 1
                        S.deferred_defense_return_to_offense = False
                        S.deferred_defense_actor_key = ""
                    elif msel == "counterattack":
                        fn_ctr = getattr(S, "bs_counterattack_execute", None)
                        ctr = fn_ctr(unit_key=str(akey), incoming_damage=int(pend_amt or 0)) if callable(fn_ctr) else {"executed": False, "success": False}
                        ctr_ok = bool(isinstance(ctr, dict) and ctr.get("executed", False))
                        ctr_success = bool(isinstance(ctr, dict) and ctr.get("success", False))

                        if callable(getattr(S, "battle_log_add", None)):
                            if ctr_success:
                                S.battle_log_add("{color=#66FF99}Contraataque exitoso (4/4): no recibes daño y ganas acción ofensiva.{/color}")
                            elif ctr_ok:
                                _rp = int(ctr.get("reiatsu_penalty", 0) or 0)
                                _ep = int(ctr.get("energy_penalty", 0) or 0)
                                S.battle_log_add("{color=#FF8888}Contraataque fallado: -%s Reiatsu base y -%s Energía base. Recibes daño completo.{/color}" % (str(_rp), str(_ep)))

                        if ctr_success:
                            S.extra_offensive_actions = int(getattr(S, "extra_offensive_actions", 0) or 0) + 1
                        elif ctr_ok:
                            fn_apply_key = getattr(S, "bs_apply_damage_to_unit_key", None)
                            if callable(fn_apply_key):
                                fn_apply_key(str(akey), int(pend_amt or 0), source_key=_src_key, reason="combat")
                            else:
                                S.player_hp = max(0, int(getattr(S, "player_hp", 0) or 0) - int(pend_amt or 0))

                        S.deferred_defense_return_to_offense = False
                        S.deferred_defense_actor_key = ""
                    elif msel == "def_from_atk":
                        S.defense_for_attack_active = True
                        S.extra_offensive_actions = 0
                        S.extra_defensive_actions = int(getattr(S, "extra_defensive_actions", 0) or 0) + 1
                        S.deferred_defense_return_to_offense = False
                        S.deferred_defense_actor_key = ""
                        renpy.jump("battle_defensive_turn")
                    else:
                        renpy.jump("battle_defensive_turn")

    # ============================================================
    # Snapshot de recursos al inicio del turno (STORE = real)
    # ============================================================
    $ import renpy.store as S
    $ S.turn_reiatsu_start = getattr(S, "player_reiatsu", 0)
    $ S.offense_cancelled = False
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
        player_name = ""
        slot_idx = 0

        fn_ctx = getattr(S, "bs_get_turn_ctx", None)
        fn_key = getattr(S, "bs_unit_key", None)
        fn_get = getattr(S, "bs_get_unit_by_key", None)

        if callable(fn_ctx):
            ctx = fn_ctx()
            slot_idx = int(ctx.get("owner_slot", 0) or 0)
            if callable(fn_key):
                S.current_actor_unit_key = str(fn_key("player", slot_idx) or "")
            if callable(fn_get):
                u = fn_get(getattr(S, "current_actor_unit_key", ""))
                if isinstance(u, dict):
                    player_name = str(u.get("char_id", "") or "")

        if not player_name:
            _bp = getattr(S, "battle_player", None)
            if isinstance(_bp, dict):
                player_name = str(_bp.get("name", "") or "")
        if not player_name:
            player_name = str(getattr(S, "battle_player_id", "Harribel") or "Harribel")

        S.turn_owner_slot = int(slot_idx or 0)
        S.turn_owner_team = "player"
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
    $ _slot_txt = " ({})".format(S.bs_slot_tag(getattr(S, "turn_owner_team", "player"), int(getattr(S, "turn_owner_slot", 0) or 0)) if callable(getattr(S, "bs_slot_tag", None)) else "S{}".format(int(getattr(S, "turn_owner_slot", 0) or 0) + 1)) if str(getattr(S, "battle_team_mode", "1v1") or "1v1").lower() == "2v2" else ""
    $ battle_log_phase("TURNO OFENSIVO{} – {}".format(_slot_txt, player_name))

    $ bs_ui_show("battle_popup_turn",
                        text="Turno ofensivo{} — {}".format(_slot_txt, player_name),
                        color="#FFD700")
    $ bs_ui_pause(0.6, hard=True)
    $ bs_ui_hide("battle_popup_turn")

    # ============================================================
    # UI selección
    # ============================================================
    $ battle_mode = "offensive"
    $ S.turn_confirmed = False
    $ actions_available = actions
    $ operation_clear()

    show screen battle_command_menu
    show screen technique_selector
    $ bs_ui_restart()

    python:
        import renpy.store as S
        while not getattr(S, "turn_confirmed", False):
            bs_ui_pause(0.1, hard=True)

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

        _mode_now = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        _policy_now = str(getattr(S, "offensive_targeting_policy", "single_target") or "single_target").strip().lower()
        _split_effects_blocked = False
        if _mode_now == "2v2" and _policy_now in ("split_equal", "split_manual"):
            try:
                fn_valid = getattr(S, "bs_get_valid_target_keys", None)
                _targets = list(fn_valid("enemy") or []) if callable(fn_valid) else []
                _split_effects_blocked = (len(_targets) > 1)
            except:
                _split_effects_blocked = True

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

        if _split_effects_blocked:
            # En daño dividido 2v2, todos los efectos especiales se desactivan:
            # - Sin tiradas de dados (directo/negador)
            # - Sin NO ATK
            # - Sin daño directo indefendible
            # - Sin reducción de defensa
            try:
                S.next_defense_reduction = 0.0
            except:
                pass

            if used_direct:
                try:
                    base_d = int(getattr(S, "direct_base_damage", 0) or 0)
                except:
                    base_d = 0
                try:
                    dmg_d = int(getattr(S, "direct_pending_damage", 0) or base_d)
                except:
                    dmg_d = base_d

                try:
                    S.direct_pending_damage = 0
                except:
                    pass

            try:
                _blog("{color=#BBBBBB}Modo dividir daño: efectos especiales desactivados (sin dados/negador/directo/reducción).{/color}")
            except:
                pass

        elif used_direct or used_noatk:
            def _roll_for_action(action_label):
                roll_local = None
                try:
                    fn_roll = getattr(S, "roll_3d", None)
                    if callable(fn_roll):
                        roll_local = fn_roll()
                except:
                    roll_local = None

                if isinstance(roll_local, dict):
                    # log de slots (preferir store-safe)
                    try:
                        fn_slots = getattr(S, "log_dice_slots", None)
                        if not callable(fn_slots):
                            fn_slots = globals().get("log_dice_slots", None)
                        if callable(fn_slots):
                            _blog("{color=#BBBBBB}Tirada — %s{/color}" % str(action_label or "Técnica"))
                            _blog(fn_slots(roll_local.get("rolls", [])))
                    except:
                        pass

                return roll_local

            _dice_actions = []
            for _nm in (selected or []):
                if _nm in ("Ataque Negador", "Ataque Directo") and _nm not in _dice_actions:
                    _dice_actions.append(_nm)

            _dice_panels = []
            for _nm in _dice_actions:
                _roll = _roll_for_action(_nm)
                _ok = bool(isinstance(_roll, dict) and _roll.get("success", False))
                if isinstance(_roll, dict):
                    _dice_panels.append({"label": str(_nm or "Tirada"), "rolls": list(_roll.get("rolls", []) or [])})

                if _nm == "Ataque Directo":
                    S.direct_success = bool(_ok)
                    if _ok:
                        try:
                            _blog("Resultado: Éxito", "#FFD700")
                        except:
                            pass
                    else:
                        try:
                            _blog("Resultado: Fracaso", "#C586C0")
                        except:
                            pass

                if _nm == "Ataque Negador":
                    S.noatk_success = bool(_ok)
                    if _ok:
                        # El target de NO ATK se resuelve al final del turno
                        # (cuando ya existe offensive_target_key/plan estable).
                        try:
                            if callable(fmt_purple) and callable(fmt_gold):
                                _blog(fmt_purple("Ataque Negador → ") + fmt_gold("ÉXITO"))
                            else:
                                _blog("Ataque Negador → ÉXITO", "#C586C0")
                        except:
                            _blog("Ataque Negador → ÉXITO", "#C586C0")
                    else:
                        try:
                            _blog("Ataque Negador → FALLÓ", "#C586C0")
                        except:
                            pass

            # Mostrar tiradas en centro:
            # - 1 técnica => 1 tarjeta centrada.
            # - 2 técnicas => 2 tarjetas lado a lado.
            try:
                fn_show = getattr(S, "show_dice_result", None)
                if callable(fn_show):
                    if len(_dice_panels) >= 2:
                        fn_show(_dice_panels)
                    elif len(_dice_panels) == 1:
                        fn_show({"rolls": list(_dice_panels[0].get("rolls", []) or [])}, label_text=str(_dice_panels[0].get("label", "Tirada") or "Tirada"))
                else:
                    if len(_dice_panels) >= 2:
                        bs_ui_show("dice_roll_result_multi", entries=_dice_panels)
                    elif len(_dice_panels) == 1:
                        bs_ui_show("dice_roll_result", rolls=list(_dice_panels[0].get("rolls", []) or []), label_text=str(_dice_panels[0].get("label", "Tirada") or "Tirada"))
            except:
                pass

            # === ATAQUE DIRECTO FALLADO ===
            # El daño ya está contabilizado como defendible en attack_records
            # desde offensive_actions; aquí solo limpiamos pending legacy.
            if (not getattr(S, "direct_success", False)) and ("Ataque Directo" in getattr(S, "last_selected_actions", [])):
                try:
                    S.direct_pending_damage = 0
                except:
                    pass

            try:
                bs_ui_pause(0.8, hard=True)
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
                    base_i, dmg_i = pair
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

                    # Evitar display_menu en python (puede dejar stack transient abierto en 7.4.x).
                    # Fallback estable: asignación round-robin por paquetes.
                    if not valid_keys:
                        manual_cancelled = True
                        break
                    chosen = valid_keys[i % len(valid_keys)]
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
                        # Intentar respetar preselección externa si existe; sino fallback estable.
                        pre = str(getattr(S, "offensive_selected_target_key", "") or "")
                        if pre in valid_keys:
                            selected_key = pre
                        else:
                            selected_key = valid_keys[0]

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
                    effect_scope = str(getattr(S, "offensive_effect_scope", "primary") or "primary").strip().lower()
                    if effect_scope not in ("primary", "all", "none", "all_if_buff"):
                        effect_scope = "primary"
                    S.offensive_damage_plan = fn_make_plan(
                        source_key=getattr(S, "current_actor_unit_key", None),
                        entries=entries,
                        mode=("split_manual" if manual_completed else policy),
                        skill_id="offensive_turn",
                        effect_scope=effect_scope,
                        meta={"total_expected": total_available, "manual_completed": bool(manual_completed)},
                    )

                try:
                    fn_desc = getattr(S, "bs_describe_unit_key", None)
                    if callable(getattr(S, "battle_log_add", None)):
                        lbls = []
                        for e in entries:
                            tk = str(e.get("target_key", "") or "")
                            if not tk:
                                continue
                            if callable(fn_desc):
                                lbls.append(str(fn_desc(tk, default_side="enemy", default_slot=0) or tk))
                            else:
                                lbls.append(tk)
                        if lbls:
                            S.battle_log_add("{color=#88DDFF}Target asignado: %s{/color}" % (" + ".join(lbls)))
                except:
                    pass

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
