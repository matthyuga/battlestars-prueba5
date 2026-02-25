# ============================================================
# 04D_DEFENSIVE_CORE.rpy – Turno defensivo del jugador (Núcleo)
# Versión v9.3 – StoreSafe + OneShotBoost Sync
# ------------------------------------------------------------
# - Todo el estado del turno vive en renpy.store (S.*)
# - Compatible con 04D_DEFENSIVE_ACTIONS v14 (def_boost_pending one-shot)
# - HUD limpio y colas limpias
# ============================================================

label battle_defensive_turn:

    # ========================================================
    # 🧹 LIMPIEZA INICIAL DE HUD / SIMULACIONES
    # ========================================================
    python:
        import renpy.store as S

        # Reset simulación del jugador
        S.simulated_reiatsu = getattr(S, "player_reiatsu", 0)
        S.simulated_energy  = getattr(S, "player_energy", 0)

        # Reset simulación del enemigo
        S.enemy_simulated_reiatsu = getattr(S, "enemy_reiatsu", 0)
        S.enemy_simulated_energy  = getattr(S, "enemy_energy", 0)

        # En turno defensivo nunca debe haber técnicas ofensivas en espera
        if hasattr(S, "pending_tech_list"):
            S.pending_tech_list = []

        # Cola de acciones del jugador limpia
        if not hasattr(S, "player_action_queue"):
            S.player_action_queue = []
        else:
            S.player_action_queue[:] = []

        # Reset de summary_lines para esta operación defensiva
        S.summary_lines = []

        # Defaults de estado defensivo (store-safe)
        S.reduc_val = 0
        S.total_block = 0
        S.blocks_list = []
        S.reflected = 0
        S.awaiting_turn_end = False

        # Si no existe, crear flag one-shot de potenciar
        if not hasattr(S, "def_boost_pending"):
            S.def_boost_pending = False

    # ========================================================
    # 🔥 FIX ABSOLUTO — Si NO hay daño real, NO hay turno def.
    # ========================================================
    python:
        import renpy.store as S
        inc = int(getattr(S, "incoming_damage", 0) or 0)
        no_damage = (inc <= 0)

    if no_damage:

        $ incoming_damage = 0
        $ battle_reset_used_by_type()

        # ⭐⭐⭐ FIX FOCUS-PRESERVE ⭐⭐⭐
        if not skip_focus_reset:
            $ reset_concentrar("defensive")
            $ concentrar_activo = False
            $ can_focus = True

        # (opcional) si querés que Potenciar se pierda cuando no hubo defensa:
        # python:
        #     import renpy.store as S
        #     S.def_boost_pending = False

        python:
            import renpy.store as S
            _bp = getattr(S, "battle_player", None)
            if isinstance(_bp, dict):
                player_name = str(_bp.get("name", "") or "")
            else:
                player_name = ""
            if not player_name:
                player_name = str(getattr(S, "battle_player_id", "Harribel") or "Harribel")
        $ battle_turn_change("player")
        $ battle_popup_turn("Turno ofensivo — {}".format(player_name), "#FFD700", delay=0.7)
        jump battle_offensive_turn

    # ========================================================
    # 🔥 A partir de aquí: SIEMPRE hay daño real que defender
    # ========================================================
    scene black
    with fade

    # --- Daño entrante ---
    python:
        import renpy.store as S
        base_damage = int(getattr(S, "incoming_damage", 0) or 0)

        # M6 MVP 2v2:
        # - El defensor protege la unidad objetivo principal.
        # - Si hay split, solo el entry del target defendido se procesa en este turno;
        #   los demás entries se aplican por target (passthrough sin cover avanzado).
        mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        S.defense_target_key = str(getattr(S, "current_actor_unit_key", "") or "")

        if mode == "2v2":
            plan = getattr(S, "enemy_damage_plan", None)
            fn_ctx = getattr(S, "bs_get_turn_ctx", None)
            fn_key = getattr(S, "bs_unit_key", None)
            fn_parse = getattr(S, "bs_parse_unit_key", None)
            fn_apply_key = getattr(S, "bs_apply_damage_to_unit_key", None)

            if callable(fn_ctx) and callable(fn_key):
                ctx = fn_ctx()
                S.defense_target_key = str(fn_key("player", int(ctx.get("owner_slot", 0) or 0)) or "")

            if isinstance(plan, dict):
                entries = list(plan.get("entries", []) or [])
                defend_amount = 0
                passthrough = []
                first_key = ""

                for e in entries:
                    if not isinstance(e, dict):
                        continue
                    tkey = str(e.get("target_key", "") or "")
                    amt = max(0, int(e.get("amount", 0) or 0))
                    if not tkey or amt <= 0:
                        continue
                    if not first_key:
                        first_key = tkey
                    if tkey == S.defense_target_key:
                        defend_amount += amt
                    else:
                        passthrough.append((tkey, amt))

                if defend_amount <= 0 and first_key:
                    # fallback: defender el principal del plan
                    if callable(fn_parse):
                        info = fn_parse(first_key, default_side="player", default_slot=0)
                        if str(info.get("team", "player") or "player") == "player":
                            S.defense_target_key = first_key
                    defend_amount = sum([a for (k, a) in [(str(e.get("target_key", "") or ""), max(0, int(e.get("amount", 0) or 0))) for e in entries if isinstance(e, dict)] if k == S.defense_target_key])

                # Aplicar split no defendido por target
                if callable(fn_apply_key):
                    for tkey, amt in passthrough:
                        try:
                            fn_apply_key(tkey, amt, source_key=getattr(S, "current_enemy_unit_key", None), reason="combat_split_passthrough", tags=["split", "passthrough"])
                        except:
                            pass

                if defend_amount > 0:
                    base_damage = int(defend_amount)
                    S.incoming_damage = int(defend_amount)

    # --- Variables del turno (store) ---
    python:
        import renpy.store as S
        S.reduc_val = 0
        S.total_block = 0
        S.blocks_list = []
        S.reflected = 0
        S.awaiting_turn_end = False
        S.focus_activated = False

        # sincronizar simulación → estado real
        S.simulated_reiatsu = S.player_reiatsu
        S.simulated_energy  = S.player_energy

    # ========================================================
    # ⭐ FOCUS DEFENSIVO – preservación correcta
    # ========================================================
    python:
        import renpy.store as S

        # Si Concentrar/Potenciar NO estaba activo → reset normal
        if not getattr(S, "concentrar_activo", False):
            reset_concentrar("defensive")
            S.can_focus = can_use_concentrar("defensive")
        else:
            S.can_focus = False

        S.focus_pending = False

    # ========================================================
    # 🔥 FIX ANTI-INMORTALIDAD DESDE EL CORE
    # ========================================================
    python:
        import renpy.store as S
        S.will_die_from_damage = (S.player_hp - base_damage <= 0)
        S.player_is_dead       = (S.player_hp <= 0)

    # --- Encabezado visual ---
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

    $ _slot_txt = " (S{})".format(int(getattr(S, "turn_owner_slot", 0) or 0) + 1) if str(getattr(S, "battle_team_mode", "1v1") or "1v1").lower() == "2v2" else ""
    $ operation_clear()
    $ battle_log_phase("TURNO DEFENSIVO{} – {}".format(_slot_txt, player_name))
    $ battle_popup_turn("Turno defensivo{} — {}".format(_slot_txt, player_name), "#00BFFF", delay=0.6)

    # ========================================================
    # ⭐ UI DEFENSIVA (Selector Moderno)
    # ========================================================
    $ battle_mode = "defensive"
    $ turn_confirmed = False

    $ actions_available       = 1 + extra_defensive_actions
    $ extra_defensive_actions = 0
    $ actions_available_start = actions_available

    show screen battle_command_menu
    show screen technique_selector
    $ renpy.restart_interaction()

    python:
        import renpy.store as S
        while True:
            if getattr(S, "turn_confirmed", False):
                break
            renpy.pause(0.1, hard=True)

    hide screen battle_command_menu
    hide screen technique_selector

    # --- Técnicas seleccionadas ---
    python:
        import renpy.store as S
        selected = list(getattr(S, "player_action_queue", []))
        S.player_action_queue[:] = []

    # ========================================================
    # 🔹 MÓDULO 1 — Procesamiento de técnicas defensivas
    # (Actions escribe resultados en S.reduc_val / S.blocks_list / S.reflected)
    # ========================================================
    call defensive_process_actions(selected, base_damage)

    # ========================================================
    # 🔹 MÓDULO 2 — Matemática + logs (Operation)
    # Pasamos desde store para evitar desync
    # ========================================================
    call defensive_operation(base_damage, S.reduc_val, S.blocks_list, S.reflected)
    # devuelve: received_damage, hp_after

    # ========================================================
    # 🔹 MÓDULO 3 — Resolución final
    # ========================================================
    call defensive_resolve(received_damage, hp_after, S.reflected)

    return
