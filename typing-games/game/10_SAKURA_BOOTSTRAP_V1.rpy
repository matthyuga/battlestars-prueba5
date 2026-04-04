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

# Rutas de imagen recomendadas (sube tus fondos aquí cuando quieras):
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

    # Capa para contraste
    add Solid("#00000055")

    text "TYPING LEGENDS" xalign 0.5 yalign 0.08 size 68 color "#FFD884" outlines [(2, "#3a2200", 0, 0)]

    textbutton "Epic Spell Academy (Bloqueado)" action NullAction() xalign 0.25 yalign 0.73
    textbutton "Sakura Sunshine Academy" action Return("goto_sakura_gate") xalign 0.74 yalign 0.73

    textbutton "START" action Return("goto_sakura_gate") xalign 0.5 yalign 0.86
    textbutton "SETTINGS" action ShowMenu("preferences") xalign 0.18 yalign 0.95

screen tl_sakura_gate_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/tl/sakura_gate.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"

    add Solid("#00000033")

    text "SAKURA SUNSHINE ACADEMY" xalign 0.5 yalign 0.09 size 56 color "#FFD7F1" outlines [(2, "#5a1d4a", 0, 0)]

    textbutton "ENTER" action Return("register") xalign 0.5 yalign 0.9
    textbutton "Volver" action Return("back") xalign 0.1 yalign 0.93

screen tl_registration_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/tl/sakura_hallway.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"

    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 980
        ysize 560
        background Solid("#1B1524DD")

        vbox:
            spacing 18
            xalign 0.5
            yalign 0.5

            text "Registro de Jugador" xalign 0.5 size 48 color "#FFD7F1"

            hbox:
                spacing 24
                text "Nombre:" size 30
                input value VariableInputValue("tl_player_name") length 20 allow " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZáéíóúÁÉÍÓÚñÑ0123456789_-." xmaximum 520

            text "Sexo del jugador" size 30
            hbox:
                spacing 18
                textbutton "Masculino" action SetVariable("tl_player_gender", "male")
                textbutton "Femenino" action SetVariable("tl_player_gender", "female")
                textbutton "Ninguno" action SetVariable("tl_player_gender", "none")

            text "Modo de experiencia" size 30
            hbox:
                spacing 18
                textbutton "1) Lore desactivado" action SetVariable("tl_experience_mode", 1)
                textbutton "2) Lore normal" action SetVariable("tl_experience_mode", 2)
                textbutton "3) Lore + romance" action SetVariable("tl_experience_mode", 3)

            text "Regla activa: si eliges 'Ninguno', el modo se fuerza a 1 (sin lore ni romance)." size 20 color "#D0BFD6"
            text "Estado actual -> Sexo: [tl_player_gender] | Modo: [tl_experience_mode]" size 22 color "#F6E5FF"

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

    add Solid("#0000005F")

    text "Sakura Sunshine Academy" xalign 0.5 yalign 0.06 size 56 color "#FFD7F1" outlines [(2, "#5a1d4a", 0, 0)]
    text "Jugador: [tl_player_name if tl_player_name else 'Invitado']  |  Sexo: [tl_player_gender]  |  Modo: [tl_experience_mode]" xalign 0.5 yalign 0.13 size 22

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
                    textbutton "Probar Typing Lab" action [Hide("tl_lessons_mock_screen"), Jump("typing_lab_start")]
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
