# ===========================================================
# 41_LESSON_SCENES_V1.rpy
# Capa Visual (Fase 3B): escenas de lecciones
# ===========================================================

init python:
    import time

    def tl_keyboard_mock_rows():
        return [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Ñ"],
            ["Z", "X", "C", "V", "B", "N", "M"],
            ["ESPACIO"],
        ]


    def tl_key_color_for(key_name):
        key = str(key_name or "").strip().upper()
        palette = {
            "F": "#8A5DFF",
            "J": "#8A5DFF",
            "A": "#4472C4",
            "S": "#C0504D",
            "D": "#9BBB59",
            "K": "#9BBB59",
            "L": "#C0504D",
            "Ñ": "#4472C4",
            "ESPACIO": "#8B7355",
        }
        return palette.get(key, "#767676")


    def tl_keyboard_mock_blocked_keys():
        return [
            "K_F11", "K_F5",
        ]


    def tl_typing_mock_reset(target_letters=None):
        seq = list(target_letters or ["F", "J", "F", "J", "ESPACIO"])
        store.tl_typing_mock_state = {
            "sequence": seq,
            "cursor": 0,
            "hits": 0,
            "mistakes": 0,
            "last_key": "",
            "error_flash_until": 0.0,
            "completed": False,
        }
        return True


    def tl_typing_mock_press_key(key_text=""):
        st = getattr(store, "tl_typing_mock_state", None)
        if not isinstance(st, dict):
            tl_typing_mock_reset()
            st = getattr(store, "tl_typing_mock_state", {})

        if bool(st.get("completed", False)):
            return False

        seq = list(st.get("sequence", []))
        cur = int(st.get("cursor", 0) or 0)
        if cur >= len(seq):
            st["completed"] = True
            store.tl_typing_mock_state = st
            return True

        pressed = str(key_text or "").strip().upper()
        expected = str(seq[cur] or "").strip().upper()
        st["last_key"] = pressed

        if pressed == expected:
            st["cursor"] = cur + 1
            st["hits"] = int(st.get("hits", 0) or 0) + 1
            if st["cursor"] >= len(seq):
                st["completed"] = True
        else:
            st["mistakes"] = int(st.get("mistakes", 0) or 0) + 1
            st["error_flash_until"] = float(time.time()) + 0.25

        store.tl_typing_mock_state = st
        return True


    def tl_warmup_letter_pool():
        return ["a", "s", "d", "f", "j", "k", "l", "ñ"]


    def tl_warmup_finger_for_key(key_text=""):
        k = str(key_text or "").strip().lower()
        finger_map = {
            "a": ("left", "meñique"),
            "s": ("left", "anular"),
            "d": ("left", "medio"),
            "f": ("left", "índice"),
            "j": ("right", "índice"),
            "k": ("right", "medio"),
            "l": ("right", "anular"),
            "ñ": ("right", "meñique"),
        }
        return finger_map.get(k, ("none", "none"))


    def tl_warmup_prepare(rounds=3, reps_per_round=10):
        rr = int(max(3, min(5, int(rounds or 3))))
        rpr = int(max(8, int(reps_per_round or 10)))
        store.tl_typing_warmup_state = {
            "rounds_total": rr,
            "rounds_done": 0,
            "round_index": 1,
            "reps_per_round": rpr,
            "index": 0,
            "sequence": [],
            "current_letter": "",
            "error_flash_until": 0.0,
            "done": False,
            "phase": "setup",
        }
        return None


    def tl_warmup_start():
        import random
        st = getattr(store, "tl_typing_warmup_state", None)
        if not isinstance(st, dict):
            tl_warmup_prepare(3, 10)
            st = getattr(store, "tl_typing_warmup_state", {})

        pool = list(tl_warmup_letter_pool())
        rpr = int(st.get("reps_per_round", 10) or 10)
        seq = [random.choice(pool) for _ in range(rpr)]

        st["rounds_done"] = 0
        st["round_index"] = 1
        st["index"] = 0
        st["sequence"] = list(seq)
        st["current_letter"] = str(seq[0] if len(seq) > 0 else "a")
        st["error_flash_until"] = 0.0
        st["done"] = False
        st["phase"] = "run"
        store.tl_typing_warmup_state = st
        return None


    def tl_warmup_set_rounds(rounds=3):
        st = getattr(store, "tl_typing_warmup_state", None)
        if not isinstance(st, dict):
            tl_warmup_prepare(rounds=rounds, reps_per_round=10)
            return None
        rr = int(max(3, min(5, int(rounds or 3))))
        st["rounds_total"] = rr
        if int(st.get("round_index", 1) or 1) > rr:
            st["round_index"] = rr
        store.tl_typing_warmup_state = st
        return None


    def tl_warmup_press_key(key_text=""):
        st = getattr(store, "tl_typing_warmup_state", None)
        if not isinstance(st, dict):
            tl_warmup_prepare(3, 10)
            st = getattr(store, "tl_typing_warmup_state", {})

        if str(st.get("phase", "setup") or "setup") != "run":
            return None

        if bool(st.get("done", False)):
            return None

        seq = list(st.get("sequence", []))
        idx = int(st.get("index", 0) or 0)
        if idx >= len(seq):
            idx = max(0, len(seq) - 1)

        pressed = str(key_text or "").strip().lower()
        expected = str(seq[idx] if len(seq) > 0 else "").strip().lower()

        if pressed == expected:
            idx += 1
            if idx >= len(seq):
                st["rounds_done"] = int(st.get("rounds_done", 0) or 0) + 1
                total_rounds = int(st.get("rounds_total", 3) or 3)
                if st["rounds_done"] >= total_rounds:
                    st["done"] = True
                    st["index"] = len(seq)
                    st["current_letter"] = ""
                    st["phase"] = "setup"
                else:
                    import random
                    pool = list(tl_warmup_letter_pool())
                    rpr = int(st.get("reps_per_round", 10) or 10)
                    new_seq = [random.choice(pool) for _ in range(rpr)]
                    st["sequence"] = list(new_seq)
                    st["index"] = 0
                    st["current_letter"] = str(new_seq[0] if len(new_seq) > 0 else "a")
                    st["round_index"] = int(st.get("round_index", 1) or 1) + 1
            else:
                st["index"] = idx
                st["current_letter"] = str(seq[idx])
                st["error_flash_until"] = 0.0
        else:
            st["error_flash_until"] = float(time.time()) + 0.30

        store.tl_typing_warmup_state = st
        return None


default tl_typing_mock_state = {}
default tl_typing_warmup_state = {}


screen tl_lesson_intro_scene(sublesson_id="1_1_intro", lesson_id="lesson_1"):
    tag menu
    modal True

    $ _meta = lesson_get_sublesson_meta(sublesson_id, lesson_id=lesson_id)
    $ _steps = _meta.get("steps", []) if isinstance(_meta, dict) else []
    $ _last = max(0, len(_steps) - 1)
    $ _safe_page = max(0, min(_last, int(tl_intro_page if tl_intro_page is not None else 0)))
    $ _seg = lesson_get_segment(sublesson_id, _safe_page, lesson_id=lesson_id)
    $ _title = str(_seg.get("title", _meta.get("title", "Introducción"))) if isinstance(_seg, dict) else str(_meta.get("title", "Introducción"))

    $ _teacher_id = str(tl_selected_teacher or "").strip().lower()
    if len(_teacher_id) == 0:
        $ _teacher_id = "haru"

    $ _points = []
    if isinstance(_seg, dict):
        if _teacher_id == "misaki" and isinstance(_seg.get("points_misaki", None), (list, tuple)):
            $ _points = list(_seg.get("points_misaki", []))
        elif _teacher_id == "haru" and isinstance(_seg.get("points_haru", None), (list, tuple)):
            $ _points = list(_seg.get("points_haru", []))
        else:
            $ _points = list(_seg.get("points", [])) if isinstance(_seg.get("points", []), (list, tuple)) else []

    $ _teacher_line = "Continuemos con el módulo."
    if isinstance(_seg, dict):
        if isinstance(_seg.get("teacher_lines", None), dict):
            $ _teacher_line = str(_seg.get("teacher_lines", {}).get(_teacher_id, _seg.get("teacher_line", _teacher_line)))
        else:
            $ _teacher_line = str(_seg.get("teacher_line", _teacher_line))

    $ _teacher_rec = character_db_get(_teacher_id, "teachers") if "character_db_get" in globals() else {}
    $ _teacher_name = str(_teacher_rec.get("display_name", "Docente")) if isinstance(_teacher_rec, dict) else "Docente"
    $ _portrait_primary = str(_teacher_rec.get("portrait_primary", "")) if isinstance(_teacher_rec, dict) else ""
    $ _portrait_fallback = str(_teacher_rec.get("portrait_fallback", "")) if isinstance(_teacher_rec, dict) else ""
    $ _teacher_portrait = tl_asset(_portrait_primary) if len(_portrait_primary) > 0 else None
    if not _teacher_portrait and len(_portrait_fallback) > 0:
        $ _teacher_portrait = tl_asset(_portrait_fallback)

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#00000090")

    use tl_ui_panel_center(
        title=_title,
        points=_points
    )

    use tl_ui_teacher_panel(
        teacher_name=_teacher_name,
        teacher_line=_teacher_line,
        teacher_portrait=_teacher_portrait,
        can_continue=lesson_can_advance(sublesson_id, _safe_page, lesson_id=lesson_id),
        can_advance=(not lesson_can_advance(sublesson_id, _safe_page, lesson_id=lesson_id)),
        on_continue=SetVariable("tl_intro_page", min(_last, _safe_page + 1)),
        on_advance=[SetVariable("tl_intro_page", 0), Return("complete")],
        on_back=[SetVariable("tl_intro_page", 0), Return("back_class")]
    )


screen tl_lesson_placeholder_scene(sublesson_id="", lesson_id="lesson_1"):
    tag menu
    modal True

    $ _meta = lesson_get_sublesson_meta(sublesson_id, lesson_id=lesson_id)
    $ _title = str(_meta.get("title", "Sublección placeholder")) if isinstance(_meta, dict) else "Sublección placeholder"
    $ _objective = str(_meta.get("objective", "Contenido temporal.")) if isinstance(_meta, dict) else "Contenido temporal."
    $ _points = [
        "Escena placeholder activa para esta sublección.",
        "La implementación visual/manual se hará en siguientes fases.",
        "Puedes volver al panel para continuar con otra subsección.",
    ]

    $ _teacher_id = str(tl_selected_teacher or "").strip().lower()
    if len(_teacher_id) == 0:
        $ _teacher_id = "haru"
    $ _teacher_rec = character_db_get(_teacher_id, "teachers") if "character_db_get" in globals() else {}
    $ _teacher_name = str(_teacher_rec.get("display_name", "Docente")) if isinstance(_teacher_rec, dict) else "Docente"
    $ _portrait_primary = str(_teacher_rec.get("portrait_primary", "")) if isinstance(_teacher_rec, dict) else ""
    $ _portrait_fallback = str(_teacher_rec.get("portrait_fallback", "")) if isinstance(_teacher_rec, dict) else ""
    $ _teacher_portrait = tl_asset(_portrait_primary) if len(_portrait_primary) > 0 else None
    if not _teacher_portrait and len(_portrait_fallback) > 0:
        $ _teacher_portrait = tl_asset(_portrait_fallback)

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#00000090")

    use tl_ui_panel_center(
        title=_title,
        points=_points
    )

    use tl_ui_teacher_panel(
        teacher_name=_teacher_name,
        teacher_line=_objective,
        teacher_portrait=_teacher_portrait,
        can_continue=False,
        can_advance=False,
        on_continue=NullAction(),
        on_advance=NullAction(),
        on_back=Return("back_class")
    )


screen tl_typing_keyboard_mock_scene(sublesson_id="1_4_keys_exercise", lesson_id="lesson_1"):
    tag menu
    modal True

    $ _meta = lesson_get_sublesson_meta(sublesson_id, lesson_id=lesson_id)
    $ _title = str(_meta.get("title", "Ejercicio teclas")) if isinstance(_meta, dict) else "Ejercicio teclas"
    $ _rows = tl_keyboard_mock_rows()
    $ _target_letters = ["F", "J", "F", "J", "ESPACIO"]
    $ _blocked_keys = tl_keyboard_mock_blocked_keys()
    $ _key_bindings = [
        ("a", "A"), ("s", "S"), ("d", "D"), ("f", "F"), ("g", "G"),
        ("h", "H"), ("j", "J"), ("k", "K"), ("l", "L"),
        ("q", "Q"), ("w", "W"), ("e", "E"), ("r", "R"), ("t", "T"),
        ("y", "Y"), ("u", "U"), ("i", "I"), ("o", "O"), ("p", "P"),
        ("z", "Z"), ("x", "X"), ("c", "C"), ("v", "V"), ("b", "B"),
        ("n", "N"), ("m", "M"),
    ]
    $ _state = tl_typing_mock_state if isinstance(tl_typing_mock_state, dict) else {}
    $ _cursor = int(_state.get("cursor", 0) or 0)
    $ _hits = int(_state.get("hits", 0) or 0)
    $ _mistakes = int(_state.get("mistakes", 0) or 0)
    $ _completed = bool(_state.get("completed", False))
    $ _now = float(time.time())
    $ _error_active = _now < float(_state.get("error_flash_until", 0.0) or 0.0)

    on "show" action Function(tl_typing_mock_reset, _target_letters)

    for _shortcut in _blocked_keys:
        key _shortcut action NullAction()
    for _binding in _key_bindings:
        key _binding[0] action Function(tl_typing_mock_press_key, _binding[1])
    key "K_SPACE" action Function(tl_typing_mock_press_key, "ESPACIO")

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#000000B8")

    frame:
        background Solid("#0D0D0DE8")
        xalign 0.5
        yalign 0.5
        xsize 1180
        ysize 640
        padding (30, 24, 30, 24)

        vbox:
            spacing 18

            text _title size 34 color "#F5F5F5" xalign 0.5

            frame:
                background Solid("#1E1E1EE6")
                xfill True
                ysize 120
                padding (16, 14, 16, 14)

                vbox:
                    spacing 8
                    hbox:
                        xfill True
                        text "Letras a tipear" size 24 color "#D6D6D6"
                        text "Aciertos: [_hits]   Errores: [_mistakes]" size 18 color "#C9D8F8" xalign 1.0
                    hbox:
                        spacing 8
                        for _idx, _letter in enumerate(_target_letters):
                            frame:
                                background Solid("#3D7F54" if _idx < _cursor else ("#3E5B96" if _idx == _cursor else "#22304A"))
                                xsize (100 if _letter == "ESPACIO" else 52)
                                ysize 36
                                xpadding 6
                                ypadding 6
                                text _letter size 20 color "#EAF2FF" xalign 0.5 yalign 0.5
                    if _error_active:
                        frame:
                            background Solid("#D13535")
                            xfill True
                            ysize 4

            frame:
                background Solid("#151515EE")
                xfill True
                ysize 290
                padding (14, 14, 14, 14)

                vbox:
                    spacing 8
                    text "Teclado simulado" size 24 color "#D6D6D6"
                    for _row in _rows:
                        hbox:
                            spacing 6
                            xalign 0.5
                            for _key in _row:
                                $ _w = 380 if _key == "ESPACIO" else 56
                                frame:
                                    background Solid(tl_key_color_for(_key))
                                    xsize _w
                                    ysize 44
                                    xpadding 4
                                    ypadding 4
                                    text _key size 19 color "#F8F8F8" xalign 0.5 yalign 0.5

            frame:
                background Solid("#181818EE")
                xfill True
                ysize 190
                padding (16, 10, 16, 0)

                hbox:
                    spacing 42
                    xalign 0.5
                    yalign 1.0

                    vbox:
                        spacing 6
                        text "Mano izquierda" size 22 color "#D6D6D6" xalign 0.5
                        hbox:
                            spacing 8
                            for _name, _height in [
                                ("Meñique", 96),
                                ("Anular", 126),
                                ("Medio", 136),
                                ("Índice", 118),
                                ("Pulgar", 78),
                            ]:
                                vbox:
                                    spacing 4
                                    frame:
                                        background Solid("#2A2A2A")
                                        xsize 70
                                        ysize 24
                                        text _name size 15 color "#CFCFCF" xalign 0.5 yalign 0.5
                                    fixed:
                                        xsize 70
                                        ysize 140
                                        frame:
                                            background Solid("#5B8BD8")
                                            xsize 46
                                            ysize _height
                                            xalign 0.5
                                            yalign 1.0

                    vbox:
                        spacing 6
                        text "Mano derecha" size 22 color "#D6D6D6" xalign 0.5
                        hbox:
                            spacing 8
                            for _name, _height in [
                                ("Pulgar", 78),
                                ("Índice", 118),
                                ("Medio", 136),
                                ("Anular", 126),
                                ("Meñique", 96),
                            ]:
                                vbox:
                                    spacing 4
                                    frame:
                                        background Solid("#2A2A2A")
                                        xsize 70
                                        ysize 24
                                        text _name size 15 color "#CFCFCF" xalign 0.5 yalign 0.5
                                    fixed:
                                        xsize 70
                                        ysize 140
                                        frame:
                                            background Solid("#5B8BD8")
                                            xsize 46
                                            ysize _height
                                            xalign 0.5
                                            yalign 1.0

            hbox:
                xfill True
                text ("Tip: escribe la secuencia. F/J/ESPACIO deben avanzar la barra superior." if not _completed else "¡Secuencia completada! Puedes continuar.") size 18 color "#D9D9D9"
                textbutton "Cancelar":
                    xalign 0.92
                    action Return("back_class")
                textbutton "Continuar":
                    xalign 1.0
                    action Return("complete")
                    sensitive _completed


screen tl_typing_warmup_rounds_scene(sublesson_id="1_4b_typing_lab", lesson_id="lesson_1"):
    tag menu
    modal True

    default _letters = "abcdefghijklmnopqrstuvwxyzñ"

    $ _meta = lesson_get_sublesson_meta(sublesson_id, lesson_id=lesson_id)
    $ _title = str(_meta.get("title", "1.4B Typing Lab")) if isinstance(_meta, dict) else "1.4B Typing Lab"
    $ _state = tl_typing_warmup_state if isinstance(tl_typing_warmup_state, dict) else {}
    $ _round_total = int(_state.get("rounds_total", 3) or 3)
    $ _round_index = int(_state.get("round_index", 1) or 1)
    $ _done_rounds = int(_state.get("rounds_done", 0) or 0)
    $ _idx = int(_state.get("index", 0) or 0)
    $ _seq = list(_state.get("sequence", []) or [])
    $ _rpr = int(_state.get("reps_per_round", 10) or 10)
    $ _current = str(_state.get("current_letter", "") or "").upper()
    $ _done = bool(_state.get("done", False))
    $ _phase = str(_state.get("phase", "setup") or "setup")
    $ _error_active = float(time.time()) < float(_state.get("error_flash_until", 0.0) or 0.0)
    $ _hand_id, _finger_id = tl_warmup_finger_for_key(_current)
    $ _rows = tl_keyboard_mock_rows()
    $ _show_round = (_round_total if _round_index > _round_total else _round_index)
    $ _show_letter_idx = (_rpr if (_idx + 1) > _rpr else (_idx + 1))

    on "show" action Function(tl_warmup_prepare, 3, 10)

    if _phase == "run":
        for _k in _letters:
            key _k action Function(tl_warmup_press_key, _k)
        key "K_SPACE" action NullAction()
        key "K_F11" action NullAction()
        key "K_F5" action NullAction()
        key "dismiss" action NullAction()
        key "game_menu" action NullAction()
        key "rollback" action NullAction()

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#000000B8")

    frame:
        background Solid("#0D0D0DE8")
        xalign 0.5
        yalign 0.5
        xsize 1180
        ysize 650
        padding (30, 24, 30, 24)

        vbox:
            spacing 14

            text _title size 34 color "#F5F5F5" xalign 0.5

            frame:
                background Solid("#1E1E1EE6")
                xfill True
                ysize 122
                padding (16, 10, 16, 10)
                vbox:
                    spacing 6
                    hbox:
                        xfill True
                        text "Warmup dedos · asdf | jklñ" size 22 color "#D6D6D6"
                        text ("Ronda [_show_round]/[_round_total] · Letra [_show_letter_idx]/[_rpr]" if _phase == "run" else "Modo preparación") size 18 color "#C9D8F8" xalign 1.0
                    hbox:
                        xfill True
                        text (_current if not _done else "✓") size 58 color "#F1F1F1" xalign 0.5
                    if _error_active:
                        text "✖" size 38 color "#FF4D4D" xalign 0.5
                    else:
                        text " " size 38 xalign 0.5

            hbox:
                spacing 8
                xalign 0.5
                text "Repeticiones:" size 18 color "#D9D9D9" yalign 0.5
                textbutton "3" action Function(tl_warmup_set_rounds, 3) sensitive (_phase != "run")
                textbutton "4" action Function(tl_warmup_set_rounds, 4) sensitive (_phase != "run")
                textbutton "5" action Function(tl_warmup_set_rounds, 5) sensitive (_phase != "run")
                text "Completadas: [_done_rounds]" size 18 color "#BEECC6" yalign 0.5

            frame:
                background Solid("#151515EE")
                xfill True
                ysize 250
                padding (14, 14, 14, 14)
                vbox:
                    spacing 8
                    text "Teclado simulado (tecla objetivo en rojo)" size 24 color "#D6D6D6"
                    for _row in _rows:
                        hbox:
                            spacing 6
                            xalign 0.5
                            for _key in _row:
                                $ _w = 380 if _key == "ESPACIO" else 56
                                $ _is_target = (str(_key).strip().lower() == str(_current).strip().lower())
                                frame:
                                    background Solid("#A21E1E" if _is_target else tl_key_color_for(_key))
                                    xsize _w
                                    ysize 42
                                    text _key size 18 color "#F8F8F8" xalign 0.5 yalign 0.5

            frame:
                background Solid("#181818EE")
                xfill True
                ysize 165
                padding (16, 10, 16, 0)
                hbox:
                    spacing 42
                    xalign 0.5
                    yalign 1.0
                    vbox:
                        spacing 6
                        text "Mano izquierda" size 22 color "#D6D6D6" xalign 0.5
                        hbox:
                            spacing 8
                            for _name, _height in [("Meñique", 96), ("Anular", 126), ("Medio", 136), ("Índice", 118), ("Pulgar", 78)]:
                                $ _active = (_hand_id == "left" and _finger_id == _name.lower())
                                vbox:
                                    spacing 4
                                    frame:
                                        background Solid("#4A1F1F" if _active else "#2A2A2A")
                                        xsize 70
                                        ysize 24
                                        text _name size 15 color "#CFCFCF" xalign 0.5 yalign 0.5
                                    fixed:
                                        xsize 70
                                        ysize 130
                                        frame:
                                            background Solid("#5B8BD8")
                                            xsize 46
                                            ysize _height
                                            xalign 0.5
                                            yalign 1.0
                                        if _active:
                                            frame:
                                                background Solid("#D32F2F")
                                                xsize 18
                                                ysize 18
                                                xalign 0.5
                                                yalign 0.2
                    vbox:
                        spacing 6
                        text "Mano derecha" size 22 color "#D6D6D6" xalign 0.5
                        hbox:
                            spacing 8
                            for _name, _height in [("Pulgar", 78), ("Índice", 118), ("Medio", 136), ("Anular", 126), ("Meñique", 96)]:
                                $ _active = (_hand_id == "right" and _finger_id == _name.lower())
                                vbox:
                                    spacing 4
                                    frame:
                                        background Solid("#4A1F1F" if _active else "#2A2A2A")
                                        xsize 70
                                        ysize 24
                                        text _name size 15 color "#CFCFCF" xalign 0.5 yalign 0.5
                                    fixed:
                                        xsize 70
                                        ysize 130
                                        frame:
                                            background Solid("#5B8BD8")
                                            xsize 46
                                            ysize _height
                                            xalign 0.5
                                            yalign 1.0
                                        if _active:
                                            frame:
                                                background Solid("#D32F2F")
                                                xsize 18
                                                ysize 18
                                                xalign 0.5
                                                yalign 0.2

            hbox:
                xfill True
                text ("Pulsa Iniciar para entrar al modo teclado puro." if _phase != "run" else "Pulsa la letra correcta para avanzar (si fallas, aparece cruz).") size 18 color "#D9D9D9"
                textbutton "Iniciar":
                    xalign 0.88
                    action Function(tl_warmup_start)
                    sensitive (_phase != "run")
                textbutton "Salir":
                    xalign 0.92
                    action Return("back_class")
                textbutton "Continuar":
                    xalign 1.0
                    action Return("complete")
                    sensitive _done
