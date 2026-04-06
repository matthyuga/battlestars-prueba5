# ===========================================================
# 41_LESSON_SCENES_V1.rpy
# Capa Visual (Fase 3B): escenas de lecciones
# ===========================================================

screen tl_lesson_intro_scene(sublesson_id="1_1_intro", lesson_id="lesson_1"):
    tag menu
    modal True

    $ _meta = lesson_get_sublesson_meta(sublesson_id, lesson_id=lesson_id)
    $ _steps = _meta.get("steps", []) if isinstance(_meta, dict) else []
    $ _last = max(0, len(_steps) - 1)
    $ _safe_page = max(0, min(_last, int(tl_intro_page if tl_intro_page is not None else 0)))
    $ _seg = lesson_get_segment(sublesson_id, _safe_page, lesson_id=lesson_id)
    $ _title = str(_seg.get("title", _meta.get("title", "Introducción"))) if isinstance(_seg, dict) else str(_meta.get("title", "Introducción"))
    $ _points = _seg.get("points", []) if isinstance(_seg, dict) else []
    $ _teacher_line = str(_seg.get("teacher_line", "Continuemos con el módulo.")) if isinstance(_seg, dict) else "Continuemos con el módulo."

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

