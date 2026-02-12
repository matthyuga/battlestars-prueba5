# ===========================================================
# 06D_BATTLE_POPUP_TURN.RPY – Popup de Inicio / Turno
# ===========================================================
# v1.2 Silent Cinematic Sync Edition (Ren’Py 7.4.9)
# -----------------------------------------------------------
# - Muestra textos tipo “¡Preparados!” / “¡Fight!” / “Turno enemigo”
# - Sin sonido (para uso en intros visuales)
# - Compatible con Core 1.95, HUD y FX activos
# ===========================================================

init -968 python:
    # -------------------------------------------------------
    # 🔹 Popup animado (sin sonido)
    # -------------------------------------------------------
    def battle_popup_turn(text, color="#FFD700", delay=0.8, glow=True):
        """
        Muestra un mensaje central animado.
        Puede usarse para '¡Preparados!', '¡Fight!' o avisos de turno.
        """
        try:
            renpy.show_screen("battle_popup_turn", text=text, color=color, glow=glow)
            renpy.pause(delay)
            renpy.hide_screen("battle_popup_turn")
        except Exception as e:
            renpy.log("battle_popup_turn error: {}".format(e))


# -----------------------------------------------------------
# 🔹 SCREEN – Popup centrado cinematográfico
# -----------------------------------------------------------
screen battle_popup_turn(text="", color="#FFD700", glow=True):
    zorder 300
    modal False

    if glow:
        # Leve aura de fondo, mejora la visibilidad sin fade
        add Solid("#FFFFFF18") at popup_glow_aura

    text text:
        color color
        size 64
        bold True
        outlines [(4, "#FFFFFF40", 0, 0)]
        xalign 0.5
        yalign 0.5
        at popup_turn_anim


# -----------------------------------------------------------
# 🔹 ANIMACIÓN – Entrada / salida suave
# -----------------------------------------------------------
transform popup_turn_anim:
    alpha 0.0 zoom 0.7
    linear 0.25 alpha 1.0 zoom 1.0
    linear 0.35 alpha 1.0
    linear 0.25 alpha 0.0

transform popup_glow_aura:
    alpha 0.0 zoom 1.0
    linear 0.25 alpha 0.25 zoom 1.05
    linear 0.25 alpha 0.15 zoom 1.0
    repeat 2
