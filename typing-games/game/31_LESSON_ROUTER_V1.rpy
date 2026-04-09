# ===========================================================
# 31_LESSON_ROUTER_V1.rpy
# Capa de Engine/Lógica (Fase 2B): router de sublecciones
# ===========================================================

label tl_route_selected_sublesson:
    $ _has_return_stack = bool(len(renpy.game.context().return_stack))
    $ _selected = str(tl_selected_sublesson or "").strip().lower()
    if len(_selected) == 0:
        if _has_return_stack:
            return "back_class"
        jump tl_classes_lesson_panel_flow

    $ _meta = lesson_get_sublesson_meta(_selected, lesson_id="lesson_1")
    if not isinstance(_meta, dict) or len(_meta.keys()) == 0:
        if _has_return_stack:
            return "error"
        jump tl_classes_lesson_panel_flow

    $ _scene_type = str(_meta.get("scene_type", "placeholder") or "placeholder").strip().lower()
    $ _result = "back_class"

    if _scene_type in ("intro_dialogue", "lesson_dialogue"):
        call screen tl_lesson_intro_scene(
            sublesson_id=_selected,
            lesson_id="lesson_1"
        )
        $ _result = _return
    elif _scene_type == "typing_keyboard_mock":
        call screen tl_typing_keyboard_mock_scene(
            sublesson_id=_selected,
            lesson_id="lesson_1"
        )
        $ _result = _return
    elif _scene_type == "typing_warmup_rounds":
        call screen tl_typing_warmup_rounds_scene(
            sublesson_id=_selected,
            lesson_id="lesson_1"
        )
        $ _result = _return
    else:
        call screen tl_lesson_placeholder_scene(
            sublesson_id=_selected,
            lesson_id="lesson_1"
        )
        $ _result = _return

    if _result == "complete":
        $ _ok = lesson_complete(_selected, lesson_id="lesson_1", module_id="clases")
        if not _ok:
            if _has_return_stack:
                return "error"
            jump tl_classes_lesson_panel_flow
        if _has_return_stack:
            return "complete"
        jump tl_classes_lesson_panel_flow
    elif _result == "back_class" or _result is None:
        if _has_return_stack:
            return "back_class"
        jump tl_classes_lesson_panel_flow
    else:
        if _has_return_stack:
            return "back_class"
        jump tl_classes_lesson_panel_flow
