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
    if bool(getattr(store, "bs_battle_legacy_damage_popups_enabled", False)):
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

screen battle_hit_feedback_layer():
    zorder 245
    modal False

    if bool(getattr(store, "bs_battle_hit_feedback_enabled", True)):

        $ _visible_fn = getattr(store, "bs_battle_hit_feedback_visible_events", None)
        if callable(_visible_fn):
            $ _visible_payload = _visible_fn()
            $ _hit_events = list(_visible_payload.get("hits", []) or [])
            $ _result_events = list(_visible_payload.get("results", []) or [])
        else:
            $ _hit_events = list(getattr(store, "battle_hit_feedback_events", []) or [])[-6:]
            $ _result_events = list(getattr(store, "battle_hit_feedback_result_events", []) or [])[-4:]

        for _i, fx in enumerate(_hit_events):
            $ _target = str(fx.get("target", "enemy") or "enemy")
            $ _value = int(fx.get("value", 0) or 0)
            $ _hit = int(fx.get("hit", 1) or 1)
            $ _grade = str(fx.get("grade", "C") or "C")
            $ _color = str(fx.get("color", "#FF6666") or "#FF6666")
            $ _slot = int(_i % 4)
            $ _kind = str(fx.get("kind", "normal") or "normal")
            $ _label = str(fx.get("label", "") or "")
            if not _label:
                $ _label = "CONCENTRAR" if _kind == "focus" else ("%s HIT" % _hit)
            $ _grade_text = "" if _kind == "focus" else _grade
            $ _show_value = (_kind != "focus" and _value > 0)
            $ _label_color = "#C586C0" if _kind == "focus" else "#FFFFFF"

            if _target == "enemy":
                fixed at battle_hit_feedback_enemy(_slot):
                    xsize 360
                    ysize 128
                    text _label:
                        xpos 0
                        ypos 0
                        size 30
                        color _label_color
                        bold True
                        outlines [(4, "#000000", 0, 0), (1, "#FF3B3B", 0, 0)]
                    if _show_value:
                        text ("-%s" % battle_fmt_num(_value)):
                            xpos 72
                            ypos 28
                            size 50
                            color _color
                            bold True
                            outlines [(5, "#090009", 0, 0), (1, "#FFFFFF", 0, 0)]
                    if _grade_text:
                        text _grade_text:
                            xpos 240
                            ypos 6
                            size 42
                            color ("#FFD84A" if _grade in ("A", "S") else "#CFE8FF")
                            bold True
                            outlines [(3, "#000000", 0, 0)]
            else:
                fixed at battle_hit_feedback_player(_slot):
                    xsize 360
                    ysize 128
                    text _label:
                        xpos 190
                        ypos 0
                        size 30
                        color _label_color
                        bold True
                        outlines [(4, "#000000", 0, 0), (1, "#5CCBFF", 0, 0)]
                    if _show_value:
                        text ("-%s" % battle_fmt_num(_value)):
                            xpos 52
                            ypos 28
                            size 50
                            color _color
                            bold True
                            outlines [(5, "#000914", 0, 0), (1, "#FFFFFF", 0, 0)]
                    if _grade_text:
                        text _grade_text:
                            xpos 0
                            ypos 6
                            size 42
                            color ("#FFD84A" if _grade in ("A", "S") else "#CFE8FF")
                            bold True
                            outlines [(3, "#000000", 0, 0)]

        for _ri, fx in enumerate(_result_events):
            $ _target = str(fx.get("target", "enemy") or "enemy")
            $ _value = int(fx.get("value", 0) or 0)
            $ _color = str(fx.get("color", "#FF6666") or "#FF6666")
            $ _slot = int(_ri % 3)
            $ _kind = str(fx.get("kind", "final") or "final")
            $ _label = str(fx.get("label", "") or "")
            if not _label:
                $ _label = "ENTRANTE" if _kind == "incoming" else ("RECIBIDO" if _target == "player" else "FINAL")
            $ _label_color = "#FFD84A" if _kind == "incoming" else ("#FF5A5A" if _target == "player" else "#FFD84A")
            $ _show_value = (_value > 0)

            if _target == "enemy":
                fixed at battle_result_feedback_enemy(_slot):
                    xsize 360
                    ysize 128
                    text _label:
                        xpos 0
                        ypos 0
                        size 34
                        color _label_color
                        bold True
                        outlines [(4, "#000000", 0, 0), (1, "#FF3B3B", 0, 0)]
                    if _show_value:
                        text ("-%s" % battle_fmt_num(_value)):
                            xpos 22
                            ypos 34
                            size 66
                            color _color
                            bold True
                            outlines [(5, "#090009", 0, 0), (1, "#FFFFFF", 0, 0)]
            else:
                fixed at battle_result_feedback_player(_slot):
                    xsize 360
                    ysize 128
                    text _label:
                        xpos 120
                        ypos 0
                        size 34
                        color _label_color
                        bold True
                        outlines [(4, "#000000", 0, 0), (1, "#5CCBFF", 0, 0)]
                    if _show_value:
                        text ("-%s" % battle_fmt_num(_value)):
                            xpos 10
                            ypos 34
                            size 66
                            color _color
                            bold True
                            outlines [(5, "#000914", 0, 0), (1, "#FFFFFF", 0, 0)]

screen focus_particles():
    zorder 350
    modal False
    # add Solid("#00BFFF11") at focus_aura_pulse
    # text "✦" size 38 color "#AEE6FF" at focus_particle_burst(0.00, 0.45, 0.60)
    # text "✦" size 28 color "#CFEFFF" at focus_particle_burst(0.06, 0.50, 0.58)
    # text "✦" size 34 color "#9FD8FF" at focus_particle_burst(0.12, 0.55, 0.62)
