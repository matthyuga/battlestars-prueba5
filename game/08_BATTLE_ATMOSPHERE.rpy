# ===========================================================
# 08_BATTLE_ATMOSPHERE_DYNAMIC.RPY – Desactivado (Versión limpia)
# ===========================================================
# v2.3 NoOverlay Edition (Ren’Py 7.4.9)
# -----------------------------------------------------------
# - Elimina completamente los tintes, viñetas y transiciones
# - Mantiene las funciones para compatibilidad con otros módulos
# - No dibuja ninguna capa sobre el fondo
# ===========================================================

init -968 python:

    # -------------------------------------------------------
    # 🔹 Estado interno de atmósfera
    # -------------------------------------------------------
    _atmo_current = "off"
    _atmo_target = "off"
    _atmo_transitioning = False
    _atmo_force = False

    # -------------------------------------------------------
    # 🔹 Mapa sin color ni viñeta
    # -------------------------------------------------------
    _atmo_map = {
        "off":       ("#00000000", "#00000000", 0.0),
        "desert":    ("#00000000", "#00000000", 0.0),
        "lab":       ("#00000000", "#00000000", 0.0),
        "void":      ("#00000000", "#00000000", 0.0),
        "boss":      ("#00000000", "#00000000", 0.0),
        "critical":  ("#00000000", "#00000000", 0.0),
        "lowhp":     ("#00000000", "#00000000", 0.0),
        "focus":     ("#00000000", "#00000000", 0.0),
        "victory":   ("#00000000", "#00000000", 0.0),
    }

    # -------------------------------------------------------
    # 🔹 Función base (mantiene compatibilidad)
    # -------------------------------------------------------
    def battle_set_atmosphere(target="off", force=False):
        global _atmo_current
        _atmo_current = target
        # No muestra nada visualmente

    # -------------------------------------------------------
    # 🔹 Actualización por HP (sin efecto visual)
    # -------------------------------------------------------
    def battle_update_atmosphere_by_hp(player_hp, enemy_hp):
        return  # Desactivado

    # -------------------------------------------------------
    # 🔹 Flash temporal (sin efecto)
    # -------------------------------------------------------
    def battle_atmo_flash(mode="critical", duration=1.0):
        return  # Desactivado

    # -------------------------------------------------------
    # 🔹 Eventos reactivos (sin efecto)
    # -------------------------------------------------------
    def battle_atmo_on_event(event="neutral"):
        return  # Desactivado


# ===========================================================
# 🔹 SCREEN PRINCIPAL – Desactivado
# ===========================================================
screen battle_atmosphere_layer(name="off"):
    zorder 6
    modal False
    # No agrega ningún color ni viñeta
    pass


# ===========================================================
# 🔹 TRANSFORMS – Placeholder sin animación
# ===========================================================
transform atmo_breathe:
    alpha 1.0

transform atmo_vignette:
    alpha 0.0
