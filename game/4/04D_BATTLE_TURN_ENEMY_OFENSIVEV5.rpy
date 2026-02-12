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

    # ============================================================
    # ⭐ ATAQUE NEGADOR — cancelar turno ofensivo IA
    # ============================================================
    python:
        if getattr(S, "enemy_skip_attack", False):

            S.enemy_skip_attack = False

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
                S.battle_popup_turn("Turno ofensivo — Harribel", "#FFD700", 0.7)
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

        # --------------------------------------------------------
        # ⭐ REFLECT PENDIENTE CONTRA IA (target = IA)
        # --------------------------------------------------------
        reflected_self = 0
        ref_source = None

        try:
            rman = getattr(S, "reflect", None)
            if rman:
                reflected_self, ref_source = rman.consume_info(S.current_enemy_id)
            else:
                reflected_self = int(reflect.consume(S.current_enemy_id) or 0)
        except:
            reflected_self = 0
            ref_source = None

        try:
            reflected_self = int(reflected_self or 0)
        except:
            reflected_self = 0

        if reflected_self < 0:
            reflected_self = 0

        if reflected_self > 0:
            # aplicar daño REAL a la IA
            try:
                S.enemy_hp = max(0, int(getattr(S, "enemy_hp", 0) or 0) - reflected_self)
            except:
                pass

            # sync HP bars
            try:
                battle_update_hp_bars(getattr(S, "player_hp", 0), getattr(S, "enemy_hp", 0))
            except:
                pass

            # log
            try:
                src_txt = (" (fuente: %s)" % ref_source) if ref_source else ""
                S.battle_log_add(
                    "{color=#00FFFF}%s recibe %s de reflect%s{/color}" %
                    (enemy_name, S.battle_fmt_num(reflected_self), src_txt)
                )
            except:
                pass

            # visual
            try:
                battle_visual_float("enemy", reflected_self, "#00FFFF", is_final=True)
                renpy.pause(0.25, hard=True)
            except:
                pass

            # si murió por reflect → terminar combate (SIN "$" aquí)
            if int(getattr(S, "enemy_hp", 0) or 0) <= 0:
                try:
                    fmt_gold = getattr(S, "fmt_gold", globals().get("fmt_gold", None))
                    if callable(fmt_gold):
                        S.battle_log_add(fmt_gold(u"¡Victoria!"))
                    else:
                        S.battle_log_add(u"¡Victoria!", "#FFD700")
                except:
                    pass
                renpy.jump("battle_end")

        # ============================================================
        # ⭐ LOOP REAL DE EJECUCIÓN IA
        # ============================================================
        while enemy_ai.current_plan:
            ai_execute_offensive_action(enemy_ai)
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

        total_damage = int(S.incoming_damage or 0)

        try:
            S.battle_log_add(
                S.log_operation(
                    formula_text,
                    0,          # reflect ya aplicado al HP
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
        dmg_directo    = int(S.incoming_direct_damage or 0)

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

        $ player_hp = max(0, player_hp - incoming_damage)
        $ battle_update_hp_bars(player_hp, enemy_hp)

        $ extra_offensive_actions += 1
        $ enemy_ai.reset_turn()

        $ battle_turn_change("player")
        $ battle_popup_turn("Turno ofensivo — Harribel", "#FFD700", delay=0.7)
        jump battle_offensive_turn

    # ============================================================
    # ⭐ DEFENSA POR ATAQUE
    # ============================================================
    if maneuver_selected == "def_from_atk":

        python:
            import renpy.store as S
            S.defense_for_attack_active = True

        $ extra_offensive_actions = 0
        $ extra_defensive_actions += 1
        $ enemy_ai.reset_turn()

        $ battle_turn_change("player")
        $ battle_popup_turn("Turno defensivo — Harribel", "#00BFFF", delay=0.6)
        jump battle_defensive_turn

    # ============================================================
    # ⭐ DEFENSA NORMAL
    # ============================================================
    $ enemy_ai.reset_turn()
    $ battle_turn_change("player")
    $ battle_popup_turn("Turno defensivo — Harribel", "#00BFFF", delay=0.8)
    call battle_defensive_turn

    return
