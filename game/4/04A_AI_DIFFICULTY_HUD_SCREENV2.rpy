# ============================================================
# 04A_AI_DIFFICULTY_HUD_SCREEN.rpy – UI del HUD AI
# v1.6.1 SCREEN (OFFENSE + DEFENSE)
# ------------------------------------------------------------
# Contiene:
# - estilos
# - screen ai_difficulty_hud()
# ============================================================

# ------------------------------------------------------------
# 🎨 ESTILOS (Ren'Py 7.4)
# ------------------------------------------------------------
init -19:
    style ai_diff_frame is default
    style ai_diff_frame:
        background "#000A"
        xpadding 14
        ypadding 10

    style ai_diff_btn is default
    style ai_diff_btn:
        xpadding 12
        ypadding 8
        xminimum 240
        background "#222C"
        hover_background "#444C"
        insensitive_background "#2226"

    style ai_diff_btn_text is default
    style ai_diff_btn_text:
        color "#FFFFFF"
        hover_color "#FFFFFF"
        insensitive_color "#AAAAAA"
        outlines [ (2, "#000C", 0, 0) ]
        size 18
        bold True

    style ai_diff_mini_btn is ai_diff_btn
    style ai_diff_mini_btn:
        xminimum 0
        xpadding 8
        ypadding 6

    style ai_diff_mini_btn_text is ai_diff_btn_text
    style ai_diff_mini_btn_text:
        size 16
        bold True


# ------------------------------------------------------------
# 🧠 HUD PRINCIPAL IA
# ------------------------------------------------------------
screen ai_difficulty_hud():

    on "show" action [Function(ai_sync_from_persistent_if_needed), Function(ai_unit_profile_sync_from_persistent_if_needed)]
    on "replace" action [Function(ai_sync_from_persistent_if_needed), Function(ai_unit_profile_sync_from_persistent_if_needed)]

    if ui_show_options_panel:
        fixed:
            xalign 0.985
            yalign 0.985
            xanchor 1.0
            yanchor 1.0
            xsize 360
            ysize 360

            add "gui/battle/hud_ai/frames/frame_secondary_options.png" xalign 0.5 yalign 0.5

            vbox:
                xpos 22
                ypos 22
                spacing 8

                textbutton ai_level_text():
                    style "ai_diff_btn"
                    text_style "ai_diff_btn_text"
                    text_color ai_level_color()
                    xminimum 316
                    xalign 0.0
                    action Function(ai_cycle_level)

                textbutton ai_save_text():
                    style "ai_diff_btn"
                    text_style "ai_diff_btn_text"
                    text_color ai_save_color()
                    xminimum 316
                    xalign 0.0
                    action Function(ai_toggle_save)

                textbutton ai_ui_enemy_slot_text():
                    style "ai_diff_btn"
                    text_style "ai_diff_btn_text"
                    text_color "#80DEEA"
                    xminimum 316
                    xalign 0.0
                    action Function(ai_ui_cycle_enemy_slot)

                textbutton ai_ui_target_rule_text():
                    style "ai_diff_btn"
                    text_style "ai_diff_btn_text"
                    text_color "#FFD700"
                    xminimum 316
                    xalign 0.0
                    action Function(ai_ui_cycle_target_rule)

                textbutton "🔄 Reset Stats Ofensivos":
                    style "ai_diff_btn"
                    text_style "ai_diff_btn_text"
                    xminimum 316
                    xalign 0.0
                    action Function(ai_reset_finisher_stats)

                textbutton "🔄 Reset Stats Defensivos":
                    style "ai_diff_btn"
                    text_style "ai_diff_btn_text"
                    xminimum 316
                    xalign 0.0
                    action Function(ai_reset_defense_stats)
