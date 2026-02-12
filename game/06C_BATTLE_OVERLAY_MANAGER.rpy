# ===========================================================
# 06C_BATTLE_OVERLAY_MANAGER.RPY – Registro de Overlays
# ===========================================================
# v1.0 Split Edition (Ren’Py 7.4.9)
# -----------------------------------------------------------
# - Registra pantallas persistentes de HUD y FX
# - Asegura visibilidad post-scene black
# ===========================================================

init 999 python:
    style.hp_bar_player = Style("bar")
    style.hp_bar_enemy  = Style("bar")

    overlays = [
        "battle_hp_overlay",
        "battle_damage_popups",
        "battle_turn_summary_overlay"
    ]

    for scr in overlays:
        if scr not in config.overlay_screens:
            config.overlay_screens.append(scr)
