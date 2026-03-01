# ============================================================
# 04A_BATTLE_CHARACTER_SELECT.rpy – Selección de jugador/oponente + HUD Dificultad IA
# ============================================================

# Dificultad “temporal” (si NO guardás)
default ai_difficulty = "basic"   # "basic" / "intermediate" / "advanced"

# Switch: si True, usa persistent; si False, usa ai_difficulty
default ai_difficulty_save = False

# Defaults de selección (compat)
default battle_player_id = "Harribel"
default battle_enemy_id = "Hollow"
default battle_team_mode = "1v1"   # "1v1" | "2v2"
default battle_player_ids = []
default battle_enemy_ids = []
default battle_player_slot_0 = ""
default battle_player_slot_1 = ""
default battle_enemy_slot_0 = ""
default battle_enemy_slot_1 = ""
default battle_enemy_pick_mode = "random"   # "random" | "manual"

init -5 python:
    def bs_show_select_screens():
        """Muestra screens base de selección usando wrappers compatibles."""
        import renpy.store as S
        fn_show = getattr(S, "ui_show_screen_safe", None)
        if callable(fn_show):
            fn_show("battle_log_screen")
            fn_show("ai_difficulty_hud")
        else:
            renpy.show_screen("battle_log_screen")
            renpy.show_screen("ai_difficulty_hud")


label battle_select_player:
    scene bg_battle_base
    $ bs_show_select_screens()

    menu:
        "Selecciona modo de combate"
        "1v1":
            $ battle_team_mode = "1v1"
            jump battle_select_player_1v1

        "2v2":
            $ battle_team_mode = "2v2"
            jump battle_select_player_slot_0


label battle_select_player_1v1:
    scene bg_battle_base
    $ bs_show_select_screens()
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
    $ bs_show_select_screens()
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


label battle_select_player_slot_0:
    scene bg_battle_base
    $ bs_show_select_screens()
    "2v2 — Selecciona tu personaje (slot 1)."

    menu:
        "Harribel":
            $ battle_player_slot_0 = "Harribel"
            jump battle_select_player_slot_1
        "Grimmjow":
            $ battle_player_slot_0 = "Grimmjow"
            jump battle_select_player_slot_1
        "Nel":
            $ battle_player_slot_0 = "Nel"
            jump battle_select_player_slot_1
        "Hollow":
            $ battle_player_slot_0 = "Hollow"
            jump battle_select_player_slot_1


label battle_select_player_slot_1:
    scene bg_battle_base
    $ bs_show_select_screens()
    "2v2 — Selecciona tu personaje (slot 2, sin duplicados)."

    menu:
        "Harribel" if battle_player_slot_0 != "Harribel":
            $ battle_player_slot_1 = "Harribel"
            jump battle_select_enemy_mode_2v2
        "Grimmjow" if battle_player_slot_0 != "Grimmjow":
            $ battle_player_slot_1 = "Grimmjow"
            jump battle_select_enemy_mode_2v2
        "Nel" if battle_player_slot_0 != "Nel":
            $ battle_player_slot_1 = "Nel"
            jump battle_select_enemy_mode_2v2
        "Hollow" if battle_player_slot_0 != "Hollow":
            $ battle_player_slot_1 = "Hollow"
            jump battle_select_enemy_mode_2v2


label battle_select_enemy_mode_2v2:
    scene bg_battle_base
    $ bs_show_select_screens()
    "2v2 — Selección de equipo IA"

    python:
        import renpy.store as S
        p0 = str(getattr(S, "battle_player_slot_0", "Harribel") or "Harribel")
        p1 = str(getattr(S, "battle_player_slot_1", "Grimmjow") or "Grimmjow")
        if p0 == p1:
            p1 = "Grimmjow" if p0 != "Grimmjow" else "Nel"
        S.battle_player_ids = [p0, p1]

    menu:
        "Aleatorio":
            $ battle_enemy_pick_mode = "random"
            jump battle_select_enemy_slots_2v2_random
        "Elegir manualmente":
            $ battle_enemy_pick_mode = "manual"
            jump battle_select_enemy_slot_0_2v2


label battle_select_enemy_slot_0_2v2:
    scene bg_battle_base
    $ bs_show_select_screens()
    "2v2 — Elige enemigo (slot 1)."

    menu:
        "Hollow":
            $ battle_enemy_slot_0 = "Hollow"
            jump battle_select_enemy_slot_1_2v2
        "Grimmjow":
            $ battle_enemy_slot_0 = "Grimmjow"
            jump battle_select_enemy_slot_1_2v2
        "Nel":
            $ battle_enemy_slot_0 = "Nel"
            jump battle_select_enemy_slot_1_2v2
        "Harribel":
            $ battle_enemy_slot_0 = "Harribel"
            jump battle_select_enemy_slot_1_2v2


label battle_select_enemy_slot_1_2v2:
    scene bg_battle_base
    $ bs_show_select_screens()
    "2v2 — Elige enemigo (slot 2, sin duplicados)."

    menu:
        "Hollow" if battle_enemy_slot_0 != "Hollow":
            $ battle_enemy_slot_1 = "Hollow"
            jump battle_finalize_teams_2v2
        "Grimmjow" if battle_enemy_slot_0 != "Grimmjow":
            $ battle_enemy_slot_1 = "Grimmjow"
            jump battle_finalize_teams_2v2
        "Nel" if battle_enemy_slot_0 != "Nel":
            $ battle_enemy_slot_1 = "Nel"
            jump battle_finalize_teams_2v2
        "Harribel" if battle_enemy_slot_0 != "Harribel":
            $ battle_enemy_slot_1 = "Harribel"
            jump battle_finalize_teams_2v2


label battle_select_enemy_slots_2v2_random:
    python:
        import renpy.store as S
        pool = ["Hollow", "Grimmjow", "Nel", "Harribel"]

        candidates = [c for c in pool if c not in (S.battle_player_ids or [])]
        if len(candidates) < 2:
            candidates = list(pool)

        renpy.random.shuffle(candidates)
        e0 = str(candidates[0] if len(candidates) > 0 else "Hollow")
        e1 = str(candidates[1] if len(candidates) > 1 else ("Grimmjow" if e0 != "Grimmjow" else "Nel"))
        if e0 == e1:
            for c in pool:
                if c != e0:
                    e1 = c
                    break

        S.battle_enemy_slot_0 = e0
        S.battle_enemy_slot_1 = e1

    jump battle_finalize_teams_2v2


label battle_finalize_teams_2v2:
    python:
        import renpy.store as S
        p0 = str(getattr(S, "battle_player_slot_0", "Harribel") or "Harribel")
        p1 = str(getattr(S, "battle_player_slot_1", "Grimmjow") or "Grimmjow")
        e0 = str(getattr(S, "battle_enemy_slot_0", "Hollow") or "Hollow")
        e1 = str(getattr(S, "battle_enemy_slot_1", "Nel") or "Nel")

        if p0 == p1:
            p1 = "Grimmjow" if p0 != "Grimmjow" else "Nel"
        if e0 == e1:
            e1 = "Grimmjow" if e0 != "Grimmjow" else "Nel"

        S.battle_player_ids = [p0, p1]
        S.battle_enemy_ids = [e0, e1]

        # Compat 1v1 fields usan slot 0
        S.battle_player_id = p0
        S.battle_enemy_id = e0

    "2v2 listo. Tu equipo: [battle_player_slot_0] + [battle_player_slot_1]."
    "Equipo enemigo: [battle_enemy_slot_0] + [battle_enemy_slot_1]."
    jump battle_start
