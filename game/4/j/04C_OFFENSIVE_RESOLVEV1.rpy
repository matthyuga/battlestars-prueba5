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
            dmg_total = max(0, int(final_damage or 0)) + max(0, int(direct_damage or 0))
            fn_apply = getattr(S, "bs_apply_damage", None)
            if callable(fn_apply):
                fn_apply("enemy", dmg_total, source="player", reason="combat")
            else:
                cur_hp = int(getattr(S, "enemy_hp", 0) or 0)
                cur_hp = max(0, cur_hp - dmg_total)
                S.enemy_hp = cur_hp

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
