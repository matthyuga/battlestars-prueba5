# ===========================================================
# 06A_BATTLE_HUD_COMPAT_STUBS.rpy
# HUD simplificado para piloto (sin sistema HUD avanzado legacy).
# ===========================================================

init python:
    def _hud_ghost_decay(current, target, speed=0.30):
        try:
            c = float(current or 0.0)
            t = float(target or 0.0)
            s = float(speed or 0.30)
        except:
            return int(target or 0)
        if c <= t:
            return int(t)
        step = max(1.0, (c - t) * max(0.05, min(0.95, s)))
        n = c - step
        if n < t:
            n = t
        return int(n)


screen battle_hp_overlay():
    zorder 90
    default _pghost = 0
    default _eghost = 0

    if bool(getattr(store, "battle_active", False)):
        $ _php = int(getattr(store, "player_hp", 0) or 0)
        $ _ehp = int(getattr(store, "enemy_hp", 0) or 0)
        $ _pmax = int(getattr(store, "battle_hp_player_max", max(1, _php)) or max(1, _php))
        $ _emax = int(getattr(store, "battle_hp_enemy_max", max(1, _ehp)) or max(1, _ehp))
        $ _prei = int(getattr(store, "player_reiatsu", 0) or 0)
        $ _pene = int(getattr(store, "player_energy", 0) or 0)
        $ _erei = int(getattr(store, "enemy_reiatsu", 0) or 0)
        $ _eene = int(getattr(store, "enemy_energy", 0) or 0)
        $ _bar_w = 300

        if _pghost <= 0:
            $ _pghost = _php
        if _eghost <= 0:
            $ _eghost = _ehp

        timer 0.08 repeat True action [
            SetScreenVariable("_pghost", _hud_ghost_decay(_pghost, _php, 0.25)),
            SetScreenVariable("_eghost", _hud_ghost_decay(_eghost, _ehp, 0.25))
        ]

        frame:
            xalign 0.02
            yalign 0.02
            xsize 360
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
                fixed:
                    xmaximum _bar_w
                    ymaximum 24
                    bar value StaticValue(max(0, _pghost), max(1, _pmax)) xmaximum _bar_w left_bar "#9A9A9A88" right_bar "#00000044"
                    bar value StaticValue(max(0, _php), max(1, _pmax)) xmaximum _bar_w left_bar "#6EC8E9FF" right_bar "#003847CC"

        frame:
            xalign 0.98
            yalign 0.02
            xsize 360
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
                fixed:
                    xmaximum _bar_w
                    ymaximum 24
                    xalign 1.0
                    bar value StaticValue(max(0, _eghost), max(1, _emax)) xmaximum _bar_w left_bar "#9A9A9A88" right_bar "#00000044" xalign 1.0
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
