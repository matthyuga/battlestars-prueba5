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

    on "show" action Function(ai_sync_from_persistent_if_needed)
    on "replace" action Function(ai_sync_from_persistent_if_needed)

    frame style "ai_diff_frame":
        xalign 0.98
        yalign 0.06

        vbox:
            spacing 6

            # ====================================================
            # 🧠 DIFICULTAD
            # ====================================================
            textbutton ai_level_text():
                style "ai_diff_btn"
                text_style "ai_diff_btn_text"
                text_color ai_level_color()
                action Function(ai_cycle_level)

            # ====================================================
            # 💾 GUARDAR
            # ====================================================
            textbutton ai_save_text():
                style "ai_diff_btn"
                text_style "ai_diff_btn_text"
                text_color ai_save_color()
                action Function(ai_toggle_save)

            # ====================================================
            # ⚔️ OFENSIVA – FINISHER MODE
            # ====================================================
            if ai_finisher_mode_get() == "stats":

                hbox:
                    spacing 6

                    frame:
                        background "#0006"
                        xpadding 4
                        ypadding 4
                        textbutton ai_weight_pct_text("attack_reducer", "R"):
                            style "ai_diff_mini_btn"
                            text_style "ai_diff_mini_btn_text"
                            action Function(ai_cycle_weight, "attack_reducer")

                    frame:
                        background "#0006"
                        xpadding 4
                        ypadding 4
                        textbutton ai_weight_pct_text("stronger_attack", "S"):
                            style "ai_diff_mini_btn"
                            text_style "ai_diff_mini_btn_text"
                            action Function(ai_cycle_weight, "stronger_attack")

                    frame:
                        background "#0006"
                        xpadding 4
                        ypadding 4
                        textbutton ai_weight_pct_text("direct_attack", "D"):
                            style "ai_diff_mini_btn"
                            text_style "ai_diff_mini_btn_text"
                            action Function(ai_cycle_weight, "direct_attack")

                    frame:
                        background "#0006"
                        xpadding 4
                        ypadding 4
                        textbutton ai_weight_pct_text("noatk_attack", "N"):
                            style "ai_diff_mini_btn"
                            text_style "ai_diff_mini_btn_text"
                            action Function(ai_cycle_weight, "noatk_attack")

                textbutton "🎯 Stats Ofensivos (R/S/D/N)":
                    style "ai_diff_btn"
                    text_style "ai_diff_btn_text"
                    text_color ai_test_color()
                    action Function(ai_cycle_finisher_mode)

            else:
                textbutton ai_finisher_mode_text():
                    style "ai_diff_btn"
                    text_style "ai_diff_btn_text"
                    text_color ai_test_color()
                    action Function(ai_cycle_finisher_mode)

            textbutton "🔄 Reset Stats Ofensivos":
                style "ai_diff_btn"
                text_style "ai_diff_btn_text"
                action Function(ai_reset_finisher_stats)

            # ====================================================
            # 🛡️ DEFENSA – MODE
            # ====================================================
            textbutton ai_defense_mode_text():
                style "ai_diff_btn"
                text_style "ai_diff_btn_text"
                text_color ai_defense_color()
                action Function(ai_cycle_defense_mode)

            # 🔗 CONCAT
            textbutton ai_defense_concat_text():
                style "ai_diff_btn"
                text_style "ai_diff_btn_text"
                text_color ai_defense_concat_color()
                action Function(ai_toggle_defense_concat)

            # ====================================================
            # 🛡️ DEFENSA – STATS
            # ====================================================
            if ai_defense_mode_get() == "stats":

                hbox:
                    spacing 6

                    frame:
                        background "#0006"
                        xpadding 4
                        ypadding 4
                        textbutton ai_defense_weight_pct_text("def_extra", "E"):
                            style "ai_diff_mini_btn"
                            text_style "ai_diff_mini_btn_text"
                            action Function(ai_cycle_defense_weight, "def_extra")

                    frame:
                        background "#0006"
                        xpadding 4
                        ypadding 4
                        textbutton ai_defense_weight_pct_text("def_reduct", "R"):
                            style "ai_diff_mini_btn"
                            text_style "ai_diff_mini_btn_text"
                            action Function(ai_cycle_defense_weight, "def_reduct")

                    frame:
                        background "#0006"
                        xpadding 4
                        ypadding 4
                        textbutton ai_defense_weight_pct_text("def_reflect", "F"):
                            style "ai_diff_mini_btn"
                            text_style "ai_diff_mini_btn_text"
                            action Function(ai_cycle_defense_weight, "def_reflect")

                textbutton "🛡️ Stats Defensivos (E/R/F)":
                    style "ai_diff_btn"
                    text_style "ai_diff_btn_text"
                    text_color ai_defense_color()
                    action NullAction()

            textbutton "🔄 Reset Stats Defensivos":
                style "ai_diff_btn"
                text_style "ai_diff_btn_text"
                action Function(ai_reset_defense_stats)

            # ====================================================
            # 🧿 FOCUS
            # ====================================================
            textbutton ai_focus_text():
                style "ai_diff_btn"
                text_style "ai_diff_btn_text"
                text_color ai_focus_color()
                action Function(ai_toggle_focus)
