# ===========================================================
# 90_LEGACY_LESSONS_V1.rpy
# Legacy: implementación anterior de lecciones/sublecciones (referencia)
# Nota: NO forma parte del flujo activo.
# Flujo activo: 21_LESSONS_DB_V1 + 30_LESSON_ENGINE_V1 + 31_LESSON_ROUTER_V1 + 41_LESSON_SCENES_V1.
# ===========================================================

screen tl_sublesson_intro_screen():
    tag menu
    modal True

    $ _segments = [
        {
            "title": u"Introducción a la escritura al tacto",
            "points": [
                u"Escribir sin mirar el teclado.",
                u"Construir memoria muscular paso a paso.",
                u"Priorizar precisión antes que velocidad.",
            ],
            "teacher": u"Comenzamos con base sólida: postura, ritmo y control.",
        },
        {
            "title": u"Postura inicial",
            "points": [
                u"Espalda recta y hombros relajados.",
                u"Dedos base en A S D F y J K L Ñ.",
                u"Pulgares preparados para la barra espaciadora.",
            ],
            "teacher": u"Una buena postura evita fatiga y mejora tu estabilidad al teclear.",
        },
        {
            "title": u"Técnica de práctica",
            "points": [
                u"Pulsa suave y vuelve al punto base.",
                u"Mantén respiración y ritmo constante.",
                u"No aceleres hasta dominar los movimientos.",
            ],
            "teacher": u"Si mantienes ritmo, cada repetición te hará más preciso.",
        },
        {
            "title": u"Errores comunes",
            "points": [
                u"Mirar el teclado en cada pulsación.",
                u"Tensionar manos, brazos u hombros.",
                u"Golpear teclas con fuerza innecesaria.",
            ],
            "teacher": u"Los errores son parte del proceso; lo importante es corregir con calma.",
        },
        {
            "title": u"Listo para empezar",
            "points": [
                u"Objetivo inmediato: constancia y exactitud.",
                u"Haz pausas breves durante la práctica.",
                u"Al final revisaremos avance y hábitos.",
            ],
            "teacher": u"Excelente, ya estás listo. Avancemos a la primera práctica guiada.",
        },
    ]
    $ _last = max(0, len(_segments) - 1)
    $ _safe_page = max(0, min(_last, int(tl_intro_page if tl_intro_page is not None else 0)))
    $ _seg = _segments[_safe_page] if len(_segments) > 0 else {"title": u"Introducción", "points": [u"Contenido no disponible"], "teacher": u"Continuemos."}
    $ _title = unicode(_seg.get("title", u"Introducción"))
    $ _teacher_line = unicode(_seg.get("teacher", u"Continuemos con el módulo."))
    $ _points = _seg.get("points", [])
    $ _teacher_name = tl_selected_teacher.title() if tl_selected_teacher else "Docente"
    if tl_selected_teacher == "haru":
        $ _teacher_portrait = tl_asset("gui/characters-sakura-sunshine/male/teachers/Haru.png")
        if not _teacher_portrait:
            $ _teacher_portrait = tl_asset("gui/characters-sakura-sunshine/female/teachers/Ayame.png")
    elif tl_selected_teacher == "misaki":
        $ _teacher_portrait = tl_asset("gui/characters-sakura-sunshine/female/teachers/Misaki.png")
        if not _teacher_portrait:
            $ _teacher_portrait = tl_asset("gui/characters-sakura-sunshine/male/teachers/Masato.png")
    else:
        $ _teacher_portrait = None

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#00000090")

    frame:
        xalign 0.5
        yalign 0.34
        xsize 980
        ysize 300
        background Solid("#151019EE")

        vbox:
            spacing 12
            xalign 0.5
            yalign 0.10

            text "[_title]" size 44 color "#FFD7F1" xalign 0.5

            if len(_points) > 0:
                text "• [_points[0]]" size 30 xalign 0.5
            if len(_points) > 1:
                text "• [_points[1]]" size 30 xalign 0.5
            if len(_points) > 2:
                text "• [_points[2]]" size 30 xalign 0.5

            text "Tramo [(_safe_page + 1)]/[max(1, len(_segments))]" size 22 color "#DCCEE8" xalign 0.5

    frame:
        xalign 0.5
        yalign 1.0
        yoffset -26
        xsize 1140
        ysize 230
        background Solid("#17121EEC")

        hbox:
            spacing 16
            xalign 0.5
            yalign 0.5

            vbox:
                spacing 8
                xsize 190

                frame:
                    xsize 190
                    ysize 150
                    background Solid("#241D2C")
                    if _teacher_portrait:
                        add _teacher_portrait fit "contain" xalign 0.5 yalign 0.5
                    else:
                        text "Sin retrato" xalign 0.5 yalign 0.5 size 22 color "#E8D9F0"

                frame:
                    xsize 190
                    ysize 34
                    background Solid("#2A2230")
                    text "[_teacher_name]" xalign 0.5 yalign 0.5 size 21 color "#FFD7F1"

            vbox:
                spacing 10
                yalign 0.5

                frame:
                    xsize 680
                    ysize 96
                    background Solid("#211A29")
                    text "[_teacher_line]" xalign 0.03 yalign 0.5 size 24 color "#F7E8FF"

                hbox:
                    spacing 14
                    textbutton "Continuar" action SetVariable("tl_intro_page", min(_last, _safe_page + 1)) sensitive (_safe_page < _last)
                    textbutton "Avanzar" action [SetVariable("tl_intro_page", 0), Return("complete")] sensitive (_safe_page == _last)
                    textbutton "Atrás" action [SetVariable("tl_intro_page", 0), Return("back_class")]


screen tl_sublesson_content_screen(sub_id="", sub_title="", objective="", summary="", next_hint=""):
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#00000099")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 980
        ysize 580
        background Solid("#151019EE")

        vbox:
            spacing 14
            xalign 0.5
            yalign 0.08

            text "Lección 1 · [sub_title]" size 40 color "#FFD7F1" xalign 0.5
            text "Submódulo: [sub_id]" size 22 color "#E8D9F0" xalign 0.5

            frame:
                xsize 860
                ysize 230
                background Solid("#221A2CEB")
                vbox:
                    spacing 10
                    xalign 0.5
                    yalign 0.5
                    text "Objetivo: [objective]" size 24 xalign 0.5 text_align 0.5
                    text "[summary]" size 22 xalign 0.5 text_align 0.5
                    if len((next_hint or "").strip()) > 0:
                        text "Siguiente paso recomendado: [next_hint]" size 20 color "#DCCEE6" xalign 0.5 text_align 0.5

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Completar subsección" action Return("complete")
                textbutton "Volver a clase" action Return("back_class")


screen tl_lessons_mock_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
        text "⚠ Falta asset: images/sakura-sunshine/sakura-sunshine-academy-salon.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1120
        ysize 640
        background Solid("#151019DE")

        hbox:
            spacing 24
            xalign 0.5
            yalign 0.05

            vbox:
                spacing 10
                xsize 560
                $ _c11 = get_check("clases", "lesson_1", "1_1_intro")
                $ _c12 = get_check("clases", "lesson_1", "1_2_home_row")
                $ _c13 = get_check("clases", "lesson_1", "1_3_results")
                $ _c14 = get_check("clases", "lesson_1", "1_4_keys_exercise")
                $ _c15 = get_check("clases", "lesson_1", "1_5_exam_help")
                $ _c16 = get_check("clases", "lesson_1", "1_6_words_exercise")
                $ _c17 = get_check("clases", "lesson_1", "1_7_phrases_exercise")
                $ _lesson_done = sum([1 for _v in [_c11, _c12, _c13, _c14, _c15, _c16, _c17] if _v])

                text "Clases · Lección 1 (mock)" size 38 color "#FFD7F1"
                text "Progreso Lección 1: [_lesson_done]/7" size 24 color "#EADAF2"
                textbutton "1.1 Introducción{}".format("  ✓" if _c11 else "") action Function(set_check, "clases", "lesson_1", "1_1_intro", True)
                textbutton "1.2 Teclas de la Fila Central{}".format("  ✓" if _c12 else "") action Function(set_check, "clases", "lesson_1", "1_2_home_row", True)
                textbutton "1.3 Ver resultados{}".format("  ✓" if _c13 else "") action Function(set_check, "clases", "lesson_1", "1_3_results", True)
                textbutton "1.4 Ejercicio de Teclas{}".format("  ✓" if _c14 else "") action Function(set_check, "clases", "lesson_1", "1_4_keys_exercise", True)
                textbutton "1.5 Ayuda: Exámenes{}".format("  ✓" if _c15 else "") action Function(set_check, "clases", "lesson_1", "1_5_exam_help", True)
                textbutton "1.6 Ejercicio de Palabras{}".format("  ✓" if _c16 else "") action Function(set_check, "clases", "lesson_1", "1_6_words_exercise", True)
                textbutton "1.7 Ejercicio de Párrafos{}".format("  ✓" if _c17 else "") action Function(set_check, "clases", "lesson_1", "1_7_phrases_exercise", True)

                null height 18
                text "Puedes usar capturas de Typing Master en esta etapa (sí, totalmente)." size 20 color "#DCCEE6"

                hbox:
                    spacing 18
                    textbutton "Probar Typing Lab" action Return("open_typing_lab")
                    textbutton "Marcar todo Lección 1" action [
                        Function(set_check, "clases", "lesson_1", "1_1_intro", True),
                        Function(set_check, "clases", "lesson_1", "1_2_home_row", True),
                        Function(set_check, "clases", "lesson_1", "1_3_results", True),
                        Function(set_check, "clases", "lesson_1", "1_4_keys_exercise", True),
                        Function(set_check, "clases", "lesson_1", "1_5_exam_help", True),
                        Function(set_check, "clases", "lesson_1", "1_6_words_exercise", True),
                        Function(set_check, "clases", "lesson_1", "1_7_phrases_exercise", True),
                    ]
                    textbutton "Finalizar Lección 1" action Return("complete_lesson_1") sensitive (_lesson_done >= 7)
                    textbutton "Volver al hub" action Return("back")

            vbox:
                spacing 10
                text "Preview de apoyo" size 30 color "#FFD7F1"

                $ slide = tl_asset("images/tl/tm_lesson_slide_01.png")
                if slide:
                    add slide fit "contain" xsize 480 ysize 360
                else:
                    frame:
                        xsize 480
                        ysize 360
                        background Solid("#2A2230")
                        text "Sube aquí: images/tl/tm_lesson_slide_01.png" xalign 0.5 yalign 0.5 size 22
