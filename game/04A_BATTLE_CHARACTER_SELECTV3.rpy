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
default battle_multiplayer_manual = False
default battle_player_count = 1
default battle_enemy_count = 1


label battle_select_player:
    scene bg_battle_base
    show screen battle_log_screen
    show screen ai_difficulty_hud

    menu:
        "Selecciona modo de combate"
        "1v1":
            $ battle_team_mode = "1v1"
            jump battle_select_player_1v1

        "2v2":
            $ battle_team_mode = "2v2"
            $ battle_multiplayer_manual = False
            jump battle_select_player_slot_0

        "Multijugador (manual P/E)":
            $ battle_multiplayer_manual = True
            jump battle_select_multiplayer_player_count


label battle_select_multiplayer_player_count:
    scene bg_battle_base
    show screen battle_log_screen
    show screen ai_difficulty_hud
    "Multijugador — Elige cantidad de jugadores del equipo PLAYER (P)."

    menu:
        "P = 1":
            $ battle_player_count = 1
            jump battle_select_multiplayer_enemy_count
        "P = 2":
            $ battle_player_count = 2
            jump battle_select_multiplayer_enemy_count


label battle_select_multiplayer_enemy_count:
    scene bg_battle_base
    show screen battle_log_screen
    show screen ai_difficulty_hud
    "Multijugador — Elige cantidad de jugadores del equipo ENEMY (E)."

    menu:
        "E = 1":
            $ battle_enemy_count = 1
            jump battle_select_player_slot_0
        "E = 2":
            $ battle_enemy_count = 2
            jump battle_select_player_slot_0


label battle_select_player_1v1:
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


label battle_select_player_slot_0:
    scene bg_battle_base
    show screen battle_log_screen
    show screen ai_difficulty_hud
    $ _msg_mode = "Multijugador" if battle_multiplayer_manual else "2v2"
    "[_msg_mode] — Selecciona tu personaje (slot 1)."

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
    show screen battle_log_screen
    show screen ai_difficulty_hud
    $ _msg_mode = "Multijugador" if battle_multiplayer_manual else "2v2"
    "[_msg_mode] — Selecciona tu personaje (slot 2, sin duplicados)."

    if battle_multiplayer_manual and int(battle_player_count or 1) <= 1:
        $ battle_player_slot_1 = ""
        jump battle_select_enemy_mode_2v2

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
    show screen battle_log_screen
    show screen ai_difficulty_hud
    $ _msg_mode = "Multijugador" if battle_multiplayer_manual else "2v2"
    "[_msg_mode] — Selección de equipo IA"

    python:
        import renpy.store as S
        p0 = str(getattr(S, "battle_player_slot_0", "Harribel") or "Harribel")
        p1 = str(getattr(S, "battle_player_slot_1", "Grimmjow") or "Grimmjow")
        if (not getattr(S, "battle_multiplayer_manual", False)) and p0 == p1:
            p1 = "Grimmjow" if p0 != "Grimmjow" else "Nel"
        pcount = int(getattr(S, "battle_player_count", 2) or 2) if getattr(S, "battle_multiplayer_manual", False) else 2
        if pcount <= 1:
            S.battle_player_ids = [p0]
            S.battle_player_slot_1 = ""
        else:
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
    show screen battle_log_screen
    show screen ai_difficulty_hud
    $ _msg_mode = "Multijugador" if battle_multiplayer_manual else "2v2"
    "[_msg_mode] — Elige enemigo (slot 1)."

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
    show screen battle_log_screen
    show screen ai_difficulty_hud
    $ _msg_mode = "Multijugador" if battle_multiplayer_manual else "2v2"
    "[_msg_mode] — Elige enemigo (slot 2, sin duplicados)."

    if battle_multiplayer_manual and int(battle_enemy_count or 1) <= 1:
        $ battle_enemy_slot_1 = ""
        jump battle_finalize_teams_2v2

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

        ecount = int(getattr(S, "battle_enemy_count", 2) or 2) if getattr(S, "battle_multiplayer_manual", False) else 2
        S.battle_enemy_slot_0 = e0
        S.battle_enemy_slot_1 = "" if ecount <= 1 else e1

    jump battle_finalize_teams_2v2


label battle_finalize_teams_2v2:
    python:
        import renpy.store as S
        p0 = str(getattr(S, "battle_player_slot_0", "Harribel") or "Harribel")
        p1 = str(getattr(S, "battle_player_slot_1", "Grimmjow") or "Grimmjow")
        e0 = str(getattr(S, "battle_enemy_slot_0", "Hollow") or "Hollow")
        e1 = str(getattr(S, "battle_enemy_slot_1", "Nel") or "Nel")

        pmulti = bool(getattr(S, "battle_multiplayer_manual", False))
        pcount = int(getattr(S, "battle_player_count", 2) or 2) if pmulti else 2
        ecount = int(getattr(S, "battle_enemy_count", 2) or 2) if pmulti else 2

        if pcount <= 1:
            p_ids = [p0]
            S.battle_player_slot_1 = ""
        else:
            if p0 == p1:
                p1 = "Grimmjow" if p0 != "Grimmjow" else "Nel"
            p_ids = [p0, p1]

        if ecount <= 1:
            e_ids = [e0]
            S.battle_enemy_slot_1 = ""
        else:
            if e0 == e1:
                e1 = "Grimmjow" if e0 != "Grimmjow" else "Nel"
            e_ids = [e0, e1]

        S.battle_player_ids = p_ids
        S.battle_enemy_ids = e_ids
        S.battle_team_mode = "1v1" if (len(p_ids) == 1 and len(e_ids) == 1) else "2v2"

        # Compat 1v1 fields usan slot 0
        S.battle_player_id = p0
        S.battle_enemy_id = e0

    if len(battle_player_ids) > 1:
        "Equipo PLAYER listo: [battle_player_ids[0]] + [battle_player_ids[1]]."
    else:
        "Equipo PLAYER listo: [battle_player_ids[0]]."

    if len(battle_enemy_ids) > 1:
        "Equipo ENEMY listo: [battle_enemy_ids[0]] + [battle_enemy_ids[1]]."
    else:
        "Equipo ENEMY listo: [battle_enemy_ids[0]]."

    if battle_multiplayer_manual:
        $ _pcount_txt = len(battle_player_ids)
        $ _ecount_txt = len(battle_enemy_ids)
        "Modo multijugador manual: P[_pcount_txt] vs E[_ecount_txt]."
    elif battle_team_mode == "2v2":
        "2v2 listo."
    else:
        "1v1 listo."
    jump battle_start
