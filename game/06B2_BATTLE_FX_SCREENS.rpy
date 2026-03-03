# ===========================================================
# 06B2_BATTLE_FX_SCREENS.RPY – Screens visuales de efectos
# v1.01 NoFX Edition (Ren’Py 7.4.9)
# -----------------------------------------------------------
# Todos los efectos de glow, shockwave y glitch desactivados.
# ===========================================================

screen battle_light_glow(glow_color="#FFF", glow_alpha=0.4, glow_time=0.4):
    zorder 180
    modal False
    # add Solid(glow_color) alpha 0.0 at glow_fade(glow_alpha, glow_time)

screen battle_combo_shockwave(wave_color="#FFF", wave_alpha=0.4, wave_time=0.6):
    zorder 185
    modal False
    # add Solid(wave_color) alpha 0.0 at shockwave_expand(wave_alpha, wave_time)

screen battle_glitch_overlay(glitch_color="#FF0000", glitch_time=0.25):
    zorder 195
    modal False
    # add Solid(glitch_color) alpha 0.0 at glitch_flash(glitch_time)

screen battle_damage_popups():
    zorder 200
    modal False
    for fx in battle_floating_texts:
        if fx["target"] == "enemy":
            if fx["type"] == "critical":
                text "-{}".format(battle_fmt_num(fx["value"])) color fx["color"] size 60 outlines [(3, "#FFFFAA", 0, 0)] at float_damage_enemy_critical
            elif fx["type"] == "power":
                text "-{}".format(battle_fmt_num(fx["value"])) color fx["color"] size 48 outlines [(2, "#FFD93D", 0, 0)] at float_damage_enemy_power
            else:
                text "-{}".format(battle_fmt_num(fx["value"])) color fx["color"] size 40 at float_damage_enemy_normal
        else:
            text "-{}".format(battle_fmt_num(fx["value"])) color fx["color"] size 34 at float_damage_player

screen focus_particles():
    zorder 350
    modal False
    # add Solid("#00BFFF11") at focus_aura_pulse
    # text "✦" size 38 color "#AEE6FF" at focus_particle_burst(0.00, 0.45, 0.60)
    # text "✦" size 28 color "#CFEFFF" at focus_particle_burst(0.06, 0.50, 0.58)
    # text "✦" size 34 color "#9FD8FF" at focus_particle_burst(0.12, 0.55, 0.62)
