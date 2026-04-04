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
#   portal_main.jpg
#   sakura_gate.jpg
#   sakura_hallway.jpg
#   sakura_classroom.jpg
#   tm_lesson_slide_01.png ...

image tl_fallback_dark = Solid("#131321")
image tl_fallback_rose = Solid("#2A1D2D")

transform tl_soft_focus:
    blur 2.6
    alpha 0.96

screen tl_main_menu_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/tl/portal_main.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_dark"
        text "⚠ Falta asset: images/tl/portal_main.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

    # Capa para contraste
    add Solid("#00000030")

    text "TYPING LEGENDS" xalign 0.5 yalign 0.08 size 68 color "#FFD884" outlines [(2, "#3a2200", 0, 0)]

    # Hotspots sobre puertas (coordenadas pensadas para 1280x720 aprox)
    # Epic: visible pero bloqueado
    button:
        xpos 165
        ypos 220
        xsize 360
        ysize 330
        background Solid("#FFFFFF00")
        hovered SetVariable("tl_selected_academy", "epic")
        action NullAction()

    # Sakura: seleccionable
    button:
        xpos 740
        ypos 220
        xsize 380
        ysize 330
        background Solid("#FFFFFF00")
        action SetVariable("tl_selected_academy", "sakura")

    # Indicadores de selección
    if tl_selected_academy == "epic":
        frame:
            xpos 150
            ypos 205
            xsize 390
            ysize 360
            background Solid("#5DA9FF33")
        text "Epic Spell Academy (bloqueado)" xalign 0.26 yalign 0.73 size 28
    else:
        text "Epic Spell Academy (bloqueado)" xalign 0.26 yalign 0.73 size 28 color "#DDDDDD"

    if tl_selected_academy == "sakura":
        frame:
            xpos 725
            ypos 205
            xsize 410
            ysize 360
            background Solid("#FF8ACD44")
        text "Sakura Sunshine Academy (seleccionada)" xalign 0.73 yalign 0.73 size 28 color "#FFD5EC"
    else:
        text "Sakura Sunshine Academy" xalign 0.73 yalign 0.73 size 28 color "#DDDDDD"

    # START usa el botón central de la imagen (recuadro invisible)
    button:
        xpos 495
        ypos 585
        xsize 290
        ysize 85
        background Solid("#FFFFFF00")
        action Return("goto_sakura_gate") if tl_selected_academy == "sakura" else NullAction()

    textbutton "SETTINGS" action ShowMenu("preferences") xalign 0.18 yalign 0.95

screen tl_sakura_gate_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/tl/sakura_gate.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"
        text "⚠ Falta asset: images/tl/sakura_gate.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

    add Solid("#00000022")

    text "SAKURA SUNSHINE ACADEMY" xalign 0.5 yalign 0.09 size 56 color "#FFD7F1" outlines [(2, "#5a1d4a", 0, 0)]

    # Recuadro sobre botón ENTER de la imagen
    button:
        xpos 500
        ypos 600
        xsize 280
        ysize 90
        background Solid("#FFFFFF00")
        action Return("register")

    textbutton "Volver" action Return("back") xalign 0.1 yalign 0.93

screen tl_registration_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/tl/sakura_hallway.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"
        text "⚠ Falta asset: images/tl/sakura_hallway.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

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

            hbox:
                spacing 24
                xalign 0.5
                text "Nombre:" size 32
                input value VariableInputValue("tl_player_name") length 20 allow " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZáéíóúÁÉÍÓÚñÑ0123456789_-." xmaximum 520

            text "Sexo del jugador" size 32
            hbox:
                spacing 18
                xalign 0.5
                textbutton "Masculino{}".format(" ✓" if tl_player_gender == "male" else "") action SetVariable("tl_player_gender", "male")
                textbutton "Femenino{}".format(" ✓" if tl_player_gender == "female" else "") action SetVariable("tl_player_gender", "female")
                textbutton "Ninguno{}".format(" ✓" if tl_player_gender == "none" else "") action SetVariable("tl_player_gender", "none")

            text "Modo de experiencia" size 32
            hbox:
                spacing 18
                xalign 0.5
                textbutton "1) Lore desactivado{}".format(" ✓" if tl_experience_mode == 1 else "") action SetVariable("tl_experience_mode", 1)
                textbutton "2) Lore normal{}".format(" ✓" if tl_experience_mode == 2 else "") action SetVariable("tl_experience_mode", 2)
                textbutton "3) Lore + romance{}".format(" ✓" if tl_experience_mode == 3 else "") action SetVariable("tl_experience_mode", 3)

            text "Regla activa: si eliges 'Ninguno', el modo se fuerza a 1 (sin lore ni romance)." size 22 color "#D0BFD6"
            text "Estado actual -> Sexo: [tl_player_gender] | Modo: [tl_experience_mode]" size 24 color "#F6E5FF"

            hbox:
                spacing 20
                xalign 0.5
                textbutton "Continuar" action Return("continue")
                textbutton "Volver" action Return("back")

screen tl_sakura_hub_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/tl/sakura_hallway.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"
        text "⚠ Falta asset: images/tl/sakura_hallway.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

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
            text "Progreso académico (checks): [(_mod_progress['done'])]/[(_mod_progress['total'])]" size 22 xalign 0.5
            text "En esta etapa construiremos primero Clases (lecciones)." size 22 xalign 0.5
            text "Luego conectamos Práctica / Exámenes / Actividades / Diario / Biblioteca." size 20 xalign 0.5

screen tl_lessons_mock_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/tl/sakura_classroom.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
        text "⚠ Falta asset: images/tl/sakura_classroom.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

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
                text "Clases · Lección 1 (mock)" size 38 color "#FFD7F1"
                text "1.1 Introducción" size 30
                text "1.2 Teclas de la Fila Central" size 30
                text "1.3 Ver resultados" size 30
                text "1.4 Ejercicio de Teclas" size 30
                text "1.5 Ayuda: Exámenes" size 30
                text "1.6 Ejercicio de Palabras" size 30
                text "1.7 Ejercicio de Párrafos" size 30

                null height 18
                text "Puedes usar capturas de Typing Master en esta etapa (sí, totalmente)." size 20 color "#DCCEE6"

                hbox:
                    spacing 18
                    textbutton "Probar Typing Lab" action Return("open_typing_lab")
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

label tl_boot_start:
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
        jump tl_sakura_hub

    if _return == "go_practice":
        $ tl_current_module = "Práctica"
        "Módulo Práctica (modo libre) en construcción."
        jump tl_sakura_hub

    if _return == "go_exams":
        $ tl_current_module = "Exámenes"
        "Módulo Exámenes en construcción."
        jump tl_sakura_hub

    if _return == "go_activities":
        $ tl_current_module = "Actividades"
        "Módulo Actividades en construcción."
        jump tl_sakura_hub

    if _return == "go_diary":
        $ tl_current_module = "Diario"
        "Módulo Diario en construcción."
        jump tl_sakura_hub

    if _return == "go_library":
        $ tl_current_module = "Biblioteca"
        "Módulo Biblioteca en construcción."
        jump tl_sakura_hub

    if _return == "to_main":
        jump tl_boot_start

    jump tl_sakura_hub
