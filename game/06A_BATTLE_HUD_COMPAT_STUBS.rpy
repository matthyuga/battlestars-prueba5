# ===========================================================
# 06A_BATTLE_HUD_COMPAT_STUBS.rpy
# HUD simplificado para piloto (sin sistema HUD avanzado legacy).
# ===========================================================

screen battle_hp_overlay():
    zorder 90

    if bool(getattr(store, "battle_active", False)):
        $ _php = int(getattr(store, "player_hp", 0) or 0)
        $ _ehp = int(getattr(store, "enemy_hp", 0) or 0)
        $ _pmax = int(getattr(store, "battle_hp_player_max", max(1, _php)) or max(1, _php))
        $ _emax = int(getattr(store, "battle_hp_enemy_max", max(1, _ehp)) or max(1, _ehp))
        $ _prei = int(getattr(store, "player_reiatsu", 0) or 0)
        $ _pene = int(getattr(store, "player_energy", 0) or 0)
        $ _erei = int(getattr(store, "enemy_reiatsu", 0) or 0)
        $ _eene = int(getattr(store, "enemy_energy", 0) or 0)

        frame:
            xalign 0.02
            yalign 0.02
            xsize 420
            ysize 125
            background "#0006"
            padding (8, 8)
            vbox:
                spacing 4
                hbox:
                    spacing 8
                    add im.Scale("gui/battle/hud_ai/portraits/portrait_harribel_head.png", 64, 64)
                    vbox:
                        spacing 2
                        text "Jugador (Harribel)" size 17 color "#00BFFF"
                        text ("HP %s / %s" % (_php, _pmax)) size 15
                        text ("Reiatsu %s | Energía %s" % (_prei, _pene)) size 14
                bar value StaticValue(max(0, _php), max(1, _pmax)) xmaximum 390

        frame:
            xalign 0.98
            yalign 0.02
            xsize 420
            ysize 125
            background "#0006"
            padding (8, 8)
            vbox:
                spacing 4
                hbox:
                    xalign 1.0
                    spacing 8
                    vbox:
                        xalign 1.0
                        spacing 2
                        text "Enemigo (Hollow)" size 17 color "#FF7777" xalign 1.0
                        text ("HP %s / %s" % (_ehp, _emax)) size 15 xalign 1.0
                        text ("Reiatsu %s | Energía %s" % (_erei, _eene)) size 14 xalign 1.0
                    add im.Scale("gui/battle/hud_ai/portraits/portrait_hollow_head.png", 64, 64)
                bar value StaticValue(max(0, _ehp), max(1, _emax)) xmaximum 390 xalign 1.0


screen battle_ui_hotkeys():
    zorder 95
    if bool(getattr(store, "battle_active", False)):
        frame:
            xalign 0.5
            yalign 0.985
            background "#0007"
            padding (8, 6)
            text "Ofensiva/Defensiva + selector de técnicas activo (modo tutorial)" size 15
