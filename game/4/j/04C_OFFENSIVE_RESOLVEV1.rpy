# ============================================================
# RESOLUTOR – Separa daño defendible & directo
# ============================================================

label battle_offensive_resolve_enemy:

    python:
        import renpy.store as S

        enemy_name = getattr(getattr(S, "enemy_ai", None), "name", "Enemigo")
        global direct_damage, final_damage
        direct_damage = 0
        fn_set_direct = getattr(S, "bs_set_direct_pending", None)
        if callable(fn_set_direct):
            fn_set_direct("enemy", 0, mirror_legacy=True)
        else:
            S._last_player_direct_damage = 0

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
            fn_set_direct = getattr(S, "bs_set_direct_pending", None)
            if callable(fn_set_direct):
                fn_set_direct("enemy", int(direct_damage or 0), mirror_legacy=True)
            else:
                S._last_player_direct_damage = int(direct_damage or 0)
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
            defendible_total = max(0, int(final_damage or 0))
            direct_total = max(0, int(direct_damage or 0))
            dmg_total = defendible_total + direct_total
            target_key = str(getattr(S, "offensive_target_key", "") or "")
            plan = getattr(S, "offensive_damage_plan", None)

            fn_apply_key = getattr(S, "bs_apply_damage_to_unit_key", None)
            fn_apply = getattr(S, "bs_apply_damage", None)

            if isinstance(plan, dict) and callable(fn_apply_key):
                # IMPORTANTE: reescalar plan al daño defendible real para evitar desync
                # (ej: log muestra 300 tras defensa, pero plan original tenía 400).
                entries = list(plan.get("entries", []) or [])
                base_entries = []
                original_total = 0
                for e in entries:
                    if not isinstance(e, dict):
                        continue
                    tk = str(e.get("target_key", "") or "")
                    amt = max(0, int(e.get("amount", 0) or 0))
                    if not tk or amt <= 0:
                        continue
                    base_entries.append((tk, amt))
                    original_total += amt

                alloc = {}
                if base_entries and original_total > 0 and defendible_total > 0:
                    rem = int(defendible_total)
                    for idx, pair in enumerate(base_entries):
                        tk, amt = pair
                        if idx == len(base_entries) - 1:
                            take = rem
                        else:
                            take = int((int(amt) * int(defendible_total)) // int(original_total))
                            if take > rem:
                                take = rem
                        rem -= max(0, int(take or 0))
                        if take > 0:
                            alloc[tk] = int(alloc.get(tk, 0) or 0) + int(take)

                if direct_total > 0:
                    primary = target_key
                    if (not primary) and base_entries:
                        primary = str(base_entries[0][0] or "")
                    if primary:
                        alloc[primary] = int(alloc.get(primary, 0) or 0) + int(direct_total)

                if alloc:
                    src = getattr(S, "current_actor_unit_key", None)
                    for tk, amt in alloc.items():
                        if int(amt or 0) > 0:
                            fn_apply_key(tk, int(amt), source_key=src, reason="combat")
                elif target_key:
                    fn_apply_key(target_key, dmg_total, source_key=getattr(S, "current_actor_unit_key", None), reason="combat")
            elif target_key and callable(fn_apply_key):
                fn_apply_key(target_key, dmg_total, source_key=getattr(S, "current_actor_unit_key", None), reason="combat")
            elif callable(fn_apply):
                fn_apply("enemy", dmg_total, source="player", reason="combat")
            else:
                fn_set = getattr(S, "bs_set_hp", None)
                cur_hp = int(getattr(S, "enemy_hp", 0) or 0)
                cur_hp = max(0, cur_hp - dmg_total)
                if callable(fn_set):
                    fn_set("enemy", cur_hp)
                else:
                    S.enemy_hp = cur_hp

            # limpiar selección/plan del turno
            try:
                S.offensive_damage_plan = None
                S.offensive_target_key = ""
            except:
                pass

            fn_sync = getattr(S, "bs_sync_hp_ui", None)
            if callable(fn_sync):
                fn_sync()

            # Refuerzo visual inmediato (evita redraw diferido)
            try:
                fn_bars = getattr(S, "battle_update_hp_bars", None)
                if callable(fn_bars):
                    fn_bars(getattr(S, "player_hp", 0), getattr(S, "enemy_hp", 0))
            except:
                pass
        except:
            pass

    # ============================================================
    # VISUALES
    # ============================================================
    if direct_damage > 0:
        $ battle_visual_float("enemy", direct_damage, "#FFDD55", is_final=True)
        $ renpy.pause(0.3, hard=True)

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
    python:
        import renpy.store as S
        _enemy_defeated = False
        fn_team_def = getattr(S, "bs_is_team_defeated", None)
        if callable(fn_team_def):
            _enemy_defeated = bool(fn_team_def("enemy"))
        else:
            _enemy_defeated = (int(getattr(S, "enemy_hp", 0) or 0) <= 0)

    if _enemy_defeated:
        $ battle_log_add(fmt_gold("¡Victoria!"))
        jump battle_end

    python:
        import renpy.store as S
        _mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        _next_team = "enemy"
        if _mode == "2v2" and callable(getattr(S, "bs_turn_advance", None)) and callable(getattr(S, "bs_parse_unit_key", None)):
            nk = str(S.bs_turn_advance(mirror_legacy=True) or "")
            _next_team = str(S.bs_parse_unit_key(nk, default_side="enemy", default_slot=0).get("team", "enemy") or "enemy")
        else:
            _fn_turn = getattr(S, "battle_turn_change", None)
            if callable(_fn_turn):
                _fn_turn("enemy")
            _next_team = "enemy"

    if _next_team == "enemy":
        $ battle_turn_change("enemy")
        $ renpy.show_screen("battle_popup_turn", text="Turno ofensivo — {}".format(enemy_name), color="#FFD700")
        $ renpy.pause(0.7, hard=True)
        $ renpy.hide_screen("battle_popup_turn")
        jump battle_enemy_turn
    else:
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
        $ renpy.show_screen("battle_popup_turn", text="Turno ofensivo — {}".format(_pname), color="#FFD700")
        $ renpy.pause(0.7, hard=True)
        $ renpy.hide_screen("battle_popup_turn")
        jump battle_offensive_turn
