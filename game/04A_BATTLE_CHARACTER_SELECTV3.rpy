# ============================================================
# 04A_BATTLE_CHARACTER_SELECT.rpy – Selección de jugador/oponente + HUD Dificultad IA
# ============================================================

# Dificultad “temporal” (si NO guardás)
default ai_difficulty = "basic"   # "basic" / "intermediate" / "advanced"

# Switch: si True, usa persistent; si False, usa ai_difficulty
default ai_difficulty_save = False
default ai_difficulty_hud_visible = False

# Defaults de selección (compat)
default battle_player_id = ""
default battle_enemy_id = ""
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

init -20 python:
    import renpy.store as S

    if not hasattr(persistent, "ai_difficulty"):
        persistent.ai_difficulty = "basic"
    if not hasattr(S, "bs_saga_register_hero_usage"):
        def _noop_usage_register(_hero_id):
            return None
        S.bs_saga_register_hero_usage = _noop_usage_register

    def ai_difficulty_current():
        use_persistent = bool(getattr(S, "ai_difficulty_save", False))
        if use_persistent:
            return str(getattr(persistent, "ai_difficulty", "basic") or "basic")
        return str(getattr(S, "ai_difficulty", "basic") or "basic")

    def ai_difficulty_set(level):
        lv = str(level or "basic").strip().lower()
        if lv not in ("basic", "intermediate", "advanced"):
            lv = "basic"
        S.ai_difficulty = lv
        if bool(getattr(S, "ai_difficulty_save", False)):
            persistent.ai_difficulty = lv
        return None

    def battle_select_available_ids(include_all=False):
        out = []
        fn_roster = getattr(S, "bs_saga_resolve_roster_v1", None)
        if callable(fn_roster):
            out = [str(x) for x in list(fn_roster(bool(include_all), True) or []) if str(x)]
        fn_pool = getattr(S, "get_combat_character_ids", None)
        if (not out) and callable(fn_pool):
            out = [str(x) for x in list(fn_pool(bool(include_all)) or []) if str(x)]
        if not out:
            fn_ready = getattr(S, "bs_saga_combat_ready_ids", None)
            if callable(fn_ready):
                out = [str(x) for x in list(fn_ready() or []) if str(x)]
        unique = []
        seen = {}
        for hid in out:
            k = str(hid or "").strip().lower()
            if not k or seen.get(k):
                continue
            seen[k] = True
            unique.append(str(hid))
        return unique

    def battle_select_pick_default(index=0, exclude=None, include_all=False):
        pool = battle_select_available_ids(include_all)
        exc = {str(x).strip().lower() for x in (exclude or []) if str(x).strip()}
        filtered = [hid for hid in pool if hid.lower() not in exc]
        src = filtered if filtered else pool
        if not src:
            return ""
        idx = int(index or 0)
        if idx < 0:
            idx = 0
        if idx >= len(src):
            idx = len(src) - 1
        return str(src[idx] or "")

    def battle_select_options(exclude=None, include_all=True):
        pool = battle_select_available_ids(include_all)
        exc = {str(x).strip().lower() for x in (exclude or []) if str(x).strip()}
        out = []
        for hid in pool:
            h = str(hid or "").strip()
            if not h:
                continue
            if h.lower() in exc:
                continue
            out.append(h)
        return out

screen ai_difficulty_hud():
    zorder 200
    key "ctrl_p" action ToggleVariable("ai_difficulty_hud_visible")
    if ai_difficulty_hud_visible:
        frame:
            xalign 0.985
            yalign 0.02
            xsize 360
            background Solid("#0008")
            padding (10, 8)
            vbox:
                spacing 6
                text "Dificultad IA" size 22 color "#FFD166"
                $ _ai = ai_difficulty_current()
                text ("Actual: " + _ai.upper()) size 17 color "#DCEBFF"
                hbox:
                    spacing 6
                    textbutton "Basic" action Function(ai_difficulty_set, "basic")
                    textbutton "Intermedio" action Function(ai_difficulty_set, "intermediate")
                    textbutton "Avanzado" action Function(ai_difficulty_set, "advanced")
                textbutton ("Guardar en perfil: ON" if ai_difficulty_save else "Guardar en perfil: OFF"):
                    action [ToggleVariable("ai_difficulty_save"), Function(ai_difficulty_set, ai_difficulty_current())]

screen battle_select_dynamic_list_screen(title_txt, options, subtitle_txt=""):
    modal True
    tag menu
    frame:
        xalign 0.5
        yalign 0.5
        xmaximum 800
        ymaximum 620
        padding (20, 16)
        vbox:
            spacing 10
            text "[title_txt]" size 30 color "#FFD166"
            if subtitle_txt:
                text "[subtitle_txt]" size 18 color "#DCEBFF"
            viewport:
                mousewheel True
                draggable True
                ymaximum 420
                vbox:
                    spacing 8
                    for opt in (options or []):
                        textbutton "[opt]":
                            xfill True
                            action Return(str(opt))
            textbutton "Cancelar":
                xfill True
                action Return("")


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

    $ _player_opts = battle_select_options([], True)
    if not _player_opts:
        "No hay héroes disponibles para selección."
        jump battle_select_player
    call screen battle_select_dynamic_list_screen("Selecciona tu personaje", _player_opts)
    $ _pick = _return
    if not _pick:
        jump battle_select_player
    $ battle_player_id = str(_pick)
    $ bs_saga_register_hero_usage(str(_pick).lower())
    jump battle_select_opponent


label battle_select_opponent:
    scene bg_battle_base
    show screen battle_log_screen
    show screen ai_difficulty_hud
    "Selecciona a tu oponente."

    $ _enemy_opts = battle_select_options([battle_player_id], True)
    if not _enemy_opts:
        $ _enemy_opts = battle_select_options([], True)
    if not _enemy_opts:
        "No hay oponentes disponibles."
        jump battle_select_player_1v1
    call screen battle_select_dynamic_list_screen("Selecciona a tu oponente", _enemy_opts)
    $ _pick = _return
    if not _pick:
        jump battle_select_player_1v1
    $ battle_enemy_id = str(_pick)
    jump battle_start


label battle_select_player_slot_0:
    scene bg_battle_base
    show screen battle_log_screen
    show screen ai_difficulty_hud
    $ _msg_mode = "Multijugador" if battle_multiplayer_manual else "2v2"
    "[_msg_mode] — Selecciona tu personaje (slot 1)."

    $ _opts = battle_select_options([], True)
    if not _opts:
        "No hay héroes disponibles para armar el equipo PLAYER."
        jump battle_select_player
    call screen battle_select_dynamic_list_screen("Equipo PLAYER — Slot 1", _opts)
    $ _pick = _return
    if not _pick:
        jump battle_select_player
    $ battle_player_slot_0 = str(_pick)
    $ bs_saga_register_hero_usage(str(_pick).lower())
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

    $ _opts = battle_select_options([battle_player_slot_0], True)
    if not _opts:
        $ battle_player_slot_1 = ""
        jump battle_select_enemy_mode_2v2
    call screen battle_select_dynamic_list_screen("Equipo PLAYER — Slot 2", _opts, "Sin duplicados.")
    $ _pick = _return
    if not _pick:
        jump battle_select_player_slot_0
    $ battle_player_slot_1 = str(_pick)
    $ bs_saga_register_hero_usage(str(_pick).lower())
    jump battle_select_enemy_mode_2v2


label battle_select_enemy_mode_2v2:
    scene bg_battle_base
    show screen battle_log_screen
    show screen ai_difficulty_hud
    $ _msg_mode = "Multijugador" if battle_multiplayer_manual else "2v2"
    "[_msg_mode] — Selección de equipo IA"

    python:
        import renpy.store as S
        p0 = str(getattr(S, "battle_player_slot_0", "") or battle_select_pick_default(0))
        p1 = str(getattr(S, "battle_player_slot_1", "") or battle_select_pick_default(1, exclude=[p0]))
        if (not getattr(S, "battle_multiplayer_manual", False)) and p0 == p1:
            p1 = battle_select_pick_default(0, exclude=[p0])
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

    $ _exclude = list(battle_player_ids or [])
    $ _opts = battle_select_options(_exclude, True)
    if not _opts:
        $ _opts = battle_select_options([], True)
    if not _opts:
        "No hay candidatos para equipo ENEMY."
        jump battle_select_enemy_mode_2v2
    call screen battle_select_dynamic_list_screen("Equipo ENEMY — Slot 1", _opts)
    $ _pick = _return
    if not _pick:
        jump battle_select_enemy_mode_2v2
    $ battle_enemy_slot_0 = str(_pick)
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

    $ _exclude = [battle_enemy_slot_0]
    $ _opts = battle_select_options(_exclude, True)
    if not _opts:
        $ battle_enemy_slot_1 = ""
        jump battle_finalize_teams_2v2
    call screen battle_select_dynamic_list_screen("Equipo ENEMY — Slot 2", _opts, "Sin duplicados.")
    $ _pick = _return
    if not _pick:
        jump battle_select_enemy_slot_0_2v2
    $ battle_enemy_slot_1 = str(_pick)
    jump battle_finalize_teams_2v2


label battle_select_enemy_slots_2v2_random:
    python:
        import renpy.store as S
        pool = list(battle_select_available_ids(True) or battle_select_available_ids(False))

        candidates = [c for c in pool if c not in (S.battle_player_ids or [])]
        if len(candidates) < 2:
            candidates = list(pool)

        renpy.random.shuffle(candidates)
        e0 = str(candidates[0] if len(candidates) > 0 else battle_select_pick_default(0))
        e1 = str(candidates[1] if len(candidates) > 1 else battle_select_pick_default(0, exclude=[e0]))
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
        p0 = str(getattr(S, "battle_player_slot_0", "") or battle_select_pick_default(0))
        p1 = str(getattr(S, "battle_player_slot_1", "") or battle_select_pick_default(1, exclude=[p0]))
        e0 = str(getattr(S, "battle_enemy_slot_0", "") or battle_select_pick_default(0, exclude=[p0, p1]))
        e1 = str(getattr(S, "battle_enemy_slot_1", "") or battle_select_pick_default(1, exclude=[e0]))

        pmulti = bool(getattr(S, "battle_multiplayer_manual", False))
        pcount = int(getattr(S, "battle_player_count", 2) or 2) if pmulti else 2
        ecount = int(getattr(S, "battle_enemy_count", 2) or 2) if pmulti else 2

        if pcount <= 1:
            p_ids = [p0]
            S.battle_player_slot_1 = ""
        else:
            if p0 == p1:
                p1 = battle_select_pick_default(0, exclude=[p0])
            p_ids = [p0, p1]

        if ecount <= 1:
            e_ids = [e0]
            S.battle_enemy_slot_1 = ""
        else:
            if e0 == e1:
                e1 = battle_select_pick_default(0, exclude=[e0])
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
