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
        $ _pmax_rei = int(getattr(store, "player_reiatsu_base", _prei) or _prei)
        $ _pmax_ene = int(getattr(store, "player_energy_base", _pene) or _pene)
        $ _emax_rei = int(getattr(store, "enemy_reiatsu_base", _erei) or _erei)
        $ _emax_ene = int(getattr(store, "enemy_energy_base", _eene) or _eene)
        $ _pmax_rei = max(1, _pmax_rei)
        $ _pmax_ene = max(1, _pmax_ene)
        $ _emax_rei = max(1, _emax_rei)
        $ _emax_ene = max(1, _emax_ene)
        $ _prei_show = max(0, min(_prei, _pmax_rei))
        $ _pene_show = max(0, min(_pene, _pmax_ene))
        $ _erei_show = max(0, min(_erei, _emax_rei))
        $ _eene_show = max(0, min(_eene, _emax_ene))
        $ _bar_w = 240

        frame:
            xalign 0.02
            yalign 0.02
            xsize 360
            ysize 182
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
                        text ("Reiatsu %s / %s" % (_prei_show, _pmax_rei)) size 14
                        text ("Energía %s / %s" % (_pene_show, _pmax_ene)) size 14
                bar value StaticValue(max(0, _php), max(1, _pmax)) xmaximum _bar_w left_bar "#6EC8E9FF" right_bar "#003847CC"

        frame:
            xalign 0.98
            yalign 0.02
            xsize 360
            ysize 182
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
                        text ("Reiatsu %s / %s" % (_erei_show, _emax_rei)) size 14 xalign 1.0
                        text ("Energía %s / %s" % (_eene_show, _emax_ene)) size 14 xalign 1.0
                    add im.Scale("gui/battle/hud_ai/portraits/portrait_hollow_head.png", 64, 64)
                bar value StaticValue(max(0, _ehp), max(1, _emax)) xmaximum _bar_w left_bar "#6EC8E9FF" right_bar "#003847CC" xalign 1.0


screen battle_ui_hotkeys():
    zorder 95
    if bool(getattr(store, "battle_active", False)):
        frame:
            xalign 0.5
            yalign 0.985
            background "#0007"
            padding (8, 6)
            text "Ofensiva/Defensiva + selector de técnicas activo (modo tutorial)" size 15
