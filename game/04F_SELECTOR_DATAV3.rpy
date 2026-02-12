# ============================================================
# 04F_SELECTOR_DATA.rpy – Datos del Selector de Técnicas
# Versión v4.2 – Selector State Hardened + EnemySim Unified
# ------------------------------------------------------------
# - Variables limpias
# - Compatibilidad con Concentrar/Potenciar moderno
# - Preparado para el sistema dinámico real del 04X
# - NEW: flag global para ocultar/mostrar el panel "Técnicas en espera"
# - FIX: Unifica simulación enemigo (simulated_enemy_*)
# - FIX: Helpers seguros para reset/limpieza (NO reasigna listas)
# ============================================================

# -------------------------------
# 🧩 Variables globales (estado)
# -------------------------------
default skip_focus_reset = False

default extra_offensive_actions = 0
default extra_defensive_actions = 0

# Cola del jugador (IMPORTANTE: NUNCA reasignar, siempre mutar con [:])
default player_action_queue = []

# Estado del selector/turno
default battle_mode = "offensive"
default turn_confirmed = False

default actions_available = 1
default actions_available_start = 1

# -------------------------------
# 🔋 Recursos simulados (selector usa SOLO simulación)
# -------------------------------
default simulated_reiatsu = 0
default simulated_energy  = 0

# ✅ Simulación enemigo (única fuente de verdad para UI/HUD del selector)
default simulated_enemy_reiatsu = 0
default simulated_enemy_energy  = 0

# -------------------------------
# 🧷 Flags internos
# -------------------------------
# Nota: concentrar_activo debe ser SOLO UI (no lógica dura).
default concentrar_activo = False

# Nota: este flag es de routing/turno (ideal moverlo al core, se mantiene por compat)
default defense_for_attack_active = False

# ------------------------------------------------------------
# 👁️ UI Toggle: Panel "Técnicas en espera" (technique_selector)
# ------------------------------------------------------------
# Permite ocultar/mostrar el panel con una tecla (U),
# sin afectar la cola ni la simulación de recursos.
default show_technique_selector = True

# -------------------------------
# 🖼️ Config gráfico
# -------------------------------
init -961 python:
    BTN_ZOOM = 0.60

transform tech_btn_scale:
    zoom BTN_ZOOM


# ============================================================
# 🛡️ HELPERS – Blindaje del selector (store-safe)
# ============================================================
init -960 python:
    import renpy.store as S

    def selector_clear_queue():
        """
        Limpia la cola del jugador sin reasignar la lista.
        Evita desync con screens que mantienen referencia.
        """
        try:
            if hasattr(S, "player_action_queue"):
                S.player_action_queue[:] = []
        except:
            pass

    def selector_reset_simulation():
        """
        Sincroniza simulación con recursos reales (jugador + enemigo).
        Llamar SIEMPRE al entrar al selector o al cancelar todo.
        """
        try:
            S.simulated_reiatsu = int(getattr(S, "player_reiatsu", 0) or 0)
            S.simulated_energy  = int(getattr(S, "player_energy", 0) or 0)
        except:
            S.simulated_reiatsu = 0
            S.simulated_energy  = 0

        try:
            S.simulated_enemy_reiatsu = int(getattr(S, "enemy_reiatsu", 0) or 0)
            S.simulated_enemy_energy  = int(getattr(S, "enemy_energy", 0) or 0)
        except:
            S.simulated_enemy_reiatsu = 0
            S.simulated_enemy_energy  = 0

    def selector_reset_ui_state():
        """
        Resetea flags UI del selector sin tocar lógica de combate.
        """
        try:
            S.turn_confirmed = False
        except:
            pass

        # Por defecto, mostrar panel (el usuario lo puede toggle)
        try:
            if not hasattr(S, "show_technique_selector"):
                S.show_technique_selector = True
        except:
            pass

    def selector_hard_reset():
        """
        Reset completo recomendado ANTES de abrir technique_selector.
        (No toca multiplicadores reales de focus; eso lo maneja el core.)
        """
        selector_clear_queue()
        selector_reset_simulation()
        selector_reset_ui_state()
