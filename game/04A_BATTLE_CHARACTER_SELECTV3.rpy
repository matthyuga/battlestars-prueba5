# ============================================================
# 04A_BATTLE_CHARACTER_SELECT.rpy – Selección de jugador/oponente + HUD Dificultad IA
# ============================================================

# Dificultad “temporal” (si NO guardás)
default ai_difficulty = "basic"   # "basic" / "intermediate" / "advanced"

# Switch: si True, usa persistent; si False, usa ai_difficulty
default ai_difficulty_save = False

# Defaults de selección (compat)
default battle_player_id = "Harribel"


label battle_select_player:
    scene bg_battle_base
    show screen battle_log_screen
    show screen ai_difficulty_hud
    "Selecciona tu personaje."

    menu:
        "Harribel":
            $ battle_player_id = "Harribel"
            jump battle_select_opponent

        "Grimmjow":
            $ battle_player_id = "Grimmjow"
            jump battle_select_opponent

        "Nel":
            $ battle_player_id = "Nel"
            jump battle_select_opponent

        "Hollow":
            $ battle_player_id = "Hollow"
            jump battle_select_opponent


label battle_select_opponent:
    scene bg_battle_base
    show screen battle_log_screen
    show screen ai_difficulty_hud
    "Selecciona a tu oponente."

    menu:
        "Hollow":
            $ battle_enemy_id = "Hollow"
            jump battle_start

        "Grimmjow":
            $ battle_enemy_id = "Grimmjow"
            jump battle_start

        "Nel":
            $ battle_enemy_id = "Nel"
            jump battle_start

