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

    def _hud_percent_step(value, max_value):
        try:
            v = float(value or 0.0)
            m = float(max_value or 1.0)
        except:
            return 0
        if m <= 0.0:
            return 0
        return max(0, min(100, int(round(100.0 * v / m))))

    def _hud_upflare_step_path(side, fill_name, percent):
        try:
            p = max(0, min(100, int(percent or 0)))
        except:
            p = 0
        return "gui/battle/hud_rebel/upflare_bars/steps/%s/%s_%03d.png" % (side, fill_name, p)


default bs_battle_hud_rebel_style = "upflare"


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
        $ _php_fake = max(0, min(int(_php_fake or 0), _pmax))
        $ _ehp_fake = max(0, min(int(_ehp_fake or 0), _emax))
        $ _php_damage_fake = max(0, min(int(_php_damage_fake or 0), _pmax))
        $ _ehp_damage_fake = max(0, min(int(_ehp_damage_fake or 0), _emax))
        if bool(getattr(store, "bs_battle_low_spec_mode", False)):
            $ _php_fake = _php
            $ _ehp_fake = _ehp
            $ _php_damage_fake = _php
            $ _ehp_damage_fake = _ehp
            $ _php_damage_alpha = 0.0
            $ _ehp_damage_alpha = 0.0
            $ _prei_fake = _prei_show
            $ _pene_fake = _pene_show
            $ _erei_fake = _erei_show
            $ _eene_fake = _eene_show
        else:
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
            at Transform(alpha=0.0)
            vbox:
                spacing 4
                hbox:
                    spacing 8
                    $ _picon_fn = getattr(store, "bs_battle_head_portrait", None)
                    $ _picon_disp_fn = getattr(store, "bs_battle_head_portrait_displayable", None)
                    $ _picon = str(_picon_fn(getattr(store, "battle_player_id", ""), "player") if callable(_picon_fn) else "images/character/Jugador_a.png")
                    if callable(_picon_disp_fn):
                        add _picon_disp_fn(getattr(store, "battle_player_id", ""), "player", 64, 64)
                    else:
                        add im.Scale(_picon, 64, 64)
                    vbox:
                        spacing 2
                        $ _pdisp_fn = getattr(store, "bs_battle_display_name", None)
                        $ _player_display_name = str(getattr(store, "battle_player_id", "Jugador") or "Jugador")
                        if callable(_pdisp_fn):
                            $ _player_display_name = str(_pdisp_fn(getattr(store, "battle_player_id", _player_display_name), fallback=_player_display_name))
                        text "Jugador ({})".format(_player_display_name) size 17 color "#00BFFF"
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
            at Transform(alpha=0.0)
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
                        $ _edisp_fn = getattr(store, "bs_battle_display_name", None)
                        $ _enemy_display_name = str(getattr(store, "battle_enemy_id", "Enemigo") or "Enemigo")
                        if callable(_edisp_fn):
                            $ _enemy_display_name = str(_edisp_fn(getattr(store, "battle_enemy_id", _enemy_display_name), fallback=_enemy_display_name))
                        text "Enemigo ({})".format(_enemy_display_name) size 17 color "#FF7777" xalign 1.0
                        text ("HP %s / %s" % (_ehp_fake, _emax)) size 15 xalign 1.0
                        text ("Reiatsu %s / %s" % (_erei_fake, _emax_rei)) size 14 xalign 1.0
                        text ("Energía %s / %s" % (_eene_fake, _emax_ene)) size 14 xalign 1.0
                    $ _eicon_fn = getattr(store, "bs_battle_head_portrait", None)
                    $ _eicon_disp_fn = getattr(store, "bs_battle_head_portrait_displayable", None)
                    $ _eicon = str(_eicon_fn(getattr(store, "battle_enemy_id", ""), "enemy") if callable(_eicon_fn) else "gui/battle/hud_rebel/portraits/portrait_enemy_hollow_rebel_facing.png")
                    if callable(_eicon_disp_fn):
                        add _eicon_disp_fn(getattr(store, "battle_enemy_id", ""), "enemy", 64, 64)
                    else:
                        add im.Scale(_eicon, 64, 64)
                fixed:
                    xmaximum _bar_w
                    ymaximum 18
                    xalign 1.0
                    if _ehp_damage_fake > _ehp_fake and _ehp_damage_alpha > 0.0:
                        bar value StaticValue(max(0, _ehp_damage_fake), max(1, _emax)) xmaximum _bar_w left_bar "#9EA4AAFF" right_bar "#00000000" at Transform(alpha=_ehp_damage_alpha) xalign 1.0
                    # right_bar más transparente para no tapar el segmento fake gris.
                    bar value StaticValue(max(0, _ehp_fake), max(1, _emax)) xmaximum _bar_w left_bar "#6EC8E9FF" right_bar "#00384722" xalign 1.0


        # Rebel HUD skin.
        $ _rebel_hud_w = int(config.screen_width)
        fixed:
            xpos 0
            ypos 0
            xsize _rebel_hud_w
            ysize 154

            $ _hud_p_name = str(_player_display_name)
            $ _hud_e_name = str(_enemy_display_name)
            $ _rebel_portrait_w = 162
            $ _rebel_portrait_h = 135
            $ _rebel_portrait_new_w = 190
            $ _rebel_portrait_new_h = 146
            $ _rebel_nameplate_w = 266
            $ _rebel_nameplate_h = 38
            $ _hud_rebel_style = str(getattr(store, "bs_battle_hud_rebel_style", "legacy") or "legacy")
            $ _upflare_bar_w = 420
            $ _upflare_bar_h = 96
            $ _upflare_player_bar_x = 86
            $ _upflare_enemy_bar_x = 29
            $ _upflare_bar_y = 22
            $ _upflare_hp_y = 38
            $ _p_hp_w = max(0, min(292, int(292.0 * float(max(0, min(_php_fake, _pmax))) / float(max(1, _pmax)))))
            $ _e_hp_w = max(0, min(292, int(292.0 * float(max(0, min(_ehp_fake, _emax))) / float(max(1, _emax)))))
            $ _p_dmg_w = max(0, min(292, int(292.0 * float(max(0, min(_php_damage_fake, _pmax))) / float(max(1, _pmax)))))
            $ _e_dmg_w = max(0, min(292, int(292.0 * float(max(0, min(_ehp_damage_fake, _emax))) / float(max(1, _emax)))))
            $ _p_hp_up_pct = _hud_percent_step(_php_fake, _pmax)
            $ _e_hp_up_pct = _hud_percent_step(_ehp_fake, _emax)
            $ _p_dmg_up_pct = _hud_percent_step(_php_damage_fake, _pmax)
            $ _e_dmg_up_pct = _hud_percent_step(_ehp_damage_fake, _emax)
            $ _p_hp_up_path = _hud_upflare_step_path("player", "hp_fill_green_upflare", _p_hp_up_pct)
            $ _e_hp_up_path = _hud_upflare_step_path("enemy", "hp_fill_green_upflare", _e_hp_up_pct)
            $ _p_dmg_up_path = _hud_upflare_step_path("player", "hp_fill_damage_red_upflare", _p_dmg_up_pct)
            $ _e_dmg_up_path = _hud_upflare_step_path("enemy", "hp_fill_damage_red_upflare", _e_dmg_up_pct)

            fixed:
                xpos 6
                ypos 3
                xsize 535
                ysize 150

                $ _p_rebel_portrait_path_fn = getattr(store, "bs_battle_rebel_portrait_path", None)
                $ _p_rebel_portrait_path = _p_rebel_portrait_path_fn(getattr(store, "battle_player_id", ""), "player") if callable(_p_rebel_portrait_path_fn) else ""
                if _hud_rebel_style == "upflare":
                    if _p_rebel_portrait_path:
                        add im.Scale(_p_rebel_portrait_path, _rebel_portrait_new_w, _rebel_portrait_new_h) xpos -10 ypos -7
                    else:
                        add im.Scale("gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel_v3.png", _rebel_portrait_new_w, _rebel_portrait_new_h) xpos -10 ypos -7

                    fixed:
                        xpos _upflare_player_bar_x
                        ypos _upflare_bar_y
                        xsize _upflare_bar_w
                        ysize _upflare_bar_h
                        add "gui/battle/hud_rebel/upflare_bars/hp_frame_upflare_player.png"
                        if _php_damage_fake > _php_fake and _php_damage_alpha > 0.0:
                            add _p_dmg_up_path at Transform(alpha=_php_damage_alpha)
                        add _p_hp_up_path

                    add im.Scale("gui/battle/hud_rebel/nameplates/nameplate_player_modern.png", _rebel_nameplate_w, _rebel_nameplate_h) xpos 128 ypos 0
                    text ("Jugador (%s)" % _hud_p_name) xpos 158 ypos 8 size 16 color "#FFFFFF" outlines [(2, "#241208", 0, 0)]
                    text ("%s / %s" % (_php_fake, _pmax)) xpos (_upflare_player_bar_x + 210) ypos _upflare_hp_y xanchor 0.5 size 30 color "#F8F8FF" outlines [(3, "#241033", 0, 0)]
                    text ("EP %s / %s" % (_prei_fake, _pmax_rei)) xpos 154 ypos 116 size 14 color "#57CFFF"
                    text ("EC %s / %s" % (_pene_fake, _pmax_ene)) xpos 346 ypos 116 size 14 color "#FFC24A"
                else:
                    if _p_rebel_portrait_path:
                        add im.Scale(_p_rebel_portrait_path, _rebel_portrait_new_w, _rebel_portrait_new_h) xpos -10 ypos -7
                    else:
                        add im.Scale("gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel_v3.png", _rebel_portrait_new_w, _rebel_portrait_new_h) xpos -10 ypos -7
                    add im.Scale("gui/battle/hud_rebel/frames/hp_frame_empty_no_numbers.png", 418, 112) xpos 98 ypos 0

                    add im.Scale("gui/battle/hud_rebel/nameplates/nameplate_player_modern.png", _rebel_nameplate_w, _rebel_nameplate_h) xpos 128 ypos 2
                    text ("Jugador (%s)" % _hud_p_name) xpos 158 ypos 10 size 16 color "#FFFFFF" outlines [(2, "#241208", 0, 0)]
                    text ("%s / %s" % (_php_fake, _pmax)) xpos 244 ypos 31 size 29 color "#F8F8FF" outlines [(3, "#241033", 0, 0)]

                    fixed:
                        xpos 176
                        ypos 79
                        xsize 292
                        ysize 18
                        if _php_damage_fake > _php_fake and _php_damage_alpha > 0.0:
                            if _p_dmg_w > 0:
                                add im.Scale("gui/battle/hud_rebel/bars/hp_fill_damage_red_player.png", _p_dmg_w, 18) at Transform(alpha=_php_damage_alpha)
                        if _p_hp_w > 0:
                            add im.Scale("gui/battle/hud_rebel/bars/hp_fill_green_player.png", _p_hp_w, 18)

                    text ("EP %s / %s" % (_prei_fake, _pmax_rei)) xpos 150 ypos 112 size 14 color "#57CFFF"
                    text ("EC %s / %s" % (_pene_fake, _pmax_ene)) xpos 345 ypos 112 size 14 color "#FFC24A"

            fixed:
                xalign 1.0
                ypos 3
                xsize 535
                ysize 150

                $ _e_rebel_portrait_path_fn = getattr(store, "bs_battle_rebel_portrait_path", None)
                $ _e_rebel_portrait_path = _e_rebel_portrait_path_fn(getattr(store, "battle_enemy_id", ""), "enemy") if callable(_e_rebel_portrait_path_fn) else ""
                if _hud_rebel_style == "upflare":
                    fixed:
                        xpos _upflare_enemy_bar_x
                        ypos _upflare_bar_y
                        xsize _upflare_bar_w
                        ysize _upflare_bar_h
                        add "gui/battle/hud_rebel/upflare_bars/hp_frame_upflare_enemy.png"
                        if _ehp_damage_fake > _ehp_fake and _ehp_damage_alpha > 0.0:
                            add _e_dmg_up_path at Transform(alpha=_ehp_damage_alpha)
                        add _e_hp_up_path

                    if _e_rebel_portrait_path:
                        add im.Scale(_e_rebel_portrait_path, _rebel_portrait_new_w, _rebel_portrait_new_h) xpos 356 ypos -7
                    else:
                        add im.Scale("gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel_facing_v3.png", _rebel_portrait_new_w, _rebel_portrait_new_h) xpos 356 ypos -7

                    add im.Scale("gui/battle/hud_rebel/nameplates/nameplate_enemy_modern.png", _rebel_nameplate_w, _rebel_nameplate_h) xpos 70 ypos 0
                    text ("Enemigo (%s)" % _hud_e_name) xpos 100 ypos 8 size 16 color "#FFFFFF" outlines [(2, "#210908", 0, 0)]
                    text ("%s / %s" % (_ehp_fake, _emax)) xpos (_upflare_enemy_bar_x + 210) ypos _upflare_hp_y xanchor 0.5 size 30 color "#F8F8FF" outlines [(3, "#331018", 0, 0)]
                    text ("EP %s / %s" % (_erei_fake, _emax_rei)) xpos 72 ypos 116 size 14 color "#57CFFF"
                    text ("EC %s / %s" % (_eene_fake, _emax_ene)) xpos 272 ypos 116 size 14 color "#FFC24A"
                else:
                    add im.Scale("gui/battle/hud_rebel/frames/hp_frame_empty_no_numbers_enemy.png", 418, 112) xpos 19 ypos 0
                    if _e_rebel_portrait_path:
                        add im.Scale(_e_rebel_portrait_path, _rebel_portrait_new_w, _rebel_portrait_new_h) xpos 356 ypos -7
                    else:
                        add im.Scale("gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel_facing_v3.png", _rebel_portrait_new_w, _rebel_portrait_new_h) xpos 356 ypos -7

                    add im.Scale("gui/battle/hud_rebel/nameplates/nameplate_enemy_modern.png", _rebel_nameplate_w, _rebel_nameplate_h) xpos 70 ypos 2
                    text ("Enemigo (%s)" % _hud_e_name) xpos 100 ypos 10 size 16 color "#FFFFFF" outlines [(2, "#210908", 0, 0)]
                    text ("%s / %s" % (_ehp_fake, _emax)) xpos 220 ypos 31 size 29 color "#F8F8FF" outlines [(3, "#331018", 0, 0)]

                    fixed:
                        xpos 67
                        ypos 79
                        xsize 292
                        ysize 18
                        if _ehp_damage_fake > _ehp_fake and _ehp_damage_alpha > 0.0:
                            if _e_dmg_w > 0:
                                add im.Scale("gui/battle/hud_rebel/bars/hp_fill_damage_red_enemy.png", _e_dmg_w, 18) xalign 1.0 at Transform(alpha=_ehp_damage_alpha)
                        if _e_hp_w > 0:
                            add im.Scale("gui/battle/hud_rebel/bars/hp_fill_green_enemy.png", _e_hp_w, 18) xalign 1.0

                    text ("EP %s / %s" % (_erei_fake, _emax_rei)) xpos 72 ypos 112 size 14 color "#57CFFF"
                    text ("EC %s / %s" % (_eene_fake, _emax_ene)) xpos 272 ypos 112 size 14 color "#FFC24A"


screen battle_ui_hotkeys():
    zorder 95
    if bool(getattr(store, "battle_active", False)):
        null
