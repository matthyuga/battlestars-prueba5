# Typing Legends / Sakura Sunshine Academy
# Arquitectura base (MVP):
# 1) Menú inicial Typing Legends (Epic bloqueado, Sakura activo)
# 2) Puerta/entrada Sakura
# 3) Registro de jugador (sexo + modo experiencia)
# 4) Hub de academia con módulos
# 5) Vista de lecciones (aula con desenfoque + oscurecido suave)

init -15 python:
    import renpy.store as S

    def tl_asset(path):
        """Retorna path si existe; si no, retorna None para fallback visual."""
        return path if renpy.loadable(path) else None

    def tl_set_mode_guard(gender, mode):
        """Regla actual definida por diseño:
        - si género = none -> solo modo 1
        """
        g = str(gender or "none")
        try:
            m = int(mode)
        except:
            m = 1
        if g == "none":
            return 1
        return 1 if m not in (1, 2, 3) else m


default tl_player_name = ""
default tl_player_gender = "none"       # male | female | none
default tl_experience_mode = 1           # 1=lore off, 2=lore normal, 3=lore+romance
default tl_current_module = "Clases"
default tl_selected_academy = "sakura"  # epic | sakura

# Rutas de imagen recomendadas:
# typing-games/game/images/tl/
#   typing-games-menu.jpg
#   sakura-sunshine/sakura-sunshine-academy-entrada.jpg
#   sakura-sunshine/sakura-sunshine-academy-pasillo.jpg
#   sakura-sunshine/sakura-sunshine-academy-salon.jpg
#   tm_lesson_slide_01.png ...

image tl_fallback_dark = Solid("#131321")
image tl_fallback_rose = Solid("#2A1D2D")

transform tl_soft_focus:
    blur 2.6
    alpha 0.96

screen tl_main_menu_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/typing-games-menu.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_dark"
        text "⚠ Falta asset: images/typing-games-menu.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

    # Capa para contraste
    add Solid("#00000012")

    # Hotspots sobre puertas (coordenadas pensadas para 1280x720 aprox)
    # Epic: seleccionable pero bloqueado al iniciar (solo Sakura habilita START)
    button:
        xpos 120
        ypos 170
        xsize 420
        ysize 380
        background Solid("#FFFFFF00")
        action SetVariable("tl_selected_academy", "epic")

    # Sakura: seleccionable
    button:
        xpos 700
        ypos 170
        xsize 440
        ysize 380
        background Solid("#FFFFFF00")
        action SetVariable("tl_selected_academy", "sakura")

    # Indicadores visuales de selección (sin textos superpuestos)
    if tl_selected_academy == "epic":
        frame:
            xpos 112
            ypos 162
            xsize 436
            ysize 396
            background Solid("#5DA9FF22")

    if tl_selected_academy == "sakura":
        frame:
            xpos 692
            ypos 162
            xsize 456
            ysize 396
            background Solid("#FF8ACD22")

    # START en el botón central de la imagen
    button:
        xpos 430
        ypos 540
        xsize 420
        ysize 110
        background Solid("#FFFFFF00")
        action Return("goto_sakura_gate")
        sensitive (tl_selected_academy == "sakura")

    textbutton "SETTINGS" action ShowMenu("preferences") xpos 170 ypos 655

screen tl_sakura_gate_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-entrada.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"
        text "⚠ Falta asset: images/sakura-sunshine/sakura-sunshine-academy-entrada.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

    add Solid("#00000010")

    # Recuadro sobre botón ENTER de la imagen (1280x720)
    button:
        xpos 430
        ypos 560
        xsize 420
        ysize 110
        background Solid("#FFFFFF00")
        action Return("register")

    textbutton "Volver" action Return("back") xpos 110 ypos 650

screen tl_registration_screen():
    tag menu
    modal True
    default _reg_step = 1

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"
        text "⚠ Falta asset: images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1060
        ysize 600
        background Solid("#1B1524DD")

        vbox:
            spacing 18
            xalign 0.5
            yalign 0.5

            text "Registro de Jugador" xalign 0.5 size 52 color "#FFD7F1"
            text "Paso [_reg_step]/3" size 24 color "#D0BFD6" xalign 0.5

            if _reg_step == 1:
                hbox:
                    spacing 24
                    xalign 0.5
                    text "Nombre:" size 32
                    input value VariableInputValue("tl_player_name") length 20 allow " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZáéíóúÁÉÍÓÚñÑ0123456789_-." xmaximum 520

                text "Debes ingresar un nombre para continuar." size 22 color "#D0BFD6"

                hbox:
                    spacing 20
                    xalign 0.5
                    textbutton "Siguiente" action SetScreenVariable("_reg_step", 2) sensitive (len((tl_player_name or "").strip()) > 0)
                    textbutton "Volver" action Return("back")

            elif _reg_step == 2:
                text "Sexo del jugador" size 32
                hbox:
                    spacing 18
                    xalign 0.5
                    textbutton "Masculino{}".format(" ✓" if tl_player_gender == "male" else "") action SetVariable("tl_player_gender", "male")
                    textbutton "Femenino{}".format(" ✓" if tl_player_gender == "female" else "") action SetVariable("tl_player_gender", "female")
                    textbutton "Ninguno{}".format(" ✓" if tl_player_gender == "none" else "") action SetVariable("tl_player_gender", "none")

                hbox:
                    spacing 20
                    xalign 0.5
                    textbutton "Siguiente" action SetScreenVariable("_reg_step", 3)
                    textbutton "Atrás" action SetScreenVariable("_reg_step", 1)

            else:
                text "Modo de experiencia" size 32
                hbox:
                    spacing 18
                    xalign 0.5
                    textbutton "1) Lore desactivado{}".format(" ✓" if tl_experience_mode == 1 else "") action SetVariable("tl_experience_mode", 1)
                    textbutton "2) Lore normal{}".format(" ✓" if tl_experience_mode == 2 else "") action SetVariable("tl_experience_mode", 2)
                    textbutton "3) Lore + romance{}".format(" ✓" if tl_experience_mode == 3 else "") action SetVariable("tl_experience_mode", 3)

                text "Regla activa: si eliges 'Ninguno', el modo se fuerza a 1 (sin lore ni romance)." size 22 color "#D0BFD6"
                text "Estado actual -> Nombre: [tl_player_name] | Sexo: [tl_player_gender] | Modo: [tl_experience_mode]" size 24 color "#F6E5FF"

                hbox:
                    spacing 20
                    xalign 0.5
                    textbutton "Continuar" action Return("continue") sensitive (len((tl_player_name or "").strip()) > 0)
                    textbutton "Atrás" action SetScreenVariable("_reg_step", 2)

screen tl_sakura_hub_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"
        text "⚠ Falta asset: images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

    add Solid("#0000005F")

    text "Sakura Sunshine Academy" xalign 0.5 yalign 0.06 size 56 color "#FFD7F1" outlines [(2, "#5a1d4a", 0, 0)]

    if tl_player_name:
        text "Jugador: [tl_player_name]  |  Sexo: [tl_player_gender]  |  Modo: [tl_experience_mode]" xalign 0.5 yalign 0.13 size 22
    else:
        text "Jugador: Invitado  |  Sexo: [tl_player_gender]  |  Modo: [tl_experience_mode]" xalign 0.5 yalign 0.13 size 22

    # Opciones (tuerca) separado arriba a la derecha
    textbutton "⚙" action ShowMenu("preferences") xalign 0.965 yalign 0.05

    frame:
        xalign 0.13
        yalign 0.56
        xsize 420
        ysize 610
        background Solid("#1A1120D8")

        vbox:
            spacing 14
            xalign 0.5
            yalign 0.06

            text "Módulos" size 40 color "#FFD7F1" xalign 0.5

            textbutton "Clases" action Return("go_lessons")
            textbutton "Práctica" action Return("go_practice")
            textbutton "Exámenes" action Return("go_exams")
            textbutton "Actividades" action Return("go_activities")
            textbutton "Diario" action Return("go_diary")
            textbutton "Biblioteca" action Return("go_library")
            textbutton "Salir al menú" action Return("to_main")

    frame:
        xalign 0.62
        yalign 0.60
        xsize 680
        ysize 560
        background Solid("#251A2EDD")

        vbox:
            spacing 14
            xalign 0.5
            yalign 0.08

            text "Vista previa del módulo" size 36 color "#FFD7F1" xalign 0.5
            text "Módulo actual: [tl_current_module]" size 28 xalign 0.5
            $ _mod_progress = get_check_progress(tl_current_module)
            text "Progreso académico (checks): [_mod_progress['done']]/[_mod_progress['total']]" size 22 xalign 0.5
            text "En esta etapa construiremos primero Clases (lecciones)." size 22 xalign 0.5
            text "Luego conectamos Práctica / Exámenes / Actividades / Diario / Biblioteca." size 20 xalign 0.5

screen tl_lessons_mock_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
        text "⚠ Falta asset: images/sakura-sunshine/sakura-sunshine-academy-salon.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

    # Oscurecido para que la UI se lea mejor
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

screen tl_diary_checklist_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"
        text "⚠ Falta asset: images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

    add Solid("#00000088")
    $ _checks = _academic_ensure_store()

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1120
        ysize 640
        background Solid("#151019DE")

        vbox:
            spacing 10
            xalign 0.5
            yalign 0.04

            text "Diario académico · Checklist" size 42 color "#FFD7F1" xalign 0.5

            viewport:
                draggable True
                mousewheel True
                ymaximum 470

                vbox:
                    spacing 8
                    for _module_id, _lessons in _checks.items():
                        $ _mod_prog = get_check_progress(_module_id)
                        text "[_module_id.title()]  [_mod_prog['done']]/[_mod_prog['total']]" size 28 color "#F7E8FF"
                        for _lesson_id, _steps in _lessons.items():
                            $ _lesson_done = sum([1 for _v in _steps.values() if _v])
                            $ _lesson_total = len(_steps)
                            text "  - [_lesson_id]  [_lesson_done]/[_lesson_total]" size 22 color "#DDD0E7"
                            for _step_id, _done in _steps.items():
                                text "      {} {}".format("✓" if _done else "□", _step_id) size 19 color ("#8FFFAD" if _done else "#D2C6DE")

            hbox:
                spacing 16
                xalign 0.5
                textbutton "Volver al hub" action Return("back")

screen tl_social_profile_screen():
    tag menu
    modal True

    default _aff_tip = "Pasa el cursor por una barra para ver la afinidad actual."

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"
        text "⚠ Falta asset: images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1160
        ysize 660
        background Solid("#151019DE")

        vbox:
            spacing 10
            xalign 0.5
            yalign 0.04

            text "Ficha social · Afinidad por personaje" size 42 color "#FFD7F1" xalign 0.5
            text "Sistema social separado del académico (solo barras c0..c10)." size 20 color "#E5D5EE" xalign 0.5

            viewport:
                draggable True
                mousewheel True
                ymaximum 470

                vbox:
                    spacing 8
                    for _cid in AFFINITY_CHARACTER_IDS:
                        $ _pts = get_affinity(_cid)
                        $ _rom_enabled = is_romance_enabled(tl_experience_mode, tl_player_gender, _cid)
                        $ _rom_msg = get_romance_lock_message(tl_experience_mode, tl_player_gender, _cid)
                        hbox:
                            spacing 12
                            xalign 0.5

                            text "[_cid.title()]" size 24 xminimum 160

                            frame:
                                xsize 220
                                ysize 30
                                background Solid("#00000000")
                                add get_affinity_bar_image(_cid) xalign 0.0 yalign 0.5

                                button:
                                    xfill True
                                    yfill True
                                    background Solid("#00000000")
                                    hovered SetScreenVariable("_aff_tip", "Afinidad actual {} / 10 ({})".format(_pts, _cid))
                                    unhovered SetScreenVariable("_aff_tip", "Pasa el cursor por una barra para ver la afinidad actual.")
                                    action NullAction()

                            textbutton "+ Interacción" action Function(award_affinity_event, _cid, "interaction_success")
                            textbutton "+ Misión" action Function(award_affinity_event, _cid, "social_mission_success")

                            if _rom_enabled:
                                frame:
                                    xsize 48
                                    ysize 48
                                    background Solid("#00000000")
                                    add get_romance_heart_image(_cid) fit "contain" xalign 0.5 yalign 0.5
                                textbutton "+ Romance" action Function(add_romance, _cid, 1)
                            else:
                                text _rom_msg size 16 color "#FFB9D5" xmaximum 220

            text "[_aff_tip]" size 19 color "#FFD7F1" xalign 0.5

            hbox:
                spacing 16
                xalign 0.5
                textbutton "Volver al hub" action Return("back")

screen tl_practice_mode_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 880
        ysize 520
        background Solid("#151019DE")

        vbox:
            spacing 16
            xalign 0.5
            yalign 0.08

            text "Práctica · Modo libre" size 42 color "#FFD7F1" xalign 0.5
            text "Selecciona modo de práctica para Typing Lab" size 22 color "#E8D9F0" xalign 0.5

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Letras" action SetVariable("typing_lab_selected_mode", "letters")
                textbutton "Palabras" action SetVariable("typing_lab_selected_mode", "words")
                textbutton "Frases" action SetVariable("typing_lab_selected_mode", "phrases")

            text "Modo actual: [typing_lab_selected_mode]" size 24 xalign 0.5

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Iniciar práctica" action Return("start_practice")
                textbutton "Volver al hub" action Return("back")

screen tl_exam_entry_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 900
        ysize 520
        background Solid("#151019DE")

        vbox:
            spacing 16
            xalign 0.5
            yalign 0.08

            text "Examen académico · Intento 1" size 42 color "#FFD7F1" xalign 0.5
            text "Umbral de aprobación: 50 puntos" size 26 color "#FFE5B1" xalign 0.5
            text "Modo del examen: frases" size 22 color "#E8D9F0" xalign 0.5

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Rendir examen" action Return("start_exam")
                textbutton "Volver al hub" action Return("back")

screen tl_activities_quest_screen():
    tag menu
    modal True

    default _msg = "Completa la quest social para subir afinidad."

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"
    add Solid("#00000088")

    $ _quest_done = get_check("actividades", "activity_1", "quest_1")
    $ _airi_aff = get_affinity("airi")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 980
        ysize 580
        background Solid("#151019DE")

        vbox:
            spacing 14
            xalign 0.5
            yalign 0.08

            text "Actividades · Quest social 1" size 42 color "#FFD7F1" xalign 0.5
            text "Quest: Ayuda a Airi a ordenar notas para la clase." size 24 color "#E8D9F0" xalign 0.5
            text "Estado: {}".format("Completada ✓" if _quest_done else "Pendiente") size 24 xalign 0.5
            text "Afinidad Airi: [_airi_aff]/10" size 24 color "#FFD7F1" xalign 0.5

            if not _quest_done:
                textbutton "Completar quest (+1 afinidad Airi)" action [
                    Function(set_check, "actividades", "activity_1", "quest_1", True),
                    Function(award_affinity_event, "airi", "social_mission_success"),
                    SetScreenVariable("_msg", "Quest completada. +1 afinidad para Airi."),
                ] xalign 0.5
            else:
                text "Ya completaste esta quest en esta partida." size 20 color "#BEECC6" xalign 0.5

            text "[_msg]" size 20 color "#FFE5B1" xalign 0.5

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Ver ficha social" action [Hide("tl_activities_quest_screen"), Show("tl_social_profile_screen")]
                textbutton "Volver al hub" action Return("back")

screen tl_diary_tabs_screen():
    tag menu
    modal True

    default _tab = "academic"

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"
    add Solid("#00000088")

    $ _checks = _academic_ensure_store()

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1160
        ysize 660
        background Solid("#151019DE")

        vbox:
            spacing 10
            xalign 0.5
            yalign 0.04

            text "Diario" size 42 color "#FFD7F1" xalign 0.5

            hbox:
                spacing 12
                xalign 0.5
                textbutton "Académico (checks)" action SetScreenVariable("_tab", "academic")
                textbutton "Social (barras/corazón)" action SetScreenVariable("_tab", "social")

            if _tab == "academic":
                viewport:
                    draggable True
                    mousewheel True
                    ymaximum 470

                    vbox:
                        spacing 8
                        for _module_id, _lessons in _checks.items():
                            $ _mod_prog = get_check_progress(_module_id)
                            text "[_module_id.title()]  [_mod_prog['done']]/[_mod_prog['total']]" size 28 color "#F7E8FF"
                            for _lesson_id, _steps in _lessons.items():
                                $ _lesson_done = sum([1 for _v in _steps.values() if _v])
                                $ _lesson_total = len(_steps)
                                text "  - [_lesson_id]  [_lesson_done]/[_lesson_total]" size 22 color "#DDD0E7"
            else:
                viewport:
                    draggable True
                    mousewheel True
                    ymaximum 470

                    vbox:
                        spacing 8
                        for _cid in AFFINITY_CHARACTER_IDS:
                            $ _pts = get_affinity(_cid)
                            $ _rom_enabled = is_romance_enabled(tl_experience_mode, tl_player_gender, _cid)
                            hbox:
                                spacing 12
                                text "[_cid.title()]" size 24 xminimum 160
                                add get_affinity_bar_image(_cid) xsize 220 ysize 30
                                text "[_pts]/10" size 20 color "#FFD7F1"
                                if _rom_enabled:
                                    add get_romance_heart_image(_cid) xsize 38 ysize 38
                                    text "[get_romance(_cid)]/24" size 18 color "#FFB9D5"
                                else:
                                    text "[get_romance_lock_message(tl_experience_mode, tl_player_gender, _cid)]" size 16 color "#FFB9D5"

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Volver al hub" action Return("back")

screen tl_library_index_screen():
    tag menu
    modal True

    default _tab = "courses"

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1140
        ysize 650
        background Solid("#151019DE")

        vbox:
            spacing 10
            xalign 0.5
            yalign 0.04

            text "Biblioteca" size 42 color "#FFD7F1" xalign 0.5
            hbox:
                spacing 12
                xalign 0.5
                textbutton "Cursos" action SetScreenVariable("_tab", "courses")
                textbutton "Personajes" action SetScreenVariable("_tab", "characters")

            if _tab == "courses":
                vbox:
                    spacing 8
                    $ _cl = get_check_progress("clases")
                    $ _pr = get_check_progress("practica")
                    $ _ex = get_check_progress("examenes")
                    $ _ac = get_check_progress("actividades")
                    text "Clases · Desbloqueado · [_cl['done']]/[_cl['total']]" size 24
                    text "Práctica · Desbloqueado · [_pr['done']]/[_pr['total']]" size 24
                    text "Exámenes · Desbloqueado · [_ex['done']]/[_ex['total']]" size 24
                    text "Actividades · Desbloqueado · [_ac['done']]/[_ac['total']]" size 24
            else:
                viewport:
                    draggable True
                    mousewheel True
                    ymaximum 470

                    vbox:
                        spacing 8
                        for _cid in AFFINITY_CHARACTER_IDS:
                            $ _aff = get_affinity(_cid)
                            $ _unlocked = (_aff >= 1)
                            text "[_cid.title()] · {} · Afinidad: [_aff]/10".format("Desbloqueado" if _unlocked else "Bloqueado") size 22

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Volver al hub" action Return("back")

label tl_boot_start:
    $ _academic_ensure_store()
    $ _affinity_ensure_store()
    $ _romance_ensure_store()
    call screen tl_main_menu_screen
    if _return == "goto_sakura_gate":
        jump tl_sakura_gate
    jump tl_boot_start

label tl_sakura_gate:
    call screen tl_sakura_gate_screen
    if _return == "register":
        jump tl_player_registration
    if _return == "back":
        jump tl_boot_start
    jump tl_sakura_gate

label tl_player_registration:
    call screen tl_registration_screen
    if _return == "continue":
        $ tl_experience_mode = tl_set_mode_guard(tl_player_gender, tl_experience_mode)
        jump tl_sakura_hub
    if _return == "back":
        jump tl_sakura_gate
    jump tl_player_registration

label tl_sakura_hub:
    call screen tl_sakura_hub_screen

    if _return == "go_lessons":
        $ tl_current_module = "Clases"
        call screen tl_lessons_mock_screen
        if _return == "open_typing_lab":
            call typing_lab_start
        if _return == "complete_lesson_1":
            "Lección 1 completada con checks."
        jump tl_sakura_hub

    if _return == "go_practice":
        $ tl_current_module = "Práctica"
        call screen tl_practice_mode_screen
        if _return == "start_practice":
            call typing_lab_start
        jump tl_sakura_hub

    if _return == "go_exams":
        $ tl_current_module = "Exámenes"
        call screen tl_exam_entry_screen
        if _return == "start_exam":
            $ typing_lab_selected_mode = "phrases"
            call typing_lab_start
            $ _exam_score = int(typing_lab_state.get("total_score", 0) if isinstance(typing_lab_state, dict) else 0)
            if _exam_score >= 50:
                $ set_check("examenes", "exam_1", "attempt_1", True)
                "Examen aprobado. Puntaje: [_exam_score]"
            else:
                "Examen no aprobado. Puntaje: [_exam_score] (mínimo 50)."
        jump tl_sakura_hub

    if _return == "go_activities":
        $ tl_current_module = "Actividades"
        call screen tl_activities_quest_screen
        jump tl_sakura_hub

    if _return == "go_diary":
        $ tl_current_module = "Diario"
        call screen tl_diary_tabs_screen
        jump tl_sakura_hub

    if _return == "go_library":
        $ tl_current_module = "Biblioteca"
        call screen tl_library_index_screen
        jump tl_sakura_hub

    if _return == "to_main":
        jump tl_boot_start

    jump tl_sakura_hub
