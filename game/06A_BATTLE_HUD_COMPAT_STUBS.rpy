# ===========================================================
# 06A_BATTLE_HUD_COMPAT_STUBS.rpy
# HUD simplificado para piloto (sin sistema HUD avanzado legacy).
# ===========================================================

screen battle_hp_overlay():
    zorder 90

    $ _php = int(getattr(store, "player_hp", 0) or 0)
    $ _ehp = int(getattr(store, "enemy_hp", 0) or 0)
    $ _pmax = int(getattr(store, "battle_hp_player_max", max(1, _php)) or max(1, _php))
    $ _emax = int(getattr(store, "battle_hp_enemy_max", max(1, _ehp)) or max(1, _ehp))

    frame:
        xalign 0.02
        yalign 0.02
        xsize 520
        ysize 135
        background "#0008"
        padding (10, 10)
        vbox:
            spacing 6
            add "gui/battle/hud_ai/portraits/portrait_harribel_head.png" xalign 0.0
            text "Jugador (Harribel)" size 18 color "#00BFFF"
            bar value StaticValue(max(0, _php), max(1, _pmax)) xmaximum 470
            text "HP [ _php ] / [ _pmax ]" size 16

    frame:
        xalign 0.98
        yalign 0.02
        xsize 520
        ysize 135
        background "#0008"
        padding (10, 10)
        vbox:
            spacing 6
            add "gui/battle/hud_ai/portraits/portrait_hollow_head.png" xalign 1.0
            text "Enemigo (Hollow)" size 18 color "#FF7777" xalign 1.0
            bar value StaticValue(max(0, _ehp), max(1, _emax)) xmaximum 470 xalign 1.0
            text "HP [ _ehp ] / [ _emax ]" size 16 xalign 1.0


screen battle_ui_hotkeys():
    zorder 95
    frame:
        xalign 0.5
        yalign 0.985
        background "#0007"
        padding (8, 6)
        text "Ofensiva/Defensiva + selector de técnicas activo (modo tutorial)" size 15
