# ===========================================================
# 06A_BATTLE_HUD_COMPAT_STUBS.rpy
# HUD simplificado para piloto (sin sistema HUD avanzado legacy).
# ===========================================================

init python:
    def _hud_fake_hp_step(current, target):
        try:
            c = float(current or 0.0)
            t = float(target or 0.0)
        except:
            return int(target or 0)
        if c == t:
            return int(t)
        d = abs(t - c)
        step = max(1.0, d * 0.24)
        if c < t:
            n = c + step
            if n > t:
                n = t
        else:
            n = c - step
            if n < t:
                n = t
        return int(n)

    def _hud_fake_resource_step(current, target):
        try:
            c = float(current or 0.0)
            t = float(target or 0.0)
        except:
            return int(target or 0)
        if c == t:
            return int(t)
        d = abs(t - c)
        step = max(1.0, d * 0.35)
        if c < t:
            n = c + step
            if n > t:
                n = t
        else:
            n = c - step
            if n < t:
                n = t
        return int(n)

    def _hud_hp_fake_on_damage(fake_value, shown_hp, hp_now, hp_prev):
        """
        Barra fake gris: solo aparece al recibir daño y conserva el valor previo
        para luego desvanecerse vía alpha.
        """
        try:
            fake_v = float(fake_value or 0.0)
            shown_v = float(shown_hp or 0.0)
            hp_n = float(hp_now or 0.0)
            hp_p = float(hp_prev or 0.0)
        except:
            return int(shown_hp or 0)

        # Si hubo daño en HP real, congelamos la fake en el valor previo visible.
        if hp_n < hp_p:
            return int(max(fake_v, shown_v, hp_p))

        # Si la fake quedó por debajo de la barra real (curación/reset), la corregimos.
        if fake_v < shown_v:
            return int(shown_v)

        return int(fake_v)

    def _hud_hp_fake_alpha_step(alpha_now, fake_value, shown_hp, hp_now, hp_prev):
        try:
            a = float(alpha_now or 0.0)
            fake_v = float(fake_value or 0.0)
            shown_v = float(shown_hp or 0.0)
            hp_n = float(hp_now or 0.0)
            hp_p = float(hp_prev or 0.0)
        except:
            return 0.0

        # Recibir daño: reaparece fuerte.
        if hp_n < hp_p:
            return 0.8

        # Si no hay diferencia visible, apagar.
        if fake_v <= shown_v:
            return 0.0

        # Fade progresivo (sin perseguir a la barra real).
        return max(0.0, a - 0.06)


screen battle_hp_overlay():
    zorder 90
    default _php_fake = 0
    default _ehp_fake = 0
    default _php_damage_fake = 0
    default _ehp_damage_fake = 0
    default _php_damage_alpha = 0.0
    default _ehp_damage_alpha = 0.0
    default _php_prev_real = 0
    default _ehp_prev_real = 0
    default _prei_fake = 0
    default _pene_fake = 0
    default _erei_fake = 0
    default _eene_fake = 0

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
        if _php_fake <= 0:
            $ _php_fake = _php
        if _ehp_fake <= 0:
            $ _ehp_fake = _ehp
        if _php_damage_fake <= 0:
            $ _php_damage_fake = _php
        if _ehp_damage_fake <= 0:
            $ _ehp_damage_fake = _ehp
        if _php_prev_real <= 0:
            $ _php_prev_real = _php
        if _ehp_prev_real <= 0:
            $ _ehp_prev_real = _ehp
        if _prei_fake <= 0:
            $ _prei_fake = _prei_show
        if _pene_fake <= 0:
            $ _pene_fake = _pene_show
        if _erei_fake <= 0:
            $ _erei_fake = _erei_show
        if _eene_fake <= 0:
            $ _eene_fake = _eene_show
        timer 0.08 repeat True action [
            SetScreenVariable("_php_fake", _hud_fake_hp_step(_php_fake, _php)),
            SetScreenVariable("_ehp_fake", _hud_fake_hp_step(_ehp_fake, _ehp)),
            SetScreenVariable("_php_damage_fake", _hud_hp_fake_on_damage(_php_damage_fake, _php_fake, _php, _php_prev_real)),
            SetScreenVariable("_ehp_damage_fake", _hud_hp_fake_on_damage(_ehp_damage_fake, _ehp_fake, _ehp, _ehp_prev_real)),
            SetScreenVariable("_php_damage_alpha", _hud_hp_fake_alpha_step(_php_damage_alpha, _php_damage_fake, _php_fake, _php, _php_prev_real)),
            SetScreenVariable("_ehp_damage_alpha", _hud_hp_fake_alpha_step(_ehp_damage_alpha, _ehp_damage_fake, _ehp_fake, _ehp, _ehp_prev_real)),
            SetScreenVariable("_php_prev_real", _php),
            SetScreenVariable("_ehp_prev_real", _ehp),
            SetScreenVariable("_prei_fake", _hud_fake_resource_step(_prei_fake, _prei_show)),
            SetScreenVariable("_pene_fake", _hud_fake_resource_step(_pene_fake, _pene_show)),
            SetScreenVariable("_erei_fake", _hud_fake_resource_step(_erei_fake, _erei_show)),
            SetScreenVariable("_eene_fake", _hud_fake_resource_step(_eene_fake, _eene_show))
        ]

        frame:
            xalign 0.0
            yalign 0.0
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
                        text ("HP %s / %s" % (_php_fake, _pmax)) size 15
                        text ("Reiatsu %s / %s" % (_prei_fake, _pmax_rei)) size 14
                        text ("Energía %s / %s" % (_pene_fake, _pmax_ene)) size 14
                fixed:
                    xmaximum _bar_w
                    ymaximum 18
                    if _php_damage_fake > _php_fake and _php_damage_alpha > 0.0:
                        bar value StaticValue(max(0, _php_damage_fake), max(1, _pmax)) xmaximum _bar_w left_bar "#9EA4AAFF" right_bar "#00000000" at Transform(alpha=_php_damage_alpha)
                    # right_bar más transparente para no tapar el segmento fake gris.
                    bar value StaticValue(max(0, _php_fake), max(1, _pmax)) xmaximum _bar_w left_bar "#6EC8E9FF" right_bar "#00384722"

        frame:
            xalign 1.0
            yalign 0.0
            xsize 360
            ysize 182
            background "#0006"
            padding (8, 8)
            vbox:
                spacing 4
                hbox:
                    xfill True
                    xalign 1.0
                    spacing 8
                    null xfill True
                    vbox:
                        xalign 1.0
                        spacing 2
                        text "Enemigo (Hollow)" size 17 color "#FF7777" xalign 1.0
                        text ("HP %s / %s" % (_ehp_fake, _emax)) size 15 xalign 1.0
                        text ("Reiatsu %s / %s" % (_erei_fake, _emax_rei)) size 14 xalign 1.0
                        text ("Energía %s / %s" % (_eene_fake, _emax_ene)) size 14 xalign 1.0
                    add im.Scale("gui/battle/hud_ai/portraits/portrait_hollow_head.png", 64, 64)
                fixed:
                    xmaximum _bar_w
                    ymaximum 18
                    xalign 1.0
                    if _ehp_damage_fake > _ehp_fake and _ehp_damage_alpha > 0.0:
                        bar value StaticValue(max(0, _ehp_damage_fake), max(1, _emax)) xmaximum _bar_w left_bar "#9EA4AAFF" right_bar "#00000000" at Transform(alpha=_ehp_damage_alpha) xalign 1.0
                    # right_bar más transparente para no tapar el segmento fake gris.
                    bar value StaticValue(max(0, _ehp_fake), max(1, _emax)) xmaximum _bar_w left_bar "#6EC8E9FF" right_bar "#00384722" xalign 1.0


screen battle_ui_hotkeys():
    zorder 95
    if bool(getattr(store, "battle_active", False)):
        null
