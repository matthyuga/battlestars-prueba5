# ===========================================================
# 05_BATTLE_OVERLAY_SUMMARY.RPY – HUD resumen de turno
# ===========================================================
# v1.2 (Sync + Fade)
# -----------------------------------------------------------
# - Muestra un resumen del último combo (golpes + daño total)
# - Solo se ve si el log está oculto
# - Se actualiza automáticamente tras cada turno ofensivo
# - Efecto de aparición suave (alpha)
# - Compatible con Ren’Py 7.4.9
# ===========================================================

init -975 python:
    # Variables persistentes entre turnos
    battle_last_combo_hits = 0
    battle_last_combo_damage = 0
    battle_last_combo_visible = False

    # -------------------------------------------------------
    # Guardar resumen del turno
    # -------------------------------------------------------
    def battle_save_turn_summary(hits=0, damage=0):
        """
        Guarda la cantidad de golpes y el daño total del último turno ofensivo.
        """
        global battle_last_combo_hits, battle_last_combo_damage, battle_last_combo_visible
        battle_last_combo_hits = int(hits)
        battle_last_combo_damage = int(damage)
        battle_last_combo_visible = True

    # -------------------------------------------------------
    # Limpiar resumen (al finalizar el combate)
    # -------------------------------------------------------
    def battle_clear_turn_summary():
        global battle_last_combo_hits, battle_last_combo_damage, battle_last_combo_visible
        battle_last_combo_hits = 0
        battle_last_combo_damage = 0
        battle_last_combo_visible = False


# -----------------------------------------------------------
# SCREEN – Overlay con fade automático
# -----------------------------------------------------------
screen battle_turn_summary_overlay():
    zorder 90
    modal False

    if battle_last_combo_visible and not renpy.get_screen("battle_log_screen"):
        frame:
            at combo_fade
            background "#000A"
            xalign 0.0 yalign 1.0
            xmaximum 320
            ypadding 10
            xpadding 14
            vbox:
                spacing 2
                text "Último combo:" color "#FFD700" size 22 bold True
                text "{} golpes – {} daño".format(
                    battle_last_combo_hits,
                    battle_fmt_num(battle_last_combo_damage)
                ) color "#FFFFFF" size 20


# -----------------------------------------------------------
# TRANSFORM – Fade suave
# -----------------------------------------------------------
transform combo_fade:
    alpha 0.0
    linear 0.4 alpha 1.0
    on hide:
        linear 0.4 alpha 0.0


# -----------------------------------------------------------
# Auto-display del overlay
# -----------------------------------------------------------
init python:
    config.overlay_screens.append("battle_turn_summary_overlay")
