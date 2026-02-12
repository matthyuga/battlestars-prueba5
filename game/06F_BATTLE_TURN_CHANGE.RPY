# ===========================================================
# 06F_BATTLE_TURN_CHANGE.RPY – Indicador de Cambio de Turno
# ===========================================================
# v1.0 Silent Transition Edition (Ren’Py 7.4.9)
# -----------------------------------------------------------
# - Muestra “Tu turno” / “Turno enemigo” con resplandor lateral
# - Sin sonido ni pausa dura
# - Compatible con HUD y Core actual
# ===========================================================

init -966 python:
    def battle_turn_change(owner="player"):
        """
        Muestra el efecto visual al cambiar de turno.
        owner puede ser 'player' o 'enemy'.
        """
        try:
            if owner == "player":
                renpy.show_screen("battle_turn_change", text="🔹 TU TURNO", color="#00BFFF", side="left")
            else:
                renpy.show_screen("battle_turn_change", text="🔻 TURNO ENEMIGO", color="#FF4444", side="right")
            renpy.pause(1.0)
            renpy.hide_screen("battle_turn_change")
        except Exception as e:
            renpy.log("battle_turn_change error: {}".format(e))


# -----------------------------------------------------------
# 🔹 SCREEN – Texto + resplandor lateral
# -----------------------------------------------------------
screen battle_turn_change(text="", color="#00BFFF", side="left"):
    zorder 310
    modal False

    if side == "left":
        add Solid(color + "22") xalign 0.0 yalign 0.5 at turn_flash_left
    else:
        add Solid(color + "22") xalign 1.0 yalign 0.5 at turn_flash_right

    text text:
        size 52
        bold True
        color color
        outlines [(3, "#FFFFFF40", 0, 0)]
        xalign 0.5
        yalign 0.5
        at turn_text_anim


# -----------------------------------------------------------
# 🔹 TRANSFORMS
# -----------------------------------------------------------
transform turn_text_anim:
    alpha 0.0 zoom 0.9
    linear 0.25 alpha 1.0 zoom 1.0
    linear 0.30 alpha 1.0
    linear 0.25 alpha 0.0

transform turn_flash_left:
    alpha 0.0 zoom 1.0 xanchor 0.0
    linear 0.25 alpha 0.3 xoffset 60
    linear 0.25 alpha 0.1 xoffset 0
    linear 0.25 alpha 0.0

transform turn_flash_right:
    alpha 0.0 zoom 1.0 xanchor 1.0
    linear 0.25 alpha 0.3 xoffset -60
    linear 0.25 alpha 0.1 xoffset 0
    linear 0.25 alpha 0.0
