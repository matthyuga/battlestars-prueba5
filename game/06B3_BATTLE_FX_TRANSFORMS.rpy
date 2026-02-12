# ===========================================================
# 06B3_BATTLE_FX_TRANSFORMS.RPY – Animaciones ATL
# ===========================================================
# v1.0 Modular Split Edition (Ren’Py 7.4.9)
# -----------------------------------------------------------
# Todas las transformaciones usadas por los FX.
# ===========================================================

transform glow_fade(max_a=0.4, d=0.4):
    alpha 0.0
    linear d/4 alpha max_a
    linear d/2 alpha (max_a * 0.8)
    linear d/4 alpha 0.0

transform shockwave_expand(max_a=0.4, d=0.6):
    xalign 0.5 yalign 0.5
    alpha 0.0 zoom 0.2
    linear d/6 alpha max_a zoom 1.1
    linear d/3 alpha (max_a * 0.7) zoom 1.6
    linear d/3 alpha 0.0 zoom 2.0

transform glitch_flash(d=0.25):
    alpha 0.0
    linear d/6 alpha 0.3
    linear d/6 alpha 0.0
    linear d/6 alpha 0.25
    linear d/6 alpha 0.0
    linear d/6 alpha 0.15
    linear d/6 alpha 0.0

transform burst_flash:
    alpha 0.0 zoom 0.2
    linear 0.1 alpha 0.5 zoom 1.0
    linear 0.3 alpha 0.0 zoom 1.4

transform float_damage_enemy_normal:
    xalign 0.80 yalign 0.30
    alpha 1.0 zoom 1.0
    linear 0.10 yoffset -15
    linear 0.9 alpha 0.0 yoffset -60

transform float_damage_enemy_power:
    xalign 0.80 yalign 0.30
    alpha 1.0 zoom 1.1
    linear 0.10 yoffset -20
    linear 0.15 zoom 1.2
    linear 1.0 alpha 0.0 yoffset -80

transform float_damage_enemy_critical:
    xalign 0.80 yalign 0.30
    alpha 1.0 zoom 1.0
    easein 0.08 yoffset -25 zoom 1.25
    easeout 0.10 zoom 1.05
    linear 1.0 alpha 0.0 yoffset -100
    on show:
        parallel:
            linear 0.2 rotate 3
            linear 0.2 rotate -3
            linear 0.2 rotate 2
            linear 0.2 rotate 0
        parallel:
            linear 0.2 alpha 1.0
            linear 0.8 alpha 0.0

transform float_damage_player:
    xalign 0.20 yalign 0.70
    linear 0.10 yoffset -10
    linear 1.00 alpha 0.0 yoffset -60

transform focus_aura_pulse:
    xalign 0.50 yalign 0.50
    alpha 0.0 zoom 1.00
    linear 0.15 alpha 1.0 zoom 1.05
    linear 0.15 alpha 0.6 zoom 1.00
    repeat 2

transform focus_particle_burst(d=0.0, xa=0.5, ya=0.5):
    xalign xa yalign ya
    alpha 0.0
    pause d
    linear 0.10 alpha 1.0
    linear 0.50 yoffset -40 alpha 0.0
