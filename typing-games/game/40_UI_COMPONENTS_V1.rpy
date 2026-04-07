# ===========================================================
# 40_UI_COMPONENTS_V1.rpy
# Capa Visual (Fase 3A): componentes reutilizables
# ===========================================================

screen tl_ui_panel_center(title="", points=None):
    $ _points = points if isinstance(points, (list, tuple)) else []

    frame:
        xalign 0.5
        yalign 0.34
        xsize 980
        ysize 360
        background Solid("#151019EE")

        vbox:
            spacing 12
            xalign 0.5
            yalign 0.06

            text "[title]" size 44 color "#FFD7F1" xalign 0.5

            frame:
                xsize 900
                ysize 245
                padding (12, 10)
                background Solid("#221A2CEB")

                viewport:
                    draggable True
                    mousewheel True
                    xmaximum 874
                    ymaximum 220

                    vbox:
                        spacing 8
                        for _line in _points:
                            text "• [_line]" size 24


screen tl_ui_teacher_panel(
    teacher_name="Docente",
    teacher_line="",
    teacher_portrait=None,
    can_continue=False,
    can_advance=False,
    on_continue=None,
    on_advance=None,
    on_back=None
):
    $ _continue_action = on_continue if on_continue is not None else NullAction()
    $ _advance_action = on_advance if on_advance is not None else NullAction()
    $ _back_action = on_back if on_back is not None else Return("back_class")

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
                    if teacher_portrait:
                        add teacher_portrait fit "contain" xalign 0.5 yalign 0.5
                    else:
                        text "Sin retrato" xalign 0.5 yalign 0.5 size 22 color "#E8D9F0"

                frame:
                    xsize 190
                    ysize 34
                    background Solid("#2A2230")
                    text "[teacher_name]" xalign 0.5 yalign 0.5 size 21 color "#FFD7F1"

            vbox:
                spacing 10
                yalign 0.5

                frame:
                    xsize 680
                    ysize 96
                    background Solid("#211A29")
                    text "[teacher_line]" xalign 0.03 yalign 0.5 size 24 color "#F7E8FF"

                hbox:
                    spacing 14
                    textbutton "Continuar" action _continue_action sensitive can_continue
                    textbutton "Avanzar" action _advance_action sensitive can_advance
                    textbutton "Atrás" action _back_action


screen tl_ui_sublesson_selector_panel(
    title="Lección · Submódulos",
    progress_text="Progreso: 0/0 checks",
    entries=None,
    selected_label="Ninguna"
):
    $ _entries = entries if isinstance(entries, (list, tuple)) else []

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1120
        ysize 650
        background Solid("#151019DE")

        hbox:
            spacing 20
            xalign 0.5
            yalign 0.06

            vbox:
                spacing 8
                xsize 620
                text "[title]" size 40 color "#FFD7F1"
                text "[progress_text]" size 24 color "#E8D9F0"

                for row in _entries:
                    textbutton "[row]"

            vbox:
                spacing 14
                xsize 420
                text "Sublección seleccionada" size 30 color "#FFD7F1" xalign 0.5
                frame:
                    xsize 400
                    ysize 210
                    background Solid("#241D2C")
                    text "[selected_label]" xalign 0.5 yalign 0.5 size 24
