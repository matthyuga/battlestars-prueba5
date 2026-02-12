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
# 🔹 Defaults (para que battle_enemy_id exista siempre)
# ===========================================================
default battle_enemy_id = "Hollow"

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
    call battle_select_opponent


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

    # Normalización: el sistema usa "Nel" (Neliel solo display)
    if enemy_id == "Neliel":
        $ enemy_id = "Nel"
        $ S.battle_enemy_id = "Nel"

    # =======================================================
    # ⚙️ Variables base (HP inicial)
    # =======================================================
    $ player_hp = 10000
    $ enemy_hp  = 10000

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

    # =======================================================
    # 🌆 Fondo de batalla aleatorio
    # =======================================================
    $ fondo_random = renpy.random.choice(["black", "black2", "fondo3", "hollow1", "hollow12"])
    scene expression fondo_random

    # =======================================================
    # 👤 Cargar fichas desde CHARACTER_DATA
    # =======================================================
    # IMPORTANTE: get_character debe devolver COPIA (dict) para no contaminar plantillas.
    $ battle_player = get_character("Harribel")
    $ battle_enemy  = get_character(enemy_id)

    # Nombre visible (solo UI/logs)
    $ enemy_name = battle_enemy.get("name", enemy_id)

    # =======================================================
    # 🏜️ Configuración inicial de ambiente y HUD
    # =======================================================
    $ battle_set_background("harribel")
    $ battle_set_atmosphere("desert")
    $ battle_update_damage_overlay(player_hp, 10000)
    $ battle_update_hp_bars(player_hp, enemy_hp)
    $ battle_show_hud(True)

    # =======================================================
    # 🔋 Inicializar Recursos — Reiatsu/Energía
    # =======================================================
    $ player_reiatsu = battle_player.get("Reiatsu", 0)
    $ player_energy  = battle_player.get("Energy", 0)

    $ enemy_reiatsu  = battle_enemy.get("Reiatsu", 0)
    $ enemy_energy   = battle_enemy.get("Energy", 0)

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
        $ S.set_battle_identity("Harribel", enemy_id)

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
    # 🎲 Determinar quién ataca primero (SYNC con battle_turn_owner)
    # =======================================================
    $ battle_turn_owner = random.choice(["player", "enemy"])

    if battle_turn_owner == "player":
        $ battle_popup_turn("¡Harribel ataca primero!", "#00BFFF", delay=0.8)
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
