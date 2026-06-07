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
        rolled_direct = 0
        guaranteed_direct = 0
        try:
            if getattr(S, "direct_success", False):
                rolled_direct = max(0, int(getattr(S, "direct_pending_damage", 0) or 0))
        except:
            rolled_direct = 0
        try:
            guaranteed_direct = max(0, int(getattr(S, "direct_guaranteed_pending_damage", 0) or 0))
        except:
            guaranteed_direct = 0

        if (rolled_direct + guaranteed_direct) > 0:

            S.direct_success = False

            direct_damage = int(rolled_direct) + int(guaranteed_direct)
            fn_set_direct = getattr(S, "bs_set_direct_pending", None)
            if callable(fn_set_direct):
                fn_set_direct("enemy", int(direct_damage or 0), mirror_legacy=True)
            else:
                S._last_player_direct_damage = int(direct_damage or 0)
            S.direct_pending_damage = 0
            S.direct_base_damage    = 0
            S.direct_guaranteed_pending_damage = 0
            S.direct_guaranteed_base_damage = 0

            try:
                if callable(fmt_gold) and callable(fmt_red) and callable(battle_fmt_num):
                    _blog(fmt_gold("Daño directo aplicado: ") + fmt_red(battle_fmt_num(direct_damage)))
                else:
                    _blog("Daño directo aplicado: {}".format(direct_damage), "#FFD700")
            except:
                _blog("Daño directo aplicado: {}".format(direct_damage), "#FFD700")

        mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()

        # ====================================================
        # ⭐ DEFENSAS/ENTRADA DE DAÑO ENEMIGO
        # - 1v1: defensa reactiva inmediata (legacy)
        # - 2v2: encolar por target para que cada slot defienda en su turno
        # ====================================================
        if mode != "2v2":
            fn_def = getattr(S, "enemy_compute_reactive_defense", None)
            info = {}
            if callable(fn_def):
                info = fn_def(total_damage)
                try:
                    final_damage = int(info.get("final_damage", total_damage) or 0)
                except:
                    final_damage = int(total_damage or 0)
            else:
                final_damage = int(total_damage or 0)
            try:
                fn_mai = getattr(S, "bs_mai_apply_after_enemy_defense", None)
                if callable(fn_mai):
                    fn_mai(int(total_damage or 0), str(getattr(S, "offensive_target_key", "") or "enemy:0"), info)
            except:
                pass
        else:
            final_damage = int(total_damage or 0)

        try:
            defendible_total = max(0, int(final_damage or 0))
            direct_total = max(0, int(direct_damage or 0))
            dmg_total = defendible_total + direct_total
            enemy_hp_before_visual = max(0, int(getattr(S, "enemy_hp", 0) or 0))
            target_key = str(getattr(S, "offensive_target_key", "") or "")
            plan = getattr(S, "offensive_damage_plan", None)
            effect_targets = []
            try:
                fn_eff_targets = getattr(S, "bs_effect_targets_from_plan", None)
                if callable(fn_eff_targets):
                    effect_targets = list(fn_eff_targets(plan, bool(getattr(S, "buff_allow_split_effects", False))) or [])
            except:
                effect_targets = []
            S.pending_split_effect_targets_enemy = list(effect_targets)

            fn_apply_key = getattr(S, "bs_apply_damage_to_unit_key", None)
            fn_apply = getattr(S, "bs_apply_damage", None)

            alloc = {}
            alloc_direct = {}
            if isinstance(plan, dict):
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
                        alloc_direct[primary] = int(alloc_direct.get(primary, 0) or 0) + int(direct_total)
            elif target_key:
                if defendible_total > 0:
                    alloc[target_key] = int(defendible_total)
                if direct_total > 0:
                    alloc_direct[target_key] = int(direct_total)

            if mode == "2v2":
                pend = getattr(S, "enemy_pending_damage_by_key", None)
                if not isinstance(pend, dict):
                    pend = {}
                for tk, amt in alloc.items():
                    ai = max(0, int(amt or 0))
                    if not tk or ai <= 0:
                        continue
                    pend[tk] = int(pend.get(tk, 0) or 0) + ai
                S.enemy_pending_damage_by_key = pend

                pend_direct = getattr(S, "enemy_pending_direct_damage_by_key", None)
                if not isinstance(pend_direct, dict):
                    pend_direct = {}
                for tk, amt in alloc_direct.items():
                    ai = max(0, int(amt or 0))
                    if not tk or ai <= 0:
                        continue
                    pend_direct[tk] = int(pend_direct.get(tk, 0) or 0) + ai
                S.enemy_pending_direct_damage_by_key = pend_direct
                fn_set_incoming_ctx = getattr(S, "bs_set_incoming_ctx_2v2", None)
                _tkey = str(target_key or (list(alloc.keys())[0] if alloc else ""))
                _src_key = str(getattr(S, "current_actor_unit_key", "") or "")
                if callable(fn_set_incoming_ctx):
                    fn_set_incoming_ctx(target_key=_tkey, source_key=_src_key, owner_team="enemy", owner_slot=int(getattr(S, "turn_owner_slot", 0) or 0), phase="off")
                else:
                    S.incoming_damage_target_key = _tkey
                    S.incoming_damage_source_key = _src_key
                    S.incoming_damage_sources = [_src_key]

                # Debuff de defensa pendiente por target (2v2 deferred)
                deb_map = getattr(S, "enemy_pending_def_reduction_by_key", None)
                if not isinstance(deb_map, dict):
                    deb_map = {}
                try:
                    deb_pct = float(getattr(S, "next_defense_reduction", 0.0) or 0.0)
                except:
                    deb_pct = 0.0
                if deb_pct > 0.0:
                    for tk_eff in (effect_targets or []):
                        if not tk_eff:
                            continue
                        curp = float(deb_map.get(tk_eff, 0.0) or 0.0)
                        deb_map[tk_eff] = min(0.90, curp + deb_pct)
                    S.enemy_pending_def_reduction_by_key = deb_map
                    S.next_defense_reduction = 0.0

                try:
                    if callable(getattr(S, "battle_log_add", None)) and (alloc or alloc_direct):
                        fn_desc = getattr(S, "bs_describe_unit_key", None)
                        parts = []
                        for tk, amt in alloc.items():
                            if callable(fn_desc):
                                parts.append("{}:+{}".format(fn_desc(tk, default_side="enemy", default_slot=0), int(amt or 0)))
                            else:
                                parts.append("{}:+{}".format(tk, int(amt or 0)))
                        for tk, amt in alloc_direct.items():
                            if callable(fn_desc):
                                parts.append("{}:D+{}".format(fn_desc(tk, default_side="enemy", default_slot=0), int(amt or 0)))
                            else:
                                parts.append("{}:D+{}".format(tk, int(amt or 0)))
                        S.battle_log_add("{color=#B39DDB}Daño en cola 2v2 → %s{/color}" % (" | ".join(parts)), group="queue_2v2")
                except:
                    pass

                # Negador en 2v2: cancelar solo al target real del efecto, no al próximo actor global.
                if bool(getattr(S, "noatk_success", False)):
                    try:
                        skip_map = getattr(S, "enemy_skip_attack_by_key", None)
                        if not isinstance(skip_map, dict):
                            skip_map = {}

                        skip_target = str(target_key or "")
                        if (not skip_target) and alloc:
                            skip_target = str(list(alloc.keys())[0] or "")

                        if skip_target:
                            skip_map[skip_target] = True
                            S.enemy_skip_attack_by_key = skip_map
                            S.enemy_skip_attack = False
                    except:
                        pass
            else:
                # 1v1 mantiene semántica global legacy.
                if bool(getattr(S, "noatk_success", False)):
                    S.enemy_skip_attack = True

                merged_apply = {}
                for tk, amt in (alloc or {}).items():
                    ai = max(0, int(amt or 0))
                    if tk and ai > 0:
                        merged_apply[tk] = int(merged_apply.get(tk, 0) or 0) + ai
                for tk, amt in (alloc_direct or {}).items():
                    ai = max(0, int(amt or 0))
                    if tk and ai > 0:
                        merged_apply[tk] = int(merged_apply.get(tk, 0) or 0) + ai

                if merged_apply and callable(fn_apply_key):
                    src = getattr(S, "current_actor_unit_key", None)
                    for tk, amt in merged_apply.items():
                        if int(amt or 0) > 0:
                            fn_apply_key(tk, int(amt), source_key=src, reason="combat")
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

            if mode != "2v2":
                fn_sync = getattr(S, "bs_sync_hp_ui", None)
                if callable(fn_sync):
                    fn_sync()

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
    $ _is_2v2 = str(getattr(store, "battle_team_mode", "1v1") or "1v1").strip().lower() == "2v2"
    if not _is_2v2:
        python:
            import renpy.store as S
            try:
                _enemy_hp_before_visual = int(enemy_hp_before_visual or 0)
            except:
                _enemy_hp_before_visual = int(getattr(S, "enemy_hp", 0) or 0) + int(final_damage or 0) + int(direct_damage or 0)
            try:
                _enemy_hp_after_visual = int(getattr(S, "enemy_hp", 0) or 0)
            except:
                _enemy_hp_after_visual = 0
            _enemy_hp_loss_visual = max(0, int(_enemy_hp_before_visual) - int(_enemy_hp_after_visual))
            if _enemy_hp_loss_visual <= 0:
                _enemy_hp_loss_visual = max(0, int(final_damage or 0) + int(direct_damage or 0))

        if _enemy_hp_loss_visual > 0:
            $ battle_visual_float("enemy", _enemy_hp_loss_visual, "#FF4444", is_final=True)
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
            try:
                fn_desc = getattr(S, "bs_describe_unit_key", None)
                nm = str(fn_desc(nk) if callable(fn_desc) else nk)
                if callable(getattr(S, "battle_log_add", None)):
                    S.battle_log_add("{color=#80DEEA}[DEBUG] TURN_ADVANCE next_actor_id=%s next_name=%s{/color}" % (str(nk), str(nm)))
            except:
                pass
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
