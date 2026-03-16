# ===========================================================
# 04B_BATTLE_START.RPY – Inicio y preparación del combate
# ===========================================================
# Versión: v5.2 Resource+Identity+ID Selection + Safe Resets (Ren’Py 7.4.9)
# -----------------------------------------------------------
# - Inicializa Reiatsu/Energía del jugador y enemigo
# - Carga fichas desde CHARACTER_DATA (get_character)
# - Selección de enemigo por ID (battle_enemy_id)
# - Identidad dinámica (usa IDs del sistema)
# - Limpieza total de reflejos (store-safe)
# - Resets: focus/boost/costos/logs/operación/tech sequence
# - Sync: battle_turn_owner
# ===========================================================

# ===========================================================
# 🔹 Declaración de fondos de batalla
# ===========================================================
image black    = "images/black.png"
image black2   = "images/black2.png"
image fondo3   = "images/fondo3.png"
image hollow1  = "images/hollow1.png"
image hollow12 = "images/hollow12.png"

# ===========================================================
# 🔹 Desactivar rollback, skip y rueda del ratón
# ===========================================================
init -900 python:
    config.keymap['rollback'] = []
    config.keymap['hide_windows'] = []
    config.keymap['skip'] = []
    config.keymap['fast_skip'] = []
    config.keymap['stop_skipping'] = []
    config.keymap['toggle_skip'] = []
    config.keymap['toggle_afm'] = []

    config.rollback_enabled = False
    config.hard_rollback_limit = 0

# ===========================================================
# 🔹 Defaults
# ===========================================================
# battle_enemy_id / battle_player_id y modo 2v2 se definen en
# 04A_BATTLE_CHARACTER_SELECTV3.rpy para evitar defaults duplicados.
# (Opcional, recomendado si no los tenés como default en otro lado)
# default battle_player = None
# default battle_enemy  = None

# ===========================================================
# 🔹 INICIO DEL JUEGO
# ===========================================================
label start:
    scene fondo3 with fade

    # Mostrar log UNA sola vez (evita redundancia/“parpadeo”)
    show screen battle_log_screen

    "Sistema cargado correctamente."

    if not ui_safe_mode_prompted:
        menu:
            "¿Activar modo seguro del HUD?"
            "Sí (panel simple sin PNG)":
                $ ui_safe_mode = True
            "No (HUD visual con PNG)":
                $ ui_safe_mode = False
        $ ui_safe_mode_prompted = True

    call battle_select_player


# ===========================================================
# 🔹 INICIO DEL COMBATE
# ===========================================================
label battle_start:
    $ import random
    $ import renpy.store as S

    # =======================================================
    # 🎯 Selección del enemigo (ID del sistema)
    # =======================================================
    $ enemy_id = getattr(S, "battle_enemy_id", "Hollow")
    $ player_id = getattr(S, "battle_player_id", "Harribel")
    $ battle_team_mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()

    # Normalización: el sistema usa "Nel" (Neliel solo display)
    if enemy_id == "Neliel":
        $ enemy_id = "Nel"
        $ S.battle_enemy_id = "Nel"

    # Mantener coherencia con tu core (si existe como default)
    $ battle_reflected_pending = 0

    # -------------------------------------------------------
    # 🧹 Limpieza segura de reflejos previos (STORE-SAFE)
    # -------------------------------------------------------
    if hasattr(S, "reflected_buffer") and hasattr(S.reflected_buffer, "clear"):
        $ S.reflected_buffer.clear()

    if hasattr(S, "enemy_reflect_buffer") and hasattr(S.enemy_reflect_buffer, "clear"):
        $ S.enemy_reflect_buffer.clear()

    # -------------------------------------------------------
    # 🧼 Resets de estado temporal (FOCUS/BOOST/COSTOS/SECUENCIA/OPERACIÓN)
    # -------------------------------------------------------
    # Reseteo oficial de focus/boost + focus_cost_active
    if hasattr(S, "reset_focus_multipliers"):
        $ S.reset_focus_multipliers()

    # Por compatibilidad extra: nunca entrar a combate con costo duplicado
    if hasattr(S, "focus_cost_active"):
        $ S.focus_cost_active = False

    # Reset secuencia de técnicas del turno (si existe)
    if hasattr(S, "battle_reset_tech_sequence"):
        $ S.battle_reset_tech_sequence()
    elif hasattr(S, "battle_turn_tech_sequence"):
        $ S.battle_turn_tech_sequence = []

    # Reset de operación final (si existe)
    if hasattr(S, "operation_clear"):
        $ S.operation_clear()

    # Limpieza de resumen del turno (si existe)
    if hasattr(S, "battle_clear_turn_summary"):
        $ S.battle_clear_turn_summary()

    # Log
    $ battle_log_clear()
    $ battle_log_phase("COMIENZA EL COMBATE")

    # Contador de turnos ofensivos (global por combate)
    $ S.battle_turn_index = 0
    $ S._last_turn_actor_key = ""
    $ S.enemy_pending_damage_by_key = {}
    $ S.player_pending_damage_by_key = {}
    $ S.enemy_pending_def_reduction_by_key = {}
    $ S.player_skip_attack_by_key = {}
    $ S.enemy_skip_attack_by_key = {}
    $ S.counterattack_used_in_battle = False
    $ S.sacrifice_used_in_battle = False
    $ S.sacrifice_receiver_key = ""
    $ S.counterattack_resolution_mode = ("typing" if bool(getattr(S, "counterattack_typing_enabled", False)) else "dice")
    python:
        import renpy.store as S
        fn_ctr_typing_reset = getattr(S, "bs_counterattack_typing_reset_state", None)
        if callable(fn_ctr_typing_reset):
            fn_ctr_typing_reset()
        else:
            S.counterattack_typing_state = {
                "active": False,
                "sequence": [],
                "total": 0,
                "index": 0,
                "current_letter": "",
                "seconds_per_letter": float(getattr(S, "counterattack_typing_seconds_per_letter", 2.0) or 2.0),
                "time_left": 0.0,
                "last_status": "idle",
                "result": None,
                "pending_next_index": None,
                "feedback_time_left": 0.0,
                "close_in": 0.0,
            }

    # =======================================================
    # 🌆 Fondo de batalla aleatorio
    # =======================================================
    $ fondo_random = renpy.random.choice(["black", "black2", "fondo3", "hollow1", "hollow12"])
    scene expression fondo_random

    # =======================================================
    # 👤 Cargar fichas desde CHARACTER_DATA
    # =======================================================
    # IMPORTANTE: get_character debe devolver COPIA (dict) para no contaminar plantillas.
    $ battle_player = get_character(player_id)
    $ battle_enemy  = get_character(enemy_id)

    # Nombre visible (solo UI/logs)
    $ enemy_name = battle_enemy.get("name", enemy_id)
    $ player_name = battle_player.get("name", player_id)

    # =======================================================
    # ⚙️ Variables base (HP inicial) desde CHARACTER_DATA + editor de slots
    # =======================================================
    $ player_hp = get_character_hp(player_id)
    $ enemy_hp  = get_character_hp(enemy_id)

    python:
        import renpy.store as S
        fn_pool = getattr(S, "spa_get_pool_final", None)
        if callable(fn_pool):
            player_hp = int(fn_pool("player:0", "hp", player_hp) or player_hp)
            enemy_hp = int(fn_pool("enemy:0", "hp", enemy_hp) or enemy_hp)

        try:
            battle_player["HP"] = int(player_hp)
            battle_enemy["HP"] = int(enemy_hp)
        except:
            pass

    # Sincronizar máximos globales para HUD, FX y overlays
    $ battle_hp_player_max = player_hp
    $ battle_hp_enemy_max  = enemy_hp
    $ battle_hp_player = player_hp
    $ battle_hp_enemy  = enemy_hp

    # Modelo de equipos/unidades (1v1 compat / 2v2 real)
    python:
        import renpy.store as S
        mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()

        if mode == "2v2" and callable(getattr(S, "bs_init_teams", None)):
            p_ids = list(getattr(S, "battle_player_ids", []) or [])
            e_ids = list(getattr(S, "battle_enemy_ids", []) or [])
            if len(p_ids) < 1:
                p_ids = [str(getattr(S, "battle_player_slot_0", player_id) or player_id)]
            if len(e_ids) < 1:
                e_ids = [str(getattr(S, "battle_enemy_slot_0", enemy_id) or enemy_id)]

            p_units = []
            e_units = []
            fn_pool = getattr(S, "spa_get_pool_final", None)
            for idx, cid in enumerate(p_ids[:2]):
                hp = get_character_hp(cid)
                rei = int(get_character(cid).get("Reiatsu", 0) or 0)
                ene = int(get_character(cid).get("Energy", 0) or 0)
                if callable(fn_pool):
                    ukey = "player:{}".format(idx)
                    hp = int(fn_pool(ukey, "hp", hp) or hp)
                    rei = int(fn_pool(ukey, "reiatsu", rei) or rei)
                    ene = int(fn_pool(ukey, "energy", ene) or ene)
                p_units.append({"char_id": cid, "hp": hp, "max_hp": hp, "reiatsu": rei, "energy": ene, "max_reiatsu": rei, "max_energy": ene, "base_reiatsu": rei, "base_energy": ene})
            for idx, cid in enumerate(e_ids[:2]):
                hp = get_character_hp(cid)
                rei = int(get_character(cid).get("Reiatsu", 0) or 0)
                ene = int(get_character(cid).get("Energy", 0) or 0)
                if callable(fn_pool):
                    ukey = "enemy:{}".format(idx)
                    hp = int(fn_pool(ukey, "hp", hp) or hp)
                    rei = int(fn_pool(ukey, "reiatsu", rei) or rei)
                    ene = int(fn_pool(ukey, "energy", ene) or ene)
                e_units.append({"char_id": cid, "hp": hp, "max_hp": hp, "reiatsu": rei, "energy": ene, "max_reiatsu": rei, "max_energy": ene, "base_reiatsu": rei, "base_energy": ene})

            S.bs_init_teams(player_units=p_units, enemy_units=e_units)

            # compat legacy/UI usa unidad activa por lado
            fn_sync = getattr(S, "bs_sync_to_legacy", None)
            if callable(fn_sync):
                fn_sync()

            p_active = getattr(S, "bs_get_active_unit", lambda x: None)("player")
            e_active = getattr(S, "bs_get_active_unit", lambda x: None)("enemy")
            if isinstance(p_active, dict):
                S.battle_player_id = str(p_active.get("char_id", player_id) or player_id)
            if isinstance(e_active, dict):
                S.battle_enemy_id = str(e_active.get("char_id", enemy_id) or enemy_id)
        else:
            fn_init_teams = getattr(S, "bs_init_single_teams", None)
            if callable(fn_init_teams):
                fn_init_teams(
                    player_char_id=player_id,
                    enemy_char_id=enemy_id,
                    player_hp=player_hp,
                    player_max_hp=battle_hp_player_max,
                    enemy_hp=enemy_hp,
                    enemy_max_hp=battle_hp_enemy_max,
                )

    # =======================================================
    # 🏜️ Configuración inicial de ambiente y HUD
    # =======================================================
    $ battle_set_background("harribel")
    $ battle_set_atmosphere("desert")
    $ battle_update_damage_overlay(player_hp, battle_hp_player_max)
    $ battle_update_hp_bars(player_hp, enemy_hp)
    $ battle_show_hud(True)

    # =======================================================
    # 🔋 Inicializar Recursos — Reiatsu/Energía (+ editor por slot)
    # =======================================================
    $ player_reiatsu = battle_player.get("Reiatsu", 0)
    $ player_energy  = battle_player.get("Energy", 0)

    $ enemy_reiatsu  = battle_enemy.get("Reiatsu", 0)
    $ enemy_energy   = battle_enemy.get("Energy", 0)

    $ player_reiatsu_base = player_reiatsu
    $ player_energy_base  = player_energy
    $ enemy_reiatsu_base  = enemy_reiatsu
    $ enemy_energy_base   = enemy_energy

    python:
        import renpy.store as S
        fn_pool = getattr(S, "spa_get_pool_final", None)
        if callable(fn_pool):
            player_reiatsu = int(fn_pool("player:0", "reiatsu", player_reiatsu) or player_reiatsu)
            player_energy = int(fn_pool("player:0", "energy", player_energy) or player_energy)
            enemy_reiatsu = int(fn_pool("enemy:0", "reiatsu", enemy_reiatsu) or enemy_reiatsu)
            enemy_energy = int(fn_pool("enemy:0", "energy", enemy_energy) or enemy_energy)

        S.player_reiatsu_base = int(player_reiatsu or 0)
        S.player_energy_base = int(player_energy or 0)
        S.enemy_reiatsu_base = int(enemy_reiatsu or 0)
        S.enemy_energy_base = int(enemy_energy or 0)

        try:
            battle_player["Reiatsu"] = int(player_reiatsu)
            battle_player["Energy"] = int(player_energy)
            battle_enemy["Reiatsu"] = int(enemy_reiatsu)
            battle_enemy["Energy"] = int(enemy_energy)
        except:
            pass

        # Mantener battle_state sincronizado (fuente SSOT de consumo).
        fn_set_res = getattr(S, "bs_set_unit_resources", None)
        if callable(fn_set_res):
            fn_set_res("player:0", player_reiatsu, player_energy)
            fn_set_res("enemy:0", enemy_reiatsu, enemy_energy)

    # ⭐ Sincronizar simulación del enemigo
    $ simulated_enemy_reiatsu = enemy_reiatsu
    $ simulated_enemy_energy  = enemy_energy

    $ simulated_reiatsu = player_reiatsu
    $ simulated_energy  = player_energy
    $ simulated_enemy_reiatsu = enemy_reiatsu
    $ simulated_enemy_energy  = enemy_energy

    # ⭐ Sincronizar simulación del jugador
    $ simulated_reiatsu = player_reiatsu
    $ simulated_energy  = player_energy

    $ battle_log_add("Reiatsu Inicial: {}".format(player_reiatsu), "#88CCFF")
    $ battle_log_add("Energía Inicial: {}".format(player_energy),  "#FF8844")

    # =======================================================
    # 🧩 Asignar identidades dinámicas (usar ID, no display)
    # =======================================================
    if hasattr(S, "set_battle_identity"):
        $ S.set_battle_identity(player_id, enemy_id)

    # =======================================================
    # 🧠 Inicializar IA según enemigo elegido (usar ID)
    # =======================================================
    if enemy_id == "Grimmjow":
        $ enemy_ai = BattleAI_Grimmjow("Grimmjow", battle_techniques)
        $ battle_set_atmosphere("arena")

    elif enemy_id == "Nel":
        $ enemy_ai = BattleAI_Nel("Nel", battle_techniques)
        $ battle_set_atmosphere("forest")

    else:
        $ enemy_ai = BattleAI_Hollow("Hollow", battle_techniques)
        $ battle_set_atmosphere("desert")

    # =======================================================
    # 🧩 Panel debug (toggle “T”)
    # =======================================================
    show screen debug_battle_identity

    # =======================================================
    # 🌀 Aparición visual del enemigo (display)
    # =======================================================
    $ battle_popup_turn("¡{} aparece en el campo de batalla!".format(enemy_name), "#FF5555", delay=0.8)

    # =======================================================
    # 🎲 Determinar primer actor del combate
    # =======================================================
    if battle_team_mode == "2v2" and hasattr(S, "bs_set_turn_order_keys"):
        $ _order = ["player:0", "enemy:0", "player:1", "enemy:1"]
        $ _actor_key = S.bs_set_turn_order_keys(_order, start_index=0, mirror_legacy=True)
        $ _ctx_now = S.bs_get_turn_ctx() if hasattr(S, "bs_get_turn_ctx") else {"owner_team": "player", "owner_slot": 0}
        $ _owner_now = str(_ctx_now.get("owner_team", "player") or "player")
    else:
        $ _first_owner = random.choice(["player", "enemy"])
        if hasattr(S, "bs_set_turn_owner"):
            $ S.bs_set_turn_owner(_first_owner, mirror_legacy=True)
        else:
            $ battle_turn_owner = _first_owner
        $ _ctx_now = S.bs_get_turn_ctx() if hasattr(S, "bs_get_turn_ctx") else {"owner_team": getattr(S, "battle_turn_owner", _first_owner), "owner_slot": 0}
        $ _owner_now = _ctx_now.get("owner_team", _first_owner)

    if _owner_now == "player":
        $ battle_popup_turn("¡{} ataca primero!".format(player_name), "#00BFFF", delay=0.8)
        jump battle_offensive_turn

    else:
        if enemy_id == "Grimmjow":
            $ battle_log_add("Grimmjow se prepara para pelear...", "#FF6666")
        elif enemy_id == "Nel":
            $ battle_log_add("Nel sonríe con calma... lista para combatir.", "#99FFFF")
        else:
            $ battle_log_add("Un Hollow salvaje aparece en la Zona.", "#FF8888")

        $ battle_popup_turn("¡{} ataca primero!".format(enemy_name), "#FF5555", delay=0.8)
        jump battle_enemy_turn
