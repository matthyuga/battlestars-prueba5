# ============================================================
# 04D_DEFENSIVE_RESOLVE.rpy – Resolución final del turno
# ============================================================
# Versión v11.4 – Reflect TargetFix + ClearFix + StoreIdentity Sync
# ------------------------------------------------------------
# ✔ Store-safe (S.*) evita desync
# ✔ Limpieza completa de estado defensivo
# ✔ One-shot Potenciar: se limpia al morir (y opcional al finalizar)
# ✔ Reflect robusto (no crashea si reflect no existe)
# ✔ ✅ FIX: Reflect se guarda en el OBJETIVO correcto (atacante/enemigo)
# ✔ ✅ FIX: Usa S.current_actor_id / S.current_enemy_id (store real, no frozen)
# ✔ ✅ FIX: clear() correcto (usa clear_all o clear(id) válido)
# ✔ NEW: aplica daño DIRECTO de IA (no defendible) desde enemy_direct_pending_damage
# ============================================================

label defensive_resolve(received_damage, hp_after, reflected):

    python:
        import renpy.store as S
        received_damage = int(received_damage or 0)
        hp_after = int(hp_after or 0)
        reflected = int(reflected or 0)

        # =========================================================
        # ✅ (NEW) DAÑO DIRECTO DE LA IA (NO DEFENDIBLE)
        # - viene de AI_EXECUTION: S.enemy_direct_pending_damage
        # - se aplica acá porque este label "asienta" el daño real
        # =========================================================
        fn_consume_direct = getattr(S, "bs_consume_direct_pending", None)
        if callable(fn_consume_direct):
            direct_enemy = int(fn_consume_direct("player") or 0)
        else:
            direct_enemy = int(getattr(S, "enemy_direct_pending_damage", 0) or 0)
            if direct_enemy > 0:
                # consumir el pendiente (SIEMPRE, para evitar dobles)
                S.enemy_direct_pending_damage = 0

        if direct_enemy > 0:
            try:
                S.enemy_direct_base_damage = 0
            except:
                pass

            # aplicar directo al HP post-defensa (no defendible)
            hp_after = max(0, int(hp_after) - int(direct_enemy))

            # log + visual (store-safe)
            try:
                fmt_gold = getattr(S, "fmt_gold", None)
                fmt_red  = getattr(S, "fmt_red", None)
                bfn      = getattr(S, "battle_fmt_num", None)

                if callable(fmt_gold) and callable(fmt_red) and callable(bfn):
                    S.battle_log_add(fmt_gold("Daño directo recibido: ") + fmt_red(bfn(direct_enemy)))
                else:
                    S.battle_log_add("Daño directo recibido: {}".format(direct_enemy), "#FFD700")
            except:
                pass

            try:
                S.battle_visual_float("player", direct_enemy, "#FFDD55", is_final=True)
            except:
                pass

        # (importante) reflejo se evalúa con el HP post-directo
        S._def_resolve_hp_after = hp_after


    # --------------------------------------------------------
    # (1) REFLECT — Solo si el jugador sigue vivo
    # --------------------------------------------------------
    if hp_after > 0 and reflected > 0:
        python:
            import renpy.store as S
            try:
                # ✅ store IDs reales (arreglado en 00_GLOBALS_SYSTEM)
                source_id = getattr(S, "current_actor_id", "ID_ACTOR_UNKNOWN")  # quien reflejó (defensor)
                target_id = getattr(S, "current_enemy_id", "ID_ENEMY_UNKNOWN")  # quien recibirá (atacante)

                # ✅ hardening: solo helper público
                fnq = getattr(S, "reflect_queue", None) or globals().get("reflect_queue", None)
                if callable(fnq):
                    fnq(target_id, source_id, int(reflected or 0))
                else:
                    try:
                        S.battle_log_add(
                            "{color=#FFA500}[WARN] reflect_queue no disponible en defensive_resolve; reflect omitido{/color}"
                        )
                    except:
                        pass

            except:
                pass

    # --------------------------------------------------------
    # (2) Aplicar daño REAL al objetivo defendido
    # --------------------------------------------------------
    python:
        import renpy.store as S
        mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        def_key = str(getattr(S, "defense_target_key", "") or getattr(S, "incoming_damage_target_key", "") or "")

        if mode == "2v2" and callable(getattr(S, "bs_parse_unit_key", None)):
            info_def = S.bs_parse_unit_key(def_key, default_side="player", default_slot=0)
            if str(info_def.get("team", "player") or "player") != "player":
                try:
                    ctx = S.bs_get_turn_ctx() if callable(getattr(S, "bs_get_turn_ctx", None)) else {"owner_slot":0}
                    def_key = str(S.bs_unit_key("player", int(ctx.get("owner_slot", 0) or 0)) if callable(getattr(S, "bs_unit_key", None)) else "")
                except:
                    def_key = ""

        if (def_key or mode == "1v1") and callable(getattr(S, "bs_apply_damage_to_unit_key", None)):
            if not def_key:
                try:
                    def_key = str(S.bs_get_active_unit_key("player") if callable(getattr(S, "bs_get_active_unit_key", None)) else "player:0")
                except:
                    def_key = "player:0"

            hp_before_u = int(getattr(S, "defense_hp_before", 0) or 0)
            dmg_apply = max(0, int(received_damage or 0))
            _rr = S.bs_apply_damage_to_unit_key(def_key, dmg_apply, source_key=getattr(S, "current_enemy_unit_key", None), reason="combat_defended_target", tags=["defense"])

            # alinear aliases legacy con la unidad defendida real
            try:
                if callable(getattr(S, "bs_get_unit_by_key", None)):
                    du = S.bs_get_unit_by_key(def_key)
                    if isinstance(du, dict):
                        S.player_hp = int(du.get("hp", getattr(S, "player_hp", 0)) or 0)
            except:
                pass
        else:
            # hp_after ya incluye el directo si existió
            fn_set_hp = getattr(S, "bs_set_hp", None)
            if callable(fn_set_hp):
                fn_set_hp("player", int(hp_after or 0))
            else:
                S.player_hp = int(hp_after or 0)

        fn_sync_hp = getattr(S, "bs_sync_hp_ui", None)
        if callable(fn_sync_hp):
            fn_sync_hp()

    $ player_hp = getattr(S, "player_hp", int(hp_after or 0))
    $ battle_update_hp_bars(player_hp, enemy_hp)

    if received_damage > 0:
        $ battle_visual_float("player", received_damage, "#66CCFF", is_final=True)

    # --------------------------------------------------------
    # (3) Limpieza general del turno defensivo
    # --------------------------------------------------------
    $ battle_reset_used_by_type()

    python:
        import renpy.store as S

        # El daño entrante se consume por completo en el turno defensivo
        S.incoming_damage = 0
        S.incoming_damage_target_key = ""
        S.incoming_damage_source_key = ""
        S.incoming_damage_sources = []
        try:
            incoming_damage = 0
        except:
            pass

        # Sincronizar simulación para próximo turno
        S.simulated_reiatsu = getattr(S, "player_reiatsu", 0)
        S.simulated_energy  = getattr(S, "player_energy", 0)

        # Limpieza de estado defensivo del turno
        S.reduc_val = 0
        S.total_block = 0
        S.blocks_list = []
        S.reflected = 0
        S.awaiting_turn_end = False

        # Limpiar debuffs
        if hasattr(S, "next_defense_reduction"):
            S.next_defense_reduction = 0.0

        # Focus pending (no el “concentrar_activo” persistente)
        if hasattr(S, "focus_pending"):
            S.focus_pending = False

        # pct reflect mostrado en operation
        if hasattr(S, "last_reflect_pct"):
            S.last_reflect_pct = None
        if hasattr(S, "last_reflect_pct_txt"):
            S.last_reflect_pct_txt = None

        # Limpieza interna debug/temporales (si existe)
        if hasattr(S, "_def_resolve_hp_after"):
            try:
                del S._def_resolve_hp_after
            except:
                pass
        if hasattr(S, "defense_hp_before"):
            try:
                del S.defense_hp_before
            except:
                pass
        if hasattr(S, "defense_target_key"):
            try:
                del S.defense_target_key
            except:
                pass

        # Nota: S.def_boost_pending (Potenciar one-shot) se deja tal cual
        # porque puede haber quedado pendiente si el jugador no llegó a ejecutar
        # la defensa objetivo. Si preferís que expire al finalizar el turno, descomenta:
        # S.def_boost_pending = False

    # --------------------------------------------------------
    # (4) Anti-inmortalidad
    # --------------------------------------------------------
    python:
        import renpy.store as S
        _player_defeated = False
        fn_team_def = getattr(S, "bs_is_team_defeated", None)
        if callable(fn_team_def):
            _player_defeated = bool(fn_team_def("player"))
        else:
            _player_defeated = (int(player_hp or 0) <= 0)

    if _player_defeated:

        python:
            import renpy.store as S

            # Reset total de focus y maniobras
            S.concentrar_activo = False
            S.can_focus = True
            S.skip_focus_reset = False
            S.maneuver_selected = "none"
            S.defense_for_attack_active = False

            # Si muere, cualquier potenciar pendiente se pierde
            if hasattr(S, "def_boost_pending"):
                S.def_boost_pending = False

            # ✅ Limpiar reflect acumulado (FIX: antes llamaba clear() sin args)
            try:
                reflect_obj = getattr(S, "reflect", None) or globals().get("reflect", None)
                if reflect_obj:
                    # preferimos clear_all si existe
                    if hasattr(reflect_obj, "clear_all"):
                        reflect_obj.clear_all()
                    else:
                        # fallback: intentar limpiar target + source actuales
                        try:
                            reflect_obj.clear(getattr(S, "current_actor_id", "player"))
                        except:
                            pass
                        try:
                            reflect_obj.clear(getattr(S, "current_enemy_id", "enemy"))
                        except:
                            pass
            except:
                pass

            if hasattr(S, "next_defense_reduction"):
                S.next_defense_reduction = 0.0

        $ battle_log_add("{color=#FF4444}Derrota{/color}")
        jump battle_end

    # --------------------------------------------------------
    # (5) Decidir el próximo turno
    # --------------------------------------------------------
    python:
        import renpy.store as S

        _mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        if getattr(S, "defense_for_attack_active", False):
            S.defense_for_attack_active = False
            next_turn = "enemy"
        elif bool(getattr(S, "deferred_defense_return_to_offense", False)):
            next_turn = "player_same_actor"
        elif _mode == "2v2" and callable(getattr(S, "bs_turn_advance", None)) and callable(getattr(S, "bs_parse_unit_key", None)):
            nk = str(S.bs_turn_advance(mirror_legacy=True) or "")
            next_turn = str(S.bs_parse_unit_key(nk, default_side="player", default_slot=0).get("team", "player") or "player")
        else:
            next_turn = "player"

        enemy_name = str(getattr(getattr(S, "enemy_ai", None), "name", getattr(S, "battle_enemy_id", "Enemigo")) or "Enemigo")
        _bp = getattr(S, "battle_player", None)
        if isinstance(_bp, dict):
            player_name = str(_bp.get("name", "") or "")
        else:
            player_name = ""
        if not player_name:
            player_name = str(getattr(S, "battle_player_id", "Harribel") or "Harribel")

    # --------------------------------------------------------
    # (6) Saltar al turno que corresponda
    # --------------------------------------------------------
    if next_turn == "enemy":
        $ battle_turn_change("enemy")
        $ battle_popup_turn("Turno ofensivo — {}".format(enemy_name), "#FFD700", delay=0.7)
        jump battle_enemy_turn

    elif next_turn == "player_same_actor":
        python:
            import renpy.store as S
            S.deferred_defense_return_to_offense = False
            S.deferred_defense_actor_key = ""
        $ battle_turn_change("player")
        $ battle_popup_turn("Turno ofensivo — {}".format(player_name), "#FFD700", delay=0.7)
        jump battle_offensive_turn

    else:
        python:
            import renpy.store as S
            S.deferred_defense_return_to_offense = False
            S.deferred_defense_actor_key = ""
        $ battle_turn_change("player")
        $ battle_popup_turn("Turno ofensivo — {}".format(player_name), "#FFD700", delay=0.7)
        jump battle_offensive_turn
