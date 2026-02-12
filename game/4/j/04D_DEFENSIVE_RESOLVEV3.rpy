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
        direct_enemy = int(getattr(S, "enemy_direct_pending_damage", 0) or 0)
        if direct_enemy > 0:
            # consumir el pendiente (SIEMPRE, para evitar dobles)
            S.enemy_direct_pending_damage = 0
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

                reflect_obj = getattr(S, "reflect", None) or globals().get("reflect", None)
                if reflect_obj:
                    # Compatibilidad:
                    # - Si ReflectManager nuevo acepta source_id, lo usamos.
                    # - Si es legacy (solo add(actor, value)), cae sin source.
                    try:
                        reflect_obj.add(target_id, reflected, source_id=source_id)
                    except TypeError:
                        reflect_obj.add(target_id, reflected)

            except:
                pass

    # --------------------------------------------------------
    # (2) Aplicar daño REAL al jugador
    # --------------------------------------------------------
    python:
        import renpy.store as S
        # hp_after ya incluye el directo si existió
        S.player_hp = int(hp_after or 0)

    $ player_hp = hp_after
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

        # Limpieza interna debug (si existe)
        if hasattr(S, "_def_resolve_hp_after"):
            try:
                del S._def_resolve_hp_after
            except:
                pass

        # Nota: S.def_boost_pending (Potenciar one-shot) se deja tal cual
        # porque puede haber quedado pendiente si el jugador no llegó a ejecutar
        # la defensa objetivo. Si preferís que expire al finalizar el turno, descomenta:
        # S.def_boost_pending = False

    # --------------------------------------------------------
    # (4) Anti-inmortalidad
    # --------------------------------------------------------
    if player_hp <= 0:

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

        if getattr(S, "defense_for_attack_active", False):
            S.defense_for_attack_active = False
            next_turn = "enemy"
            enemy_name = S.enemy_ai.name
        else:
            next_turn = "player"
            player_name = "Harribel"

    # --------------------------------------------------------
    # (6) Saltar al turno que corresponda
    # --------------------------------------------------------
    if next_turn == "enemy":
        $ battle_turn_change("enemy")
        $ battle_popup_turn("Turno ofensivo — {}".format(enemy_name), "#FFD700", delay=0.7)
        jump battle_enemy_turn

    else:
        $ battle_turn_change("player")
        $ battle_popup_turn("Turno ofensivo — {}".format(player_name), "#FFD700", delay=0.7)
        jump battle_offensive_turn
