# ===========================================================
# 09_BATTLE_DAMAGE_OVERLAY.RPY – Indicadores visuales de daño
# v2.41 Visual Sync Fix (Ren’Py 7.4.9)
# -----------------------------------------------------------
# - Mantiene solo overlays 10/50/80
# - Transición más fluida entre estados
# ===========================================================

init -967 python:

    _overlay_current = None

    def battle_update_damage_overlay(player_hp, player_hp_max=10000):
        """
        Lógica automática de overlays según porcentaje de HP.
        """
        global _overlay_current
        try:
            ratio = float(player_hp) / float(player_hp_max)
        except:
            ratio = 1.0

        # 🔧 FIX – rangos más suaves
        if ratio <= 0.20:
            overlay = "10"
        elif ratio <= 0.50:
            overlay = "50"
        elif ratio <= 0.80:
            overlay = "80"
        else:
            overlay = None

        if overlay == _overlay_current:
            return

        if _overlay_current:
            renpy.hide_screen("battle_damage_overlay")

        if overlay:
            renpy.show_screen("battle_damage_overlay", overlay_name=overlay)

        _overlay_current = overlay


# ===========================================================
# 🔹 SCREEN PRINCIPAL
# ===========================================================
screen battle_damage_overlay(overlay_name="80"):
    zorder 15
    modal False

    if overlay_name == "80":
        add "images/overlays/80.png" at overlay_fade
    elif overlay_name == "50":
        add "images/overlays/50.png" at overlay_fade
    elif overlay_name == "10":
        add "images/overlays/10.png" at overlay_fade


# ===========================================================
# 🔹 TRANSICIÓN (fade-in/out suave, sin flash inicial)
# ===========================================================
transform overlay_fade:
    alpha 1.0                      # empieza visible, sin fundido desde negro
    linear 0.6 alpha 0.9
    block:
        linear 1.2 alpha 1.0
        linear 1.2 alpha 0.8
        repeat

