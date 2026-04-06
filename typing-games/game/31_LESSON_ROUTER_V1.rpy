# ===========================================================
# 31_LESSON_ROUTER_V1.rpy
# Capa de Engine/Lógica (Fase 2B): router de sublecciones
# ===========================================================

label tl_route_selected_sublesson:
    $ _selected = str(tl_selected_sublesson or "").strip().lower()
    if len(_selected) == 0:
        return "back_class"

    $ _meta = lesson_get_sublesson_meta(_selected, lesson_id="lesson_1")
    if not isinstance(_meta, dict) or len(_meta.keys()) == 0:
        return "error"

    $ _scene_type = str(_meta.get("scene_type", "placeholder") or "placeholder").strip().lower()
    $ _state = str(_meta.get("state", "placeholder") or "placeholder").strip().lower()
    $ _result = "back_class"

    if _scene_type == "intro_dialogue" and _selected == "1_1_intro":
        call screen tl_sublesson_intro_screen
        $ _result = _return
    else:
        $ _sub_id = str(_meta.get("id", _selected))
        $ _sub_title = str(_meta.get("title", _selected))
        $ _objective = str(_meta.get("objective", "Contenido temporal."))
        $ _summary = "Sublección en construcción. Placeholder activo para la nueva arquitectura."
        if _state == "real":
            $ _summary = "Contenido real definido en DB, pendiente de escena dedicada."

        call screen tl_sublesson_content_screen(
            sub_id=_sub_id,
            sub_title=_sub_title,
            objective=_objective,
            summary=_summary,
            next_hint="Continuará en siguientes fases."
        )
        $ _result = _return

    if _result == "complete":
        $ _ok = lesson_complete(_selected, lesson_id="lesson_1", module_id="clases")
        if not _ok:
            return "error"
        return "complete"
    elif _result == "back_class":
        return "back_class"
    else:
        return "error"

