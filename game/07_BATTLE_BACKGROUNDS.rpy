# ===========================================================
# 07_BATTLE_BACKGROUNDS.RPY – Escenarios y Overlays Dinámicos
# v2.44 Base+Desert Only (Ren’Py 7.4.9)
# - Usa solo bg_battle_base y bg_battle_desert
# - Sin overlay oscuro inicial
# - Fade-in suave desde el fondo base
# ===========================================================

init -969 python:

    def battle_set_background(mode="neutral"):
        """
        Muestra el fondo de batalla partiendo de bg_battle_base.
        No usa overlays oscuros.
        """
        # Limpia y coloca el fondo base elegido por ti (fondo3.png)
        renpy.scene()
        renpy.show("bg_battle_base")

        # Si el modo es Harribel, encima hace fade al desierto
        if mode == "harribel":
            renpy.show("bg_battle_desert", at_list=[fade_in_bg])
        else:
            # Default: solo queda el base (no hay otros fondos definidos)
            pass

        # Disolver suave, SIN oscurecer
        #renpy.with_statement(Dissolve(0.6, alpha=True, color="#FFFFFF"))

    def battle_flash_overlay(color="#FFFFFF", intensity=0.5):
        """
        Overlay temporal para impactos. Por defecto blanco (no oscurece).
        """
        renpy.show_screen("battle_background_overlay", color=color, alpha=float(intensity or 0.0))
        renpy.restart_interaction()


# ===========================================================
# Screen del overlay de flash (solo cuando alpha > 0)
# ===========================================================
screen battle_background_overlay(color="#FFFFFF", alpha=0.0):
    zorder 1
    modal False
    if alpha > 0.0:
        add Solid(color) alpha alpha at background_fade


# ===========================================================
# Transforms
# ===========================================================
transform background_fade:
    alpha 0.0
    linear 0.15 alpha 0.6
    linear 0.30 alpha 0.0

transform fade_in_bg:
    alpha 0.0
    linear 1.0 alpha 1.0
