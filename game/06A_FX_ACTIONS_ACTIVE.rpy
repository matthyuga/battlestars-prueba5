# ===========================================================
# 06B_BATTLE_FX_ACTIONS.RPY – FX desactivables (modo silencioso)
# ===========================================================
# v1.30 Silent Toggle Edition (Ren’Py 7.4.9)
# -----------------------------------------------------------
# - Permite activar o desactivar todos los FX visuales con FX_ENABLED
# - Mantiene compatibilidad con el resto del sistema
# ===========================================================

init -969 python:

    # =======================================================
    # ⚙️ Modo global de efectos visuales
    # =======================================================
    FX_ENABLED = False   # ← cambia a True si querés reactivar todos los FX

    # -------------------------------------------------------
    # 🔹 ATAQUE FUERTE / CRÍTICO
    # -------------------------------------------------------
    def battle_fx_slash():
        if not FX_ENABLED:
            return
        battle_light_glow("#FF3333", 0.5)
        renpy.show_screen("fx_slash")
        renpy.pause(0.25)
        renpy.hide_screen("fx_slash")

    # -------------------------------------------------------
    # 🔹 TÉCNICA ESPECIAL / EXTRA
    # -------------------------------------------------------
    def battle_fx_pulse(color="#FFAA00"):
        if not FX_ENABLED:
            return
        battle_light_glow(color, 0.4)
        renpy.show_screen("fx_pulse", color=color)
        renpy.pause(0.35)
        renpy.hide_screen("fx_pulse")

    # -------------------------------------------------------
    # 🔹 CONCENTRAR (aura + partículas)
    # -------------------------------------------------------
    def battle_fx_focus():
        if not FX_ENABLED:
            return
        battle_light_glow("#00BFFF", 0.45)
        renpy.show_screen("fx_focus")
        renpy.pause(0.50)
        renpy.hide_screen("fx_focus")
        try:
            battle_atmo_flash("lab")
        except:
            pass

    # -------------------------------------------------------
    # 🔹 DEFENSA / BARRERA
    # -------------------------------------------------------
    def battle_fx_barrier():
        if not FX_ENABLED:
            return
        battle_light_glow("#00FFAA", 0.35)
        renpy.show_screen("fx_barrier")
        renpy.pause(0.40)
        renpy.hide_screen("fx_barrier")

    # -------------------------------------------------------
    # 🔹 REFLEJO
    # -------------------------------------------------------
    def battle_fx_reflect():
        if not FX_ENABLED:
            return
        battle_light_glow("#00FFFF", 0.4)
        renpy.show_screen("fx_reflect")
        renpy.pause(0.30)
        renpy.hide_screen("fx_reflect")
